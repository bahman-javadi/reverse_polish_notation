import unittest

from binary_expression_tree.binary_expression_tree import ExpressionTree as ExpressionTreeClass


# Todo: this is a very limited data set. Needs to be completed.
class TestExpressionTree(unittest.TestCase):
    """
    Unit tests for ExpressionTree class
    """

    def test_0_simple_prn_success(self):
        postorder_expression = '2, 3, +, 5, *'
        exp_tree = ExpressionTreeClass()
        result, infix_expression_string = exp_tree.process(postorder_expression)
        self.assertEqual('(2 + 3) * 5', infix_expression_string)
        self.assertEqual(25, result)

    def test_1_simple_prn_success(self):
        postorder_expression = '10, 7, 2, -, /'
        exp_tree = ExpressionTreeClass()
        result, infix_expression_string = exp_tree.process(postorder_expression)
        self.assertEqual('10 / (7 - 2)', infix_expression_string)
        self.assertEqual(2, result)

    def test_2_simple_prn_success(self):
        postorder_expression = '10,3,+,2,+,5, *'
        exp_tree = ExpressionTreeClass()
        result, infix_expression_string = exp_tree.process(postorder_expression)
        self.assertEqual('(10 + 3 + 2) * 5', infix_expression_string)
        self.assertEqual(75, result)

    def test_3_simple_prn_success(self):
        postorder_expression = '5,2,6,*,+,200,+'
        exp_tree = ExpressionTreeClass()
        result, infix_expression_string = exp_tree.process(postorder_expression)
        self.assertEqual('5 + 2 * 6 + 200', infix_expression_string)
        self.assertEqual(217, result)

    def test_4_simple_prn_success(self):
        postorder_expression = '2,100,100,+,*, 10, 100, 2, *, /, +, 9, +'
        exp_tree = ExpressionTreeClass()
        result, infix_expression_string = exp_tree.process(postorder_expression)
        self.assertEqual('2 * (100 + 100) + 10 / (100 * 2) + 9', infix_expression_string)

    def test_1_invalid_operand_prn_construction_throws_exception(self):
        postorder_expression = '2, a, +, 5, *'
        exp_tree = ExpressionTreeClass()
        self.assertRaises(ValueError, exp_tree._construct_from_postfix, postorder_expression)


if __name__ == '__main__':
    unittest.main()
