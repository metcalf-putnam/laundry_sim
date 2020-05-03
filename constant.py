import enum
import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_LOGIC_EVENT = pygame.USEREVENT + 100
LEVEL_TIME = 30_000
WASHER_TIME = 3500  # milliseconds
DRYER_TIME = 4500  # milliseconds


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
    NEWGAME = 1
    NEXTLEVEL = 2


class LaundryState(enum.Enum):
    UNWASHED = 0
    WASHED = 1
    DRIED = 2


class MachineState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2