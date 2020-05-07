import pygame
import pygame.freetype
import pygame_gui

# Local imports
import constant as c
import image_utils
import pile
import level_utils
import laundry
import game_logic

FPS = 100 # frames per second
WHITE = (255, 255, 255)
PADDING = 8

# TODO: have way of listing/storing level variables (and think through how player choices impact)
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
    game_state = c.GameState.TITLE

    player_images = image_utils.load_laundry_images('images/laundry/in_hand')
    player = laundry.Player(player_images)

    running = True
    while running:
        if game_state == c.GameState.TITLE:
            game_state = title_screen(screen)

        if game_state == c.GameState.NEW_GAME:
            game_state = play_level(screen, player)

        if game_state == c.GameState.GAME_OVER:
            game_state = game_over(screen, player.score)

        if game_state == c.GameState.QUIT:
            pygame.quit()
            return


def game_over(screen, score):
    background = pygame.Surface((800, 600))
    background.fill((0,0,0))
    background.set_alpha(1)
    manager = pygame_gui.UIManager((800, 600))
    score_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((250, 175), (300, 100)),
                                                 text='your score: ' + str(score),
                                                 manager=manager)

    new_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                text='new game',
                                                manager=manager)
    clock = pygame.time.Clock()

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                return c.GameState.QUIT

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == new_game_button:
                        print('new game time!')
                        return c.GameState.NEW_GAME

            manager.process_events(event)

        manager.update(time_delta)
        screen.blit(background, (0, 0))
        manager.draw_ui(screen)

        pygame.display.update()


def title_screen(screen):
    background = pygame.Surface((800, 600))
    background.fill((0,0,50))

    manager = pygame_gui.UIManager((800, 600))

    title = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((250, 175), (300, 100)),
                                                 text='Laundry Simulator',
                                                 manager=manager)

    new_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                text='new game',
                                                manager=manager)
    clock = pygame.time.Clock()

    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                return c.GameState.QUIT

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == new_game_button:
                        print('new game time!')
                        return c.GameState.NEW_GAME

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(background, (0, 0))
        manager.draw_ui(screen)

        pygame.display.update()

def play_level(screen, player):
    background = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Make washers and dryers
    washer_group, dryer_group = level_utils.make_washers_and_dryers((0, 0), 2, 2)

    # Images and sprites for player and laundry piles
    pile_images = image_utils.load_laundry_images('images/laundry/in_pile')
    pile_in = pile.Pile(15, 7, pile_images, c.LaundryState.UNWASHED)
    pile_out = pile.Pile(c.SCREEN_WIDTH - 105, 7, pile_images, c.LaundryState.DRIED)

    # Labels for laundry piles
    # TODO: make more dynamic/adjustable labels based on position of piles
    pile_in_label, pile_in_rect = level_utils.make_label(WHITE, 'inbox')
    pile_in_rect.bottomleft = (10, c.SCREEN_HEIGHT)
    pile_out_label, pile_out_rect = level_utils.make_label(WHITE, 'outbox')
    pile_out_rect.bottomright = (c.SCREEN_WIDTH - PADDING, c.SCREEN_HEIGHT)

    daily_clock = level_utils.DailyClock()

    # Generating orders
    orders = level_utils.generate_orders(order_num_min=8, order_num_max=8, load_num_min=1, load_num_max=1)
    customers = level_utils.generate_customers(orders)
    inactive_customers = pygame.sprite.Group(customers)  # all customers start off inactive

    # Storing all sprites to master group
    all_sprites = pygame.sprite.Group(washer_group, dryer_group, pile_in, pile_out, player)
    logic = game_logic.GameLogic(orders, pile_in, pile_out, player)

    running = True
    while running:
        id = 0
        time_delta = clock.tick(FPS) / 1000.0
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return c.GameState.QUIT
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                print("click!!!")
                print("the current time is: " + str(pygame.time.get_ticks()))
                mouse_up = True
            if event.type > pygame.USEREVENT:
                id = event.type - pygame.USEREVENT
                print(id)
            if event.type == c.FAIL_STATE:
                return c.GameState.GAME_OVER
            if event.type == c.GAME_LOGIC_EVENT:
                logic.handle_event(event.type)
            if event.type == c.NOON_EVENT:
                for customer in inactive_customers:
                    all_sprites.add(customer)
                    inactive_customers.remove(customer)

        if not customers:
            print("final score: " + str(logic.score))
            return c.GameState.GAME_OVER # TODO: update/change

        # Updating objects
        all_sprites.update(time_delta, pygame.mouse.get_pos(), mouse_up, logic, id)
        pile_in.update_y_pos()
        pile_out.update_y_pos()
        clock_text = daily_clock.get_updated_text(time_delta)
        clock_label, clock_rect = level_utils.make_label(WHITE, clock_text)
        clock_rect.topright = (c.SCREEN_WIDTH - PADDING, PADDING)

        # Drawing background, sprites, and labels
        screen.blit(background, (0, 0))
        screen.blit(pile_in_label, pile_in_rect)
        screen.blit(pile_out_label, pile_out_rect)
        screen.blit(clock_label, clock_rect)
        all_sprites.draw(screen)

        # Updating display with the latest
        pygame.display.update()


if __name__ == "__main__":
    main()
