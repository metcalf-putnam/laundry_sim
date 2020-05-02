import pygame
import constant as c


class Player(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.empty_images = images[0]
        self.unwashed_images = images[1]
        self.washed_images = images[2]
        self.dried_images = images[3]
        self.animation_time = 0.2
        self.current_time = 0
        self.index = 0
        self.image = self.empty_images[self.index]
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
        if self.load is None:
            images = self.empty_images
        else:
            if self.load.state is c.LaundryState.UNWASHED:
                images = self.unwashed_images
            elif self.load.state is c.LaundryState.WASHED:
                images = self.washed_images
            else:
                images = self.dried_images

        self.index = min(self.index, len(images) - 1)

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(images)

        self.image = images[self.index]