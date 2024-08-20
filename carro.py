import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *
import serial
import threading

estadoAnterior = False
contador = 0
bpm = 0
o2 = 0

# Configuración de pines GPIO para el sensor
TRC500_PIN = 24  # Ejemplo de pin GPIO para el sensor TRC500

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRC500_PIN, GPIO.IN)

# Inicialización de pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480  # Tamaño de la pantalla táctil
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font_large = pygame.font.SysFont("Arial", 100, bold=False, italic=False)  # Fuente grande para el recuento de pasos
font_small = pygame.font.SysFont("Arial", 15, bold=False, italic=False)  # Fuente pequeña para ritmo, ppm y pulso

# Cargar las imágenes
logo = pygame.image.load("/home/caro/Imágenes/ideal.png")
logo = pygame.transform.scale(logo, (60, 60))
logo_rect = logo.get_rect(midtop=(SCREEN_WIDTH/2, 10))

welnes_logo = pygame.image.load("/home/caro/Imágenes/welnes.png")
new_width = 150
welnes_logo = pygame.transform.scale(welnes_logo, (new_width, int(new_width * welnes_logo.get_height() / welnes_logo.get_width())))
welnes_logo_rect = welnes_logo.get_rect(midtop=(SCREEN_WIDTH/2, logo_rect.bottom + 1))

mts_logo = pygame.image.load("/home/caro/Imágenes/mts.png")
mts_logo = pygame.transform.scale(mts_logo, (100, 100))
mts_logo_rect = mts_logo.get_rect(midleft=(SCREEN_WIDTH - 400, SCREEN_HEIGHT/2.2))

ritmo_logo = pygame.image.load("/home/caro/Imágenes/ritmo.png")
ritmo_logo = pygame.transform.scale(ritmo_logo, (100, 15))
ritmo_logo_rect = ritmo_logo.get_rect(midleft=(SCREEN_WIDTH - 750, mts_logo_rect.bottom + 134))

ppm_logo = pygame.image.load("/home/caro/Imágenes/ppm.png")
ppm_logo = pygame.transform.scale(ppm_logo, (100, 15))
ppm_logo_rect = ppm_logo.get_rect(bottomright=(SCREEN_WIDTH - 500, SCREEN_HEIGHT - 70))

pulso_logo = pygame.image.load("/home/caro/Imágenes/pulso.png")
pulso_logo = pygame.transform.scale(pulso_logo, (100, 15))
pulso_logo_rect = pulso_logo.get_rect(midleft=(SCREEN_WIDTH - 460, welnes_logo_rect.bottom + 287))

bpm_logo = pygame.image.load("/home/caro/Imágenes/bpm.png")
bpm_logo = pygame.transform.scale(bpm_logo, (100, 15))
bpm_logo_rect = bpm_logo.get_rect(midleft=(SCREEN_WIDTH - 300, welnes_logo_rect.bottom + 287))

o2_logo = pygame.image.load("/home/caro/Imágenes/o2.png")
o2_logo = pygame.transform.scale(o2_logo, (100, 15))
o2_logo_rect = o2_logo.get_rect(midleft=(SCREEN_WIDTH - 140, welnes_logo_rect.bottom + 287))

# Configuración del puerto serial
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Ajusta el puerto y la velocidad de baudios según tu configuración

# Función para leer datos del puerto serial
def leer_datos_serial():
    global bpm, o2
    while True:
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8').strip()
            datos = linea.split(', ')
            for dato in datos:
                if 'HR=' in dato:
                    bpm = int(dato.split('=')[1])
                elif 'SPO2=' in dato:
                    o2 = int(dato.split('=')[1])
        time.sleep(1)  # Esperar un segundo entre lecturas para evitar sobrecargar el CPU

# Iniciar el hilo de lectura del puerto serial
hilo_serial = threading.Thread(target=leer_datos_serial, daemon=True)
hilo_serial.start()

