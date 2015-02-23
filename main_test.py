from main import *
import unittest

class DiscussionTest(unittest.TestCase):
  def test_has_to_be(self):
    game = Game({},{})
    argument = Argument()
    expected_game = Game({argument}, {})
    proponent = Proponent()
    self.assertEqual(self, proponent.has_to_be(argument, game), expected_game )







  # def setUp(self):
    # self.proponent = Proponent()
    # self.opponent = "opponent"
    # self.argument = "a"

  # def test_has_to_be(self):
    # self.assertTrue(self.proponent.has_to_be(self.argument))
