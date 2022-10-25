from kivy.core.window import Window
# import sound
import GameAudio
import kivy
import random
from kivy.app import App
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty, Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase

Window.set_system_cursor("hand")

kivy.require("2.1.0")

# registering custom font
LabelBase.register(name="aae",
                   fn_regular="assets/AAE.ttf"
                   )

# cards elements
suits = ("Pikes", "Hearts", "Clubs", "Diamonds")
ranks = ("Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace")
# jokers elements
j_ranks = ("Red Joker", "Black Joker")
# aces, black joker, and red joker have specific values. Their default values are used to finds them in the cards lists
# and applying their effect. Then their default values are replaced
values = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10,
          "Jack": 10, "Queen": 10, "King": 10, "Ace": 0.99, "Red Joker": -0.10, "Black Joker": -0.20}

# contain all cards
all_cards = []


class MainWindow(Screen):

    def play_but_change(self):

        # change Play button text to Resume
        self.ids.play_but_id.text = "Resume"
        # stop menu sound
        GameAudio.GameSound.stop_menu_sound()
        # play in game sound
        GameAudio.GameSound.play_in_game_sound()

    # switch for turn off/on game sounds
    @staticmethod
    def sound_on_off(switchObject, switchValue):

        if switchValue:
            GameAudio.GameSound.sound_off()
        else:
            GameAudio.GameSound.sound_on()


class GameInfoWindow(Screen):
    pass


class PlayerLayout(BoxLayout):
    pass


class DealerLayout(BoxLayout):
    pass


class InfoTitlesLabel(Label):
    pass


class InfoTextLabel(Label):
    pass


# for card creation
class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        # card value
        self.value = values[rank]

    # card name
    def __str__(self):
        return f"{self.rank} of {self.suit}"


# for joker cards creation
class JokerCard:

    def __init__(self, j_rank):
        self.j_rank = j_rank
        # card value
        self.value = values[j_rank]

    # card name
    def __str__(self):
        return self.j_rank


# creating the card deck
class Deck:

    def __init__(self):
        # creates and append all cards
        for suit in suits:
            for rank in ranks:
                all_cards.append(Card(suit, rank))

        # create and append only joker cards
        for j_rank in j_ranks:
            all_cards.append(JokerCard(j_rank))

    # deck shuffle
    @staticmethod
    def shuffle():
        random.shuffle(all_cards)
        return all_cards

    # deal one card
    @staticmethod
    def deal_a_card():
        return all_cards.pop()


# popup for prompt player to make a bet. Popup only when the player enter the game
class PlayerBetPopup(Popup):

    def __init__(self, **kwargs):
        super(PlayerBetPopup, self).__init__(**kwargs)

        # set duration of the popup
        Clock.schedule_once(self.player_bet_dismiss, 3)

    # dismiss the popup
    def player_bet_dismiss(self, dt):
        self.dismiss()


