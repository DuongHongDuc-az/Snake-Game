import math
import random
import pygame
import os
from snake.settings import FOOD_IMAGES

class Food:
    def __init__(self, food_manager, bounds, cell_size, snake_body=None):
        self.bounds = bounds #(x, y, w, h)
        self.cell_size = cell_size
        
        if not food_manager.images:
            self.image = pygame.Surface((cell_size, cell_size))
            self.image.fill((255, 0, 0)) 
        else:
            self.image = random.choice(food_manager.images)
        self.position = self.random_pos(snake_body)

    def random_pos(self, snake_body=None):
        start_x, start_y, width, height = self.bounds
        cols = width //self.cell_size
        rows = height//self.cell_size

        while True:
            rand_col = random.randint(0, cols-1) 
            rand_row = random.randint(0, rows-1) 
            x = start_x + rand_col*self.cell_size
            y = start_y + rand_row*self.cell_size
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
            base_size = self.image.get_width()
            new_size = int(base_size * scale)
            if new_size < 1: new_size = 1
            scaled_img = pygame.transform.smoothscale(self.image, (new_size, new_size))
            center_x = self.position[0] + self.cell_size // 2
            center_y = self.position[1] + self.cell_size // 2
            rect = scaled_img.get_rect(center=(center_x, center_y))
            surface.blit(scaled_img, rect)
        except Exception:
            surface.blit(self.image, self.position)

class FoodManager:
    def __init__(self, cell_size):
        self.images = []
        for img_name in FOOD_IMAGES:
            try:
                path = f"snake/images/foods/{img_name}"
                if os.path.exists(path):
                    loaded_img = pygame.image.load(path).convert_alpha()
                    loaded_img = pygame.transform.scale(loaded_img, (cell_size, cell_size))
                    self.images.append(loaded_img)
            except Exception as e:
                print(f"Error loading food {img_name}: {e}")
        if not self.images:
            fallback_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(fallback_surf, (255, 0, 0), (self.cell_size//2,self.cell_size//2), self.cell_size//2)
            self.images.append(fallback_surf)