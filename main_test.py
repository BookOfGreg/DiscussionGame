from main import *
import unittest

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    expected_game = Game(set([self.argument]), list())

    self.assertEqual(self.step_game.arguments, expected_game.arguments )

  def test_could_be(self):
    counter_argument = Argument()

    expected_game = Game(set([self.argument, counter_argument]), list([(counter_argument, self.argument)]) )
    new_game = self.opponent.could_be(counter_argument, self.step_game)

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def setUp(self):
    self.game = Game(set(),list())
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
    self.step_game = self.proponent.has_to_be(self.argument, self.game)