class GameWindow(Screen):
    # play menu sound
    GameAudio.GameSound.play_menu_sound()

    # for enable and disable game menu buttons - hit, stand
    h_s_status = BooleanProperty(True)

    # for enable and disable game menu button - bet
    bet_status = BooleanProperty(False)

    # slider max
    slider_max_bet = StringProperty()

    deck_creation = Deck()

    def __init__(self, **kwargs):
        super(GameWindow, self).__init__(**kwargs)

        # player credit
        self.player_credits = 50
        # bet profit percentage. Reduce and increase by special events/cards/difficulty
        self.profit_percentage = 0
        # limits slider max to player credits
        self.slider_max_bet = str(self.player_credits)
        # player cards list
        self.player_cards_list = []
        # dealer cards list
        self.dealer_cards_list = []
        # receives slider value as bet amount. Preset to insure player min bet will always be 1. Multiplied by profit
        # percentage to form the winning amount
        self.player_bet = 1
        # keep player's highest achieved credits during the game and display them at the end
        self.player_best_result = 0
        # contain player hand value. Use for bust, win, loss check
        self.player_sum_check = []
        # contain dealer hand value. Use for bust, win, loss check
        self.dealer_sum_check = []
        # keep player choice for ace card value
        self.player_ace_choice = 0
        # if True restart the game to default values
        self.game_over = False
        # turns in True if the player presses the stand button or auto-stand got triggered,
        # then the dealer's turn begins. Used as check for dealer cards display to show only two cards and to reveal
        # the hidden one
        self.player_turn_over = False
        # keep the random choice from curse/bless/no event. Depends on the event choose the correct
        # popup (curse or bless) and correct victory title text
        self.labyrinth_choice_result = ""
        # display in game_over_popup the achieved rank from ranking_scale
        self.player_rank = ""
        # if player reach last rank will make bool True which will allow to close only victory_popup and skip trying
        # to close game_over_popup. Avoids try to close game_over_popup error
        self.player_victory = False
        # if True allows popup for ace value selection in the update fnc
        self.player_has_ace = False
        # apply red joker card effect and display RJ label in player's side
        self.player_has_red_jk = False
        # apply black joker card effect and display BJ label in player's side
        self.player_has_black_jk = False
        # apply red joker card effect and display RJ label in dealer's side
        self.dealer_has_red_jk = False
        # apply black joker card effect and display BJ label in dealer's side
        self.dealer_has_black_jk = False
        # set a text depends on red joker owner. Displayed in dealer's loss/bust popup
        self.red_joker_popup_txt = ""
        # display the difficulty level
        self.difficulty = ""
        # keeps all in bonus determined by the difficult
        self.ai_progressive = 0
        # curse chance determined by the difficult
        self.no_event_chance = 0
        self.bless_chance = 0
        self.curse_chance = 0
        # display ace name in ace popup
        self.ace_name = ""
        # delta time for clock game
        self.game_update_frequency = .5
        # counts the turns played by the player and display them in the end of the game
        self.turns_counter = 1

        # buttons color
        self.buttons_color = (217 / 255, 255 / 255, 251 / 255, 1)
        # separators color
        self.sep_color = (92 / 255, 113 / 255, 105 / 255, 1)

        # size of a card
        self.card_size = (0.095, 1)
        # sets card back image
        self.card_back = Image(source="assets/back1.png",
                               size_hint=self.card_size
                               )

        # popups
        self.tie_pu = Popup
        self.dealer_bust_loss_pu = Popup
        self.dealer_turn_pu = Popup
        self.victory_pu = Popup
        self.bless_pu = Popup
        self.curse_pu = Popup
        self.rjk_pu = Popup
        self.bjk_pu = Popup
        self.res_pu = Popup
        self.player_bust_loss_pu = Popup
        self.game_over_pu = Popup
        self.ace_choice_pu = Popup

        # for events. All used to display as info in player's win popup
        self.red_jk_event = 0
        self.hit_card_event = 0
        self.two_ace_player_event = 0
        self.two_ace_dealer_event = 0
        self.all_in_event = 0
        self.aces_pick_cost = 0

        # shuffle the deck
        self.deck_creation.shuffle()

        # deal firsts cards
        self.deals_first_cards()

        # sets the difficulty for the first turn
        self.dynamic_difficulty_adjustment()

        # buttons
        self.ace_one_but = Button
        self.ace_six_but = Button
        self.ace_eleven_but = Button
        self.dealer_turn_ok_but = Button
        self.player_loss_ok_but = Button
        self.dealer_loss_ok_but = Button
        self.tie_ok_but = Button
        self.game_over_ok_but = Button
        self.victory_return_but = Button

        # the clock for update/keep tracking for game changes
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)

    # delaying actions. Prevent popups stack
    @staticmethod
    def delay_action(func_for_delay):
        Clock.schedule_once(func_for_delay, .3)

    # track for changes. First, it tracks for player's jokers/aces cards in order to calculate them
    # interrupts the game if the player is busted or auto stand
    # second (after self.player_turn_over), it checks for dealer's jokers/aces cards and calculates them
    # interrupts the game if the dealer is busted
    def update(self, dt):

        # check for joker cards in the player's hand after the bet button is pressed. Covers both jokers
        # in the first dealt-hand case
        if self.ids.bet_id.disabled:
            self.joker_cards_check(self.player_cards_list)

        # check for player's ace cards after player press stand but
        if self.player_has_ace:
            self.player_ace_after_first_dealt()

        # if player stand or auto stand and not bust, proceeds to dealer's move
        if self.player_turn_over:
            # check for joker cards in the dealer's hand after the bet button is pressed. Covers both jokers
            # in the first dealt-hand case
            self.joker_cards_check(self.dealer_cards_list)
            self.dealer_move()

    # forming the card name and selects the correct image
    def forming_card_image(self, cards_list, ind):

        card = cards_list[ind]
        card_name = str(card) + ".png"
        card_image = Image(source="assets/PNG-cards/" + card_name,
                           size_hint=self.card_size
                           )
        return card_image

    # adds card from list on to layout. Used for dealer and player
    @staticmethod
    def adds_card_image(layout_id, card):
        layout_id.add_widget(card)

    # clear widgets from layout. Used for dealer and player
    @staticmethod
    def clears_layout(layout_id):
        layout_id.clear_widgets()

    # re-append all owned card's values to sum list and return the sum of it. Used for player and dealer
    @staticmethod
    def hand_value_update(sum_list, card_list):

        # clear the list on call in order to add cards (plus the last received) without duplication
        sum_list.clear()

        # adds card values to sum_check list
        for card in card_list:
            card_value = card.value
            sum_list.append(card_value)
        # returns sum of a hand
        return sum(sum_list)

    # return a background img stretched and full size. For curse/bless popups
    @staticmethod
    def background_img(bg_img):

        bg = Image(source=bg_img)
        bg.allow_stretch = True
        bg.keep_ratio = False
        bg.size_hint_x = 1
        bg.size_hint_y = 1
        bg.opacity = 1
        return bg

    def deals_first_cards(self):

        # first cards dealt in order of blackjack game rules
        self.player_cards_list.append(self.deck_creation.deal_a_card())
        self.dealer_cards_list.append(self.deck_creation.deal_a_card())
        self.player_cards_list.append(self.deck_creation.deal_a_card())
        self.dealer_cards_list.append(self.deck_creation.deal_a_card())

        # update player hand value after first cards are dealt for jokers check (allows players jokers popups if there
        # is joker cards in firs player cards)
        self.hand_value_update(self.player_sum_check, self.player_cards_list)

        # aces calculation in firsts dealt for player
        self.first_dealt_ace_calculation(self.player_cards_list)

        # aces calculation in firsts dealt for dealer
        self.first_dealt_ace_calculation(self.dealer_cards_list)

    # display player's first two cards
    def player_first_dealt_cards_display(self):

        # first card
        self.ids.player_layout_id.add_widget(self.forming_card_image(self.player_cards_list, 0))
        # second card
        self.ids.player_layout_id.add_widget(self.forming_card_image(self.player_cards_list, 1))

    # displays dealer's the first two cards. The second dealer's card is hidden (by blackjack rules) until the player
    # finishes his/her turn
    def dealer_first_dealt_cards_display(self):

        # first card
        self.ids.dealer_layout_id.add_widget(self.forming_card_image(self.dealer_cards_list, 0))
        # second card - display card back image (the hidden card)
        self.ids.dealer_layout_id.add_widget(self.card_back)

    # check for joker cards in player cards and dealer cards. Break prevent popups stacking if both jokers are one after
    # another
    def joker_cards_check(self, lst):

        for joker_card in lst:
            # triggers red joker popup if find default rjk value
            if joker_card.value == -0.10:
                self.red_joker_popup()
                break
            # triggers black joker popup if find default bjk value
            if joker_card.value == -0.20:
                self.black_joker_popup()
                break

    # first dealt cards are aces (2ace) bonus/reduction
    def two_aces_event(self, cards_lst):

        # if dealer's first two cards are aces allow reduction to profit percentage
        if cards_lst == self.dealer_cards_list:
            # reduction 0.3 to profit percentage
            self.profit_percentage -= 0.3
            # save and display two ace decrease
            self.two_ace_dealer_event = 0.3
        # if player's first two cards are aces allow bonus to profit percentage
        elif cards_lst == self.player_cards_list:
            # add 0.3 to profit percentage
            self.profit_percentage += 0.3
            # save and display tow ace bonus
            self.two_ace_player_event = 0.3

    # calculate first cards aces for dealer and player
    def first_dealt_ace_calculation(self, cards_lst):

        # if first two cards are aces they are calculate as  9 + 1 = 10. Play bonus or reduction depends on owner
        if cards_lst[0].value == 0.99 and cards_lst[1].value == 0.99:
            for two_ace_cards in cards_lst:
                # it will replace each default ace value with new values 9 and 1
                if two_ace_cards == cards_lst[0]:
                    cards_lst[0].value = 9
                elif two_ace_cards == cards_lst[1]:
                    cards_lst[1].value = 1

            # applies two ace event
            self.two_aces_event(cards_lst)

        # if one of dealer's first two cards is ace it will always take card values 11
        elif cards_lst == self.dealer_cards_list and (cards_lst[0].value != 0.99 or cards_lst[1].value != 0.99):
            for one_ace_card in cards_lst:
                if one_ace_card.value == 0.99:
                    one_ace_card.value = 11

    # triggers for player's ace card popup after first dealt
    def player_ace_after_first_dealt(self, *args):

        for ace_card in self.player_cards_list:
            if ace_card.value == 0.99:
                # display current ace card name in ace choice popup
                self.ace_name = ace_card
                # ace choice popup
                self.ace_choice_popup()
                # break to prevent ace choice popup stacking bug
                break

    # ace popup. Player selects value for ace card
    def ace_choice_popup(self):

        # stop update
        self.clock_game.cancel()

        bx = BoxLayout()

        self.ace_one_but = Button(text="1",
                                  size_hint=(1, .8),
                                  background_color=self.buttons_color,
                                  background_down='assets/b1.png',
                                  font_size=self.ace_but_size,
                                  font_name="aae",
                                  bold=True
                                  )
        self.ace_six_but = Button(text="6",
                                  size_hint=(1, .8),
                                  background_color=self.buttons_color,
                                  background_down='assets/b1.png',
                                  font_size=self.ace_but_size,
                                  font_name="aae",
                                  bold=True
                                  )
        self.ace_eleven_but = Button(text="11",
                                     size_hint=(1, .8),
                                     background_color=self.buttons_color,
                                     background_down='assets/b1.png',
                                     font_size=self.ace_but_size,
                                     font_name="aae",
                                     bold=True
                                     )

        # on press selects value for the ace
        self.ace_one_but.bind(on_press=self.ace_value_one)
        self.ace_six_but.bind(on_press=self.ace_value_six)
        self.ace_eleven_but.bind(on_press=self.ace_value_eleven)

        bx.add_widget(self.ace_one_but)
        bx.add_widget(self.ace_six_but)
        bx.add_widget(self.ace_eleven_but)

        self.ace_choice_pu = Popup(title=f"Select a value for your {self.ace_name}",
                                   content=bx,
                                   title_size=self.titles_buttons_size,
                                   title_font="aae",
                                   separator_color=self.sep_color,
                                   size_hint=(.8, .6),
                                   auto_dismiss=False
                                   )

        self.ace_choice_pu.open()

    def ace_value_one(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable ace buttons
        self.ace_one_but.disabled = True
        self.ace_six_but.disabled = True
        self.ace_eleven_but.disabled = True
        # replace default blue disabled button
        self.ace_one_but.background_disabled_down = "assets/b1.png"
        # sets ace value to 1
        self.player_ace_choice = 1
        # ace popup dismiss
        self.delay_action(self.ace_value_popup_dismiss)

    def ace_value_six(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable ace buttons
        self.ace_one_but.disabled = True
        self.ace_six_but.disabled = True
        self.ace_eleven_but.disabled = True
        # replace default blue disabled button
        self.ace_six_but.background_disabled_down = "assets/b1.png"
        # sets ace value to 6
        self.player_ace_choice = 6
        # ace popup dismiss
        self.delay_action(self.ace_value_popup_dismiss)

    def ace_value_eleven(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable ace buttons
        self.ace_one_but.disabled = True
        self.ace_six_but.disabled = True
        self.ace_eleven_but.disabled = True
        # replace default blue disabled button
        self.ace_eleven_but.background_disabled_down = "assets/b1.png"
        # sets ace value to 11
        self.player_ace_choice = 11
        # ace popup dismiss
        self.delay_action(self.ace_value_popup_dismiss)

    # replaces default ace value with the player choice
    def replacing_ace_card_value(self):

        for player_ace_card in self.player_cards_list:
            if player_ace_card.value == 0.99:
                player_ace_card.value = self.player_ace_choice
                # prevent replacing all ace cards' value at once (if the player has more than one ace card in
                # the cards list). Returning self.player_ace_choice to 0.99 ensures the ace choice popup will
                # trigger for the next ace card
                self.player_ace_choice = 0.99

    # take the cost for ace selection from player's credit and adds it to the bet
    def ace_selection_cost(self):

        # keep the cost of current ace selection
        ace_credit_bet = 0

        # above 5k credits, ace cost is 0.04% from player credits
        if 5000 < self.player_credits:
            ace_credit_bet = round(0.04 * self.player_credits)
            # take the cost from credits
            self.player_credits -= ace_credit_bet
            # adds the cost to current bet
            self.player_bet += ace_credit_bet
        # between 500 and 5k credits, ace cost is 0.02% from player credits
        elif 500 < self.player_credits <= 5000:
            ace_credit_bet = round(0.02 * self.player_credits)
            # take the cost from credits
            self.player_credits -= ace_credit_bet
            # adds the cost to current bet
            self.player_bet += ace_credit_bet
        # between 5 and 250 credits, ace cost is 5 credits
        elif 5 < self.player_credits <= 250:
            # take the cost from credits
            self.player_credits -= 5
            # adds the cost to current bet
            self.player_bet += 5
            # add the cost to aces_transfer_cost in order to display it as information (5 - 250 case)
            self.aces_pick_cost += 5
        # takes all the credits between 0 and 5, add them to the bet. In the meantime makes credits 0
        elif 0 < self.player_credits <= 5:
            self.player_bet += self.player_credits
            # add the cost to aces_transfer_cost in order to display it as information ( 0< - 5 case)
            self.aces_pick_cost += self.player_credits
            self.player_credits = 0
        # if equal or less 0 reduce the bet with 0.02% on each ace value selection
        else:
            ace_credit_bet = round(0.02 * self.player_bet)
            self.player_bet -= ace_credit_bet

        # add the cost to aces_transfer_cost in order to display it as information (any other case except 5 - 250
        # and 0< - 5)
        self.aces_pick_cost += ace_credit_bet

    # ace selection calculation
    def ace_value_popup_dismiss(self, *args):

        # calculate ace cost
        self.ace_selection_cost()
        # update player's credit
        self.player_credit_update()
        # updates player's bet
        self.player_bet_update()
        # replace ace default value
        self.replacing_ace_card_value()
        # update player cards value
        self.hand_value_update(self.player_sum_check, self.player_cards_list)
        # dismiss ace choice popup
        self.ace_choice_pu.dismiss(self)
        # run update
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)
        # check player's hand after ace selection
        self.ace_selection_result_check()

    def ace_selection_result_check(self):

        # if player hand is exceed 21 proceed to player bust popup
        if sum(self.player_sum_check) > 21:
            self.player_hand_bust_check()
        # if no more ace value left for change (avoids - not ace choice popups) or player hand value equal 21
        #  proceeds to dealer turn popup
        else:
            if (0.99 not in self.player_sum_check) or (sum(self.player_sum_check) == 21):
                self.dealer_turn_popup()

    # on hit click
    def on_hit_click(self):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disabled hit button
        self.ids.hit_id.disabled = True
        # disable stand button
        self.ids.stand_id.disabled = True
        # disable menu button
        self.ids.menu_id.disabled = True
        # remove default blue color light
        self.ids.hit_id.background_disabled_down = "assets/b1.png"
        # delay the hit button action
        self.delay_action(self.hit_but_action)

    # hit button
    def hit_but_action(self, *args):

        # keep and display the bonus for card hit
        self.hit_card_event += 0.1
        # increase profit percentage for each new card
        self.profit_percentage += 0.1
        # adds a random card to player cards list
        self.player_cards_list.append(self.deck_creation.deal_a_card())
        # adds the last received card img on the player's layout
        self.adds_card_image(self.ids.player_layout_id, self.forming_card_image(self.player_cards_list, -1))
        # update player hand value
        self.hand_value_update(self.player_sum_check, self.player_cards_list)
        # check for player bust
        self.player_hand_bust_check()
        # check for player auto stand
        self.player_hand_value_equal_21_check()
        # enable hit button
        self.ids.hit_id.disabled = False
        # enable stand button
        self.ids.stand_id.disabled = False
        # enable menu button
        self.ids.menu_id.disabled = False
        # check for jokers after each new card. Prevents win/lose/tie and jokers popups stack
        self.joker_cards_check(self.player_cards_list)

    # stand button
    def on_stand_click(self):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable menu button
        self.ids.menu_id.disabled = True
        # disable hit and stand buttons
        self.h_s_status = True
        # append all player cards values in to the sum list. This way the next check will trigger if there is default
        # ace value. Avoids the bug to skip ace_choice_popup when player stand on first dealt (has 2 cards) and one of
        # the two cards is an ace
        self.hand_value_update(self.player_sum_check, self.player_cards_list)
        # when player finish the turn via the stand button will check for ace card default value. If there ace/s
        # allows ace value selection popup in update. This prevents ace choice popup before player finish his/her turn
        if 0.99 in self.player_sum_check:
            self.player_has_ace = True
        # if no ace/s in player list proceed to dealer move
        else:
            self.dealer_turn_popup()

    # work with KV file. Save the selected slider value to player bet
    def on_slider_value(self, slider_value):
        self.player_bet = int(slider_value.value)

    # updates player displayed credits
    def player_credit_update(self):
        self.ids.player_credit_id.text = f"credits:\n{self.player_credits}"

    # updates player displayed bet
    def player_bet_update(self):
        self.ids.player_bet_id.text = f"bet:\n{self.player_bet}"

    # check for all in
    def player_bet_check(self):

        # all in case
        if self.player_bet == self.player_credits:
            # add AI label in player's side
            self.all_in_label_display()
            # keep and display all in bonus
            self.all_in_event = self.ai_progressive
            # add all in bonus to profit percentage
            self.profit_percentage += self.all_in_event
            # make player's credits 0
            self.player_credits = 0
        # not all in case. Profit percentage stays default value
        else:
            # reduce player bet amount from player's credit
            self.player_credits -= self.player_bet

    # bet button click
    def on_bet_click(self):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disabled bet button
        self.ids.bet_id.disabled = True
        # disable menu button
        self.ids.menu_id.disabled = True
        # run delay bet button
        self.delay_action(self.bet_but_action)
        # check for jokers right after bet button is pressed. Avoids the possibility of clicking the stand button
        # before joker's popups
        self.joker_cards_check(self.player_cards_list)

    # bet button
    def bet_but_action(self, *args):

        # disable slider and bet button and enable hit and stand buttons
        self.h_s_status = False
        self.bet_status = True
        # enable menu button
        self.ids.menu_id.disabled = False
        # adds first dealt player cards images
        self.player_first_dealt_cards_display()
        # adds first dealt dealer cards images
        self.dealer_first_dealt_cards_display()
        # check player bet
        self.player_bet_check()
        # update player credits
        self.player_credit_update()

    # check for player bust or automatic stand
    def player_hand_bust_check(self):

        # player bust popup if owned hand value exceeds 21
        if self.hand_value_update(self.player_sum_check, self.player_cards_list) > 21:
            # stop update
            self.clock_game.cancel()
            # proceed to player bust/loss
            self.player_bust_loss_popup()

    # if player hand value equal 21 triggers dealer turn popup
    def player_hand_value_equal_21_check(self):

        if self.hand_value_update(self.player_sum_check, self.player_cards_list) == 21:
            # proceed to dealer bust/loss
            self.dealer_turn_popup()

    # popup for dealer's turn
    def dealer_turn_popup(self, *args):

        # stop update
        self.clock_game.cancel()

        bx = BoxLayout()
        bx_in = BoxLayout(orientation="vertical")

        self.dealer_turn_ok_but = Button(text="OK",
                                         background_color=self.buttons_color,
                                         background_down="assets/b1.png",
                                         font_size=self.titles_buttons_size,
                                         font_name="aae",
                                         bold=True,
                                         size_hint=(.3, 1)
                                         )

        self.dealer_turn_ok_but.bind(on_press=self.on_dealer_turn_ok)

        # auto stand text if player's hand value equal 21
        if self.hand_value_update(self.player_sum_check, self.player_cards_list) == 21:
            bx_in.add_widget(Label(text="Your hand value is equal 21",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))

        bx.add_widget(bx_in)
        bx.add_widget(self.dealer_turn_ok_but)

        self.dealer_turn_pu = Popup(title="Dealer's turn",
                                    separator_color=self.sep_color,
                                    title_size=self.titles_buttons_size,
                                    title_font="aae",
                                    content=bx,
                                    size_hint=(.8, .6),
                                    auto_dismiss=False
                                    )

        self.dealer_turn_pu.open()

    # on dealer turn click
    def on_dealer_turn_ok(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable ok button
        self.dealer_turn_ok_but.disabled = True
        # replace default disabled blue button color
        self.dealer_turn_ok_but.background_disabled_down = "assets/b1.png"
        self.delay_action(self.dealer_turn_popup_dismiss)

    # dealer turn calculation
    def dealer_turn_popup_dismiss(self, *args):

        # dismiss dealer turn popup
        self.dealer_turn_pu.dismiss(self)
        # proceeds to dealer's move
        self.player_turn_done()

    def player_turn_done(self, *args):

        # disable in game menu button. Avoids player go to menu during dealer move - prevent popups stack bug
        self.ids.menu_id.disabled = True
        # disable hit and stand buttons
        self.h_s_status = True
        # clears dealer's layout from widgets/img, in purpose to re-append them and show the dealer's hidden second card
        self.clears_layout(self.ids.dealer_layout_id)
        # adds dealer's first two cards, but this time second card is revealed
        self.adds_card_image(self.ids.dealer_layout_id, self.forming_card_image(self.dealer_cards_list, 0))
        self.adds_card_image(self.ids.dealer_layout_id, self.forming_card_image(self.dealer_cards_list, 1))
        # allows to proceed to dealer's move in update
        self.player_turn_over = True
        # run update. Dealer turn update a bit slower - .7
        self.clock_game = Clock.schedule_interval(self.update, .7)

    # calculate dealer's ace card after first dealt
    def dealer_ace_after_first_dealt(self):

        for dealer_ace_card in self.dealer_cards_list:
            # if the current dealer's cards sum + 11 does not exceed 21, ace card value will be 11
            # otherwise, it will become 1 to avoids bust
            if dealer_ace_card.value == 0.99:
                # - 0.99 ignoring the default ace value from the calculation
                if ((self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) - 0.99) + 11) <= 21:
                    dealer_ace_card.value = 11
                else:
                    dealer_ace_card.value = 1

    def dealer_move(self):

        # if current dealer hand value is under 17, the dealer must draw a card
        if self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) < 17:
            # the dealer receives a card
            self.dealer_cards_list.append(self.deck_creation.deal_a_card())
            # checks for ace after each dealer card draw
            self.dealer_ace_after_first_dealt()
            # add the last received dealer's card img on the dealer's layout
            self.adds_card_image(self.ids.dealer_layout_id, self.forming_card_image(self.dealer_cards_list, -1))
        # if dealer no longer under 17 proceeds to hand value check
        else:
            # when player turn is done, menu button is enabled
            self.ids.menu_id.disabled = False
            # stop update
            self.clock_game.cancel()
            # check dealer hand
            self.dealer_hand_value_check()

    # dealer hand value check
    def dealer_hand_value_check(self):

        # if the dealer's hand value is above/equal 17, but less/equal 21, the dealer's turn ends and proceed
        # to win-tie-loss check
        if 17 <= self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) <= 21:
            self.win_tie_loss_check()
        # busts the dealer if hand value exceeds 21
        else:
            self.dealer_bust_loss_popup()

    def win_tie_loss_check(self):

        # tie cases (equal hands value)
        if self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) == \
                self.hand_value_update(self.player_sum_check, self.player_cards_list):
            # different from 21 tie (both player and dealer have any equal hands value except 21)
            if self.hand_value_update(self.player_sum_check, self.player_cards_list) != 21:
                self.tie_popup()
            # blackjack tie (both player and dealer have blackjack)
            elif (self.hand_value_update(self.player_sum_check, self.player_cards_list) == 21) and \
                    (len(self.player_cards_list) == 2 and len(self.dealer_cards_list) == 2):
                self.tie_popup()
            # 21 tie but not a blackjack (both player and dealer have hands value equal 21, but it's not blackjack)
            elif (self.hand_value_update(self.player_sum_check, self.player_cards_list) == 21) and \
                    (len(self.player_cards_list) != 2 and len(self.dealer_cards_list) != 2):
                self.tie_popup()
            # player's blackjack wins over dealer's non-blackjack 21 hand value
            elif (self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) == 21) and \
                    (len(self.player_cards_list) == 2 and len(self.dealer_cards_list) > 2):
                self.dealer_bust_loss_popup()
            # dealer's blackjack wins over player's non-blackjack 21 hand value
            elif (self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) == 21) and \
                    (len(self.dealer_cards_list) == 2 and len(self.player_cards_list) > 2):
                self.player_bust_loss_popup()
        # player win with higher hand value
        elif self.hand_value_update(self.player_sum_check, self.player_cards_list) > \
                self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list):
            self.dealer_bust_loss_popup()
        # dealer win with higher hand value
        elif self.hand_value_update(self.player_sum_check, self.player_cards_list) < \
                self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list):
            self.player_bust_loss_popup()

    # player bust/loss popup
    def player_bust_loss_popup(self):

        # play loss turn sound
        GameAudio.GameSound.play_loss_turn_sound()

        # title if player is bust
        if self.hand_value_update(self.player_sum_check, self.player_cards_list) > 21:
            title = "You are busted"
        else:
            # title if dealer win with blackjack
            if (self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list)) == 21 and \
                    (len(self.dealer_cards_list) == 2):
                title = "Dealer has Blackjack"
            # title if dealer win without blackjack
            else:
                title = "Dealer's win"

        bx = BoxLayout()
        bx_in = BoxLayout(orientation="vertical")

        self.player_loss_ok_but = Button(text="OK",
                                         size_hint=(.3, 1),
                                         background_color=self.buttons_color,
                                         background_down='assets/b1.png',
                                         font_size=self.titles_buttons_size,
                                         font_name="aae",
                                         bold=True
                                         )

        bx_in.add_widget(Label(text=f"You lost your bet: {self.player_bet} credits",
                               font_size=self.text_size,
                               font_name="aae"
                               ))

        # adds events info if occurs
        if self.aces_pick_cost != 0:
            bx_in.add_widget(Label(text=f"Aces selection cost: {str(self.aces_pick_cost)} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        if self.player_has_black_jk:
            bx_in.add_widget(Label(text=f"Black Joker's impact: +{self.black_joker_impact()} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        elif self.dealer_has_black_jk:
            bx_in.add_widget(Label(text=f"Black Joker's impact: -{self.black_joker_impact()} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))

        self.player_loss_ok_but.bind(on_release=self.on_player_bust_loss_click)

        bx.add_widget(bx_in)
        bx.add_widget(self.player_loss_ok_but)

        self.player_bust_loss_pu = Popup(title=title,
                                         title_size=self.titles_buttons_size,
                                         title_font="aae",
                                         content=bx,
                                         separator_color=self.sep_color,
                                         size_hint=(.8, .6),
                                         auto_dismiss=False
                                         )

        # dealer wins remove black joker's impacts upon him
        self.player_has_black_jk = False

        # remove black joker label from player's layout
        if not self.player_has_black_jk:
            self.clears_layout(self.ids.p_bjk_id)

        self.player_bust_loss_pu.open()

    # on player loss ok button
    def on_player_bust_loss_click(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable ok button
        self.player_loss_ok_but.disabled = True
        self.delay_action(self.player_bust_loss_popup_dismiss)

    # player loss calculation
    def player_bust_loss_popup_dismiss(self, *args):

        # rescale player rank
        self.ranking_scale()
        # player bust/loss dismiss
        self.player_bust_loss_pu.dismiss(self)
        # check for victory, game over or reset ofr the new turn
        self.game_status_check()

    # dealer bust/loss popup
    def dealer_bust_loss_popup(self):

        # play win turn sound
        GameAudio.GameSound.play_win_turn_sound()

        # red joker calculation
        self.red_joker_calculation()

        # set a title
        # daler bust title
        if self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list) > 21:
            win_title = "Dealer is busted"
        else:
            # player has blackjack title
            if self.hand_value_update(self.player_sum_check, self.player_cards_list) == 21 and \
                    len(self.player_cards_list) == 2:
                win_title = "You have Blackjack"
            else:
                # player wins title (non-blackjack)
                win_title = "You win"

        bx = BoxLayout()
        # inside layout. Display events (if they occur) and final profit percentage
        bx_in = BoxLayout(orientation="vertical")

        self.dealer_loss_ok_but = Button(text="OK",
                                         size_hint=(.3, 1),
                                         background_color=self.buttons_color,
                                         background_down='assets/b1.png',
                                         font_size=self.titles_buttons_size,
                                         font_name="aae",
                                         bold=True
                                         )

        # if events occur it will be displayed in the popup
        # red joker event
        if self.red_joker_popup_txt != "":
            bx_in.add_widget(Label(text=self.red_joker_popup_txt,
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
            # sets back to an empty string, so it won't trigger the event until it occurs
            self.red_joker_popup_txt = ""
        # drawing a card bonus
        if self.hit_card_event != 0:
            bx_in.add_widget(Label(text=f"Hit a card: +{str(round(self.hit_card_event, 2))} profit percentage",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        # player's first two cards are aces
        if self.two_ace_player_event != 0:
            bx_in.add_widget(Label(text=f"Player's 2ACE: +{str(self.two_ace_player_event)} profit percentage",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        # dealer's first two cards are aces
        if self.two_ace_dealer_event != 0:
            bx_in.add_widget(Label(text=f"Dealer's 2ACE: -{str(self.two_ace_dealer_event)} profit percentage",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        # player all in
        if self.all_in_event != 0:
            bx_in.add_widget(Label(text=f"All in: +{str(self.all_in_event)} profit percentage",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        # display the final profit percentage after events calculation
        bx_in.add_widget(Label(text=f"Final profit percentage: {str(round(self.profit_percentage, 2))}",
                               font_size=self.text_size,
                               font_name="aae"
                               ))
        # display the transfer cost of ace selections for the turn
        if self.aces_pick_cost != 0:
            bx_in.add_widget(Label(text=f"Aces selection cost: {str(self.aces_pick_cost)} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        # display black joker impact depends on the owner
        if self.player_has_black_jk:
            # add credits if owned by player
            bx_in.add_widget(Label(text=f"Black Joker's impact: +{self.black_joker_impact()} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))
        elif self.dealer_has_black_jk:
            # subtracts credits if owned by dealer
            bx_in.add_widget(Label(text=f"Black Joker's impact: -{self.black_joker_impact()} credits",
                                   font_size=self.text_size,
                                   font_name="aae"
                                   ))

        self.dealer_loss_ok_but.bind(on_release=self.on_dealer_bust_loss_click)

        bx.add_widget(bx_in)
        bx.add_widget(self.dealer_loss_ok_but)

        self.dealer_bust_loss_pu = Popup(title=f"{win_title} - Credits earned:"
                                               f" {int(self.player_bet * round(self.profit_percentage, 2))}",
                                         separator_color=self.sep_color,
                                         content=bx,
                                         title_size=self.titles_buttons_size,
                                         title_font="aae",
                                         size_hint=(.9, .6),
                                         auto_dismiss=False
                                         )

        # if the player wins then remove black joker's impacts upon him
        self.dealer_has_black_jk = False

        # remove black joker label from dealer's layout
        if not self.dealer_has_black_jk:
            self.clears_layout(self.ids.d_bjk_id)

        # clear red joker label after it tricks is applied (if the event occurred)
        self.clears_layout(self.ids.p_rjk_id)
        self.clears_layout(self.ids.d_rjk_id)

        self.dealer_bust_loss_pu.open()

    # on dealer loss click
    def on_dealer_bust_loss_click(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable button
        self.dealer_loss_ok_but.disabled = True
        self.delay_action(self.dealer_bust_loss_popup_dismiss)

    # dealer loss calculation
    def dealer_bust_loss_popup_dismiss(self, *args):

        # dealer bust/loss popup dismiss
        self.dealer_bust_loss_pu.dismiss(self)
        # run curse/bless
        self.curse_bless_random_choice()
        # adding the win to player credit. Curse/bless calculation apply before (if event occurred)
        self.player_credits += int(self.player_bet * round(self.profit_percentage, 2))
        # updates player rank
        self.ranking_scale()
        # check for victory, game over or reset for the new turn
        self.game_status_check()

    def tie_popup(self):

        # play tie sound
        GameAudio.GameSound.play_tie_sound()

        bx = BoxLayout(orientation="vertical")

        self.tie_ok_but = Button(text="OK",
                                 size_hint=(1, .95),
                                 background_color=self.buttons_color,
                                 background_down='assets/b1.png',
                                 font_size=self.titles_buttons_size,
                                 font_name="aae",
                                 bold=True
                                 )

        bx.add_widget(Label(text=f"Your hand value: "
                                 + str(self.hand_value_update(self.player_sum_check, self.player_cards_list)),
                            font_size=self.text_size,
                            font_name="aae"
                            ))

        bx.add_widget(Label(text=f"Dealer's hand value: "
                                 + str(self.hand_value_update(self.dealer_sum_check, self.dealer_cards_list)),
                            font_size=self.text_size,
                            font_name="aae"
                            ))

        # adds black joker impact text if event occurred
        if self.player_has_black_jk:
            bx.add_widget(Label(text=f"Black Joker's impact: +{self.black_joker_impact()} credits",
                                font_size=self.text_size,
                                font_name="aae"
                                ))
        elif self.dealer_has_black_jk:
            bx.add_widget(Label(text=f"Black Joker's impact: -{self.black_joker_impact()} credits",
                                font_size=self.text_size,
                                font_name="aae"
                                ))

        self.tie_ok_but.bind(on_release=self.on_tie_click)
        bx.add_widget(self.tie_ok_but)

        self.tie_pu = Popup(title="Tie",
                            separator_color=self.sep_color,
                            content=bx,
                            title_size=self.titles_buttons_size,
                            title_font="aae",
                            size_hint=(.8, .6),
                            auto_dismiss=False
                            )

        self.tie_pu.open()

    # on tie click
    def on_tie_click(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # tie ok button disable
        self.tie_ok_but.disabled = True
        self.delay_action(self.tie_popup_dismiss)

    # tie calculation
    def tie_popup_dismiss(self, *args):

        # returns player's current bet to his/her credits
        self.player_credits += self.player_bet
        # tie popup dismiss
        self.tie_pu.dismiss(self)
        # check for victory, game over or reset ofr the new turn
        self.game_status_check()

    # depending on the player's current credits will trigger victory popup or game over
    # popup or resets the game for the new turn
    def game_status_check(self):

        # in case the player not reach the last rank, bless/curse popup will be triggered (if occurs) and game will
        # resset for the new turn
        # in case the player reach the last rank and bless/curse event occur, the event popup will be skipped and
        # additional message will be added to celebration screen to inform the player for the event
        if 0 < self.player_credits <= 10000:
            if self.labyrinth_choice_result == "bless":
                self.bless_popup()
            elif self.labyrinth_choice_result == "curse":
                self.curse_popup()
            # the game reset for the new turn
            self.game_reset()
        # triggers victory popup if the player accumulates credits over 25m
        elif self.player_credits > 10000:
            self.delay_action(self.victory_popup)
        # triggers game over popup if player credits are 0 or less
        elif self.player_credits <= 0:
            self.delay_action(self.game_over_popup)

    def victory_popup(self, *args):

        # stop in game sound
        GameAudio.GameSound.stop_in_game_sound()

        # play victory sound
        GameAudio.GameSound.play_victory_sound()

        # allows dismissing only victory popup
        self.player_victory = True

        # victory text changes depending on bless or curse or no event
        if self.labyrinth_choice_result == "bless":
            # bless event
            txt = f"With the blessing of the Labyrinth \nyou have reached the last rank - Conqueror of the Labyrinth"
        elif self.labyrinth_choice_result == "curse":
            # curse event
            txt = f"Despite the curse of the Labyrinth \nyou have reached the last rank - Conqueror of the Labyrinth"
        else:
            # no event
            txt = f"You have reached the last rank - Conqueror of the Labyrinth"

        # update credits
        self.player_credit_update()

        bx = BoxLayout(orientation="vertical")

        self.victory_return_but = Button(text="Return to menu",
                                         size_hint=(1, .5),
                                         background_color=self.buttons_color,
                                         background_down='assets/b1.png',
                                         font_size=self.titles_buttons_size,
                                         font_name="aae",
                                         bold=True
                                         )

        self.victory_return_but.bind(on_release=self.on_victory_click)

        bx.add_widget(Label(text="Congratulations!",
                            font_size=self.titles_buttons_size,
                            font_name="aae",
                            bold=True
                            ))
        bx.add_widget(Label(text=txt,
                            font_size=self.text_size,
                            font_name="aae"
                            ))
        bx.add_widget(Label(text=f"Your credits: {self.player_credits}",
                            font_size=self.text_size,
                            font_name="aae"
                            ))
        # adds the played turns
        bx.add_widget(Label(text=f"turns played: {str(self.turns_counter)}",
                            font_size=self.text_size,
                            font_name="aae"))

        bx.add_widget(self.victory_return_but)

        self.victory_pu = Popup(title="",
                                separator_height=0,
                                content=bx,
                                size_hint=(.9, .9),
                                auto_dismiss=False
                                )

        self.victory_pu.open()

    # on victory click
    def on_victory_click(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable victory button
        self.victory_return_but.disabled = True
        self.delay_action(self.end_of_game)

    def game_over_popup(self, *args):

        # stop in game sound
        GameAudio.GameSound.stop_in_game_sound()

        # play game over sound
        GameAudio.GameSound.play_game_over_sound()

        # updates credits
        self.player_credit_update()

        bx = BoxLayout()
        bx_in = BoxLayout(orientation="vertical")

        self.game_over_ok_but = Button(text="OK",
                                       size_hint=(.3, 1),
                                       background_color=self.buttons_color,
                                       background_down='assets/b1.png',
                                       font_size=self.titles_buttons_size,
                                       font_name="aae",
                                       bold=True
                                       )

        self.game_over_ok_but.bind(on_release=self.on_game_over_click)

        # adds info if best credits held
        if self.player_best_result != 0:
            bx_in.add_widget(Label(text=f"The most credits held: {self.player_best_result}",
                                   font_size=self.text_size,
                                   font_name="aae"))
        # adds info for rank
        if self.player_rank != "":
            bx_in.add_widget(Label(text=self.player_rank,
                                   font_size=self.text_size,
                                   font_name="aae"))
        # adds the played turns
        bx_in.add_widget(Label(text=f"turns played: {str(self.turns_counter)}",
                               font_size=self.text_size,
                               font_name="aae"))

        bx.add_widget(bx_in)
        bx.add_widget(self.game_over_ok_but)

        self.game_over_pu = Popup(title="Game over",
                                  separator_color=self.sep_color,
                                  title_size=self.titles_buttons_size,
                                  title_font="aae",
                                  content=bx,
                                  size_hint=(.8, .6),
                                  auto_dismiss=False
                                  )

        self.game_over_pu.open()

    # on game over click
    def on_game_over_click(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # disable game over button
        self.game_over_ok_but.disabled = True
        self.delay_action(self.end_of_game)

    # victory or game over
    def end_of_game(self, *args):

        # if player reach last rank it will close victory popup, otherwise will close game_over_popup
        # avoids trying to close a not opened popup error
        if self.player_victory:
            # change Resume button text to Play
            self.manager.get_screen('main').ids['play_but_id'].text = "Play"
            # dismiss victory popup
            self.victory_pu.dismiss(self)
            # changes the scree to main menu
            self.manager.current = "main"
            # play menu sound
            GameAudio.GameSound.play_menu_sound()
        else:
            self.game_over_pu.dismiss(self)
            # play in game sound
            GameAudio.GameSound.play_in_game_sound()

        # allows resetting the game to starting values
        self.game_over = True
        # resset for the new turn/game
        self.game_reset()

    def game_reset(self):

        # victory and game over resets the game to default values (game_over is True). Otherwise, does soft reset
        # for the new turn
        if self.game_over:
            self.player_credits = 50
            self.player_best_result = 0
            self.player_rank = ""
            self.player_victory = False
            self.player_has_red_jk = False
            self.player_has_black_jk = False
            self.dealer_has_red_jk = False
            self.dealer_has_black_jk = False
            self.red_joker_popup_txt = ""
            # clears RJ and BJ labels
            self.clears_layout(self.ids.p_rjk_id)
            self.clears_layout(self.ids.d_rjk_id)
            self.clears_layout(self.ids.p_bjk_id)
            self.clears_layout(self.ids.d_bjk_id)
            self.turns_counter = 0

        all_cards.clear()
        self.dealer_cards_list.clear()
        self.player_cards_list.clear()
        self.player_bet = 1
        self.player_sum_check.clear()
        self.dealer_sum_check.clear()
        self.player_ace_choice = 0
        self.game_over = False
        self.h_s_status = True
        self.bet_status = False
        self.player_turn_over = False
        self.labyrinth_choice_result = ""
        self.player_has_ace = False
        self.red_jk_event = 0
        self.hit_card_event = 0
        self.two_ace_player_event = 0
        self.two_ace_dealer_event = 0
        self.all_in_event = 0
        self.aces_pick_cost = 0
        self.ace_name = ""
        self.ids.menu_id.disabled = False

        # adds a turn
        self.turns_counter += 1

        # sets the difficulty for the new turn
        self.dynamic_difficulty_adjustment()

        # display difficulty label
        self.difficulty_label_display()

        # clears AI label from player's side
        self.clears_layout(self.ids.p_ai_id)

        # updates slider max value to player credits
        self.slider_max_bet = str(self.player_credits)
        # returns slider position in default position
        self.ids.slider_id.value = 1
        # resets visualization on player bet to 1
        self.ids.player_bet_id.text = f"bet:\n{1}"

        # clears widgets/cards from player and dealer layouts
        self.clears_layout(self.ids.player_layout_id)
        self.clears_layout(self.ids.dealer_layout_id)

        # recreating the cards deck
        self.deck_creation.__init__()
        # shuffle the deck
        self.deck_creation.shuffle()
        # deal first 4 cards to player and dealer
        self.deals_first_cards()

        # updates the player's credits
        self.player_credit_update()

        # run update
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)

    # the ranking scale determines players' rank
    def ranking_scale(self):

        # each turn save the player's best result. If the game is over by loss it will display the best achievement in
        # the game over popup
        if self.player_credits > self.player_best_result:
            self.player_best_result = self.player_credits

        # ranks depend on credits held
        if 200 < self.player_best_result <= 1000:
            self.player_rank = "You achieved 7th rank: Beginner"
        elif 1000 < self.player_best_result <= 2000:
            self.player_rank = "You achieved 6th rank: Risk-taker"
        elif 2000 < self.player_best_result <= 3000:
            self.player_rank = "You achieved 5th rank: Challenger"
        elif 3000 < self.player_best_result <= 4000:
            self.player_rank = "You achieved 4th rank: Master"
        elif 4000 < self.player_best_result <= 7000:
            self.player_rank = "You achieved 3rd rank: Grandmaster"
        elif 7000 < self.player_best_result <= 10000:
            self.player_rank = "You achieved 2nd rank: Legend"

    # player's achieved credits increase the difficulty. Adds label when difficulty goes up
    # increase the difficulty by reducing the player's bonuses for all in, profit_percentage and
    # increase curse event chance
    def dynamic_difficulty_adjustment(self):

        # default values
        if 0 < self.player_credits <= 1000:
            self.difficulty = ""
            self.profit_percentage = 1.5
            self.ai_progressive = 0.5
            self.no_event_chance = 80
            self.bless_chance = 10
            self.curse_chance = 10
        # difficulty 1
        elif 1000 < self.player_credits <= 2500:
            self.difficulty = "D1"
            self.profit_percentage = 1.3
            self.ai_progressive = 0.2
            self.no_event_chance = 70
            self.bless_chance = 10
            self.curse_chance = 20
        # difficulty 2
        elif 2500 < self.player_credits:
            self.difficulty = "D2"
            self.profit_percentage = 1.2
            self.ai_progressive = 0.1
            self.no_event_chance = 60
            self.bless_chance = 10
            self.curse_chance = 30

    # display difficulty label
    def difficulty_label_display(self):

        # clear difficulty label before adding it again. Avoids stacking labels
        self.clears_layout(self.ids.difficulty_id)

        self.ids.difficulty_id.add_widget(Label(text=self.difficulty,
                                                font_size=self.display_info_size,
                                                font_name="aae",
                                                bold=True,
                                                outline_color=(18 / 255, 18 / 255, 18 / 255),
                                                outline_width=1
                                                ))

    # display all in label
    def all_in_label_display(self):

        self.ids.p_ai_id.add_widget(Label(text="AI",
                                          font_size=self.display_info_size,
                                          font_name="aae",
                                          bold=True,
                                          outline_color=(18 / 255, 18 / 255, 18 / 255),
                                          outline_width=1
                                          ))

    # display black joker label
    def black_joker_label_display(self):

        # change by owner of the black joker, so it adds to correct layout
        layout_id = ""

        if self.player_has_black_jk:
            layout_id = self.ids.p_bjk_id
        elif self.dealer_has_black_jk:
            layout_id = self.ids.d_bjk_id

        layout_id.add_widget(Label(text="BJ",
                                   font_size=self.display_info_size,
                                   font_name="aae",
                                   bold=True,
                                   outline_color=(18 / 255, 18 / 255, 18 / 255),
                                   outline_width=1
                                   ))

    # display red joker label
    def red_joker_label_display(self):

        # # change by owner on the red joker, so it adds to correct layout
        layout_id = ""

        if self.player_has_red_jk:
            layout_id = self.ids.p_rjk_id
        elif self.dealer_has_red_jk:
            layout_id = self.ids.d_rjk_id

        layout_id.add_widget(Label(text="RJ",
                                   font_size=self.display_info_size,
                                   font_name="aae",
                                   bold=True,
                                   outline_color=(18 / 255, 18 / 255, 18 / 255),
                                   outline_width=1
                                   ))

    # adding chance for credits earned by the player to be increased or decreased
    # each player's win has default values 80% no event, 10% to bless, 10% to curse, but they change with the difficulty
    def curse_bless_random_choice(self):

        chance = self.no_event_chance, self.bless_chance, self.curse_chance
        options = "no event", "bless", "curse"
        picks = [o for o, c in zip(options, chance) for _ in range(c)]

        # bless - increase profit percentage with 30%
        if random.choice(picks) == "bless":
            self.profit_percentage += self.profit_percentage * 0.3
            self.labyrinth_choice_result = "bless"
        # curse - decrease profit percentage with 30%
        elif random.choice(picks) == "curse":
            self.profit_percentage -= self.profit_percentage * 0.3
            self.labyrinth_choice_result = "curse"

    def curse_popup(self, *args):

        # play curse sound
        GameAudio.GameSound.play_curse_sound()

        bx = BoxLayout()

        # sets 4 sec popup duration
        Clock.schedule_once(self.curse_popup_dismiss, 4)

        bx.add_widget(self.background_img("assets/curse_bg.jpg"))

        self.curse_pu = Popup(title=f"Your victory was cursed! Earned credits after:"
                                    f" {int(self.player_bet * round(self.profit_percentage, 2))}",
                              content=bx,
                              title_size=self.text_size,
                              title_font="aae",
                              separator_color=self.sep_color,
                              size_hint=(.8, .9),
                              auto_dismiss=True
                              )

        self.curse_pu.open()

    def curse_popup_dismiss(self, *args):
        self.curse_pu.dismiss(self)

    def bless_popup(self, *args):

        # play bless sound
        GameAudio.GameSound.play_bless_sound()

        bx = BoxLayout()

        # sets 4 sec popup duration
        Clock.schedule_once(self.bless_popup_dismiss, 4)

        bx.add_widget(self.background_img("assets/bless_bg.jpg"))

        self.bless_pu = Popup(title=f"Your victory was blessed! Earned credits after:"
                                    f" {int(self.player_bet * round(self.profit_percentage, 2))}",
                              content=bx,
                              title_size=self.text_size,
                              title_font="aae",
                              separator_color=self.sep_color,
                              size_hint=(.8, .9),
                              auto_dismiss=True
                              )

        self.bless_pu.open()

    def bless_popup_dismiss(self, *args):
        self.bless_pu.dismiss(self)

    def black_joker_popup(self, *args):

        # play black joker sound
        GameAudio.GameSound.play_bjk_sound()

        # stop update
        self.clock_game.cancel()

        # sets the popup's text depending on the black joker owner
        if -0.20 in self.player_sum_check:
            txt = "The Black Joker's impact is on your side"
        else:
            txt = "The Black Joker's impact is on the dealer's side"

        bx = BoxLayout(orientation="vertical")

        ok_but = Button(text="OK",
                        background_color=self.buttons_color,
                        background_down="assets/b1.png",
                        font_size=self.titles_buttons_size,
                        font_name="aae",
                        bold=True,
                        size_hint=(1, .4)
                        )

        ok_but.bind(on_press=self.black_joker_popup_dismiss)

        bx.add_widget(Label(text=txt,
                            font_size=self.titles_buttons_size,
                            font_name="aae"
                            ))

        bx.add_widget(ok_but)

        self.bjk_pu = Popup(title="",
                            separator_height=0,
                            content=bx,
                            size_hint=(.8, .6),
                            auto_dismiss=False
                            )

        self.bjk_pu.open()

    # changes default black joker card value from -0.20 to 0 for both player and dealer
    def black_joker_value_change(self, cards_lst):

        for black_joker in cards_lst:
            if black_joker.value == -0.20:
                black_joker.value = 0
                # if owned by player, turn off dealer's bool
                if cards_lst == self.player_cards_list:
                    self.player_has_black_jk = True
                    self.dealer_has_black_jk = False
                # if owned by dealer, turn off player's bool
                else:
                    self.player_has_black_jk = False
                    self.dealer_has_black_jk = True

    # black joker calculation for both player and dealer
    def black_joker_impact(self):

        # save black joker impact result
        impact_result = 0
        # sum_result is a sum of player's credit and bet
        sum_result = self.player_credits + self.player_bet

        # impact is formed as a % from the sum of the credit and the bet
        if sum_result > 5000:
            # above 5k impact is 0.1% from sum_result
            impact_result = int(sum_result * 0.1)
        elif 200 < sum_result <= 5000:
            # between 200 and 5k impact is 0.05% from sum_result
            impact_result = int(sum_result * 0.05)
        elif sum_result <= 200:
            # under 200 impact is 10
            impact_result = 10

        # if black joker owned by player add the impact to player's credit
        if self.player_has_black_jk:
            self.player_credits += impact_result
        # if black joker owned by dealer subtracts the impact from player's credit
        elif self.dealer_has_black_jk:
            self.player_credits -= impact_result

        return impact_result

    def black_joker_popup_dismiss(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # black joker card value changes for player
        self.black_joker_value_change(self.player_cards_list)
        # black joker card value changes for dealer
        self.black_joker_value_change(self.dealer_cards_list)
        # clear layouts if there is already black joker in order to append the label in the correct layout
        self.clears_layout(self.ids.d_bjk_id)
        self.clears_layout(self.ids.p_bjk_id)
        # display black joker label
        self.black_joker_label_display()
        # black joker popup dismiss
        self.bjk_pu.dismiss(self)
        # run update
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)

    def red_joker_popup(self, *args):

        # play red joker sound
        GameAudio.GameSound.play_rjk_sound()

        # stop update
        self.clock_game.cancel()

        # sets the popup's text depending on the red joker owner
        if -0.10 in self.player_sum_check:
            txt = "The Red Joker's trick is on your side"
        else:
            txt = "The Red Joker's trick is on the dealer's side"

        bx = BoxLayout(orientation="vertical")

        ok_but = Button(text="OK",
                        background_color=self.buttons_color,
                        background_down="assets/b1.png",
                        font_size=self.titles_buttons_size,
                        font_name="aae",
                        bold=True,
                        size_hint=(1, .4)
                        )

        ok_but.bind(on_press=self.red_joker_popup_dismiss)

        bx.add_widget(Label(text=txt,
                            font_size=self.titles_buttons_size,
                            font_name="aae"
                            ))

        bx.add_widget(ok_but)

        self.rjk_pu = Popup(title="",
                            separator_height=0,
                            content=bx,
                            size_hint=(.8, .6),
                            auto_dismiss=False
                            )

        self.rjk_pu.open()

    # changes default red joker card value from -0.10 to 0 for both player and dealer
    def red_joker_value_change(self, cards_lst):

        for red_joker in cards_lst:
            if red_joker.value == -0.10:
                red_joker.value = 0
                # if owned by player, turn off dealer's bool
                if cards_lst == self.player_cards_list:
                    self.player_has_red_jk = True
                    self.dealer_has_red_jk = False
                # if owned by dealer, turn off player's bool
                else:
                    self.player_has_red_jk = False
                    self.dealer_has_red_jk = True

    # the red joker's trick applies to the dealer or the player
    def red_joker_trick(self):

        # multiply len of the player list to 0.15 (0.15 profit percentage for each owned card)
        rj_trick_result = len(self.player_cards_list) * 0.15
        # save the result in order to display it as event info
        self.red_jk_event = rj_trick_result

        return rj_trick_result

    def red_joker_calculation(self):

        # the player wins and owns the red joker
        if self.player_has_red_jk:
            # increase profit percentage
            self.profit_percentage += self.red_joker_trick()
            # remove the card's effect once it's applied
            self.player_has_red_jk = False
            # sets red joker popup text
            self.red_joker_popup_txt = f"Red Joker's trick: +{str(round(self.red_jk_event, 2))} profit percentage"
        # the player wins, but the dealer owns the red joker
        elif self.dealer_has_red_jk:
            # decrease profit percentage
            self.profit_percentage -= self.red_joker_trick()
            # remove the card's effect once it's applied
            self.dealer_has_red_jk = False
            # sets red joker popup text
            self.red_joker_popup_txt = f"Red Joker's trick: -{str(round(self.red_jk_event, 2))} profit percentage"

    def red_joker_popup_dismiss(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # red joker card value changes for player
        self.red_joker_value_change(self.player_cards_list)
        # red joker card value changes for dealer
        self.red_joker_value_change(self.dealer_cards_list)
        # clear layouts if there is already red joker in order to append the label in the correct layout
        self.clears_layout(self.ids.d_rjk_id)
        self.clears_layout(self.ids.p_rjk_id)
        # display red joker label
        self.red_joker_label_display()
        # red joker popup dismiss
        self.rjk_pu.dismiss(self)
        # run update
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)

    # popup for game restart
    def restart_popup(self):

        # stop update
        self.clock_game.cancel()

        bx = BoxLayout(orientation="vertical")

        bx_in = BoxLayout(size_hint=(1, .4))

        # yes but
        yes_but = Button(text="YES",
                         background_color=self.buttons_color,
                         background_down='assets/b1.png',
                         font_size=self.titles_buttons_size,
                         font_name="aae",
                         bold=True,
                         size_hint=(.5, 1)
                         )
        # no but
        no_but = Button(text="NO",
                        background_color=self.buttons_color,
                        background_down='assets/b1.png',
                        font_size=self.titles_buttons_size,
                        font_name="aae",
                        bold=True,
                        size_hint=(.5, 1)
                        )

        no_but.bind(on_press=self.res_no_but_dismiss)
        yes_but.bind(on_press=self.res_yes_but_dismiss)

        bx.add_widget(Label(text="Do you want to restart the game?",
                            font_size=self.titles_buttons_size,
                            font_name="aae"
                            ))

        bx.add_widget(bx_in)
        # adds the buttons to internal boxlayout
        bx_in.add_widget(no_but)
        bx_in.add_widget(yes_but)

        self.res_pu = Popup(title="",
                            separator_height=0,
                            content=bx,
                            size_hint=(.8, .6),
                            auto_dismiss=False
                            )

        self.res_pu.open()

    # the "no" button resume the game
    def res_no_but_dismiss(self, *args):

        # play but sound
        GameAudio.GameSound.play_buttons_sound()
        # restart popup dismiss
        self.res_pu.dismiss(self)
        # run update
        self.clock_game = Clock.schedule_interval(self.update, self.game_update_frequency)

    # the "yes" button restart the game
    def res_yes_but_dismiss(self, *args):

        # play but resset sound
        GameAudio.GameSound.play_restart_sound()
        # allows resset the game to default values
        self.game_over = True
        # resset the game
        self.game_reset()
        # reset popup dismiss
        self.res_pu.dismiss(self)


class BjlApp(App):

    Window.borderless = True
    Window.size = (1366, 768)

    def build(self):
        return ScreenManager()


if __name__ == "__main__":
    BjlApp().run()
