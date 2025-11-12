import pygame
from snake.settings import CELL_SIZE, GREEN
class Snake:
    def __init__(self):
        # Rắn bắt đầu với 3 đoạn
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = "RIGHT"
        self.grow_flag = False

    def change_direction(self, new_direction):
        # Không cho quay 180 độ
        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_direction != opposite[self.direction]:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            head_y -= 10
        elif self.direction == "DOWN":
            head_y += 10
        elif self.direction == "LEFT":
            head_x -= 10
        elif self.direction == "RIGHT":
            head_x += 10

        # thêm đầu mới
        new_head = [head_x, head_y]
        self.body.insert(0, new_head)

        # nếu không ăn thì xóa đuôi
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def grow(self):
        self.grow_flag = True

    def draw(self, screen):
        for pos in self.body:
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))

    def get_head_pos(self):
        return self.body[0]

    def check_collision(self, width, height):
        head_x, head_y = self.body[0]
        # Va chạm tường
        if head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            return True
        # Va chạm thân
        if [head_x, head_y] in self.body[1:]:
            return True
        return False
