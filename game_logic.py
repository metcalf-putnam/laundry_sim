import pygame

# Local imports
import constant as c
import machine


class GameLogic:
    # takes in orders array, adjudicates machine and load clicks, starts first event timer for first load
    # (and then for next one
    def __init__(self, orders_array, pile_in, pile_out, player):
        self.orders_array = orders_array
        self.pile_in = pile_in
        self.pile_out = pile_out
        self.player = player

        self.set_timer_for_order()

    def set_timer_for_order(self):
        time_buffer = 500
        current_time = pygame.time.get_ticks()
        print("current time: " + str(current_time))
        cycle_time = machine.WASHER_TIME + machine.DRYER_TIME + time_buffer*5
        max_ = c.LEVEL_TIME - current_time - cycle_time
        min_ = time_buffer
        range = max_ - min_

        if self.orders_array and len(self.orders_array) > 0:
            relative_max = range//len(self.orders_array) + min_
            random_eta = 3000#randint(min_, relative_max)
            # TODO: main should tell GameLogicEvent what code to use instead in initialization?
            pygame.time.set_timer(c.GAMELOGICEVENT, random_eta, True)
            print("set timer for: " + str(random_eta))
        else:
            print("that was the last order scheduled!")

    def handle_event(self):
        print("Hey, that's my event! :D")
        if self.orders_array and len(self.orders_array) > 0:
            order = self.orders_array.pop()
            print("sending an order with " + str(len(order.loads)) + " loads to input pile")
            self.pile_in.add_order(order)
            print("orders remainings: " +  str(len(self.orders_array)))
            self.set_timer_for_order()
        else:
            print("I gots no more orders :(")
        print("current time: " + str(pygame.time.get_ticks()))

    def adjudicate_machine_click(self, machine):
        # Called when player clicks on a machine
        machine_load = machine.load
        player_load = self.player.load

        if machine_load and not player_load:
            self.player.add_load(machine.remove_load())
        elif player_load and machine.can_hold(player_load):
            machine.add_load(self.player.remove_load())

    def adjudicate_pile_click(self, animated_load):
        # Called when player clicks on a laundry pile
        player_load = self.player.load
        pile_load = animated_load.load
        print("adjudicator ")
        if pile_load and not player_load:
            print("if statement met!")
            self.player.add_load(animated_load.remove_load())
        elif player_load and not pile_load:
            print("elif met!")
            if player_load.state is animated_load.type:
                animated_load.add_load(self.player.remove_load())