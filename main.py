from argument import Argument
import cmd


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.add(argument)


class Opponent:

    def __init__(self, game):
        self.game = game

    def could_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.add(argument)

    def concede(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.concede(argument)

    def retract(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.retract(argument)


class Bot:

    def __init__(self, game):
        self.game = game

    def next_move(self):
        args = self.game.last_argument.minus()
        if not args:
            return self.game.last_argument
        args = list(args)
        args.sort(key=lambda arg: arg.step if arg.step else 1000,
                  reverse=True)
        return args[0]


class GameShell(cmd.Cmd):
    intro = "This text is displayed on loading"
    prompt = "proponent: "

    def do_has_to_be(self, arg):
        Proponent.has_to_be(arg)

    def do_quit(self, line):
        return True  # True from any do_ method will tell the game to quit.

    do_exit = do_quit
    do_stop = do_quit
    do_close = do_quit

if __name__ == "__main__":
    GameShell().cmdloop()
