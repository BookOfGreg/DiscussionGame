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
            proposed_arg = Argument.get_random()
            self.has_to_be(proposed_arg)
            return "has_to_be", proposed_arg  # Proponents first move
        args = self.game.last_argument.minus()
        args = [a for a in args if (a not in self.game.complete_arguments and
                                    a not in self.game.arguments and
                                    a.label == "In")]
        if not args:
            raise GameOverError("Can't rule out your argument {0}".format(self.game.last_argument))
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        proposed_arg = args[0]
        self.has_to_be(proposed_arg.name)
        return "has_to_be", proposed_arg


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
            proposed_arg = random.sample(self.game.retractable_args, 1)[0]
            self.retract(proposed_arg.name)
            return "retract", proposed_arg
        args = self.game.last_argument.minus()
        args = [a for a in args if a not in self.game.complete_arguments]
        if not args:
            if self.game.last_argument is self.game.main_claim:
                raise GameOverError("Main claim conceded")
            proposed_arg = self.game.last_argument
            self.concede(proposed_arg.name)
            return "concede", proposed_arg
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        proposed_arg = args[0]
        self.could_be(proposed_arg.name)
        return "could_be", proposed_arg


class GameOverError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
