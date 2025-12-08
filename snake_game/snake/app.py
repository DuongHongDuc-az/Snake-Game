import pygame
import sys
import os
import random
from snake.core.snake import Snake
from snake.core.food import Food, FoodManager
from snake.settings import CELL_SIZE, TEXTS
from snake.skin import SkinManager 
import snake.settings as settings

class Game:
    def __init__(self, name_color="Basic_purple"):
        pygame.init()
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        self.header_height = 60 

        self.clock = pygame.time.Clock()
        self.running = True
        
        self.skin_manager = SkinManager(name_color)
        self.random_food = FoodManager()
        self.load_sounds()
        self.speed = settings.SPEED
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
            print(f"Error audio: {e}")

    def reset(self):
        self.snake = Snake(self.skin_manager)
        self.food = Food(self.width, self.height, self.random_food, 
                         header_height=self.header_height, 
                         snake_body=self.snake.body)
        self.score = 0
        self.speed = settings.SPEED
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
            self.running = False 
            return

        self.snake.move()
        
        if self.snake.get_head_pos() == self.food.position:
            self.snake.grow()
            self.food.image = random.choice(self.random_food.images)
            self.food.position = self.food.random_pos(snake_body=self.snake.body)

            self.score += 1
            self.speed +=0.5
            if self.speed > 60:
                self.speed = 60
            if settings.SOUND_ON and self.eat_sound:
                self.eat_sound.set_volume(settings.SOUND_VOLUME)
                self.eat_sound.play()
            return

        head_x, head_y = self.snake.get_head_pos()

        if head_y < self.header_height:
            self.trigger_game_over()
            return

        if self.snake.check_collision(self.width, self.height):
            self.trigger_game_over()

    def trigger_game_over(self):
        if settings.SOUND_ON:
            pygame.mixer.music.stop()
            if self.game_over_sound:
                self.game_over_sound.set_volume(settings.SOUND_VOLUME)
                self.game_over_sound.play()
        self.game_over = True
        self.running = False

    def draw_grass(self):
        grass_color_1 = (167, 209, 61)
        grass_color_2 = (175, 215, 70)
        cell_size = settings.CELL_SIZE
        start_row = self.header_height // cell_size
        
        for row in range (start_row, self.height//cell_size):
            for col in range(self.width//cell_size):
                if (row+col)%2==0:
                    color = grass_color_1
                else:
                    color = grass_color_2
                rect = pygame.Rect(col*cell_size, row*cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_header(self, usn):
        pygame.draw.rect(self.screen, (40, 50, 60), (0, 0, self.width, self.header_height))
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.header_height), (self.width, self.header_height), 2)

        try:
            font = pygame.font.Font("snake/images/font.ttf", 30)
        except:
            font = pygame.font.SysFont("Arial", 30, bold=True)

        try:
            lbl_score = TEXTS[settings.LANGUAGE]["score"]
            lbl_usn = TEXTS[settings.LANGUAGE]["username"]
        except:
            lbl_score = "Score"
            lbl_usn = "User"

        txt_usn = font.render(f"{lbl_usn}: {usn}", True, (200, 200, 200))
        rect_usn = txt_usn.get_rect(left=20, centery=self.header_height//2)
        self.screen.blit(txt_usn, rect_usn)

        txt_score = font.render(f"{lbl_score}: {self.score}", True, (255, 215, 0))
        rect_score = txt_score.get_rect(right=self.width - 20, centery=self.header_height//2)
        self.screen.blit(txt_score, rect_score)

    def draw(self, usn):
        self.draw_grass()
        self.snake.draw(self.screen, self.food.position)
        self.food.draw(self.screen)
        self.draw_header(usn)
        pygame.display.flip()

    def run(self, txt="Player"):
        while self.running:
            self.handle_events()
            self.update()
            self.draw(txt)
            self.clock.tick(self.speed)
        return self.score

if __name__ == "__main__":
    game = Game()
    game.run()