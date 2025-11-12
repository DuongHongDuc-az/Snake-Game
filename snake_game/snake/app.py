import pygame
import sys
import random
from snake.core.snake import Snake
from snake.core.food import Food

CELL_SIZE = 20  

class Game:
    def _init_(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        
        self.clock = pygame.time.clock()
        self.running = True
        self.snake = Snake()
        self.food = Food(self.width, self.height)
        self.socre = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction("UP")
                elif event.type == pygame.K_DOWN:
                    self.snake.change_direction("DOWN")
                elif event.type == pygame.K_LEFT:
                    self.snake.change_direction("LEFT")
                elif event.type == pygame.K_RIGHT:
                    self.snake.change_direction("RIGHT")
    def random_pos(self, occupied):
        while True:
            x = random.randrange(0, self.width // CELL_SIZE)*CELL_SIZE
            y = random.randrange(0, self.height // CELL_SIZE)*CELL_SIZE
            if [x, y] not in occupied:
                return [x, y]
    def update(self):
        self.snake.move()
        if self.snake.get_head_pos() == self.food.position:
            self.snake.grow()
            self.food.position = self.food.random_pos(self.snake.body)
            self.score += 1
            if self.snake.check_collision(self.width, self.height):
                self.running = False
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.snake.draw(self.screen)
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(15)
        pygame.quit()
        sys.exit()
            