import pygame
import enum

# Local imports
import laundry
import constant as c

MACHINE_SIZE = (108, 130)  # (x,y) in pixels
WASHER_TIME = 3500  # milliseconds
DRYER_TIME = 4500  # milliseconds


class MachineState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2


class AnimatedMachine(pygame.sprite.Sprite):
    # TODO: clean up example code not using

    def __init__(self, id, position, images, size=c.Size.NORMAL):
        """
        Animated machine object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation, sorted into an array of arrays
        """
        super().__init__()

        self.state = MachineState.IDLE
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

        self.index = min(self.index, len(images) - 1)

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
            # this sprite was clicked
            game_logic.adjudicate_machine_click(self)

        # Switch between the two update methods by commenting/uncommenting.
        self.update_time_dependent(dt)
        # self.update_frame_dependent()


class Washer(AnimatedMachine):
    def __init__(self, id, position, images, size=c.Size.NORMAL):
        super().__init__(id, position, images)
        self.time = WASHER_TIME

    # TODO: add custom add_load function that checks if load is not soiled?

    def handle_event(self):
        self.load.get_washed()
        print("all clean now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is laundry.LaundryState.UNWASHED:
            super().add_load(load)
        if load.state is laundry.LaundryState.WASHED and self.load is None:
            print("adding load back for safe keeping")
            self.load = load
            self.state = MachineState.FINISHED

    def can_hold(self, load):
        unwashed = load.state is laundry.LaundryState.UNWASHED
        washed = load.state is laundry.LaundryState.WASHED
        print(unwashed)
        if self.load is None and (unwashed or washed) and self.state is MachineState.IDLE:
            return True
        return False


# TODO: dryer vs. washer vs. generic machine logic
# also, do we want player to be able to take clothes out prematurely? For a bit of a ding to score/profit?
# What about being able to wash soiled clothes before pre-treatment?
class Dryer(AnimatedMachine):
    def __init__(self, id, position, images, size=c.Size.NORMAL):
        super().__init__(id, position, images)
        self.time = DRYER_TIME

    def handle_event(self):
        self.load.get_dried()
        print("all dry now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is laundry.LaundryState.WASHED:
            super().add_load(load)
        if load.state is laundry.LaundryState.DRIED and self.load is None:
            self.load = load
            self.state = MachineState.FINISHED

    def can_hold(self, load):
        washed = load.state is laundry.LaundryState.WASHED
        dried = load.state is laundry.LaundryState.DRIED
        if self.load is None and (washed or dried) and self.state is MachineState.IDLE:
            return True
        return False
