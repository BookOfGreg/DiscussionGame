class Proponent:
  def has_to_be(self, argument, game):
    return game.add(argument)

class Opponent:
  def could_be(self, argument, game):
    return game.add(argument)

  def concede(self, argument, game):
    return False

#   def retract(self, argument, game):
#     return False

class Argument:
  pass
  # label = "string"
  # attackers = set(arguments...)

class Game:
  def __init__(self, arguments=None, attack_relations=None):
    if arguments is None: arguments = set()
    if attack_relations is None: attack_relations = list()

    self.attack_relations = attack_relations
    self.arguments = arguments
    self.last_argument = None

  def add(self, argument):
    if self.last_argument is not None: self.attack_relations.append((argument, self.last_argument))
    self.arguments.add(argument)
    self.last_argument = argument
    return self

if __name__ == "__main__": main()
