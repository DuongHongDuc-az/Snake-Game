import pygame
import math
from snake.settings import CELL_SIZE
from snake.skin import SkinManager
class Snake:
    def __init__(self, skin_manager):
        self.body = [[640, 360], [640, 380], [640, 400]]
        self.direction = "RIGHT"
        self.grow_flag = False
        self.skin_manager = skin_manager
        
        # Cấu hình hiệu ứng thè lưỡi
        self.tongue_interval = 3000  # Thè lưỡi mỗi 3000ms (3 giây)

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

    def draw_tongue(self, screen):
        current_time = pygame.time.get_ticks()
        
        if current_time % self.tongue_interval < 200:
            head_x, head_y = self.body[0]
            
            center_x = head_x + CELL_SIZE // 2
            center_y = head_y + CELL_SIZE // 2
            
            tongue_color = (255, 50, 50) 
            tongue_length = 12           
            tongue_width = 3          
            
            start_pos = (center_x, center_y)
            end_pos = start_pos 
            
            if self.direction == "UP":
                start_pos = (center_x, head_y + 5)
                end_pos = (center_x, head_y - tongue_length)
            elif self.direction == "DOWN":
                start_pos = (center_x, head_y + CELL_SIZE - 5)
                end_pos = (center_x, head_y + CELL_SIZE + tongue_length)
            elif self.direction == "LEFT":
                start_pos = (head_x + 5, center_y)
                end_pos = (head_x - tongue_length, center_y)
            elif self.direction == "RIGHT":
                start_pos = (head_x + CELL_SIZE - 5, center_y)
                end_pos = (head_x + CELL_SIZE + tongue_length, center_y)
            pygame.draw.line(screen, tongue_color, start_pos, end_pos, tongue_width)
    def draw(self, screen, food_pos=None):
        self.draw_tongue(screen)
        open_mouth = False
        if food_pos:
            head_x, head_y = self.body[0]
            distance = math.hypot(head_x - food_pos[0], head_y - food_pos[1])
            if distance < CELL_SIZE*4:
                open_mouth = True
        for i, pos in enumerate(self.body):
            if i == 0:
                head_surf = self.skin_manager.head_img.copy()
                if open_mouth:
                    w,h  = head_surf.get_size()
                    mouth_color = (50, 0, 0)
                    points = [
                        (w, h//2),
                        (w, 0),
                        (w-w//2, h//2),
                        (w, h)
                    ]
                    pygame.draw.polygon(head_surf, mouth_color, points)
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

