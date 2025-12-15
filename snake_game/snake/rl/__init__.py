import pygame
import sys
import os
import random
import math
from snake.core.snake import Snake
from snake.core.food import Food, FoodManager, SpecialFood
from snake.skin import SkinManager
import numpy as np
import snake.settings as settings
from snake.rl.train_dqn import train

SPEED = 60

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
        
        self.skin_manager = SkinManager(name_color, self.cell_size)
        self.random_food = FoodManager(self.cell_size)
        SpecialFood.preload_images(self.cell_size)
        self.load_sounds()
        self.speed = SPEED
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
        self.speed = SPEED
        self.game_over = False
        self.frame_iteration = 0
        if settings.SOUND_ON:
            try:
                pygame.mixer.music.play(-1)
            except: pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            # else:
            #     self.snake.handle_input(event)

    def is_collision(self, bounds, pt=None):
        if pt is None:
            pt = self.snake.body[0]
        bx, by, bw, bh = bounds

        if pt[0] < bx or pt[0] >= bx + bw or pt[1] < by or pt[1] >= by + bh:
            return True

        if [pt[0], pt[1]] in self.snake.body[1:]:
            return True

        return False

    def get_move(self, action):
        clock_wise = ["RIGHT", "DOWN", "LEFT", "UP"]
        idx = clock_wise.index(self.snake.direction)

        if np.array_equal(action, [1, 0, 0]):
            nxt_idx = idx
        elif np.array_equal(action, [0, 1, 0]):
            nxt_idx = (idx + 1) % 4
        else:
            nxt_idx = (idx - 1) % 4
        new_dir = clock_wise[nxt_idx]

        self.snake.change_direction(new_dir)
        return self.update()

    def update(self):
        self.frame_iteration += 1
        # if self.game_over:
        #     Game.reset(self)
        #     self.game_over = False
        #     return

        self.snake.move()

        reward = 0
        if self.special_food:
            if self.special_food.is_expired():
                self.special_food = None
            elif self.snake.check_eat(self.special_food.position, is_special=True):
                self.score += 5
                reward = 20
                if self.speed > 60: self.speed = 60
                
                self.special_food = None
                if settings.SOUND_ON and self.eat_sound:
                    self.eat_sound.play()

        if self.snake.check_eat(self.food.position, is_special=False):
            self.food.image = random.choice(self.random_food.images)
            self.food.position = self.food.random_pos(snake_body=self.snake.body)

            self.score += 1
            reward = 10
            if self.speed > 60: self.speed = 60
            
            if self.special_food is None and random.random() < 0.25:
                self.special_food = SpecialFood(self.random_food, self.bounds, self.cell_size, self.snake.body)

            if settings.SOUND_ON and self.eat_sound:
                self.eat_sound.play()
            return reward, self.game_over, self.score

        if self.is_collision(self.bounds) or self.frame_iteration > 500*self.snake.length:
            reward = -10
            self.trigger_game_over()
            return reward, self.game_over, self.score
        return reward, self.game_over, self.score

    def trigger_game_over(self):
        if settings.SOUND_ON:
            pygame.mixer.music.stop()
            if self.game_over_sound:
                self.game_over_sound.set_volume(settings.SOUND_VOLUME)
                self.game_over_sound.play()
        self.game_over = True

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
            lbl_score = settings.TEXTS[settings.LANGUAGE]["score"]
            lbl_usn = settings.TEXTS[settings.LANGUAGE]["username"]
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
        
        sp_pos = self.special_food.position if self.special_food else None
        self.snake.draw(self.screen, self.food.position, sp_pos)
        
        self.food.draw(self.screen)
        self.draw_header(usn)
        pygame.display.flip()

    def run(self, txt="Player"):
        train(self)
        return self.score

def main(player_name="AI"):
    game = Game()
    score = game.run(player_name)
    return score

__all__ = ["Game", "main"]
