class Proponent:
  def __init__(self, game, reasoning=None):
    # if reasoning is None: reasoning = # Default knowledge source or any argument allowed
    self.game = game
    self.reasoning = reasoning
    # load from a file or delegate to another class in knowledge/reasoning/validator.

  def has_to_be(self, argument):
    if self.is_valid_move(argument): #strict mode?
      return self.game.add(argument)
    raise InvalidMoveError("My Argument is BullShit (technical definition)")

  def possible_moves(self): # Extract to superclass
    return self.reasoning.find_moves(self.game.open_arguments())

  def is_valid_move(self, argument):
    if self.reasoning is None: return True
    if self.game.last_argument is None: return True
    return self.reasoning.is_valid((argument, self.game.last_argument))

class Opponent:
  def __init__(self, game, reasoning=None):
    self.game = game
    self.reasoning = reasoning

  def could_be(self, argument):
    if self.is_valid_move(argument): #strict mode?
      return self.game.add(argument)
    raise InvalidMoveError("My Argument is BullShit (technical definition)")

  def concede(self, argument):
    return self.game.concede(argument)

  def retract(self, argument):
    return self.game.retract(argument)

  def possible_moves(self):
    return self.reasoning.find_moves(self.game.open_arguments())

  def is_valid_move(self, argument):
    if self.reasoning is None: return True
    return self.reasoning.is_valid((argument, self.game.last_argument))

class Argument:
  def __init__(self, label=None):
    if label is None: label = "Undec"
    self.label = label

  def add_label(self, label):
    self.label = label

class ArgumentFramework:
  def __init__(self, arguments, attack_relations):
    if arguments is None: arguments = set()
    if attack_relations is None: attack_relations = list()

    self.arguments = arguments
    self.attack_relations = attack_relations

  def find_moves(self, arguments):
    possible_arguments = list()
    # This will be slow...
    for relation in self.attack_relations:
      if self._target(relation) in arguments and self._attacker(relation) not in arguments:
        possible_arguments.append(self._attacker(relation))
    return set(possible_arguments)

  def is_valid(self, attack_relation):
    return attack_relation in self.attack_relations

  def _attacker(self, relation):
    return relation[0]

  def _target(self, relation):
    return relation[1]

class Game:
  def __init__(self, arguments=None, attack_relations=None, labeled_arguments=None, complete_attack_relations=None):
    if arguments is None: arguments = set()
    if labeled_arguments is None: labeled_arguments = set()
    if attack_relations is None: attack_relations = list()
    if complete_attack_relations is None: complete_attack_relations = list()

    self.arguments = arguments
    self.labeled_arguments = labeled_arguments
    self.attack_relations = attack_relations
    self.complete_attack_relations = complete_attack_relations
    self.last_argument = None

  def add(self, argument):
    if self.last_argument is not None: self.attack_relations.append((argument, self.last_argument))
    self.arguments.add(argument)
    self.last_argument = argument
    return self

  def concede(self, argument):
    for relation in self.attack_relations:
      if self._target(relation) is argument:
        raise InvalidMoveError("An attacker of this argument is not out.")
    argument.add_label("In")
    return self.remove(argument)

  def retract(self, argument):
    for relation in self.complete_attack_relations:
      if self._target(relation) is argument:
        if self._attacker(relation).label == "In":
          argument.add_label("Out")
          return self.remove(argument)
    raise InvalidMoveError("There is no attacker of this argument that is in.")

  def remove(self, argument):
    self.arguments = self.arguments.difference({argument})
    self.labeled_arguments.add(argument)
    if len(self.attack_relations) > 0:
      last_attack_relation = self.attack_relations.pop(-1)
      self.complete_attack_relations.append(last_attack_relation)
      self.last_argument = last_attack_relation[-1]
    return self

  def _attacker(self, relation):
    return relation[0]

  def _target(self, relation):
    return relation[1]

  def open_arguments(self):
    return self.arguments

class InvalidMoveError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

def main():
  pass

if __name__ == "__main__": main()
