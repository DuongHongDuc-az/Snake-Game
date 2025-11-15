
import random
import pygame
from snake.settings import CELL_SIZE,FOOD_IMAGES

class Food:
    def __init__(self, width, height,food_manager):
        self.width = width
        self.height = height
        self.image = random.choice(food_manager.images)
        self.position = self.random_pos()

    def random_pos(self):
        x = random.randint(0, (self.width - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.height - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        return (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.position)


class FoodManager:
    def __init__(self):
        self.images = [pygame.transform.scale(
            pygame.image.load(f"snake/images/foods/{img}").convert_alpha(),
            (CELL_SIZE, CELL_SIZE)
        ) for img in FOOD_IMAGES]
        
