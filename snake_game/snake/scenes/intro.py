import pygame
import sys
from snake.settings import play_pos, option_pos, exit_pos, FONT_NAME

class Button:
    def __init__(self, pos, button_name, text):
        base_path = f"snake/images/scence_images/{button_name}"
        self.image = pygame.transform.scale(pygame.image.load(base_path), (200, 50))
        self.rect = self.image.get_rect(center=pos)

        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def is_hover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class UI:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.background = pygame.transform.scale(pygame.image.load("snake/images/scence_images/background.jpg"), (self.width, self.height))
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        # Tạo các nút
        self.btn1 = Button(play_pos, "button.png", "PLAY")
        self.btn2 = Button(option_pos, "button.png", "OPTION")
        self.btn3 = Button(exit_pos, "button.png", "EXIT")

    def run(self):
        while self.running:
            self.screen.blit(self.background, (0, 0))
            self.btn1.draw(self.screen)
            self.btn2.draw(self.screen)
            self.btn3.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                if self.btn1.is_clicked(event):
                    return 1
                if self.btn2.is_clicked(event):
                    return 2
                if self.btn3.is_clicked(event):
                    return 0


