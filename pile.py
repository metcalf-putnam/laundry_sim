import pygame

# Local imports
import constant as c
import laundry


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
            new_sprite = laundry.PilePiece((self.x_pos, y), pile_images, type)
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