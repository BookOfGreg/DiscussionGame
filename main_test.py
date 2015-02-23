from main import *
import unittest

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    game = Game(OrderedSet(),OrderedSet())
    expected_game = Game(OrderedSet([self.argument]), OrderedSet())

    self.assertEqual(self.proponent.has_to_be(self.argument, game).arguments, expected_game.arguments )

  def test_could_be(self):
    counter_argument = Argument()

    game = Game(OrderedSet([self.argument]), OrderedSet())
    expected_game = Game(OrderedSet([self.argument, counter_argument]), OrderedSet([(counter_argument, self.argument)]) )

    new_game = self.opponent.could_be(self.argument, game)
    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)


  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
