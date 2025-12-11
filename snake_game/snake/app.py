import pygame
import sys
import os
import random
import math
from snake.core.snake import Snake
from snake.core.food import Food, FoodManager, SpecialFood
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
        mode_name, grid_cols, grid_rows = settings.GRID_MODES[settings.GRID_INDEX]
        available_w = self.width
        available_h = self.height - self.header_height
        cell_w = available_w // grid_cols
        cell_h = available_h // grid_rows
        self.cell_size = min(cell_w, cell_h)
        self.play_width = self.cell_size * grid_cols
        self.play_height = self.cell_size * grid_rows
        self.offset_x = (self.width - self.play_width) // 2
        self.offset_y = self.header_height + (available_h - self.play_height) // 2
        self.bounds = (self.offset_x, self.offset_y, self.play_width, self.play_height)

        self.clock = pygame.time.Clock()
        self.running = True
        
        self.skin_manager = SkinManager(name_color,self.cell_size )
        self.random_food = FoodManager(self.cell_size)
        SpecialFood.preload_images(self.cell_size)
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
        start_col = (self.play_width // self.cell_size) // 2
        start_row = (self.play_height // self.cell_size) // 2
        start_x = self.offset_x + start_col * self.cell_size
        start_y = self.offset_y + start_row * self.cell_size
        self.snake = Snake(self.skin_manager,(start_x, start_y), self.cell_size)
        self.food = Food(self.random_food, self.bounds, self.cell_size, snake_body=self.snake.body)
        self.special_food = None
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
        
        if self.special_food:
            if self.special_food.is_expired():
                self.special_food = None
            elif self.snake.get_head_pos() == self.special_food.position:
                self.score += 5                 
                self.speed += 0.5  
                if self.speed > 60: self.speed = 60
                
                for _ in range(3): 
                    self.snake.grow()
                
                self.special_food = None
                if settings.SOUND_ON and self.eat_sound:
                    self.eat_sound.play()

        if self.snake.get_head_pos() == self.food.position:
            self.snake.grow()
            
            self.food.image = random.choice(self.random_food.images)
            self.food.position = self.food.random_pos(snake_body=self.snake.body)

            self.score += 1
            self.speed += 0.5
            if self.speed > 60: self.speed = 60
            
            if self.special_food is None and random.random() < 0.25:
                self.special_food = SpecialFood(self.random_food, self.bounds, self.cell_size, self.snake.body)

            if settings.SOUND_ON and self.eat_sound:
                self.eat_sound.play()
            return

        if self.snake.check_collision(self.bounds):
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
        grass_color_1 = (60, 90, 40)
        grass_color_2 = (80, 110, 55)
        self.screen.fill((30, 30, 30))
        cols = self.play_width // self.cell_size
        rows = self.play_height // self.cell_size
        
        for row in range (rows):
            for col in range(cols):
                if (row+col)%2==0:
                    color = grass_color_1
                else:
                    color = grass_color_2
                rect_x = self.offset_x + col * self.cell_size
                rect_y = self.offset_y + row * self.cell_size
                rect = pygame.Rect(rect_x, rect_y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.bounds, 2)
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
        
        if self.special_food:
            self.special_food.draw(self.screen)
        
        target_pos = self.food.position
        
        if self.special_food:
            head_x, head_y = self.snake.get_head_pos()
            dist_normal = math.hypot(head_x - self.food.position[0], head_y - self.food.position[1])
            dist_special = math.hypot(head_x - self.special_food.position[0], head_y - self.special_food.position[1])
            
            if dist_special < dist_normal:
                target_pos = self.special_food.position
        
        self.snake.draw(self.screen, target_pos)
        
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