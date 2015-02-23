class Proponent:
  def has_to_be(self, argument, game):
    return game.add(argument)

class Opponent:
  def could_be(self, argument, game):
    return game

#   def concede(self, argument, game):
#     return False

#   def retract(self, argument, game):
#     return False

class Argument:
  pass
  # label = "string"
  # attackers = set(arguments...)

class Game:
  def __init__(self, arguments, attack_relations):
    self.arguments = arguments
    self.attack_relations = attack_relations

  def add(self, argument):
    self.arguments.add(argument)
    return self

if __name__ == "__main__": main()
