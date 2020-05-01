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

def main():
    pygame.init()
    # Caption and Icon
    pygame.display.set_caption('Laundry Simulator')
    icon = pygame.image.load('images/washer/idle/0.png')
    pygame.display.set_icon(icon)
    game_state = GameState.TITLE
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'data/themes/quick_theme.json')
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(manager.ui_theme.get_colour('white'))

    clock = pygame.time.Clock()
    washer_images = load_idle_running_finished_images('images/washer')
    washer = Washer(1, (0, 0), washer_images)
    laundry_image = pygame.image.load('images/laundry.png').convert_alpha()
    blank_image = pygame.image.load('images/blank.png').convert_alpha()
    dryer_images = load_idle_running_finished_images('images/dryer')
    dryer = Dryer(2, (250, 0), dryer_images)

    #images = load_images(path='images/cat/')  # Make sure to provide the relative or full path to the images directory.
    #cat = AnimatedMachine(1,(700, 450), images)
    player = Player(laundry_image, blank_image)
    new_load = Load()
    player.add_load(new_load)
    all_sprites = pygame.sprite.Group(washer, dryer, player)  # Creates a sprite group and adds 'player' to it.
    game_logic = GameLogic([], [], player)

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
                mouse_up = True
            if event.type > pygame.USEREVENT:
                # need add logic for dealing with machines and other things here
                id = event.type - pygame.USEREVENT
                #print(id)
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                pass  # for pygame_gui buttons
            manager.process_events(event)

        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up, game_logic, id)
        manager.update(time_delta)

        screen.blit(background, (0, 0))
        manager.draw_ui(screen)
        all_sprites.draw(screen)
        #if selected_load:
        #    position = pygame.mouse.get_pos()
        #    screen.blit(laundry_image, position)
        pygame.display.update()


class GameLogic:
    # takes in orders array, adjudicates machine and load clicks, starts first event timer for first load
    # (and then for next one
    def __init__(self, orders_array, load_sprites, player):
        self.orders_array = orders_array
        self.load_sprites = load_sprites
        self.player = player

    def adjudicate_machine_click(self, machine):
        machine_load = machine.load
        player_load = self.player.load

        if machine_load and not player_load:
            self.player.add_load(machine.remove_load())
        elif player_load and machine.can_hold(player_load):
            machine.add_load(self.player.remove_load())


def generate_orders(order_num_min, order_num_max, load_num_min, load_num_max, p_soiled=0.0, p_express=0.0, p_large=0.0):
    # Look up pydoc
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

        size = (183, 221)  # This should match the size of the images.

        self.state =MachineState.IDLE
        self.rect = pygame.Rect(position, size)
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

    def update(self, dt, mouse_pos, mouse_up, player, id):
        self.rect = pygame.Rect(mouse_pos, self.size)
        if self.load is not None:
            self.image = self.image_has_laundry
        else:
            self.image = self.image_no_laundry

def load_images(path):
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
        images.append(image)
    return images

def load_idle_running_finished_images(path):
    idle_path = path + '/idle'
    running_path = path + '/running'
    finished_path = path + '/finished'

    idle = load_images(path=idle_path)
    running = load_images(path=running_path)
    finished = load_images(path=finished_path)

    return [idle, running, finished]

if __name__ == "__main__":
    main()
