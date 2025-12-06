import pygame
import sys
import os
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
        self.load_sounds()
        self.reset()
    def load_sounds(self):
        self.eat_sound = None
        self.game_over_sound = None
        sound_dir = "snake/sound/"
        try:
            if os.path.exists(sound_dir + "eat.mp3"):
                self.eat_sound = pygame.mixer.Sound(sound_dir + "eat.mp3")
            if os.path.exists(sound_dir + "gameover.mp3"):
                self.game_over_sound = pygame.mixer.Sound(sound_dir + "gameover.mp3")
            if os.path.exists(sound_dir + "bg_music.mp3"):
                pygame.mixer.music.load(sound_dir + "bg_music.mp3")
                pygame.mixer.music.set_volume(0.3)
        except Exception as e:
            print(f"Error aduio: {e}")
    def reset(self):
        self.snake = Snake(self.skin_manager)
        self.food = Food(self.width, self.height, self.random_food)
        self.score = 0
        self.game_over = False
        if settings.SOUND_ON:
            try:
                pygame.mixer.music.play(-1)
            except: pass
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
            if settings.SOUND_ON and self.eat_sound:
                self.eat_sound.set_volume(settings.SOUND_VOLUME)
                self.eat_sound.play()
            return

        if self.snake.check_collision(self.width, self.height):
            if settings.SOUND_ON:
                pygame.mixer.music.stop()
                if self.game_over_sound:
                    self.game_over_sound.set_volume(settings.SOUND_VOLUME)
                    self.game_over_sound.play()
            self.running = False
    def draw_grass(self):
        grass_color_1 = (167, 209, 61)
        grass_color_2 = (175, 215, 70)
        cell_size = settings.CELL_SIZE
        for row in range (self.height//cell_size):
            for col in range(self.width//cell_size):
                if (row+col)%2==0:
                    color = grass_color_1
                else:
                    color = grass_color_2
                rect = pygame.Rect(col*cell_size, row*cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)
    def draw(self, usn):
        self.draw_grass()
        self.snake.draw(self.screen, self.food.position)
        self.food.draw(self.screen)
        font = pygame.font.SysFont(None, 36)
        lbl_score = TEXTS[settings.LANGUAGE]["score"]
        lbl_usn = TEXTS[settings.LANGUAGE]["username"]
        score_text = font.render(f"{lbl_score}: {self.score}", True, (255, 255, 255))
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