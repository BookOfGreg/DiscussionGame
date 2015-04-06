# import pdb; pdb.set_trace()
import time
import cmd
import sys
import traceback
import operator
from game import Game


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
    prompt = "Cmd: "

    def do_new_game(self, arg):
        "Takes a file path to load argument into the game, and proponent and opponent bot values"
        file_path, proponent_bot, opponent_bot, claim = (arg.split() + [False, False, None])[:4]
        try:
            print("Before load graph", time.process_time())
            self.game = Game.from_file(file_path)
            print("After load graph", time.process_time())
        except FileNotFoundError as e:
            print(e)  # Reset all values to none on failure
            self.game = None
        else:
            positives = ["True", "true", "yes", "Yes", "y", "Y"]
            self.game.proponent.is_bot = proponent_bot in positives
            self.game.opponent.is_bot = opponent_bot in positives
            if claim:
                print("Proponent: has_to_be ", claim)
                self.game.proponent.has_to_be(claim)

    def do_has_to_be(self, argument):
        "When it is the Proponents turn, allows player to put forward an argument"
        if self.game.current_player is not self.game.proponent:
            return False
        try:
            self.game.proponent.has_to_be(argument)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        else:
            print("It has to be ", argument)

    def do_could_be(self, argument):
        "When it is the Opponents turn, allows player to put forward an argument"
        if self.game.current_player is not self.game.opponent:
            return False
        try:
            self.game.opponent.could_be(argument)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        else:
            print("It could be ", argument)

    def do_concede(self, arg):
        "When it is the Opponents turn, allows player to concede an argument"
        if self.game.current_player is not self.game.opponent:
            return False
        conceding_arg = self.game.last_argument.name
        try:
            self.game.opponent.concede(conceding_arg)
        except Exception:  # THIS COULD BE GAMEOVER CATCHING??
            traceback.print_exc(file=sys.stdout)
        else:
            print("I concede ", conceding_arg)

    def do_retract(self, arg):
        "When it is the Opponents turn, allows player to retract an argument"
        if self.game.current_player is not self.game.opponent:
            return False
        retracting_arg = self.game.last_argument.name
        try:
            self.game.opponent.retract(retracting_arg)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        else:
            print("I retract ", retracting_arg)

    def do_current_state(self, arg):
        print("Last Arg: {0}".format(self.game.last_argument))
        print("In Progress Args: {0}".format(self.game.arguments))
        print("Retractable Args: {0}".format(self.game.retractable_args))
        print("Completed Args: {0}".format(self.game.complete_arguments))
        print("Main Claim: {0}".format(self.game.main_claim))

    def postcmd(self, stop, line):
        if stop:
            return stop
        self._set_prompt()
        if not self.game:
            return False
        if self.game.is_game_over():
            print("Game is over, but you can continue the argument.")
            print(self.game.game_over_reason())
        while self.game.current_player and self.game.current_player.is_bot:
            action, move = self.game.current_player.next_move()
            operator.methodcaller(action, move.name)(self.game.current_player)
            print("Bot {0}{1} {2}".format(self.prompt, action, move.name))
            if self.game.is_game_over():
                print("Game is over, bot has finished its argument.")
                print(self.game.game_over_reason())
                return True
            self._set_prompt()
        self._inform_possible_arguments()

    def _inform_possible_arguments(self):
        if self.game.retractable_args:
            print("Arguments must be retracted: {0}".format(self.game.retractable_args))
            return
        if self.game.last_argument:
            print("Arguments that attack {0} are {1}".format(
                  self.game.last_argument,
                  self.game.last_argument.minus()))  # bug here when retracting

    def _set_prompt(self):
        if not self.game:
            self.prompt = "Cmd: "
            return
        if self.game.current_player == self.game.proponent:
            self.prompt = "Proponent: "
        else:
            self.prompt = "Opponent: "
    # def completedefault(self, text, line, begidx, engidx):  # use this to suggest next move?

    def do_quit(self, _):
        return True  # True from any do_ method will tell the game to quit.

    do_exit = do_quit
    do_stop = do_quit
    do_close = do_quit


if __name__ == "__main__":
    if len(sys.argv) == 3:
        gs = GameShell()
        line = "new_game {0} y y {1}".format(sys.argv[1], sys.argv[2])
        gs.onecmd(line)
        gs.postcmd(False, line)
    else:
        GameShell().cmdloop()
    print("After run", time.process_time())
