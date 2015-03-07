from argument import Argument
from labelling import Labelling


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument_name):
        argument = Argument.find(argument_name)
        if self.game.can_argue_with(argument):
            return self.game.add(argument)
        raise InvalidMoveError("My Argument is BullShit")


class Opponent:

    def __init__(self, game):
        self.game = game

    def could_be(self, argument_name):
        argument = Argument.find(argument_name)
        if self.game.can_argue_with(argument):
            return self.game.add(argument)
        raise InvalidMoveError("My argument does not attack the last argument")

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


class Game:

    """This should be used as a singleton due to it depending on Argument
    which has one instance of sqlite at any time."""

    def __init__(self, knowledge_base, arguments=None, attack_relations=None,
                 complete_arguments=None, complete_attack_relations=None):
        if arguments is None:
            arguments = set()
        if complete_arguments is None:
            complete_arguments = set()
        if attack_relations is None:
            attack_relations = list()
        if complete_attack_relations is None:
            complete_attack_relations = list()

        self.kb = knowledge_base
        self.arguments = arguments
        self.complete_arguments = complete_arguments
        self.attack_relations = attack_relations
        self.complete_attack_relations = complete_attack_relations
        self.last_argument = None

    @classmethod
    def from_file(self, path):
        kb = Argument.from_file(path)
        Argument.set_labels(Labelling.grounded(kb))
        return Game(kb)

    @classmethod
    def from_af(cls, arguments, attack_relations):
        kb = Argument.from_af(arguments, attack_relations)
        Argument.set_labels(Labelling.grounded(kb))
        return Game(kb)

    def add(self, argument):
        if self.last_argument is not None:
            self.attack_relations.append((argument, self.last_argument))
        self.arguments.add(argument)
        self.last_argument = argument
        return self

    def concede(self, argument):
        if argument != self.last_argument:
            raise InvalidMoveError(
                "Cannot concede anything but the last argument.")
        for attacker, target in self.attack_relations:
            if target == argument:  # Allows person to concede early.
                raise InvalidMoveError(
                    "An attacker of this argument is not out.")
        return self._remove(argument)

    def retract(self, argument):
        for attacker, target in self.complete_attack_relations:
            if target == argument:
                return self._remove(argument)
        raise InvalidMoveError(
            "There is no attacker of this argument that is in.")

    def can_argue_with(self, argument):
        if self.last_argument is None:  # First move
            return True
        if argument in self.complete_arguments:
            return False
        return self.last_argument in argument.plus()

    def _remove(self, argument):
        self.arguments = self.arguments.difference({argument})
        self.complete_arguments.add(argument)
        if len(self.attack_relations) > 0:
            last_attack_relation = self.attack_relations.pop(-1)
            self.complete_attack_relations.append(last_attack_relation)
            self.last_argument = last_attack_relation[-1]
        return self


class InvalidMoveError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def main():
    pass

if __name__ == "__main__":
    main()
