import pygame

#local imports
import constant as c


class Customer(pygame.sprite.Sprite):
    def __init__(self, image_dict, order = None):
        super().__init__()
        self.order = order
        self.state = c.CustomerState.NORMAL
        self.index = 0
        self.image_dict = image_dict
        self.current_time = 0
        self.animation_time = 0.2
        self.image = image_dict[self.state][0]
        self.size = (112,143)
        position = (300,300)
        self.rect = pygame.Rect(position, self.size) #TODO: fix
        self.update_image()
        self.patience = 4

    # TODO: make images for other sprites easier using dictionaries as well
    def update_image(self, dt=0):
        images = self.image_dict[self.state]
        self.index = min(self.index, len(images) - 1)
        self.current_time = self.current_time + dt

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(images)

        self.image = images[self.index]

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        self.update_state(time_delta)
        self.update_image(time_delta)
        game_logic.check_for_order(self)

    def update_state(self, time_delta):
        self.patience -= time_delta/5 #make constant? Or make attribute of different customer types?
        self.patience = max(0, self.patience)
        self.state = c.CustomerState(round(self.patience))

    def get_order(self):
        return self.order

    def receive_order(self, load_array):
        print("got it! :D ")
        return round(self.patience)

# TODO: create different logic for different types of customers
class TestCustomer(Customer):
    def __init__(self, images, order = None):
        super().__init__(images, order)