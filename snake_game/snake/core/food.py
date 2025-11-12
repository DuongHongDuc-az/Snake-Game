import random
import pygame
from snake.settings import CELL_SIZE,RED

class Food:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = self.random_pos()

    def random_pos(self):
        x = random.randint(0, (self.width - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.height - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        return (x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (*self.position, CELL_SIZE, CELL_SIZE))
