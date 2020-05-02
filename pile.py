import pygame

# Local imports
import constant as c

class Pile(pygame.sprite.OrderedUpdates):
    def __init__(self, x_pos, size, pile_images, type):
        #whatever init you need to represent a bunch of orders/loads/whatever
        super().__init__()
        self.size = size
        self.x_pos = x_pos
        self.height = 31
        self.offset = 2.2
        self.type = type
        self.free_sprites = pygame.sprite.Group()
        self.occupied_sprites = pygame.sprite.Group()

        for i in range(size):
            y = c.SCREEN_HEIGHT - i*self.height - round(self.offset*self.height)
            new_sprite = AnimatedLoad((self.x_pos, y), pile_images, type)
            self.add(new_sprite)
            self.free_sprites.add(new_sprite)

    def update_y_pos(self):
        i = 0
        self.check_free_sprites()
        for animated_load in self.occupied_sprites:
            y = c.SCREEN_HEIGHT - self.height * i - round(self.offset*self.height)
            animated_load.change_pos((self.x_pos, y))
            i += 1

        for animated_load in self.free_sprites:
            y = c.SCREEN_HEIGHT - self.height * i - round(self.offset*self.height)
            animated_load.change_pos((self.x_pos, y))
            i += 1

    def check_free_sprites(self):
        for animated_load in self:
            if animated_load.load is not None:
                self.free_sprites.remove(animated_load)
                self.occupied_sprites.add(animated_load)
            else:
                self.occupied_sprites.remove(animated_load)
                self.free_sprites.add(animated_load)

    def add_load(self, load):
        if self.free_sprites and len(self.free_sprites) > 0:
            #TODO: make a more sensical way of grabbing the first free sprite
            for animated_load in self.free_sprites:
                animated_load.add_load(load)
                self.free_sprites.remove(animated_load)
                return
        else:
            pygame.event.post(pygame.event.Event(c.FAIL_STATE))

    def add_order(self, order):
        self.check_free_sprites()
        for load in order.loads:
            self.add_load(load)
        self.update_y_pos()


class AnimatedLoad(pygame.sprite.Sprite):
    def __init__(self, position, images, type, load = None):
        super().__init__()
        self.empty_images = images[0]
        self.unwashed_images = images[1]
        self.washed_images = images[2]
        self.dried_images = images[3]
        self.type = type
        self.animation_time = 0.2
        self.current_time = 0
        self.index = 0
        self.image = self.empty_images[self.index]

        self.load = load
        self.size = (92, 31)
        self.rect = pygame.Rect(position, self.size)

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        if self.rect.collidepoint(mouse_pos) and mouse_up:
            # this sprite was clicked
            print("id: " + str(id))
            game_logic.adjudicate_pile_click(self)
        self.update_image(time_delta)

    def update_image(self, dt):
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
            print("adding load to pile!")
            self.load = load
            self.update_image(0)

    def remove_load(self):
        load = self.load
        self.load = None
        self.update_image(0)
        print("removing load from pile!")
        return load