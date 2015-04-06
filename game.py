from argument import Argument
from labelling import Labelling
from player import Proponent, Opponent
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
        self.retractable_args = list()
        self.proponent = Proponent(self)
        self.opponent = Opponent(self)
        self.current_player = self.proponent

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

    def _add(self, argument):
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
        self._toggle_player()
        return self

    could_be = _add
    has_to_be = _add

    def concede(self, argument):
        if self.retractable_args:
            raise InvalidMoveError(
                "Must retract arguments if available. {0}".format(self.retractable_args))
        for attacker, target in self.attack_relations:
            if target == argument:  # Allows person to concede early.
                raise InvalidMoveError(
                    "An attacker of this argument is not out.")
        self.retractable_args = list(set(argument.plus()).intersection(self.arguments)
                                                         .difference(set(self.complete_arguments)))
        self.arguments = self.arguments.difference({argument})
        self.complete_arguments.add(argument)

        for arg in argument.plus():
            attack_relation = (argument, arg)
            self.complete_attack_relations.append(attack_relation)
            if attack_relation in self.attack_relations:
                self.attack_relations.remove(attack_relation)
        self.last_argument = argument

    def retract(self, argument):
        for attacker, target in self.complete_attack_relations:
            if target == argument:
                self.retractable_args.remove(argument)

                self.arguments = self.arguments.difference({argument})
                self.complete_arguments.add(argument)

                for arg in argument.plus():
                    attack_relation = (argument, arg)
                    self.complete_attack_relations.append(attack_relation)
                    if attack_relation in self.attack_relations:
                        self.attack_relations.remove(attack_relation)
                self.last_argument = next(iter(argument.plus().intersection(self.arguments)))
                return

        raise InvalidMoveError(
            "There is no attacker of this argument that is in.")

    def is_game_over(self):
        if self.main_claim in self.complete_arguments:
            return True
        if (self.last_argument and len(self.last_argument.minus()) == 0
                and self.current_player == self.proponent):
            return True
        return False

    def game_over_reason(self):
        if not self.is_game_over():
            return "Game is not over yet"
        if self.main_claim in self.complete_arguments:
            return "Main claim has been condeded, Proponent wins the argument"
        if (self.last_argument and len(self.last_argument.minus()) == 0
                and self.current_player == self.proponent):
            return "There is no counter to the last argument, Opponent wins the argument"

    def _toggle_player(self):
        if self.current_player == self.proponent:
            self.current_player = self.opponent
        else:
            self.current_player = self.proponent

    def _can_argue_with(self, argument):
        if self.last_argument is None:  # First move
            return True
        if argument in self.complete_arguments:
            return False
        return self.last_argument in argument.plus()


class InvalidMoveError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
