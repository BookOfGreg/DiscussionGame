from main import *
import unittest

class Rules(unittest.TestCase):
  def test_concede_happens_when_there_are_no_attackers(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
    self.game = self.proponent.has_to_be(self.argument, Game())
    self.assertTrue(self.opponent.concede(self.argument, Game()))

  def test_concede_happens_when_all_attackers_are_retracted(self):
    pass

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    expected_game = Game(set([self.argument]))

    self.assertEqual(self.game.arguments, expected_game.arguments)

  def test_could_be(self):
    second_argument = Argument()
    new_game = self.opponent.could_be(second_argument, self.game)

    expected_game = Game(set([self.argument, second_argument]),
                         list([(second_argument, self.argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_concede(self):
    second_argument = Argument()
    third_argument = Argument()
    game_state = self.opponent.could_be(second_argument, self.game)
    game_state = self.proponent.has_to_be(third_argument, game_state)
    new_game = self.opponent.concede(third_argument, game_state)

    expected_game = Game(set([self.argument, second_argument]),
                         list([(second_argument, self.argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_retract(self):
    second_argument = Argument()
    third_argument = Argument()
    game_state = self.opponent.could_be(second_argument, self.game)
    game_state = self.proponent.has_to_be(third_argument, game_state)
    new_game = self.opponent.concede(third_argument, game_state)
    new_game = self.opponent.retract(second_argument, game_state)

    expected_game = Game(set([self.argument]),
                         list())

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
    self.game = self.proponent.has_to_be(self.argument, Game())
