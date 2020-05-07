import pygame

# Local imports
import constant as c

MACHINE_SIZE = (108, 130)  # (x,y) in pixels


# COMMENT: is there an unanimated machine?
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

        self.state = c.MachineState.IDLE
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
        # COMMENT: why not call it self.time_ms to be clearer
        self.time = 0  # milliseconds
        # COMMENT: since pygame can only have one timer per event id, it may make sense
        #  to just call this self.finished_event_id?
        self.event = pygame.USEREVENT + id  # custom event when machine is done
        self.load = None

    # TODO: if will start multiple events from machines, need way to keep track of
    # (right now just assuming all events are the loads being finished)
    def handle_event(self):
        self.state = c.MachineState.FINISHED

    def add_load(self, load):
        if self.load is None and self.state is c.MachineState.IDLE:
            self.__start__(load)
            print('load added!')

    def remove_load(self):
        # attempt to retrieve load from machine (only possible if done -- may change in future)
        print("I see you want your washed clothes back")
        if self.state is c.MachineState.FINISHED:
            load = self.load
            self.load = None
            self.state = c.MachineState.IDLE
            print("you may have them back!")
            return load

    def __start__(self, load):
        self.load = load

        pygame.time.set_timer(self.event, self.time, True)  # true == only set once
        self.state = c.MachineState.RUNNING

    def update_time_dependent(self, dt):
        """
        Updates the image of Sprite approximately every 0.1 second.

        Args:
            dt: Time elapsed between each frame.
        """
        if self.state is c.MachineState.IDLE:
            images = self.images_idle
        elif self.state is c.MachineState.RUNNING:
            images = self.images_running
        else:
            images = self.images_finished

        # COMMENT: you seem to have this animation update logic in the animatedload as well
        #  perhaps it can be extracted into a helper function?
        self.index = min(self.index, len(images) - 1)

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(images)

        self.image = images[self.index]


    def update(self, dt, mouse_pos, mouse_up, game_logic, id):
        """ Updates the mouse_over variable and returns the button's
            action value when clicked.
        """
        if id == self.id:
            self.handle_event()
        if self.rect.collidepoint(mouse_pos) and mouse_up:
            # this sprite was clicked
            game_logic.adjudicate_machine_click(self)

        self.update_time_dependent(dt)


class Washer(AnimatedMachine):
    def __init__(self, id, position, images, size=c.Size.NORMAL):
        super().__init__(id, position, images)
        self.time = c.WASHER_TIME

    # TODO: add custom add_load function that checks if load is not soiled?

    def handle_event(self):
        self.load.get_washed()
        print("all clean now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is c.LaundryState.UNWASHED:
            super().add_load(load)
        elif load.state is c.LaundryState.WASHED and self.load is None:
            print("adding load back for safe keeping")
            self.load = load
            self.state = c.MachineState.FINISHED

    def can_hold(self, load):
        unwashed = load.state is c.LaundryState.UNWASHED
        washed = load.state is c.LaundryState.WASHED
        print(unwashed)
        # COMMENT why not just return self.load is None ... ?
        if self.load is None and (unwashed or washed) and self.state is c.MachineState.IDLE:
            return True
        return False


# TODO: better dryer vs. washer vs. generic machine logic
# also, do we want player to be able to take clothes out prematurely? For a bit of a ding to score/profit?
# What about being able to wash soiled clothes before pre-treatment?
class Dryer(AnimatedMachine):
    def __init__(self, id, position, images, size=c.Size.NORMAL):
        super().__init__(id, position, images)
        self.time = c.DRYER_TIME

    def handle_event(self):
        self.load.get_dried()
        print("all dry now!")
        super().handle_event()  # turns off machine

    def add_load(self, load):
        if load.state is c.LaundryState.WASHED:
            super().add_load(load)
        elif load.state is c.LaundryState.DRIED and self.load is None:
            self.load = load
            self.state = c.MachineState.FINISHED

    def can_hold(self, load):
        washed = load.state is c.LaundryState.WASHED
        dried = load.state is c.LaundryState.DRIED
        if self.load is None and (washed or dried) and self.state is c.MachineState.IDLE:
            return True
        return False
