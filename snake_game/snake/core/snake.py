import pygame
import math
from snake.skin import SkinManager

class Snake:
    def __init__(self, skin_manager, start_pos, cell_size):
        self.cell_size = cell_size
        x, y = start_pos
        self.body = [[x, y], [x - cell_size, y], [x - 2*cell_size, y]]
        self.direction = "RIGHT"
        
        self.grow_counter = 0
        self.skin_manager = skin_manager
        self.tongue_interval = 3000
        self.can_change_dir = True 

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.change_direction("UP")
            elif event.key == pygame.K_DOWN:
                self.change_direction("DOWN")
            elif event.key == pygame.K_LEFT:
                self.change_direction("LEFT")
            elif event.key == pygame.K_RIGHT:
                self.change_direction("RIGHT")

    def change_direction(self, new_direction):
        if not self.can_change_dir:
            return

        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_direction != opposite[self.direction]:
            self.direction = new_direction
            self.can_change_dir = False

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            head_y -= self.cell_size
        elif self.direction == "DOWN":
            head_y += self.cell_size
        elif self.direction == "LEFT":
            head_x -= self.cell_size
        elif self.direction == "RIGHT":
            head_x += self.cell_size

        new_head = [head_x, head_y]
        self.body.insert(0, new_head)

        if self.grow_counter > 0:
            self.grow_counter -= 1 
        else:
            self.body.pop()
            
        self.can_change_dir = True

    def check_eat(self, food_pos, is_special=False):
        if self.get_head_pos() == food_pos:
            if is_special:
                for _ in range(3):
                    self.grow()
            else:
                self.grow()
            return True
        return False

    def grow(self):
        self.grow_counter += 1

    def draw_tongue(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time % self.tongue_interval < 200:
            head_x, head_y = self.body[0]
            cs = self.cell_size
            center_x = head_x + cs // 2
            center_y = head_y + cs // 2
            tongue_color = (255, 50, 50) 
            start_pos = (center_x, center_y)
            end_pos = start_pos 
            
            offset_short = max(1, cs // 4)
            offset_long = max(1, int(cs * 0.6))

            if self.direction == "UP":
                start_pos = (center_x, head_y + offset_short)
                end_pos = (center_x, head_y - offset_long)
            elif self.direction == "DOWN":
                start_pos = (center_x, head_y + cs - offset_short)
                end_pos = (center_x, head_y + cs + offset_long)
            elif self.direction == "LEFT":
                start_pos = (head_x + offset_short, center_y)
                end_pos = (head_x - offset_long, center_y)
            elif self.direction == "RIGHT":
                start_pos = (head_x + cs - offset_short, center_y)
                end_pos = (head_x + cs + offset_long, center_y)
            pygame.draw.line(screen, tongue_color, start_pos, end_pos, max(1, cs // 7))

    def draw(self, screen, food_pos, special_food_pos=None):
        self.draw_tongue(screen)
        
        target = food_pos
        head_x, head_y = self.body[0]
        
        if special_food_pos:
            dist_normal = math.hypot(head_x - food_pos[0], head_y - food_pos[1])
            dist_special = math.hypot(head_x - special_food_pos[0], head_y - special_food_pos[1])
            if dist_special < dist_normal:
                target = special_food_pos

        open_mouth = False
        if target:
            distance = math.hypot(head_x - target[0], head_y - target[1])
            if distance < self.cell_size * 4:
                open_mouth = True
        
        for i, pos in enumerate(self.body):
            if i == 0:
                head_surf = self.skin_manager.head_img.copy()
                if open_mouth:
                    w,h  = head_surf.get_size()
                    pygame.draw.polygon(head_surf, (50, 0, 0), [(w, h//2), (w, 0), (w-w//2, h//2), (w, h)])
                rotated_head = head_surf
                if self.direction == "UP": rotated_head = pygame.transform.rotate(rotated_head, 90)
                elif self.direction == "DOWN": rotated_head = pygame.transform.rotate(rotated_head, -90)
                elif self.direction == "LEFT": rotated_head = pygame.transform.rotate(rotated_head, 180)
                screen.blit(rotated_head, pos)
            else:
                screen.blit(self.skin_manager.body_img, pos)

    def get_head_pos(self):
        return tuple(self.body[0])

    def check_collision(self, bounds):
        head_x, head_y = self.body[0]
        bx, by, bw, bh = bounds
        
        if head_x < bx or head_x >= bx + bw or head_y < by or head_y >= by + bh:
            return True
        
        if [head_x, head_y] in self.body[1:]:
            return True
            
        return False