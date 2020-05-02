import enum
from random import random, randint
import os

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
import pygame_gui

WASHER_TIME = 3500  # milliseconds
DRYER_TIME = 4500  # milliseconds
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 100 #frames per second
FAIL_STATE = pygame.USEREVENT + 500
WHITE = (255, 255, 255)
MACHINE_SIZE = (108, 130)
GAMELOGICEVENT = pygame.USEREVENT
LEVEL_TIME = 30_000

# TODO: make outgoing orders get picked up
# TODO: add money/profit text in corner
# TODO: add large washers/dryers / large loads
# TODO: animation when finish load and/or earn money
# TODO: add level clock and "game over" screen

def main():
    pygame.init()

    # Caption and Icon
    pygame.display.set_caption('Laundry Simulator')
    icon = pygame.image.load('images/washer/idle/0.png')
    pygame.display.set_icon(icon)

    # Initializing game essentials
    game_state = GameState.TITLE
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'data/themes/quick_theme.json')
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(manager.ui_theme.get_colour('white'))
    clock = pygame.time.Clock()

    # Make washers
    washer_images = load_idle_running_finished_images('images/washer')
    washer_group = pygame.sprite.Group()
    id = 1
    for col in range(2):
        for row in range(2):
            washer = Washer(id, (MACHINE_SIZE[0]*col, MACHINE_SIZE[1]*row), washer_images)
            washer_group.add(washer)
            id += 1

    # Make dryers
    dryer_images = load_idle_running_finished_images('images/dryer')
    dryer_group = pygame.sprite.Group()
    for col in range(2):
        for row in range(2):
            dryer = Dryer(id, (round(MACHINE_SIZE[0]*(col+2)), MACHINE_SIZE[1]*row), dryer_images)
            dryer_group.add(dryer)
            id += 1

    # Images for player and laundry piles
    load_in_out_image = pygame.image.load('images/load_in_out.png').convert_alpha()
    free_spot_image = pygame.image.load('images/free_spot.png').convert_alpha()
    laundry_image = pygame.image.load('images/laundry.png').convert_alpha()
    blank_image = pygame.image.load('images/blank.png').convert_alpha()

    # TODO: make more dynamic/adjustable labels based on position of piles
    # Labels for laundry piles
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    pile_in_label = font.render('inbox', True, WHITE)
    pile_in_rect = pile_in_label.get_rect()
    pile_in_rect.bottomleft = (10, SCREEN_HEIGHT)
    pile_out_label = font.render('outbox', True, WHITE)
    pile_out_rect = pile_out_label.get_rect()
    pile_out_rect.bottomright = (SCREEN_WIDTH-8, SCREEN_HEIGHT)

    # Initializing input and output laundry piles
    pile_in = Pile(10, 7, load_in_out_image, free_spot_image, LaundryState.UNWASHED)
    pile_out = Pile(SCREEN_WIDTH-105, 7, load_in_out_image, free_spot_image, LaundryState.DRIED)

    # Initializing player
    player = Player(laundry_image, blank_image)
    #new_load = Load()
    #player.add_load(new_load)  #for debug/testing purposes

    # Generating orders
    orders = generate_orders(order_num_min=8, order_num_max=8, load_num_min=1, load_num_max=1)

    # Storing all sprites to master group
    all_sprites = pygame.sprite.Group(washer_group, dryer_group, pile_in, pile_out, player)
    game_logic = GameLogic(orders, pile_in, pile_out, player)

    running = True
    while running:
        id = 0
        time_delta = clock.tick(FPS) / 1000.0  # 60 frames per second
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                print("click!!!")
                print("the current time is: " + str(pygame.time.get_ticks()))
                mouse_up = True
            if event.type > pygame.USEREVENT:
                id = event.type - pygame.USEREVENT
                print(id)
            if event.type == pygame.USEREVENT:
                print("Ooo! An order!")
                game_logic.handle_event()
            manager.process_events(event) # gui manager

        # Updating objects
        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up, game_logic, id)
        pile_in.update_y_pos()
        pile_out.update_y_pos()
        #manager.update(time_delta)

        # Drawing background, sprites, and labels
        screen.blit(background, (0, 0))
        manager.draw_ui(screen)
        screen.blit(pile_in_label, pile_in_rect)
        screen.blit(pile_out_label, pile_out_rect)
        all_sprites.draw(screen)

        # Updating display with the latest
        pygame.display.update()


