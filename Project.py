import pygame
import random
import sys
import threading
import plux  # Bibliothèque pour les capteurs PLUX

# Initialisation Pygame
pygame.init()

# Fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape")

# Horloge
clock = pygame.time.Clock()

# Chargement des images
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

rocket_img = pygame.image.load("assets/rocket.png").convert_alpha()
rocket_img = pygame.transform.scale(rocket_img, (50, 70))
rocket_rect = rocket_img.get_rect(center=(WIDTH // 2, HEIGHT - 80))

meteor_img = pygame.image.load("assets/meteore.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (40, 40))

# Liste des météores
meteor_list = []

def spawn_meteor():
    x = random.randint(0, WIDTH - 40)
    rect = meteor_img.get_rect(topleft=(x, -40))
    meteor_list.append(rect)

# Stress (simulé)
stress_level = 30

# Variables globales pour le contrôle
changement_detecte = False
changement_detecte2 = False

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__(address)
        self.duration = 0
        self.frequency = 0
        self.prev_value = None
        self.changement_detecte = False
        self.prev_value2 = None
        self.changement_detecte2 = False

    def onRawFrame(self, nSeq, data):
        global changement_detecte, changement_detecte2
        current_value = data[0]
        current_value2 = data[1]

        # Détection de changement
        if self.prev_value is not None and self.prev_value2 is not None:
            if detect_change(self.prev_value, current_value):
                changement_detecte = True
                changement_detecte2 = False
            elif detect_change(self.prev_value2, current_value2):
                changement_detecte2 = True
                changement_detecte = False
            else:
                changement_detecte = False
                changement_detecte2 = False

        self.prev_value = current_value
        self.prev_value2 = current_value2

        return nSeq > self.duration * self.frequency

def start_sensor_thread():
    """Lance l'acquisition des capteurs dans un thread séparé"""
    device = NewDevice("98:D3:51:FE:84:FC")
    device.duration = 20  # Acquisition de 20 secondes
    device.frequency = 10  # 10 échantillons par seconde
    device.start(device.frequency, [1, 2], 16)
    device.loop()  
    device.stop()
    device.close()

# Démarrer le thread du capteur
threading.Thread(target=start_sensor_thread, daemon=True).start()

# Boucle de jeu
running = True
spawn_timer = 0

while running:
    dt = clock.tick(60)
    screen.blit(background_img, (0, 0))

    # Événements Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Déplacement de la fusée avec les capteurs
    if changement_detecte:
        rocket_rect.x -= 5
    elif changement_detecte2:
        rocket_rect.x += 5

    # Bordures
    rocket_rect.x = max(0, min(WIDTH - rocket_rect.width, rocket_rect.x))

    # Météores
    spawn_timer += dt
    if spawn_timer > 1000 - stress_level * 5:
        spawn_meteor()
        spawn_timer = 0

    for meteor in meteor_list[:]:
        meteor.y += 5
        if meteor.colliderect(rocket_rect):
            print("Touché !")
            meteor_list.remove(meteor)
        elif meteor.y > HEIGHT:
            meteor_list.remove(meteor)

    # Affichage
    screen.blit(rocket_img, rocket_rect)
    for meteor in meteor_list:
        screen.blit(meteor_img, meteor)

    pygame.display.flip()

# Quitter
pygame.quit()
sys.exit()
