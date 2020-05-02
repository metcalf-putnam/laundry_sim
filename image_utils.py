import os
import pygame

# Local imports
import constant as c

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


def load_idle_running_finished_images(path, scale):
    idle_path = path + '/idle'
    running_path = path + '/running'
    finished_path = path + '/finished'

    idle = load_images(idle_path, scale)
    running = load_images(running_path, scale)
    finished = load_images(finished_path, scale)

    return [idle, running, finished]

def load_laundry_images(path):
    empty_path = path + '/empty'
    unwashed_path = path + '/unwashed'
    washed_path = path + '/washed'
    dried_path = path + '/dried'

    empty = load_images(empty_path)
    unwashed = load_images(unwashed_path)
    washed = load_images(washed_path)
    dried = load_images(dried_path)

    return [empty, unwashed, washed, dried]