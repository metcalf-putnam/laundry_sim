import enum

# Local imports
import constant as c


class Load:
    # single load of laundry
    def __init__(self, soiled=False, size=c.Size.NORMAL):
        self.soiled = soiled
        self.size = size
        self.state = c.LaundryState.UNWASHED

    def get_washed(self):
        self.state = c.LaundryState.WASHED

    def get_dried(self):
        self.state = c.LaundryState.DRIED