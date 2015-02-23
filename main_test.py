from main import *
import unittest

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    expected_game = Game(set([self.argument]))

    self.assertEqual(self.game.arguments, expected_game.arguments)

  def test_could_be(self):
    second_argument = Argument()
    expected_game = Game(set([self.argument, second_argument]),
                         list([(second_argument, self.argument)]))
    new_game = self.opponent.could_be(second_argument, self.game)

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_concede(self):
    second_argument = Argument()
    third_argument = Argument()
    game_state = Game(set([self.argument, second_argument, third_argument]),
                      list([(second_argument, self.argument),
                            (third_argument, second_argument)]))
    new_game = self.opponent.concede(game_state, self.game)

  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
    self.game = self.proponent.has_to_be(self.argument, Game())
