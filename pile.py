import pygame

# Local imports
import constant as c
import laundry


class Pile(pygame.sprite.OrderedUpdates):
    def __init__(self, x_pos, size, pile_images, type):
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
            # Comment: You can store round(self.offset*self.height) into a variable to avoid recomputing it
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
        if self.free_sprites:
            next_sprite = next(iter(self.free_sprites))
            next_sprite.add_load(load)
            self.free_sprites.remove(next_sprite)
            self.occupied_sprites.add(next_sprite)
        else:
            pygame.event.post(pygame.event.Event(c.FAIL_STATE))

    def add_order(self, order):
        self.check_free_sprites()
        for load in order.loads:
            self.add_load(load)
        self.update_y_pos()

    def get_order(self, order):
        num_loads = len(order.loads)
        count = 0
        customer_order = pygame.sprite.Group()
        for pile_piece in self.occupied_sprites:
            if pile_piece.load in order.loads:
                print("got one load!")
                count += 1
                customer_order.add(pile_piece)
        if count == num_loads:
            return customer_order
        return None