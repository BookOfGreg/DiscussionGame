import main
import unittest

class MyTest(unittest.TestCase):
  def test_adder(self):
    self.assertEqual(main.adder(self,2,3),6)
