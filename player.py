from argument import Argument


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument_name):
        argument = Argument.find(argument_name)
        return self.game.add(argument)

    def next_move(self):
        "Bot plays the move"
        proposed_move = Bot(self.game).next_move()
        if proposed_move in self.game.arguments:
            raise GameOverError("Can't rule out your argument {0}".format(self.game.last_argument))
        self.has_to_be(proposed_move.name)  # Has to be name of bots next move.
        return "has_to_be", proposed_move


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
        action = None
        proposed_move = Bot(self.game).next_move()
        if proposed_move == self.game.last_argument:
            if proposed_move.label == "Out":
                action = "retract"
                self.retract(proposed_move.name)
            else:
                action = "concede"
                self.concede(proposed_move.name)
                if proposed_move is self.game.main_claim:
                    raise GameOverError("Main claim conceded")
        else:
            action = "could_be"
            self.could_be(proposed_move.name)
        return action, proposed_move


class Bot:

    """Suggests moves for both Proponent and Opponent.
    Prop and Opp still have responsibility to GameOver and pick verb for move"""

    def __init__(self, game):
        self.game = game

    def next_move(self):
        if not self.game.last_argument:
            return Argument.get_random()  # Proponents first move
        if self.game.retractable_args:
            return self.game.retractable_args.pop()
        args = self.game.last_argument.minus()
        args = [a for a in args if a not in self.game.complete_arguments]
        if not args:
            return self.game.last_argument
        args.sort(key=lambda arg: arg.step if arg.step else 1000,
                  reverse=True)
        return args[0]


class GameOverError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
