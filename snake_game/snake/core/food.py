import math
import random
import pygame
import os
from snake.settings import FOOD_IMAGES

class Food:
    def __init__(self, food_manager, bounds, cell_size, snake_body=None):
        self.bounds = bounds 
        self.cell_size = cell_size
        self.image = random.choice(food_manager.images) if food_manager.images else self._get_fallback()
        self.position = self.random_pos(snake_body)

    def _get_fallback(self):
        s = pygame.Surface((self.cell_size, self.cell_size))
        s.fill((255, 0, 0))
        return s

    def random_pos(self, snake_body=None):
        start_x, start_y, width, height = self.bounds
        cols, rows = width // self.cell_size, height // self.cell_size

        while True:
            x = start_x + random.randint(0, cols - 1) * self.cell_size
            y = start_y + random.randint(0, rows - 1) * self.cell_size
            
            if snake_body is None or [x, y] not in snake_body:
                return (x, y)

    def draw(self, surface):
        t = pygame.time.get_ticks()
        scale = 1.0 + 0.1 * math.sin(t * 0.005)
        new_size = max(1, int(self.image.get_width() * scale))
        
        try:
            scaled = pygame.transform.smoothscale(self.image, (new_size, new_size))
            center = (self.position[0] + self.cell_size//2, self.position[1] + self.cell_size//2)
            surface.blit(scaled, scaled.get_rect(center=center))
        except:
            surface.blit(self.image, self.position)

class FoodManager:
    def __init__(self, cell_size):
        self.images = []
        base = "snake/images/foods/"
        for name in FOOD_IMAGES:
            try:
                if os.path.exists(base + name):
                    img = pygame.image.load(base + name).convert_alpha()
                    self.images.append(pygame.transform.scale(img, (cell_size, cell_size)))
            except: pass
        
        if not self.images:
            fallback = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            pygame.draw.circle(fallback, (255, 0, 0), (cell_size//2, cell_size//2), cell_size//2)
            self.images.append(fallback)

class SpecialFood(Food):
    _loaded_images = []

    @classmethod
    def preload_images(cls, cell_size):
        if cls._loaded_images: return
        
        names = ["apple_sp.png", "grape_sp.png", "banana_sp.png", "orange_sp.png"]
        base = "snake/images/special/"
        for name in names:
            try:
                if os.path.exists(base + name):
                    img = pygame.image.load(base + name).convert_alpha()
                    cls._loaded_images.append(pygame.transform.scale(img, (cell_size, cell_size)))
            except: pass

        if not cls._loaded_images:
            fb = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            pygame.draw.circle(fb, (255, 215, 0), (cell_size//2, cell_size//2), cell_size//2)
            cls._loaded_images.append(fb)

    def __init__(self, food_manager, bounds, cell_size, snake_body):
        super().__init__(food_manager, bounds, cell_size, snake_body)
        if not SpecialFood._loaded_images: SpecialFood.preload_images(cell_size)
        self.image = random.choice(SpecialFood._loaded_images)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 10000

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def draw(self, surface):
        t = pygame.time.get_ticks()
        new_size = max(1, int(self.image.get_width() * (1.0 + 0.1 * math.sin(t * 0.005))))
        scaled = pygame.transform.scale(self.image, (new_size, new_size))
        
        mask = pygame.mask.from_surface(scaled)
        white = mask.to_surface(setcolor=(255, 255, 255, int(60 * (1 + math.sin(t * 0.015)))), unsetcolor=None)
        scaled.blit(white, (0, 0))

        center = (self.position[0] + self.cell_size//2, self.position[1] + self.cell_size//2)
        surface.blit(scaled, scaled.get_rect(center=center))