class GameLogic:
    # takes in orders array, adjudicates machine and load clicks, starts first event timer for first load
    # (and then for next one
    def __init__(self, orders_array, pile_in, pile_out, player):
        self.orders_array = orders_array
        self.pile_in = pile_in
        self.pile_out = pile_out
        self.player = player

        self.set_timer_for_order()

    def set_timer_for_order(self):
        time_buffer = 500
        current_time = pygame.time.get_ticks()
        print("current time: " + str(current_time))
        cycle_time = WASHER_TIME + DRYER_TIME + time_buffer*5
        max_ = LEVEL_TIME - current_time - cycle_time
        min_ = time_buffer
        range = max_ - min_

        if self.orders_array and len(self.orders_array) > 0:
            relative_max = range//len(self.orders_array) + min_
            random_eta = 3000#randint(min_, relative_max)
            pygame.time.set_timer(GAMELOGICEVENT, random_eta, True)
            print("set timer for: " + str(random_eta))
        else:
            print("that was the last order scheduled!")

    def handle_event(self):
        print("Hey, that's my event! :D")
        if self.orders_array and len(self.orders_array) > 0:
            order = self.orders_array.pop()
            print("sending an order with " + str(len(order.loads)) + " loads to input pile")
            self.pile_in.add_order(order)
            print("orders remainings: " +  str(len(self.orders_array)))
            self.set_timer_for_order()
        else:
            print("I gots no more orders :(")
        print("current time: " + str(pygame.time.get_ticks()))

    def adjudicate_machine_click(self, machine):
        # Called when player clicks on a machine
        machine_load = machine.load
        player_load = self.player.load

        if machine_load and not player_load:
            self.player.add_load(machine.remove_load())
        elif player_load and machine.can_hold(player_load):
            machine.add_load(self.player.remove_load())

    def adjudicate_pile_click(self, animated_load):
        # Called when player clicks on a laundry pile
        player_load = self.player.load
        pile_load = animated_load.load
        print("adjudicator ")
        if pile_load and not player_load:
            print("if statement met!")
            self.player.add_load(animated_load.remove_load())
        elif player_load and not pile_load:
            print("elif met!")
            if player_load.state is animated_load.type:
                animated_load.add_load(self.player.remove_load())

def generate_orders(order_num_min, order_num_max, load_num_min, load_num_max, p_soiled=0.0, p_express=0.0, p_large=0.0):
    # function to set cue of customers for a given level, making it easy to incorporate some amount
    # of randomness to level design
    orders = []
    num_orders = randint(order_num_min, order_num_max)
    for i in range(num_orders):
        loads = generate_loads(load_num_min, load_num_max, p_soiled, p_large)
        is_express = sample_uniform(p_express)
        ord_ = Order(loads, sample_uniform(is_express))
        orders.append(ord_)
    return orders


def generate_loads(min_load, max_load, p_soiled, p_large):
    # generates a random number of loads, with given probabilities of being soiled or large
    loads = []
    num_loads = randint(min_load, max_load)
    for i in range(num_loads):
        is_soiled = sample_uniform(p_soiled)
        is_large = sample_uniform(p_large)
        load = Load(is_soiled, is_large)
        loads.append(load)
    return loads


def sample_uniform(percentage):
    # helper function to randomly assign a variable to true or false, dependent on probability
    if random() <= percentage:
        return True
    else:
        return False


class Order:
    def __init__(self, loads, express=False):
        self.loads = loads
        self.express = express
    # add patience attribute?


class Size(enum.Enum):
    SMALL = 0
    NORMAL = 1
    LARGE = 2


