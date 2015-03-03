import sqlite3
import os

try:
  os.remove("./db.sqlite3")
except OSError:
  pass
# c.execute("INSERT INTO arguments (name, label) VALUES(?, ?)", name, label)
DB_PATH="./db.sqlite3"

def create_db():
  global conn
  global cursor
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("CREATE TABLE arguments(id INTEGER PRIMARY KEY, name text, label text);")
  cursor.execute("""CREATE TABLE attacks(id INTEGER PRIMARY KEY, attacker_id INTEGER, target_id INTEGER,
    FOREIGN KEY(attacker_id) REFERENCES arguments(id),
    FOREIGN KEY(target_id) REFERENCES arguments(id),
    UNIQUE(attacker_id, target_id) ON CONFLICT IGNORE);""")
  return conn

def delete_db():
  global conn
  try:
    conn.close()
    os.remove(DB_PATH)
  except OSError:
    pass

def reset_db():
  global conn
  global cursor
  delete_db()
  conn = create_db()
  cursor = conn.cursor()

create_db()

class Proponent:
  def __init__(self, game):
    self.game = game

  def has_to_be(self, argument):
    if self.is_valid_move(argument):
      return self.game.add(argument)
    raise InvalidMoveError("My Argument is BullShit (technical definition)")

  def is_valid_move(self, argument):
    if self.game.last_argument is None: return True
    return self.game.is_valid(argument)

class Opponent:
  def __init__(self, game):
    self.game = game

  def could_be(self, argument):
    if self.is_valid_move(argument):
      return self.game.add(argument)
    raise InvalidMoveError("My Argument is BullShit (technical definition)")

  def concede(self, argument):
    return self.game.concede(argument)

  def retract(self, argument):
    return self.game.retract(argument)

  def is_valid_move(self, argument):
    return self.game.is_valid(argument)

class Argument:
  def __init__(self, label, name):
    self.label = label
    self.name = name

class ArgumentFramework:
  def __init__(self, arguments, attack_relations):
    if arguments is None: arguments = set()
    if attack_relations is None: attack_relations = list()

    self.arguments = arguments
    self.attack_relations = attack_relations

class DBArgumentFramework:
  def __init__(self, cursor):
    self.cursor = cursor

  def attack_relations(self):
    return self.cursor.execute("SELECT * FROM attacks").fetchall()

class Game:
  def __init__(self, knowledge_base, arguments=None, attack_relations=None, complete_arguments=None, complete_attack_relations=None):
    if arguments is None: arguments = set()
    if complete_arguments is None: complete_arguments = set()
    if attack_relations is None: attack_relations = list()
    if complete_attack_relations is None: complete_attack_relations = list()

    self.knowledge_base = knowledge_base
    self.arguments = arguments
    self.complete_arguments = complete_arguments
    self.attack_relations = attack_relations
    self.complete_attack_relations = complete_attack_relations
    self.last_argument = None

  @classmethod
  def from_file(self, path):
    reset_db()
    file = open(path, "r")
    argument_line = file.readline()
    for arg in argument_line.strip().split(" "):
      cursor.execute("INSERT INTO arguments (name, label) VALUES(?, 'Undec')", arg)
    for line in file:
      attacker, target = line.strip().split(" ")
      cursor.execute("""INSERT INTO attacks (attacker_id, target_id)
        WITH attacker AS (SELECT id FROM arguments WHERE name=?),
        target AS (SELECT id FROM arguments WHERE name=?)
        SELECT * from attacker, target""", (attacker, target))
    file.close()
    conn.commit()
    return Game(DBArgumentFramework(cursor))

  def add(self, argument):
    if self.last_argument is not None: self.attack_relations.append((argument, self.last_argument))
    self.arguments.add(argument)
    self.last_argument = argument
    return self

  def concede(self, argument):
    for attacker, target in self.attack_relations:
      if target is argument:
        raise InvalidMoveError("An attacker of this argument is not out.")
    return self.remove(argument)

  def retract(self, argument):
    for attacker, target in self.complete_attack_relations:
      if target is argument:
        if attacker.label == "In":
          return self.remove(argument)
    raise InvalidMoveError("There is no attacker of this argument that is in.")

  def remove(self, argument):
    self.arguments = self.arguments.difference({argument})
    self.complete_arguments.add(argument)
    if len(self.attack_relations) > 0:
      last_attack_relation = self.attack_relations.pop(-1)
      self.complete_attack_relations.append(last_attack_relation)
      self.last_argument = last_attack_relation[-1]
    return self

  def is_valid(self, attacker):
    return (attacker, self.last_argument) in self.knowledge_base.attack_relations

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
