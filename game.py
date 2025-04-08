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

heart_img = pygame.image.load("assets/heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))

# Liste des météores
meteor_list = []

def spawn_meteor():
    x = random.randint(0, WIDTH - 40)
    rect = meteor_img.get_rect(topleft=(x, -40))
    meteor_list.append(rect)

# Liste des projectiles
projectiles = []
PROJECTILE_SPEED = 10
PROJECTILE_WIDTH, PROJECTILE_HEIGHT = 5, 10

# Stress (simulé pour l’instant)
stress_level = 30  # entre 0 et 100

# Vies du joueur
lives = 5
damage_taken = 0

def draw_stress_bar(level):
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, level * 2, 20))
    pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)
    font = pygame.font.SysFont(None, 20)
    text = font.render(f"Stress: {level}%", True, (255, 255, 255))
    screen.blit(text, (220, 10))

def draw_lives(lives):
    for i in range(lives):
        screen.blit(heart_img, (10 + i * 40, 40))

# Boucle de jeu
running = True
spawn_timer = 0

while running:
    dt = clock.tick(60)
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rocket_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        rocket_rect.x += 5
    if keys[pygame.K_q]:
        projectile_rect = pygame.Rect(
            rocket_rect.centerx - PROJECTILE_WIDTH // 2,
            rocket_rect.top,
            PROJECTILE_WIDTH,
            PROJECTILE_HEIGHT
        )
        projectiles.append(projectile_rect)

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
            damage_taken += 1
            meteor_list.remove(meteor)
            lives -= 1
            if lives <= 0:
                print("Game Over !")
                running = False
        elif meteor.y > HEIGHT:
            meteor_list.remove(meteor)

    # Mouvement des projectiles
    for projectile in projectiles[:]:
        projectile.y -= PROJECTILE_SPEED
        if projectile.y < 0:
            projectiles.remove(projectile)

    # Collision projectiles <-> météores
    for projectile in projectiles[:]:
        for meteor in meteor_list[:]:
            if projectile.colliderect(meteor):
                meteor_list.remove(meteor)
                projectiles.remove(projectile)
                break

    # Affichage
    screen.blit(rocket_img, rocket_rect)

    for meteor in meteor_list:
        screen.blit(meteor_img, meteor)

    for projectile in projectiles:
        pygame.draw.rect(screen, (255, 255, 0), projectile)

    draw_stress_bar(stress_level)
    draw_lives(lives)

    pygame.display.flip()

# Quitter
pygame.quit()
sys.exit()
