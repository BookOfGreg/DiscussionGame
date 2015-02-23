class Proponent:
  def has_to_be(self, argument, game):
    return game.add(argument)

class Opponent:
  def could_be(self, argument, game):
    return game.add(argument, (argument, game.last_argument))

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
    self.last_argument = None

  def add(self, argument, attack_relation=None):
    if attack_relation != None: self.attack_relations.append(attack_relation)
    self.arguments.add(argument)
    self.last_argument = argument
    return self

if __name__ == "__main__": main()
