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