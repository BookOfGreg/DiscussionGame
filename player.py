from argument import Argument
import random


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.has_to_be(argument)

    def next_move(self):
        "Bot plays the move"

        if not self.game.last_argument:
            proposed_arg = Argument.get_random()
            return "has_to_be", proposed_arg  # Proponents first move
        possible_args = self.game.last_argument.minus()
        args = [a for a in possible_args if (a not in self.game.complete_arguments and
                                             a not in self.game.arguments and
                                             a.label == "In")]
        if not args:
            args = [a for a in possible_args if (a not in self.game.complete_arguments and
                                                 a not in self.game.arguments)]
        if not args:  # I hate python
            return None, None
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        proposed_arg = args[0]
        return "has_to_be", proposed_arg


class Opponent:

    def __init__(self, game):
        self.game = game

    def could_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.could_be(argument)

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
            return "retract", proposed_arg
        args = self.game.last_argument.minus()
        args = [a for a in args if a not in self.game.complete_arguments]
        if not args:
            proposed_arg = self.game.last_argument
            return "concede", proposed_arg
        args.sort(key=lambda arg: arg.step if arg.step else 1000)
        proposed_arg = args[0]
        return "could_be", proposed_arg
