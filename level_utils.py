import pygame
from random import random, randint

# Local imports
import laundry
import image_utils
import machine


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
        load = laundry.Load(is_soiled, is_large)
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


def make_washers_and_dryers(starting_pos, rows_per_machine, columns_per_machine):
    washer_images = image_utils.load_machine_images('images/washer', machine.MACHINE_SIZE)
    dryer_images = image_utils.load_machine_images('images/dryer', machine.MACHINE_SIZE)
    washer_group = pygame.sprite.Group()
    dryer_group = pygame.sprite.Group()

    id_ = 1
    for col in range(columns_per_machine):
        for row in range(rows_per_machine):
            x = machine.MACHINE_SIZE[0] * col + starting_pos[0]
            y = machine.MACHINE_SIZE[1] * row + starting_pos[1]
            washer = machine.Washer(id_, (x, y), washer_images)
            washer_group.add(washer)
            id_ += 1
    for col in range(columns_per_machine):
        for row in range(rows_per_machine):
            x = machine.MACHINE_SIZE[0] * (col+columns_per_machine) + starting_pos[0]
            y = machine.MACHINE_SIZE[1] * (row) + starting_pos[1]
            dryer = machine.Dryer(id_, (x, y), dryer_images)
            dryer_group.add(dryer)
            id_ += 1 #each machine needs unique id for event catching

    return washer_group, dryer_group


def make_label(color, string):
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    label = font.render(string, True, color)
    label_rect = label.get_rect()
    return label, label_rect