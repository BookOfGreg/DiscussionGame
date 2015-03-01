from main import *
import unittest

class TestKnowledgeBaseLoaders(unittest.TestCase):
  def test_abstract_loader(self):
    first_argument = Argument("Out")
    second_argument = Argument("In")
    # example_kb = ArgumentFramework(set([first_argument, second_argument]),
    #                              list([(second_argument, first_argument)]))
    kb = ArgumentFramework.from_file("./example_kb_1.txt")
    self.assertEqual(len(kb.attack_relations), 1)
    kb = ArgumentFramework.from_file("./example_kb_2.txt")
    self.assertEqual(len(kb.attack_relations), 3)
    # There exists an argument that has 2 attackers assertion.

class TestPlayers(unittest.TestCase):
  def test_players_know_validity_of_move(self): # Could improve
    first_argument = Argument("Out")
    second_argument = Argument("In")
    knowledge = ArgumentFramework(set([first_argument, second_argument]),
                                 list([(second_argument, first_argument)]))
    game = Game(knowledge)
    proponent = Proponent(game)
    opponent = Opponent(game)
    proponent.has_to_be(first_argument)
    self.assertTrue(opponent.is_valid_move(second_argument))

class TestRules(unittest.TestCase):
  def test_concede_happens_when_there_are_no_attackers(self):
    self.assertTrue(self.opponent.concede(self.third_argument))
    self.assertEqual(self.third_argument.label, "In")

  def test_concede_happens_when_all_attackers_are_retracted(self):
    self.assertTrue(self.opponent.concede(self.third_argument))
    self.assertTrue(self.opponent.retract(self.second_argument))
    self.assertTrue(self.opponent.concede(self.first_argument))

  def test_cannot_concede_when_any_attacker_is_undecided(self):
    with self.assertRaises(InvalidMoveError):
      self.opponent.concede(self.second_argument)

  def test_retract_when_attacker_conceded(self):
    self.opponent.concede(self.third_argument)
    self.assertTrue(self.opponent.retract(self.second_argument))

  def test_cannot_retract_when_no_attackers_conceded(self):

    with self.assertRaises(InvalidMoveError):
      self.opponent.retract(self.second_argument)

  def test_could_be_attacks_last_has_to_be(self):
    self.opponent.could_be(self.fourth_argument)
    self.assertEqual(self.game.attack_relations[-1][-1], self.third_argument)

  def test_has_to_be_attacks_last_could_be(self):
    self.opponent.could_be(self.fourth_argument)
    self.proponent.has_to_be(self.fifth_argument)
    self.assertEqual(self.game.attack_relations[-1][-1], self.fourth_argument)

  def setUp(self):
    self.first_argument = Argument("In")
    self.second_argument = Argument("Out")
    self.third_argument = Argument("In")
    self.fourth_argument = Argument("Out")
    self.fifth_argument = Argument("In")
    argument_framework = ArgumentFramework(set([self.first_argument,
                                                self.second_argument,
                                                self.third_argument,
                                                self.fourth_argument,
                                                self.fifth_argument]),
                                           list([(self.second_argument, self.first_argument),
                                                 (self.third_argument, self.second_argument),
                                                 (self.fourth_argument, self.third_argument),
                                                 (self.fifth_argument, self.fourth_argument)]))
    self.game = Game(argument_framework)
    self.proponent = Proponent(self.game)
    self.opponent = Opponent(self.game)
    self.proponent.has_to_be(self.first_argument)
    self.opponent.could_be(self.second_argument)
    self.proponent.has_to_be(self.third_argument)

class TestArgument(unittest.TestCase):
  def test_argument_starts_with_label(self):
    self.assertTrue(Argument("In"))
    self.assertTrue(Argument("Out"))

  def test_arguments_can_be_in_or_out(self):
    argument = Argument("In")
    self.assertEqual(argument.label, "In")
    argument = Argument("Out")
    self.assertEqual(argument.label, "Out")

class TestMoves(unittest.TestCase):
  def test_has_to_be(self):
    expected_game = Game(self.argument_framework,
                         arguments=set([self.first_argument]))

    self.assertEqual(self.game.arguments, expected_game.arguments)

  def test_could_be(self):
    new_game = self.opponent.could_be(self.second_argument)

    expected_game = Game(self.argument_framework,
                         arguments=set([self.first_argument, self.second_argument]),
                         attack_relations=list([(self.second_argument, self.first_argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_concede(self):
    self.opponent.could_be(self.second_argument)
    self.proponent.has_to_be(self.third_argument)
    new_game = self.opponent.concede(self.third_argument)

    expected_game = Game(self.argument_framework,
                         arguments=set([self.first_argument, self.second_argument]),
                         attack_relations=list([(self.second_argument, self.first_argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_retract(self):
    self.opponent.could_be(self.second_argument)
    self.proponent.has_to_be(self.third_argument)
    self.opponent.concede(self.third_argument)
    new_game = self.opponent.retract(self.second_argument)

    expected_game = Game(self.argument_framework,
                         arguments=set([self.first_argument]),
                         attack_relations=list())

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def setUp(self):
    self.first_argument = Argument("In")
    self.second_argument = Argument("Out")
    self.third_argument = Argument("In")
    self.argument_framework = ArgumentFramework(set([self.first_argument,
                                                self.second_argument,
                                                self.third_argument]),
                                           list([(self.second_argument, self.first_argument),
                                                 (self.third_argument, self.second_argument)]))
    self.game = Game(self.argument_framework)
    self.proponent = Proponent(self.game)
    self.opponent = Opponent(self.game)
    self.proponent.has_to_be(self.first_argument)
