import pygame
import sys
import random
from   snake.core.snake    import Snake
from   snake.core.food     import Food,FoodManager
from   snake.settings      import CELL_SIZE
from   snake.skin          import SkinManager 
from snake.settings import CELL_SIZE, TEXTS
import snake.settings as settings
class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.skin_manager = SkinManager("Basic_purple")
        self.snake = Snake(self.skin_manager)
        self.random_food = FoodManager()
        self.food = Food(self.width, self.height,self.random_food)
        self.score = 0
        self.reset()
       
    def reset(self):
        self.snake = Snake(self.skin_manager)
        self.food = Food(self.width, self.height, self.random_food)
        self.score = 0
        self.game_over = False
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction("UP")
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction("DOWN")
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction("RIGHT")

    def update(self):
        if self.game_over:
            self.manager.switch_scene('intro')
            return
        self.snake.move()
        if self.snake.get_head_pos() == self.food.position:
            self.snake.grow()
            self.food.image = random.choice(self.random_food.images)
            self.food.position = self.food.random_pos()
            self.score += 1
            return

        if self.snake.check_collision(self.width, self.height):
            self.running = False

    def draw(self, usn):
        self.screen.fill((0, 0, 0))
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        font = pygame.font.SysFont(None, 36)
        lbl_score = TEXTS[settings.LANGUAGE]["score"]
        lbl_usn = TEXTS[settings.LANGUAGE]["username"]
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        usn = font.render(f"Username: {usn}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(usn, (10, 40))
        pygame.display.flip()


    def run(self, txt):
        while self.running:
            self.handle_events()
            self.update()
            self.draw(txt)
            self.clock.tick(15)
        return self.score
          

if __name__ == "__main__":
    game = Game()
    game.run()