import cmd
from game import Game
from player import Proponent, Opponent


class GameShell(cmd.Cmd):
    intro = """This is the grounded persuasion game. Commands:
    new_game (file_path, proponent is a bot, opponent is a bot) - to start a game
    quit, close, exit, stop - to leave"""
    prompt = "Cmd: "  # Proponent always goes first
    current_player = None
    opponent = None
    proponent = None
    game = None

    def do_new_game(self, arg):
        "Takes a file path to load argument into the game, and proponent and opponent bot values"
        file_path, proponent_bot, opponent_bot = (arg.split() + [False, False])[:3]
        try:
            self.game = Game.from_file(file_path)
        except FileNotFoundError as e:
            print(e)  # Reset all values to none on failure
            self.current_player = None
            self.opponent = None
            self.proponent = None
            self.game = None
        else:
            positives = ["True", "true", "yes", "Yes", "y", "Y"]
            self.proponent = Proponent(self.game)
            self.proponent.is_bot = proponent_bot in positives
            self.opponent = Opponent(self.game)
            self.opponent.is_bot = opponent_bot in positives
            self.current_player = self.proponent
            self.prompt = "Proponent: "

    def do_has_to_be(self, argument):
        "When it is the Proponents turn, allows player to put forward an argument"
        if self.current_player is not self.proponent:
            return False
        try:
            self.proponent.has_to_be(argument)
        except Exception as e:
            print(e)
        else:
            print("It has to be ", argument)
            self._toggle_player()

    def do_could_be(self, argument):
        "When it is the Opponents turn, allows player to put forward an argument"
        if self.current_player is not self.opponent:
            return False
        try:
            self.opponent.could_be(argument)
        except Exception as e:
            print(e)
        else:
            print("It could be ", argument)
            self._toggle_player()

    def do_concede(self, arg):
        "When it is the Opponents turn, allows player to concede an argument"
        if self.current_player is not self.opponent:
            return False
        try:
            self.opponent.concede(self.game.last_argument)
        except Exception as e:
            print(e)
        else:
            print("I concede ", self.game.last_argument)
            self._toggle_player()

    def do_retract(self, arg):
        "When it is the Opponents turn, allows player to retract an argument"
        if self.current_player is not self.opponent:
            return False
        try:
            self.opponent.retract(self.game.last_argument)
        except Exception as e:
            print(e)
        else:
            print("I retract ", self.game.last_argument)
            self._toggle_player()

    def postcmd(self, stop, line):
        if stop:
            return stop
        while self.current_player and self.current_player.is_bot:
            move = self.current_player.next_move()  # Hows this to work when both bots?
            print("Computer {0}played {1}".format(self.prompt, move.name))
            self._toggle_player()
            print(self.prompt, " goes next")

    # def completedefault(self, text, line, begidx, engidx):  # use this to suggest next move

    def do_quit(self, _):
        return True  # True from any do_ method will tell the game to quit.

    do_exit = do_quit
    do_stop = do_quit
    do_close = do_quit

    def _toggle_player(self):
        if self.current_player is self.proponent:
            self.current_player = self.opponent
            self.prompt = "Opponent: "
        else:
            self.current_player = self.proponent
            self.prompt = "Proponent: "

if __name__ == "__main__":
    GameShell().cmdloop()
