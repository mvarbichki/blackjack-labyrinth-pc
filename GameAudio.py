from kivy.core.audio import SoundLoader

# preloads all sound to make app lighter
in_game = SoundLoader.load("assets/sounds/in_game.wav")
menu = SoundLoader.load("assets/sounds/menu.wav")
info_menu = SoundLoader.load("assets/sounds/info_menu.wav")
bjk = SoundLoader.load("assets/sounds/bjk.wav")
bless = SoundLoader.load("assets/sounds/bless.wav")
buttons = SoundLoader.load("assets/sounds/buttons.wav")
curse = SoundLoader.load("assets/sounds/curse.wav")
game_over = SoundLoader.load("assets/sounds/game_over.wav")
info_but = SoundLoader.load("assets/sounds/info_but.wav")
loss_turn = SoundLoader.load("assets/sounds/loss_turn.wav")
play_but = SoundLoader.load("assets/sounds/play_but.wav")
rjk = SoundLoader.load("assets/sounds/rjk.wav")
tie = SoundLoader.load("assets/sounds/tie.wav")
victory = SoundLoader.load("assets/sounds/victory.wav")
win_turn = SoundLoader.load("assets/sounds/win_turn.wav")
restart_game = SoundLoader.load("assets/sounds/restart.wav")


# play/stop/volume/loop setup
class GameSound:

    @staticmethod
    def play_in_game_sound():
        if in_game:
            in_game.loop = True
            in_game.play()

    @staticmethod
    def stop_in_game_sound():
        in_game.stop()

    @staticmethod
    def play_menu_sound():
        if menu:
            menu.loop = True
            menu.play()

    @staticmethod
    def stop_menu_sound():
        menu.stop()

    @staticmethod
    def play_info_sound():
        if info_menu:
            info_menu.loop = True
            info_menu.play()

    @staticmethod
    def stop_info_sound():
        info_menu.stop()

    @staticmethod
    def play_bjk_sound():
        if bjk:
            bjk.loop = False
            bjk.play()

    @staticmethod
    def play_bless_sound():
        if bless:
            bless.loop = False
            bless.play()

    @staticmethod
    def play_buttons_sound():
        if buttons:
            buttons.loop = False
            buttons.play()

    @staticmethod
    def play_curse_sound():
        if curse:
            curse.loop = False
            curse.play()

    @staticmethod
    def play_game_over_sound():
        if game_over:
            game_over.loop = False
            game_over.play()

    @staticmethod
    def play_info_but_sound():
        if info_but:
            info_but.loop = False
            info_but.play()

    @staticmethod
    def play_loss_turn_sound():
        if loss_turn:
            loss_turn.loop = False
            loss_turn.play()

    @staticmethod
    def play_play_but_sound():
        if play_but:
            play_but.loop = False
            play_but.play()

    @staticmethod
    def play_rjk_sound():
        if rjk:
            rjk.loop = False
            rjk.play()

    @staticmethod
    def play_tie_sound():
        if tie:
            tie.loop = False
            tie.play()

    @staticmethod
    def play_victory_sound():
        if victory:
            victory.loop = False
            victory.play()

    @staticmethod
    def play_win_turn_sound():
        if win_turn:
            win_turn.loop = False
            win_turn.play()

    @staticmethod
    def play_restart_sound():
        if restart_game:
            restart_game.loop = False
            restart_game.play()

    @staticmethod
    def sound_off():
        in_game.volume = 0
        menu.volume = 0
        info_menu.volume = 0
        bjk.volume = 0
        bless.volume = 0
        buttons.volume = 0
        curse.volume = 0
        game_over.volume = 0
        info_but.volume = 0
        loss_turn.volume = 0
        play_but.volume = 0
        rjk.volume = 0
        tie.volume = 0
        victory.volume = 0
        win_turn.volume = 0
        restart_game.volume = 0

    @staticmethod
    def sound_on():
        in_game.volume = .8
        menu.volume = 1
        info_menu.volume = .8
        bjk.volume = .8
        bless.volume = .8
        buttons.volume = .8
        curse.volume = .8
        game_over.volume = 1
        info_but.volume = .8
        loss_turn.volume = 1
        play_but.volume = .8
        rjk.volume = .8
        tie.volume = .8
        victory.volume = 1
        win_turn.volume = .8
        restart_game.volume = .8