# Función para contar los pasos
def contar_pasos():
    inicio = time.time()
    pasos = 0
    metros = 0
    global estadoAnterior
    factor_ritmo = 1
    factor_ppm = 2
    factor_pulso = 3
    
    # Inicializar la pantalla con valores predeterminados
    actualizar_pantalla(0, 0, 0, 0, bpm, o2)
    
    while True:
        estadoActual = GPIO.input(TRC500_PIN)
        tiempo_transcurrido = round(time.time() - inicio)
        minutos = round(tiempo_transcurrido / 60)
        if estadoActual != estadoAnterior:
            pasos += 0.5
            metros = round((pasos / 4), 2)
            ritmo = round((metros * 0.762))
            ppm = 0  # Calcular ppm basado en la cantidad de pasos
            pulso = round((metros * 0.05), 2)  # Calcular pulso basado en la cantidad de pasos
            print("Se ha detectado un paso. Total de pasos:", pasos, "Ritmo:", ritmo, "PPM:", ppm, "Pulso:", pulso, "BPM:", bpm, "O2:", o2)
            actualizar_pantalla(metros, ritmo, minutos, pulso, bpm, o2)
            estadoAnterior = estadoActual
        else:
            # Actualizar la pantalla periódicamente si no se detecta un paso
            actualizar_pantalla(metros, ritmo, minutos, pulso, bpm, o2)
        
        time.sleep(0.2)  # Espera para evitar contar múltiples veces por el mismo paso

# Función para actualizar la pantalla táctil con el recuento de pasos y las imágenes
def actualizar_pantalla(pasos, ritmo_num, ppm_num, pulso_num, bpm_num, o2_num):
    screen.fill((0, 30, 80))

    screen.blit(logo, logo_rect)
    screen.blit(welnes_logo, welnes_logo_rect)
    screen.blit(mts_logo, mts_logo_rect)
    screen.blit(ritmo_logo, ritmo_logo_rect)
    screen.blit(ppm_logo, ppm_logo_rect)
    screen.blit(pulso_logo, pulso_logo_rect)
    screen.blit(bpm_logo, bpm_logo_rect)
    screen.blit(o2_logo, o2_logo_rect)

    texto = font_large.render("" + str(pasos), True, (255, 255, 255))
    text_rect = texto.get_rect(left=SCREEN_WIDTH - 700, centery=SCREEN_HEIGHT / 2)
    screen.blit(texto, text_rect)

    ritmo_text = font_small.render(str(ritmo_num), True, (255, 255, 255))
    ritmo_text_rect = ritmo_text.get_rect(midleft=(ritmo_logo_rect.centerx, ritmo_logo_rect.bottom - 40))
    screen.blit(ritmo_text, ritmo_text_rect)

    ppm_text = font_small.render(str(ppm_num), True, (255, 255, 255))
    ppm_text_rect = ppm_text.get_rect(midright=(ppm_logo_rect.centerx, ppm_logo_rect.bottom - 40))
    screen.blit(ppm_text, ppm_text_rect)

    pulso_text = font_small.render(str(pulso_num), True, (255, 255, 255))
    pulso_text_rect = pulso_text.get_rect(midleft=(pulso_logo_rect.centerx, pulso_logo_rect.bottom - 40))
    screen.blit(pulso_text, pulso_text_rect)

    bpm_text = font_small.render(str(bpm_num), True, (255, 255, 255))
    bpm_text_rect = bpm_text.get_rect(midleft=(bpm_logo_rect.centerx, bpm_logo_rect.bottom - 40))
    screen.blit(bpm_text, bpm_text_rect)

    o2_text = font_small.render(str(o2_num), True, (255, 255, 255))
    o2_text_rect = o2_text.get_rect(midleft=(o2_logo_rect.centerx, o2_logo_rect.bottom - 40))
    screen.blit(o2_text, o2_text_rect)

    pygame.display.flip()

try:
    contar_pasos()
except KeyboardInterrupt:
    GPIO.cleanup()
    pygame.quit()
    ser.close()