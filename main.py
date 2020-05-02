import pygame
import pygame.freetype
import pygame_gui

# Local imports
import constant as c
import image_utils
import pile
import level_utils
import machine
import player
import laundry
import game_logic

FPS = 100 #frames per second
FAIL_STATE = pygame.USEREVENT + 500
WHITE = (255, 255, 255)


# TODO: clean up initialization in main()
# TODO: make outgoing orders get picked up
# TODO: add money/profit text in corner
# TODO: add large washers/dryers / large loads
# TODO: animation when finish load and/or earn money
# TODO: add level clock and "game over" screen

def main():
    pygame.init()

    print("USEREVENT: " + str(pygame.USEREVENT))
    print("NUMEVENTS: " + str(pygame.NUMEVENTS))

    # Caption and Icon
    pygame.display.set_caption('Laundry Simulator')
    icon = pygame.image.load('images/washer/idle/0.png')
    pygame.display.set_icon(icon)

    # Initializing game essentials
    game_state = c.GameState.TITLE
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    manager = pygame_gui.UIManager((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), 'data/themes/quick_theme.json')
    background = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    background.fill(manager.ui_theme.get_colour('white'))
    clock = pygame.time.Clock()

    # Make washers
    washer_images = image_utils.load_idle_running_finished_images('images/washer', machine.MACHINE_SIZE)
    washer_group = pygame.sprite.Group()
    id = 1
    for col in range(2):
        for row in range(2):
            washer = machine.Washer(id, (machine.MACHINE_SIZE[0]*col, machine.MACHINE_SIZE[1]*row), washer_images)
            washer_group.add(washer)
            id += 1

    # Make dryers
    dryer_images = image_utils.load_idle_running_finished_images('images/dryer', machine.MACHINE_SIZE)
    dryer_group = pygame.sprite.Group()
    for col in range(2):
        for row in range(2):
            dryer = machine.Dryer(id, (round(machine.MACHINE_SIZE[0]*(col+2)), machine.MACHINE_SIZE[1]*row), dryer_images)
            dryer_group.add(dryer)
            id += 1

    # Images for player and laundry piles
    pile_images = image_utils.load_laundry_images('images/laundry/in_pile')
    player_images = image_utils.load_laundry_images('images/laundry/in_hand')

    # TODO: make more dynamic/adjustable labels based on position of piles
    # Labels for laundry piles
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    pile_in_label = font.render('inbox', True, WHITE)
    pile_in_rect = pile_in_label.get_rect()
    pile_in_rect.bottomleft = (10, c.SCREEN_HEIGHT)
    pile_in = pile.Pile(15, 7, pile_images, c.LaundryState.UNWASHED)

    pile_out_label = font.render('outbox', True, WHITE)
    pile_out_rect = pile_out_label.get_rect()
    pile_out_rect.bottomright = (c.SCREEN_WIDTH-8, c.SCREEN_HEIGHT)
    pile_out = pile.Pile(c.SCREEN_WIDTH-105, 7, pile_images, c.LaundryState.DRIED)

    # Initializing player
    player_ = player.Player(player_images)

    # Generating orders
    orders = level_utils.generate_orders(order_num_min=8, order_num_max=8, load_num_min=1, load_num_max=1)

    # Storing all sprites to master group
    all_sprites = pygame.sprite.Group(washer_group, dryer_group, pile_in, pile_out, player_)
    game_logic_ = game_logic.GameLogic(orders, pile_in, pile_out, player_)

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
                game_logic_.handle_event()
            manager.process_events(event) # gui manager

        # Updating objects
        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up, game_logic_, id)
        pile_in.update_y_pos()
        pile_out.update_y_pos()
        #manager.update(time_delta)

        # Drawing background, sprites, and labels
        screen.blit(background, (0, 0))
        manager.draw_ui(screen)
        screen.blit(pile_in_label, pile_in_rect)
        screen.blit(pile_out_label, pile_out_rect)
        all_sprites.draw(screen)

        # Updating display with the latest
        pygame.display.update()


if __name__ == "__main__":
    main()
