"""Author Greg Myers
Prototype implementation of Grounded Persuasion Game"""

from main import *
import unittest


def last(enumerable):
    return enumerable[-1]


def first(enumerable):
    return enumerable[0]

attacker = first
target = last


class TestKnowledgeBaseLoaders(unittest.TestCase):

    def test_abstract_loader(self):
        game = Game.from_file("./example_kb_2.txt")
        self.assertEqual(len(game.kb.get_arguments()), 4)
        # There exists an argument that has 2 attackers assertion.


class TestPlayers(unittest.TestCase):

    def test_players_know_validity_of_move(self):  # Could improve
        game = Game.from_af(set(["a", "b"]),
                            list([("b", "a")]))
        proponent = Proponent(game)
        opponent = Opponent(game)
        proponent.has_to_be("a")
        self.assertTrue(opponent.is_valid_move(Argument("b")))


class TestBot(unittest.TestCase):

    def test_bot_knows_which_argument_to_do_next(self):
        game = Game.from_af(set(["a", "b"]),
                            list([("b", "a")]))
        proponent = Proponent(game)
        proponent.has_to_be("a")
        bot = Bot(game)
        next_move = bot.next_move()
        self.assertEqual(next_move, Argument("b"))


class TestRules(unittest.TestCase):

    def test_concede_happens_when_there_are_no_attackers(self):
        self.assertTrue(self.opponent.concede("c"))

    def test_concede_happens_when_all_attackers_are_retracted(self):
        self.assertTrue(self.opponent.concede("c"))
        self.assertTrue(self.opponent.retract("b"))
        self.assertTrue(self.opponent.concede("a"))

    def test_cannot_concede_when_any_attacker_is_undecided(self):
        with self.assertRaises(InvalidMoveError):
            self.opponent.concede("b")

    def test_retract_when_attacker_conceded(self):
        self.opponent.concede("c")
        self.assertTrue(self.opponent.retract("b"))

    def test_cannot_retract_when_no_attackers_conceded(self):
        with self.assertRaises(InvalidMoveError):
            self.opponent.retract("b")

    def test_could_be_attacks_last_has_to_be(self):
        self.opponent.could_be("d")
        self.assertEqual(target(last(self.game.attack_relations)).name, "c")

    def test_has_to_be_attacks_last_could_be(self):
        self.opponent.could_be("d")
        self.proponent.has_to_be("e")
        self.assertEqual(target(last(self.game.attack_relations)).name, "d")

    def setUp(self):
        self.game = Game.from_af(set(["a", "b", "c", "d", "e"]),
                                 list([("b", "a"),
                                       ("c", "b"),
                                       ("d", "c"),
                                       ("e", "d")]))
        self.proponent = Proponent(self.game)
        self.opponent = Opponent(self.game)
        self.proponent.has_to_be("a")
        self.opponent.could_be("b")
        self.proponent.has_to_be("c")


class TestArgument(unittest.TestCase):

    def test_arguments_can_be_in_or_out(self):
        argument = Argument("a", "In")
        self.assertEqual(argument.label, "In")
        argument = Argument("b", "Out")
        self.assertEqual(argument.label, "Out")


class TestMoves(unittest.TestCase):

    def test_has_to_be(self):
        self.assertTrue(Argument("a") in self.game.arguments)

    def test_could_be(self):
        new_game = self.opponent.could_be("b")
        self.assertEqual(set([Argument("a"), Argument("b")]),
                         new_game.arguments)
        self.assertEqual(list([(Argument("b"), Argument("a"))]),
                         new_game.attack_relations)

    def test_concede(self):
        self.opponent.could_be("b")
        self.proponent.has_to_be("c")
        game = self.opponent.concede("c")
        self.assertTrue(Argument("c") not in game.arguments)
        self.assertTrue((Argument("b"), Argument("a"))
                        in game.attack_relations)
        self.assertFalse((Argument("c"), Argument("b"))
                         in game.attack_relations)

    def test_retract(self):
        self.opponent.could_be("b")
        self.proponent.has_to_be("c")
        self.opponent.concede("c")
        new_game = self.opponent.retract("b")
        self.assertEqual(set([Argument("a")]), new_game.arguments)
        self.assertTrue(list() == new_game.attack_relations)

    def setUp(self):
        self.game = Game.from_af(set(["a", "b", "c"]),
                                 list([("b", "a"),
                                       ("c", "b")]))
        self.proponent = Proponent(self.game)
        self.opponent = Opponent(self.game)
        self.proponent.has_to_be("a")
