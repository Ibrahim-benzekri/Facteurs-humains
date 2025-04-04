import pygame
import random
import sys
import threading


# Initialisation
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

# Variable de contrôle
control_input = "stop"

def control_listener():
    """Écoute les entrées dans la console pour contrôler la fusée"""
    global control_input
    while True:
        cmd = input("Commande (left, right, stop) : ").strip().lower()
        if cmd in ["left", "right", "stop"]:
            control_input = cmd

# Lancer l'écoute des commandes dans un thread séparé
threading.Thread(target=control_listener, daemon=True).start()

# Boucle de jeu
running = True
spawn_timer = 0

while running:
    dt = clock.tick(60)
    screen.blit(background_img, (0, 0))

    # Événements pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôler la fusée via la variable `control_input`
    if control_input == "left":
        rocket_rect.x -= 5
    elif control_input == "right":
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

