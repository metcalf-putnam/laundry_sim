import pygame
import pygame.freetype

# Local imports
import constant as c
import image_utils
import pile
import level_utils
import machine
import laundry
import game_logic

FPS = 100 #frames per second
FAIL_STATE = pygame.USEREVENT + 500
WHITE = (255, 255, 255)

# TODO: make outgoing orders get picked up
# TODO: add money/profit text in corner
# TODO: add large washers/dryers / large loads
# TODO: animation when finish load and/or earn money
# TODO: animation when trying to put load where it doesn't fit (e.g. wet clothes in output)?
# TODO: add level clock and "game over" screen


def main():
    pygame.init()

    # Caption and Icon
    pygame.display.set_caption('Laundry Simulator')
    icon = pygame.image.load('images/washer/idle/0.png')
    pygame.display.set_icon(icon)

    # Initializing game essentials
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    background = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Make washers and dryers
    washer_group, dryer_group = level_utils.make_washers_and_dryers((0,0), 2, 2)

    # Images and sprites for player and laundry piles
    pile_images = image_utils.load_laundry_images('images/laundry/in_pile')
    player_images = image_utils.load_laundry_images('images/laundry/in_hand')
    pile_in = pile.Pile(15, 7, pile_images, c.LaundryState.UNWASHED)
    pile_out = pile.Pile(c.SCREEN_WIDTH-105, 7, pile_images, c.LaundryState.DRIED)

    # Labels for laundry piles
    # TODO: make more dynamic/adjustable labels based on position of piles
    pile_in_label, pile_in_rect = level_utils.make_label(WHITE, 'inbox')
    pile_in_rect.bottomleft = (10, c.SCREEN_HEIGHT)
    pile_out_label, pile_out_rect = level_utils.make_label(WHITE, 'outbox')
    pile_out_rect.bottomright = (c.SCREEN_WIDTH-8, c.SCREEN_HEIGHT)

    # Initializing player
    player = laundry.Player(player_images)

    # Generating orders
    orders = level_utils.generate_orders(order_num_min=8, order_num_max=8, load_num_min=1, load_num_max=1)

    # Storing all sprites to master group
    all_sprites = pygame.sprite.Group(washer_group, dryer_group, pile_in, pile_out, player)
    logic = game_logic.GameLogic(orders, pile_in, pile_out, player)

    running = True
    while running:
        id = 0
        time_delta = clock.tick(FPS) / 1000.0  # 60 frames per second
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                print("click!!!")
                print("the current time is: " + str(pygame.time.get_ticks()))
                mouse_up = True
            if event.type > pygame.USEREVENT:
                id = event.type - pygame.USEREVENT
                print(id)
            if event.type == c.GAMELOGICEVENT:
                print("Ooo! An order!")
                logic.handle_event()

        # Updating objects
        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up, logic, id)
        pile_in.update_y_pos()
        pile_out.update_y_pos()

        # Drawing background, sprites, and labels
        screen.blit(background, (0, 0))
        screen.blit(pile_in_label, pile_in_rect)
        screen.blit(pile_out_label, pile_out_rect)
        all_sprites.draw(screen)

        # Updating display with the latest
        pygame.display.update()


if __name__ == "__main__":
    main()
