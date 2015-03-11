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
        self.has_to_be(proposed_move.name)  # Has to be name of bots next move.
        return proposed_move


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
        proposed_move = Bot(self.game).next_move()
        if proposed_move == self.game.last_argument:
            if proposed_move.label == "Out":
                self.retract(proposed_move.name)
            else:
                self.concede(proposed_move.name)
        else:
            self.could_be(proposed_move.name)
        return proposed_move


class Bot:

    def __init__(self, game):
        self.game = game

    def next_move(self):
        if not self.game.last_argument:
            return Argument.get_random()  # Proponents first move
        args = self.game.last_argument.minus()
        if not args:
            return self.game.last_argument
        # args = list(args)
        args = [a for a in args if a not in self.game.complete_arguments]
        args.sort(key=lambda arg: arg.step if arg.step else 1000,
                  reverse=True)
        return args[0]
