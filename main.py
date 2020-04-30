import enum
from random import random, randint
import os

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
import pygame_gui

WASHER_TIME = 60 # milliseconds
DRYER_TIME = 45 # milliseconds
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main():
    pygame.init()

    # Caption and Icon
    pygame.display.set_caption('Laundry Simulator')
    icon = pygame.image.load('washing-machine.png')
    pygame.display.set_icon(icon)
    game_state = GameState.TITLE
    window_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'data/themes/quick_theme.json')
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(manager.ui_theme.get_colour('dark_bg'))

    hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 280), (150, 40)),
                                                text='Hello',
                                                manager=manager,
                                                object_id='boohohoa')

    clock = pygame.time.Clock()
    my_machines = dict()
    loads = dict()
    id = 1
    test_washer = Washer(id)
    my_machines[id] = test_washer
    washer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0,0), (150, 200)),
                                                text='IMMA WASHER',
                                                manager=manager,
                                                object_id='washer_1')

    id = 2
    test_dryer = Dryer(id)
    my_machines[id] = test_dryer
    dryer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400,0), (150, 200)),
                                                text='IMMA DRYER',
                                                manager=manager,
                                                object_id='dryer_2')
    test_load = Load()
    loads[1] = test_load
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 500), (100, 50)),
                                               text='LAUNDRY',
                                               manager=manager,
                                               object_id='load_1')
    selected_load = None

    images = load_images(path='cat/')  # Make sure to provide the relative or full path to the images directory.
    player = AnimatedSprite(position=(700, 450), images=images)
    all_sprites = pygame.sprite.Group(player)  # Creates a sprite group and adds 'player' to it.

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0 #60 frames per second
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            if event.type > pygame.USEREVENT:
                # need add logic for dealing with machines and other things here
                print(id)
                id = event.type - pygame.USEREVENT
                if id in my_machines:
                    my_machines[id].handle_event()
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == load_button:
                    num = event.ui_object_id.split("_")[1]
                    print('ooo laundry!')
                    selected_load = loads[int(num)]
                if event.ui_element == hello_button:
                    print('Hello World!')
                    print(event.ui_object_id)
                    selected_load = None
                if event.ui_element == washer_button or event.ui_element == dryer_button:
                    num = event.ui_object_id.split("_")[1]
                    machine = my_machines[int(num)]
                    print("yes, master?")
                    if selected_load:
                        machine.add_load(selected_load)
                        selected_load = None
                        print("sent to machine!")
                    else:
                        selected_load = machine.get_load()
                        if selected_load:
                            print("load selected!") #TODO: handle how could select then deselect without moving to another machine
                            print(selected_load.state)
                        else:
                            print("no load here")


            manager.process_events(event)

        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up)
        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)
        all_sprites.draw(window_surface)

        pygame.display.update()

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
    def __init__(self, soiled = False, size=Size.NORMAL):
        self.soiled = soiled
        self.size = size
        self.state = State.UNWASHED

    def get_washed(self):
        self.state = State.WASHED

    def get_dried(self):
        self.state = State.DRIED


class State(enum.Enum):
    UNWASHED = 0
    WASHED = 1
    DRIED = 2

class Machine:
    def __init__(self, id, size=Size.NORMAL):
        self.on = False
        self.id = id
        self.time = 0 #milliseconds
        self.event = pygame.USEREVENT + id  # custom event when machine is done
        self.load = None

    #TODO: if will start multiple events from machines, need way to keep track of
    #(right now just assuming all events are the loads being finished)
    def handle_event(self):
        self.on = False

    def add_load(self, load):
        if self.load is None and self.on is False:
            self.__start__(load)
            print('load added!')
        else:
            print("can't add this one!")

    def get_load(self):
        # attempt to retrieve load from machine (only possible if done -- may change in future)
        if self.load is not None and self.on == False:
            load = self.load
            self.load = None
            return load

    def __start__(self, load):
        self.load = load
        pygame.time.set_timer(self.event, self.time, True)  # true == only set once
        print(self.event)
        print(self.time)
        self.on = True

class Washer(Machine):
    def __init__(self, id):
        super().__init__(id)
        self.time = WASHER_TIME

    #TODO: add custom add_load function that checks if load is not soiled?

    def handle_event(self):
        self.load.get_washed()
        print("all clean now!")
        super().handle_event() #turns off machine


#TODO: dryer vs. washer vs. generic machine logic
#also, do we want player to be able to take clothes out prematurely? For a bit of a ding to score/profit?
#What about being able to wash soiled clothes before pre-treatment?
class Dryer(Machine):
    def __init__(self, id):
        super().__init__(id)
        self.time = DRYER_TIME

    def handle_event(self):
        self.load.get_dried()
        print("all dry now!")
        super().handle_event() #turns off machine

    def add_load(self, load):
        if load.state is State.WASHED:
            super().add_load(load)

class GameState(enum.Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    NEXTLEVEL = 2

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
        image = pygame.image.load(path + os.sep + file_name).convert()
        images.append(image)
    return images

class AnimatedSprite(pygame.sprite.Sprite):

    def __init__(self, position, images):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation.
        """
        super().__init__()

        size = (95, 122)  # This should match the size of the images.

        self.on = False
        self.rect = pygame.Rect(position, size)
        self.images = images
        self.images_right = images
        self.images_left = [pygame.transform.flip(image, True, False) for image in images]  # Flipping every image.
        self.index = 0
        self.image = images[self.index]  # 'image' is the current image of the animation.

        self.velocity = pygame.math.Vector2(0, 0)

        self.animation_time = 0.1
        self.current_time = 0

        self.animation_frames = 6
        self.current_frame = 0

    def update_time_dependent(self, dt):
        """
        Updates the image of Sprite approximately every 0.1 second.

        Args:
            dt: Time elapsed between each frame.
        """
        if self.on:
            self.current_time += dt
            if self.current_time >= self.animation_time:
                self.current_time = 0
                self.index = (self.index + 1) % len(self.images)
        else:
            self.index = 0

        self.image = self.images[self.index]

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

    def update(self, dt, mouse_pos, mouse_up):
        """ Updates the mouse_over variable and returns the button's
            action value when clicked.
        """
        if self.rect.collidepoint(mouse_pos):
            #self.mouse_over = True
            if mouse_up:
                self.on = not self.on

        # Switch between the two update methods by commenting/uncommenting.
        self.update_time_dependent(dt)
        #self.update_frame_dependent()

if __name__ == "__main__":
    main()