import os
import random
import pygame
from snake.settings import CELL_SIZE, FOOD_COLOR

class Food:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        IMAGE_PATH = os.path.join(BASE_DIR, "images", "food.png")
        self.image = pygame.image.load(IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.position = self.random_pos()

    def random_pos(self):
        x = random.randint(0, (self.width - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.height - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        return (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.position)
