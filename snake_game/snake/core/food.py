import math
import random
import pygame
import os
from snake.settings import CELL_SIZE, FOOD_IMAGES

class Food:
    def __init__(self, width, height, food_manager, header_height=0, snake_body=None):
        self.width = width
        self.height = height
        self.header_height = header_height
        
        if not food_manager.images:
            self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image.fill((255, 0, 0)) 
        else:
            self.image = random.choice(food_manager.images)
        self.position = self.random_pos(snake_body)

    def random_pos(self, snake_body=None):
        cols = (self.width // CELL_SIZE) - 1
        rows = (self.height // CELL_SIZE) - 1
        start_row = self.header_height // CELL_SIZE
        
        if cols < 0: cols = 0
        if rows < 0: rows = 0
        if start_row > rows: start_row = rows

        while True:
            x = random.randint(0, cols) * CELL_SIZE
            y = random.randint(start_row, rows) * CELL_SIZE
            
            if snake_body is None:
                return (x, y)
            
            is_on_snake = False
            for block in snake_body:
                if int(block[0]) == x and int(block[1]) == y:
                    is_on_snake = True
                    break
            
            if not is_on_snake:
                return (x, y)

    def draw(self, surface):
        try:
            t = pygame.time.get_ticks()
            scale = 1.0 + 0.1 * math.sin(t * 0.005)
            new_size = int(CELL_SIZE * scale)
            if new_size < 1: new_size = 1
            scaled_img = pygame.transform.smoothscale(self.image, (new_size, new_size))
            center_x = self.position[0] + CELL_SIZE // 2
            center_y = self.position[1] + CELL_SIZE // 2
            rect = scaled_img.get_rect(center=(center_x, center_y))
            surface.blit(scaled_img, rect)
        except Exception:
            surface.blit(self.image, self.position)

class FoodManager:
    def __init__(self):
        self.images = []
        for img_name in FOOD_IMAGES:
            try:
                path = f"snake/images/foods/{img_name}"
                if os.path.exists(path):
                    loaded_img = pygame.image.load(path).convert_alpha()
                    loaded_img = pygame.transform.scale(loaded_img, (CELL_SIZE, CELL_SIZE))
                    self.images.append(loaded_img)
            except Exception as e:
                print(f"Error loading food {img_name}: {e}")
        if not self.images:
            fallback_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(fallback_surf, (255, 0, 0), (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
            self.images.append(fallback_surf)