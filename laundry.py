import enum

# Local imports
import constant


class Load:
    # single load of laundry
    def __init__(self, soiled=False, size=constant.Size.NORMAL):
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