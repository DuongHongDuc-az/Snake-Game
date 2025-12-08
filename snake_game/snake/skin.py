import pygame

class SkinManager:
    def __init__(self, skin_name, cell_size):
        self.skin_name = skin_name
        self.cell_size = cell_size  #
        self.load_skin()

    def load_skin(self):
        base_path = f"snake/images/snake/{self.skin_name}/"
        try:
            self.head_img = pygame.image.load(base_path + "head.png").convert_alpha()
            self.body_img = pygame.image.load(base_path + "body.png").convert_alpha()
        except:
            self.head_img = pygame.Surface((self.cell_size, self.cell_size))
            self.head_img.fill((0, 255, 0))
            self.body_img = pygame.Surface((self.cell_size, self.cell_size))
            self.body_img.fill((0, 200, 0))

        self.head_img = pygame.transform.smoothscale(self.head_img, (self.cell_size, self.cell_size))
        self.body_img = pygame.transform.smoothscale(self.body_img, (self.cell_size, self.cell_size))

    def change_skin(self, new_skin):
        self.skin_name = new_skin
        self.load_skin()