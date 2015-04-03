from argument import Argument
import random


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.add(argument)

    def next_move(self):
        "Bot plays the move"

        if not self.game.last_argument:
            return "has_to_be", Argument.get_random()  # Proponents first move
        args = self.game.last_argument.minus()
        args = [a for a in args if (a not in self.game.complete_arguments and
                                    a not in self.game.arguments and
                                    a.label == "In")]
        if not args:
            raise GameOverError("Can't rule out your argument {0}".format(self.game.last_argument))
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        return "has_to_be", args[0]


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

    def next_move(self):
        "Bot plays the move"

        if self.game.retractable_args:
            return "retract", random.sample(self.game.retractable_args, 1)[0]
        args = self.game.last_argument.minus()
        args = [a for a in args if a not in self.game.complete_arguments]
        if not args:
            if self.game.last_argument is self.game.main_claim:
                raise GameOverError("Main claim conceded")
            return "concede", self.game.last_argument
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        return "could_be", args[0]


class GameOverError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
