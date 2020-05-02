import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, has_laundry_image, no_has_laundry_image):
        super().__init__()
        self.image_has_laundry = has_laundry_image
        self.image_no_laundry = no_has_laundry_image
        self.image = self.image_no_laundry
        position = pygame.mouse.get_pos()
        self.size = (92, 67)
        self.rect = pygame.Rect(position, self.size)
        self.load = None

    def remove_load(self):
        load = self.load
        self.load = None
        return load

    def add_load(self, load):
        self.load = load

    def update(self, dt, mouse_pos, mouse_up, game_logic, id):
        self.rect = pygame.Rect(mouse_pos, self.size)
        if self.load is not None:
            self.image = self.image_has_laundry
        else:
            self.image = self.image_no_laundry