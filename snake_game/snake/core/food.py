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
class SpecialFood(Food):
    _loaded_images = []

    @classmethod
    def preload_images(cls, cell_size):
        if not cls._loaded_images:
            image_files = ["apple_sp.png", "grape_sp.png", "banana_sp.png", "orange_sp.png"]
            base_path = "snake/images/special/"
            
            for file_name in image_files:
                full_path = base_path + file_name
                if os.path.exists(full_path):
                    try:
                        img = pygame.image.load(full_path).convert_alpha()
                        img = pygame.transform.scale(img, (cell_size, cell_size))
                        cls._loaded_images.append(img)
                        print(f"Loaded: {file_name}")
                    except Exception as e:
                        print(f"Error loading {file_name}: {e}")
            
            if not cls._loaded_images:
                fallback = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (255, 215, 0), (cell_size//2, cell_size//2), cell_size//2)
                cls._loaded_images.append(fallback)

    def __init__(self, food_manager, bounds, cell_size, snake_body):
        super().__init__(food_manager, bounds, cell_size, snake_body)
        
        if not SpecialFood._loaded_images:
            SpecialFood.preload_images(cell_size)

        self.image = random.choice(SpecialFood._loaded_images)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 10000

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def draw(self, surface):
        t = pygame.time.get_ticks()
        scale = 1.0 + 0.1 * math.sin(t * 0.005)
        base_size = self.image.get_width()
        new_size = int(base_size * scale)
        if new_size < 1: new_size = 1
        
        scaled_img = pygame.transform.scale(self.image, (new_size, new_size))
        
        flash_alpha = int(60 * (1 + math.sin(t * 0.015))) 
        mask = pygame.mask.from_surface(scaled_img)
        white_surf = mask.to_surface(setcolor=(255, 255, 255, flash_alpha), unsetcolor=None)
        scaled_img.blit(white_surf, (0, 0))

        center_x = self.position[0] + self.cell_size // 2
        center_y = self.position[1] + self.cell_size // 2
        rect = scaled_img.get_rect(center=(center_x, center_y))
        surface.blit(scaled_img, rect)