class Load:
    # single load of laundry
    def __init__(self, soiled=False, size=Size.NORMAL):
        self.soiled = soiled
        self.size = size
        self.state = LaundryState.UNWASHED

    def get_washed(self):
        self.state = LaundryState.WASHED

    def get_dried(self):
        self.state = LaundryState.DRIED


class LaundryState(enum.Enum):
    UNWASHED = 0
    WASHED = 1
    DRIED = 2


class MachineState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2


class AnimatedMachine(pygame.sprite.Sprite):

    def __init__(self, id, position, images, size=Size.NORMAL):
        """
        Animated machine object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation, sorted into an array of arrays
        """
        super().__init__()

        self.state =MachineState.IDLE
        self.rect = pygame.Rect(position, MACHINE_SIZE)
        self.images_idle = images[0]
        self.images_running = images[1]
        self.images_finished = images[2]
        self.index = 0
        self.image = self.images_idle[self.index]  # 'image' is the current image of the animation.

        self.velocity = pygame.math.Vector2(0, 0)

        self.animation_time = 0.2
        self.current_time = 0

        self.animation_frames = 6
        self.current_frame = 0

        self.id = id
        self.time = 0  # milliseconds
        self.event = pygame.USEREVENT + id  # custom event when machine is done
        self.load = None

    # TODO: if will start multiple events from machines, need way to keep track of
    # (right now just assuming all events are the loads being finished)
    def handle_event(self):
        self.state = MachineState.FINISHED

    def add_load(self, load):
        if self.load is None and self.state is MachineState.IDLE:
            self.__start__(load)
            print('load added!')


    def remove_load(self):
        # attempt to retrieve load from machine (only possible if done -- may change in future)
        print("I see you want your washed clothes back")
        if self.state is MachineState.FINISHED:
            load = self.load
            self.load = None
            self.state = MachineState.IDLE
            print("you may have them back!")
            return load

    def __start__(self, load):
        self.load = load

        pygame.time.set_timer(self.event, self.time, True)  # true == only set once
        self.state = MachineState.RUNNING

    def update_time_dependent(self, dt):
        """
        Updates the image of Sprite approximately every 0.1 second.

        Args:
            dt: Time elapsed between each frame.
        """
        if self.state is MachineState.IDLE:
            images = self.images_idle
        elif self.state is MachineState.RUNNING:
            images = self.images_running
        else:
            images = self.images_finished

        self.index = min(self.index, len(images)-1)

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(images)

        self.image = images[self.index]

    def update_frame_dependent(self):
        """
        Updates the image of Sprite every 6 frame (approximately every 0.1 second if frame rate is 60).
        """
        if self.velocity.x > 0:  # Use the right images if sprite is moving right.
            self.images = self.images_right
        elif self.velocity.x < 0:
            self.images = self.images_left

        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.rect.move_ip(*self.velocity)

    def update(self, dt, mouse_pos, mouse_up, game_logic, id):
        """ Updates the mouse_over variable and returns the button's
            action value when clicked.
        """
        if id == self.id:
            self.handle_event()
        if self.rect.collidepoint(mouse_pos) and mouse_up:
            #this sprite was clicked
            game_logic.adjudicate_machine_click(self)

        # Switch between the two update methods by commenting/uncommenting.
        self.update_time_dependent(dt)
        # self.update_frame_dependent()


