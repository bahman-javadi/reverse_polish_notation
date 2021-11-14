import unittest

from binary_expression_tree.binary_exp_tree_node import ExpressionTreeNode as ExpressionTreeNodeClass
from helpers.operators import RPNOperator

class TestExpressionTreeNode(unittest.TestCase):
    """
        Unit test for ExpressionTreeNode class
    """
    def test_has_both_children(self):
        exp_tree_node = ExpressionTreeNodeClass(value='root')
        self.assertFalse(exp_tree_node.has_both_children())
        left_node = ExpressionTreeNodeClass(value='left_node')
        right_node = ExpressionTreeNodeClass(value='right_node')
        exp_tree_node.left_node = left_node
        self.assertFalse(exp_tree_node.has_both_children())
        exp_tree_node.right_node = right_node
        self.assertTrue(exp_tree_node.has_both_children())

    def test_is_an_operator(self):
        exp_tree_node = ExpressionTreeNodeClass('root', is_operator=False)
        self.assertFalse(exp_tree_node.is_an_operator())
        exp_tree_node_2 = ExpressionTreeNodeClass('root', is_operator=True)
        self.assertTrue(exp_tree_node_2.is_an_operator())

    def test_has_any_child_operator(self):
        exp_tree_node = ExpressionTreeNodeClass('root')
        self.assertFalse(exp_tree_node.has_any_child_operator())
        self.assertFalse(exp_tree_node.has_any_child_operator())
        left_node = ExpressionTreeNodeClass(value='left_node', is_operator=False)
        right_node = ExpressionTreeNodeClass(value='right_node', is_operator=True)
        exp_tree_node.left_node = left_node
        self.assertFalse(exp_tree_node.has_any_child_operator())
        exp_tree_node.right_node = right_node
        self.assertTrue(exp_tree_node.has_any_child_operator())


    def test_get_precedence(self):
        exp_tree_node = ExpressionTreeNodeClass('root1')
        self.assertRaises(ValueError, exp_tree_node.get_precedence())
        exp_tree_node_2 = ExpressionTreeNodeClass('root2', is_operator=True,
                                                  operator_class=RPNOperator('dummy', 20, (), 'l'))
        self.assertEqual(20, exp_tree_node_2.get_precedence())
