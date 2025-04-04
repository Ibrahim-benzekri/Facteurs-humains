import pygame
import random
import sys

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

# Stress (simulé pour l’instant)
stress_level = 30  # entre 0 et 100

def draw_stress_bar(level):
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, level * 2, 20))
    pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)
    font = pygame.font.SysFont(None, 20)
    text = font.render(f"Stress: {level}%", True, (255, 255, 255))
    screen.blit(text, (220, 10))

# Boucle de jeu
running = True
spawn_timer = 0

while running:
    dt = clock.tick(60)
    screen.blit(background_img, (0, 0))

    # Événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôles (simule pression main gauche/droite avec flèches)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rocket_rect.x -= 5
    if keys[pygame.K_RIGHT]:
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

    draw_stress_bar(stress_level)

    pygame.display.flip()

# Quitter
pygame.quit()
sys.exit()
