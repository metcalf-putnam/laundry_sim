import enum
import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_LOGIC_EVENT = pygame.USEREVENT + 100 #COMMENT why 100?
NOON_EVENT = pygame.USEREVENT+101
LEVEL_TIME = 30_000
WASHER_TIME = 3500  # milliseconds #COMMENT why not do WASHER_TIME_MS so its even clearer?
DRYER_TIME = 4500  # milliseconds
FAIL_STATE = pygame.USEREVENT + 500


class PileType(enum.Enum):
    IN = 0
    OUT = 1


class Size(enum.Enum):
    SMALL = 0
    NORMAL = 1
    LARGE = 2


class GameState(enum.Enum):
    #TODO: make use of these, ensure don't interfere with other event types
    QUIT = -1
    TITLE = 0
    NEW_GAME = 1
    NEXT_LEVEL = 2
    GAME_OVER = 3


class LaundryState(enum.Enum):
    UNWASHED = 0
    WASHED = 1
    DRIED = 2


class MachineState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2


class CustomerType(enum.Enum):
    TEST = 0
    MILLENNIAL = 1
    MOBSTER = 2
    OLD_MAN = 3


class CustomerState(enum.Enum):
    VERY_ANGRY = 0
    ANGRY = 1
    NORMAL = 2
    HAPPY = 3
    VERY_HAPPY = 4