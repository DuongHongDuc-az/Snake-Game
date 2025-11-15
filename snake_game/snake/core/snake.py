import pygame
from snake.settings import CELL_SIZE
from snake.skin import SkinManager
class Snake:
    def __init__(self,skin_manager):
        self.body = [[100, 40], [80, 40], [60, 40]]
        self.direction = "RIGHT"
        self.grow_flag = False
        self.skin_manager = skin_manager


    def change_direction(self, new_direction):
        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_direction != opposite[self.direction]:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            head_y -= CELL_SIZE
        elif self.direction == "DOWN":
            head_y += CELL_SIZE
        elif self.direction == "LEFT":
            head_x -= CELL_SIZE
        elif self.direction == "RIGHT":
            head_x += CELL_SIZE

        new_head = [head_x, head_y]
        self.body.insert(0, new_head)

        if self.grow_flag:
            self.grow_flag = False
        else:
            self.body.pop()

    def grow(self):
        self.grow_flag = True

    
    def draw(self, screen):
        for i, pos in enumerate(self.body):
            if i == 0:
                rotated_head = self.skin_manager.head_img
                if self.direction == "UP":
                    rotated_head = pygame.transform.rotate(rotated_head, 90)
                elif self.direction == "DOWN":
                    rotated_head = pygame.transform.rotate(rotated_head, -90)
                elif self.direction == "LEFT":
                    rotated_head = pygame.transform.rotate(rotated_head, 180)
                screen.blit(rotated_head, pos)
            else:
                screen.blit(self.skin_manager.body_img, pos)



    def get_head_pos(self):
        return tuple(self.body[0])

    def check_collision(self, width, height):
        head_x, head_y = self.body[0]
        if head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            return True
        if [head_x, head_y] in self.body[1:]:
            return True
        return False

