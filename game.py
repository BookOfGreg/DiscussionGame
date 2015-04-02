from argument import Argument
from labelling import Labelling
import time


class Game:

    """This should be used as a singleton due to it depending on Argument
    which has one instance of sqlite at any time."""

    def __init__(self, knowledge_base):
        self.arguments = set()
        self.complete_arguments = set()
        self.attack_relations = list()
        self.complete_attack_relations = list()
        self.kb = knowledge_base
        self.last_argument = None
        self.main_claim = None  # Holds the first argument.
        self.retractable_args = None

    @classmethod
    def from_file(self, path):
        kb = Argument.from_file(path)
        print("Loaded into DB, Labelling.", time.process_time())
        Labelling.grounded(kb)
        return Game(kb)

    @classmethod
    def from_af(cls, arguments, attack_relations):
        kb = Argument.from_af(arguments, attack_relations)
        Labelling.grounded(kb)
        return Game(kb)

    def add(self, argument):
        if not self._can_argue_with(argument):
            raise InvalidMoveError("Argument {0} does not attack last argument".format(argument))
        if self.retractable_args:
            raise InvalidMoveError(
                "Must retract arguments if available.")
        if self.last_argument is not None:
            self.attack_relations.append((argument, self.last_argument))
        else:
            self.main_claim = argument
        self.arguments.add(argument)
        self.last_argument = argument
        return self

    def concede(self, argument):
        if argument != self.last_argument:
            raise InvalidMoveError(
                "Cannot concede anything but the last argument.")
        if self.retractable_args:
            raise InvalidMoveError(
                "Must retract arguments if available. {0}".format(self.retractable_args))
        for attacker, target in self.attack_relations:
            if target == argument:  # Allows person to concede early.
                raise InvalidMoveError(
                    "An attacker of this argument is not out.")
        # import pdb; pdb.set_trace()
        self.retractable_args = argument.plus()  # Get from game.args instead
        return self._remove(argument)

    def retract(self, argument):
        for attacker, target in self.complete_attack_relations:
            if target == argument:
                self.retractable_args.remove(argument)
                return self._remove(argument)
        raise InvalidMoveError(
            "There is no attacker of this argument that is in.")

    def _can_argue_with(self, argument):
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
