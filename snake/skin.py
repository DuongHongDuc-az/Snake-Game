import pygame
from snake.settings import CELL_SIZE

class SkinManager:
    def __init__(self, skin_name):
        self.skin_name = skin_name
        self.load_skin()

    def load_skin(self):
        base_path = f"snake/images/snake/{self.skin_name}/"
        self.head_img = pygame.image.load(base_path + "head.png").convert_alpha()
        self.body_img = pygame.image.load(base_path + "body.png").convert_alpha()
        self.head_img = pygame.transform.scale(self.head_img, (CELL_SIZE, CELL_SIZE))
        self.body_img = pygame.transform.scale(self.body_img, (CELL_SIZE, CELL_SIZE))

    def change_skin(self, new_skin):
        self.skin_name = new_skin
        self.load_skin()

