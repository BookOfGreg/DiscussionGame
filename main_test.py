from main import *
import unittest

class TestRules(unittest.TestCase):
  def test_concede_happens_when_there_are_no_attackers(self):
    self.game = self.proponent.has_to_be(self.first_argument, Game())
    self.assertTrue(self.opponent.concede(self.first_argument, self.game))
    self.assertEqual(self.first_argument.label, "In")

  def test_concede_happens_when_all_attackers_are_retracted(self):
    self.assertTrue(self.opponent.concede(self.third_argument, self.game))
    self.assertTrue(self.opponent.retract(self.second_argument, self.game))
    self.assertTrue(self.opponent.concede(self.first_argument, self.game))

  def test_cannot_concede_when_any_attacker_is_undecided(self):
    with self.assertRaises(InvalidMoveError):
      self.opponent.concede(self.second_argument, self.game)

  def test_retract_when_attacker_conceded(self):
    self.game = self.opponent.concede(self.third_argument, self.game)
    self.assertTrue(self.opponent.retract(self.second_argument, self.game))

  def test_cannot_retract_when_no_attackers_conceded(self):

    with self.assertRaises(InvalidMoveError):
      self.opponent.retract(self.second_argument, self.game)

  def test_could_be_attacks_last_has_to_be(self):
    self.assertTrue(self.opponent.could_be(Argument(), self.game))
    # As long as the could_be signature does not change, there is no way to
    # attack anyone other than the last argument.

  def test_could_be_attacks_last_has_to_be(self):
    self.assertTrue(self.proponent.has_to_be(Argument(), self.game))
    # As long as the has_to_be signature does not change, there is no way to
    # attack anyone other than the last argument.

  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.first_argument = Argument()
    self.second_argument = Argument()
    self.third_argument = Argument()
    self.game = self.proponent.has_to_be(self.first_argument, Game())
    self.game = self.opponent.could_be(self.second_argument, self.game)
    self.game = self.proponent.has_to_be(self.third_argument, self.game)


class TestArgument(unittest.TestCase):
  def test_argument_starts_undecided(self):
    argument = Argument()
    self.assertEqual(argument.label, "Undec")

  def test_arguments_can_be_in_or_out(self):
    argument = Argument("In")
    self.assertEqual(argument.label, "In")
    argument = Argument("Out")
    self.assertEqual(argument.label, "Out")

class TestMoves(unittest.TestCase):
  def test_has_to_be(self):
    expected_game = Game(set([self.argument]))

    self.assertEqual(self.game.arguments, expected_game.arguments)

  def test_could_be(self):
    new_game = self.opponent.could_be(self.second_argument, self.game)

    expected_game = Game(set([self.argument, self.second_argument]),
                         list([(self.second_argument, self.argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_concede(self):
    game_state = self.opponent.could_be(self.second_argument, self.game)
    game_state = self.proponent.has_to_be(self.third_argument, game_state)
    new_game = self.opponent.concede(self.third_argument, game_state)

    expected_game = Game(set([self.argument, self.second_argument]),
                         list([(self.second_argument, self.argument)]))

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def test_retract(self):
    game_state = self.opponent.could_be(self.second_argument, self.game)
    game_state = self.proponent.has_to_be(self.third_argument, game_state)
    new_game = self.opponent.concede(self.third_argument, game_state)
    new_game = self.opponent.retract(self.second_argument, game_state)

    expected_game = Game(set([self.argument]),
                         list())

    self.assertEqual(new_game.arguments, expected_game.arguments)
    self.assertEqual(new_game.attack_relations, expected_game.attack_relations)

  def setUp(self):
    self.proponent = Proponent()
    self.opponent = Opponent()
    self.argument = Argument()
    self.second_argument = Argument()
    self.third_argument = Argument()
    self.game = self.proponent.has_to_be(self.argument, Game())
