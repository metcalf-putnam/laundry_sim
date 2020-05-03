import pygame

# Local imports
import constant as c


class Load:
    # single load of laundry
    def __init__(self, soiled=False, size=c.Size.NORMAL):
        self.soiled = soiled
        self.size = size
        self.state = c.LaundryState.UNWASHED

    def get_washed(self):
        self.state = c.LaundryState.WASHED

    def get_dried(self):
        self.state = c.LaundryState.DRIED


class AnimatedLoad(pygame.sprite.Sprite):
    def __init__(self, position, images, load = None):
        super().__init__()
        self.empty_images = images[0]
        self.unwashed_images = images[1]
        self.washed_images = images[2]
        self.dried_images = images[3]
        self.animation_time = 0.2
        self.current_time = 0
        self.index = 0
        self.image = self.empty_images[self.index] #default to empty
        self.load = load
        self.size = (92, 31)
        self.rect = pygame.Rect(position, self.size)
        self.update_image()

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        self.update_image(time_delta)

    def update_image(self, dt=0):
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

    def change_pos(self, pos):
        self.rect = pygame.Rect(pos, self.size)

    def add_load(self, load):
        if self.load is None:
            self.load = load
            self.update_image(dt=0)

    def remove_load(self):
        load = self.load
        self.load = None
        self.update_image(dt=0)
        return load


class PilePiece(AnimatedLoad):
    def __init__(self, position, images, type, load = None):
        super().__init__(position, images, load)
        self.type = type

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        if self.rect.collidepoint(mouse_pos) and mouse_up:
            # this sprite was clicked
            print("id: " + str(id))
            game_logic.adjudicate_pile_click(self)
        self.update_image(time_delta)


class Player(AnimatedLoad):
    def __init__(self, images):
        position = pygame.mouse.get_pos()
        super().__init__(position, images)
        self.size = (92, 67)
        self.rect = pygame.Rect(position, self.size)

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        self.change_pos(mouse_pos)
        self.update_image(time_delta)