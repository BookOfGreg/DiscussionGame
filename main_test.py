from main import *
import unittest

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    game = Game(set(),set())
    expected_game = Game(set([self.argument]), set())

    self.assertEqual(self.proponent.has_to_be(self.argument, game).arguments, expected_game.arguments )

  def test_could_be(self):
    counter_argument = Argument()

    game = Game(set([self.argument]), set())
    expected_game = Game(set([self.argument, counter_argument]), set([(counter_argument, self.argument)]) )

    self.assertEqual(self.opponent.could_be(self.argument, game).arguments, expected_game.arguments)
    self.assertEqual(self.opponent.could_be(self.argument, game).attack_relations, expected_game.attack_relations)


  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()

  # def test_has_to_be(self):
    # self.assertTrue(self.proponent.has_to_be(self.argument))
