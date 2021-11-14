import unittest
from helpers.operators import RPNOperator


class TestRPNOperator(unittest.TestCase):
    """
    Unit test for RPNOperator class
    """
    def test_rpn_operator(self):
        def dummy_callable(): return 123

        my_operator = RPNOperator(string='dummy', precedence=10, operator_callable=dummy_callable, associativity='r')
        self.assertEqual('dummy', my_operator.string)
        self.assertEqual(10, my_operator.precedence)
        self.assertEqual(123, my_operator.operator_callable())
        self.assertEqual('r', my_operator.associativity)
