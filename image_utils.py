import os
import pygame

#local imports
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


#COMMENT: instead of returning tuples that need to be interpreted based on position
# consider using a struct/dict so its more readable.
def load_machine_images(path, scale):
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


def load_customer_images(path, scale):
    images_dict = dict()
    very_angry_path = path + '/very_angry'
    angry_path = path + '/angry'
    normal_path = path + '/normal'
    happy_path = path + '/happy'
    very_happy_path = path + '/very_happy'

    images_dict[c.CustomerState.VERY_ANGRY] = load_images(very_angry_path, scale)
    images_dict[c.CustomerState.ANGRY] = load_images(angry_path, scale)
    images_dict[c.CustomerState.NORMAL] = load_images(normal_path, scale)
    images_dict[c.CustomerState.HAPPY] = load_images(happy_path, scale)
    images_dict[c.CustomerState.VERY_HAPPY] = load_images(very_happy_path, scale)

    return images_dict