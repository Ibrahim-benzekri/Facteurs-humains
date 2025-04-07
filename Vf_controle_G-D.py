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

# --- EMG Part ---
def detect_change(prev, curr, threshold=10):
    return abs(curr - prev) > threshold

# Variables globales accessibles dans le jeu
changement_detecte = False
changement_detecte2 = False
# Variables partagées entre threads
shared_state = {
    "gauche": False,
    "droite": False
}


class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__()  # pas d'argument ici !
        self.address = address  # on garde l'adresse pour start()
        self.duration = 0
        self.frequency = 0
        self.prev_value = None
        self.changement_detecte = False
        self.prev_value2 = None
        self.changement_detecte2 = False
        self.i = 0

    def onRawFrame(self, nSeq, data):
        current_value = data[0]
        current_value2 = data[1]

        if self.prev_value is not None and self.prev_value2 is not None:
            if detect_change(self.prev_value, current_value):
                self.changement_detecte = True
                self.changement_detecte2 = False
            elif detect_change(self.prev_value2, current_value2):
                self.changement_detecte2 = True
                self.changement_detecte = False
            else:
                self.changement_detecte = False
                self.changement_detecte2 = False

        self.prev_value = current_value
        self.prev_value2 = current_value2
        #print(f"value : {self.i,self.changement_detecte}")
        self.i += 1
        to_game(self.changement_detecte, self.changement_detecte2)

        return nSeq > self.duration * self.frequency

def to_game(gauche, droite):
    shared_state["gauche"] = gauche
    shared_state["droite"] = droite




def lancer_emg():
    address = "98:D3:51:FE:84:FC"
    device = NewDevice(address)
    device.duration = 9999
    device.frequency = 10
    device.start(device.frequency, [1, 2], 16)  # ✅ Corrigé ici
    device.loop()
    device.stop()
    device.close()





# --- Jeu Pygame ---
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

    running = True
    spawn_timer = 0

    while running:
        dt = clock.tick(60)
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if shared_state["gauche"]:
            rocket_rect.x += 2
        if shared_state["droite"]:
            rocket_rect.x -= 2
        print("gauche:", shared_state["gauche"], "| droite:", shared_state["droite"])
        print("i am here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
       

        rocket_rect.x = max(0, min(WIDTH - rocket_rect.width, rocket_rect.x))

        spawn_timer += dt
        if spawn_timer > 1000 - stress_level * 5:
            spawn_meteor()
            spawn_timer = 0

        for meteor in meteor_list[:]:
            meteor.y += 5
            if meteor.colliderect(rocket_rect):
                damage_taken += 1
                meteor_list.remove(meteor)
                lives -= 1
                if lives <= 0:
                    print("Game Over !")
                    running = False
            elif meteor.y > HEIGHT:
                meteor_list.remove(meteor)

        screen.blit(rocket_img, rocket_rect)
        for meteor in meteor_list:
            screen.blit(meteor_img, meteor)

        draw_stress_bar(stress_level)
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
