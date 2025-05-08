import pygame
import random
import threading
import time
import platform
import sys

osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
if platform.mac_ver()[0] != "":
    import subprocess
    from os import linesep

    p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8").split(str("\t"))[2].split(linesep)[0]
    if result.startswith("12."):
        print("macOS version is Monterrey!")
        osDic["Darwin"] = "MacOS/Intel310"
        if (
            int(platform.python_version().split(".")[0]) <= 3
            and int(platform.python_version().split(".")[1]) < 10
        ):
            print(f"Python version required is ≥ 3.10. Installed is {platform.python_version()}")
            exit()

sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")
import plux

def normalize(val, min_val=400, max_val=900):
    return max(0, min(100, int((val - min_val) / (max_val - min_val) * 100)))


# --- EMG Part ---
def detect_change(prev, curr, threshold=10):
    return abs(curr - prev) > threshold

# Variables partagées entre threads
shared_state = {
    "gauche": False,
    "droite": False,
    "tir": False,
    "stress" : False,
     "respiration": 0  
    
}

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__()
        self.address = address
        self.duration = 0
        self.frequency = 0
        self.prev_value = None
        self.prev_value2 = None

    def onRawFrame(self, nSeq, data):
        current_value = data[0]
        current_value2 = data[1]
        stress_raw = data[2]
        print(shared_state["respiration"])
        print(stress_raw)
        stress_level = normalize(stress_raw)
        shared_state["respiration"] = stress_level

        changement_detecte = False
        changement_detecte2 = False

        if self.prev_value is not None and self.prev_value2 is not None:
            if detect_change(self.prev_value, current_value):
                changement_detecte = True
            if detect_change(self.prev_value2, current_value2):
                changement_detecte2 = True

        self.prev_value = current_value
        self.prev_value2 = current_value2
        shared_state["stress"] = stress_level > 70 

       

        to_game(changement_detecte, changement_detecte2)

        return nSeq > self.duration * self.frequency


def to_game(gauche, droite):
    shared_state["gauche"] = gauche
    shared_state["droite"] = droite
    shared_state["tir"] = gauche and droite  # tir if both activated

def lancer_emg():
    address = "98:D3:51:FE:84:FC"
    device = NewDevice(address)
    device.duration = 9999
    device.frequency = 10
    device.start(device.frequency, [1, 2,3], 16)
    device.loop()
    device.stop()
    device.close()

def lancer_jeu():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Escape")
    clock = pygame.time.Clock()

    background_img = pygame.image.load("assets/background.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    rocket_img = pygame.image.load("assets/rocket.png").convert_alpha()
    rocket_img = pygame.transform.scale(rocket_img, (50, 70))
    rocket_rect = rocket_img.get_rect(center=(WIDTH // 2, HEIGHT - 80))

    meteor_img = pygame.image.load("assets/meteore.png").convert_alpha()
    meteor_img = pygame.transform.scale(meteor_img, (40, 40))

    heart_img = pygame.image.load("assets/heart.png").convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (30, 30))

    meteor_list = []

    def spawn_meteor():
        x = random.randint(0, WIDTH - 40)
        rect = meteor_img.get_rect(topleft=(x, -40))
        meteor_list.append(rect)

    stress_level = 30
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

    # Projectiles
    projectiles = []
    PROJECTILE_SPEED = 10
    PROJECTILE_WIDTH, PROJECTILE_HEIGHT = 5, 10

    running = True
    spawn_timer = 0

    while running:
        dt = clock.tick(60)
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Déplacement capteurs
        if shared_state["gauche"]:
            rocket_rect.x += 2
        if shared_state["droite"]:
            rocket_rect.x -= 2

        # Tir si les deux activés
        if shared_state["tir"]:
            projectile_rect = pygame.Rect(
                rocket_rect.centerx - PROJECTILE_WIDTH // 2,
                rocket_rect.top,
                PROJECTILE_WIDTH,
                PROJECTILE_HEIGHT
            )
            projectiles.append(projectile_rect)
            shared_state["tir"] = False  # Reset tir

        rocket_rect.x = max(0, min(WIDTH - rocket_rect.width, rocket_rect.x))

        # Météores
        spawn_timer += dt
        meteor_spawn_interval = 1000 - stress_level * 5

        # Ajout : boost si stress détecté
        if shared_state.get("stress", False):
            meteor_spawn_interval -= 300  # accélération spawn

        if spawn_timer > meteor_spawn_interval:
            spawn_meteor()
            spawn_timer = 0

        for meteor in meteor_list[:]:
            meteor.y += 5 if not shared_state.get("stress", False) else 8  # vitesse augmentée si stress
            if meteor.colliderect(rocket_rect):
                damage_taken += 1
                meteor_list.remove(meteor)
                lives -= 1
                if lives <= 0:
                    print("Game Over !")
                    running = False
            elif meteor.y > HEIGHT:
                meteor_list.remove(meteor)

        # Projectiles movement
        for projectile in projectiles[:]:
            projectile.y -= PROJECTILE_SPEED
            if projectile.y < 0:
                projectiles.remove(projectile)

        # Collision projectiles <-> meteors
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

        draw_stress_bar(shared_state["respiration"])
        draw_lives(lives)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


# --- Lancement ---
if __name__ == "__main__":
    emg_thread = threading.Thread(target=lancer_emg)
    emg_thread.daemon = True
    emg_thread.start()

    lancer_jeu()