class Washer(AnimatedMachine):
    def __init__(self, id, position, images, size = Size.NORMAL):
        super().__init__(id, position, images)
        self.time = WASHER_TIME

    # TODO: add custom add_load function that checks if load is not soiled?

    def handle_event(self):
        self.load.get_washed()
        print("all clean now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is LaundryState.UNWASHED:
            super().add_load(load)
        if load.state is LaundryState.WASHED and self.load is None:
            print("adding load back for safe keeping")
            self.load = load
            self.state = MachineState.FINISHED

    def can_hold(self, load):
        unwashed = load.state is LaundryState.UNWASHED
        washed = load.state is LaundryState.WASHED
        print(unwashed)
        if self.load is None and (unwashed or washed) and self.state is MachineState.IDLE:
            return True
        return False


# TODO: dryer vs. washer vs. generic machine logic
# also, do we want player to be able to take clothes out prematurely? For a bit of a ding to score/profit?
# What about being able to wash soiled clothes before pre-treatment?
class Dryer(AnimatedMachine):
    def __init__(self, id, position, images, size = Size.NORMAL):
        super().__init__(id, position, images)
        self.time = DRYER_TIME

    def handle_event(self):
        self.load.get_dried()
        print("all dry now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is LaundryState.WASHED:
            super().add_load(load)
        if load.state is LaundryState.DRIED and self.load is None:
            self.load = load
            self.state = MachineState.FINISHED

    def can_hold(self, load):
        washed = load.state is LaundryState.WASHED
        dried = load.state is LaundryState.DRIED
        if self.load is None and (washed or dried) and self.state is MachineState.IDLE:
            return True
        return False


class GameState(enum.Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    NEXTLEVEL = 2


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


def load_images(path, scale = None):
    """
    Loads all images in directory. The directory must only contain images.

    Args:
        path: The relative or absolute path to the directory to load images from.

    Returns:
        List of images.
    """
    images = []
    for file_name in os.listdir(path):
        image = pygame.image.load(path + os.sep + file_name).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        images.append(image)
    return images


def load_idle_running_finished_images(path):
    idle_path = path + '/idle'
    running_path = path + '/running'
    finished_path = path + '/finished'

    idle = load_images(path=idle_path, scale=MACHINE_SIZE)
    running = load_images(path=running_path, scale=MACHINE_SIZE)
    finished = load_images(path=finished_path, scale=MACHINE_SIZE)

    return [idle, running, finished]


class AnimatedLoad(pygame.sprite.Sprite):
    def __init__(self, position, occupied_image, empty_image, type, load = None):
        super().__init__()
        self.empty_image = empty_image
        self.occupied_image = occupied_image
        self.type = type
        if load is None:
            self.image = empty_image
        else:
            self.image = occupied_image #TODO: add more visuals for different laundry states
        self.load = load
        self.size = (92, 31)
        self.rect = pygame.Rect(position, self.size)

    def update(self, time_delta, mouse_pos, mouse_up, game_logic, id):
        if self.rect.collidepoint(mouse_pos) and mouse_up:
            # this sprite was clicked
            print("id: " + str(id))
            game_logic.adjudicate_pile_click(self)
        self.update_image()

    def update_image(self):
        if self.load is None:
            self.image = self.empty_image
        else:
            self.image = self.occupied_image

    def change_pos(self, pos):
        self.rect = pygame.Rect(pos, self.size)

    def add_load(self, load):
        if self.load is None:
            print("adding load to pile!")
            self.load = load
            self.update_image()

    def remove_load(self):
        load = self.load
        self.load = None
        self.update_image()
        print("removing load from pile!")
        return load


class PileType(enum.Enum):
    IN = 0
    OUT = 1


class Pile(pygame.sprite.OrderedUpdates):
    def __init__(self, x_pos, size, occupied_image, empty_image, type):
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
            y = SCREEN_HEIGHT - i*self.height - round(self.offset*self.height)
            new_sprite = AnimatedLoad((self.x_pos, y), occupied_image, empty_image, type)
            self.add(new_sprite)
            self.free_sprites.add(new_sprite)

    def update_y_pos(self):
        #need to change to use self.check_free_sprites()
        i = 0
        self.check_free_sprites()
        for animated_load in self.occupied_sprites:
            y = SCREEN_HEIGHT - self.height * i - round(self.offset*self.height)
            animated_load.change_pos((self.x_pos, y))
            i += 1

        for animated_load in self.free_sprites:
            y = SCREEN_HEIGHT - self.height * i - round(self.offset*self.height)
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
            pygame.event.post(FAIL_STATE)

    def add_order(self, order):
        self.check_free_sprites()
        for load in order.loads:
            self.add_load(load)
        self.update_y_pos()

if __name__ == "__main__":
    main()
