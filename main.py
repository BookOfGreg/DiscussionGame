import time
import cmd
import sys
from game import Game
from player import Proponent, Opponent, GameOverError  # For later.


class GameShell(cmd.Cmd):
    intro = """This is the grounded persuasion game. Commands:
    'new_game [file_path] [bot proponent] [bot opponent] [claim]' - to start a game
            -bot options are true/yes/y for bot. Other or blank for human player.
            -claim is the label of the argument you want to be main claim if the
            proponent is a bot. This can be blank for random.
    'quit', 'close', 'exit', 'stop' - to leave
In game commands. You can also use new_game and quit anytime.
    'has_to_be [arg]' - as proponent.
    'could_be [arg]' - as opponent.
    'retract [arg]' - as opponent.
    'concede [arg]' - as opponent."""
    prompt = "Cmd: "  # Proponent always goes first
    current_player = None
    opponent = None
    proponent = None
    game = None

    def do_new_game(self, arg):
        "Takes a file path to load argument into the game, and proponent and opponent bot values"
        file_path, proponent_bot, opponent_bot, claim = (arg.split() + [False, False, None])[:4]
        try:
            print("Before load graph", time.process_time())
            self.game = Game.from_file(file_path)
            print("After load graph", time.process_time())
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
            if claim:
                print("Proponent: has_to_be ", claim)
                self.proponent.has_to_be(claim)
                self._toggle_player()
            else:
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
            try:
                action, move = self.current_player.next_move()  # Hows this to work when both bots?
                print("Bot {0}{1} {2}".format(self.prompt, action, move.name))
                if action in ("could_be", "has_to_be"):
                    self._toggle_player()
            except GameOverError as e:
                print(e)
                return True
        print("Arguments that attack {0} are {1}",
              self.game.last_argument,
              self.game.last_argument.minus())

    # def completedefault(self, text, line, begidx, engidx):  # use this to suggest next move?

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
    if len(sys.argv) == 3:
        gs = GameShell()
        line = "new_game {0} y y {1}".format(sys.argv[1], sys.argv[2])
        gs.onecmd(line)
        gs.postcmd(False, line)
    else:
        GameShell().cmdloop()
    print("After run", time.process_time())
