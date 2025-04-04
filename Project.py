import platform
import sys
import pygame  # Import de Pygame

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
# Fonction de détection de changement
def detect_change(prev, curr, threshold=10):  # à ajuster selon l’amplitude de ton signal
    return abs(curr - prev) > threshold
# Fonction pour créer l'écran de jeu avec Pygame
def create_game_screen(val,val2, screen, font, screen_width, screen_height):
    """
    Crée l'écran de jeu avec Pygame et met à jour l'affichage en fonction de la moyenne.
    """
    # Remplir l'écran avec une couleur de fond
    screen.fill((255, 255, 255))  # fond blanc

    # Choisir la couleur du texte selon la moyenne
    if val:
        text = font.render("Droite", True, (0, 255, 0))  # Texte vert
    elif val2:
        text = font.render("Gauche", True, (0, 255, 0))  # Texte vert
    else:
        text = font.render("Repos", True, (255, 0, 0))  # Texte rouge

    # Placer le texte au centre de l'écran
    text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(text, text_rect)

    # Mettre à jour l'affichage
    pygame.display.flip()


class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        plux.SignalsDev.__init__(address)
        self.duration = 0
        self.frequency = 0
        self.prev_value = None
        self.changement_detecte = False
        self.prev_value2 = None
        self.changement_detecte2 = False
        self.i=0
        
    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        current_value = data[0]
        current_value2 = data[1]
        #print(f"value : {data[0]} , {data[1]}")
        # Détection de changement
        if self.prev_value is not None and self.prev_value2 is not None:
            if detect_change(self.prev_value, current_value):
                self.changement_detecte = True
                self.changement_detecte2 = False
            elif detect_change(self.prev_value2,current_value2):
                 self.changement_detecte2 = True
                 self.changement_detecte = False
            else:     
                 self.changement_detecte = False
                 self.changement_detecte2 = False   

        self.prev_value = current_value
        self.prev_value2 = current_value2
        print(f"value : {self.i,self.changement_detecte}")
        self.i=self.i+1
        # Affichage
        create_game_screen(self.changement_detecte,self.changement_detecte2, screen, font, screen_width, screen_height)

        return nSeq > self.duration * self.frequency


# example routines

def exampleAcquisition(
    address="98:D3:51:FE:84:FC",
    duration=20,
    frequency=10,
    active_ports=[1, 2, 3, 4, 5, 6],
):  # time acquisition for each frequency
    """
    Example acquisition.
    """
    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    
    # Trigger the start of the data recording: https://www.downloads.plux.info/apis/PLUX-API-Python-Docs/classplux_1_1_signals_dev.html#a028eaf160a20a53b3302d1abd95ae9f1
    device.start(device.frequency, active_ports, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


if __name__ == "__main__":
    # Initialisation de Pygame
    pygame.init()

    # Taille de la fenêtre
    screen_width = 400
    screen_height = 200
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Vérification Moyenne")

    # Police pour le texte
    font = pygame.font.SysFont("Arial", 48)

    # Utilisation des arguments du terminal (si présents) comme arguments d'entrée
    exampleAcquisition(*sys.argv[1:])

    # Fermeture de Pygame à la fin
    pygame.quit()
