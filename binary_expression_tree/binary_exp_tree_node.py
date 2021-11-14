import logging

logger = logging.getLogger(__name__)


class ExpressionTreeNode:
    """
    Tree node used in ExpressionTree
    """
    def __init__(self, value, left=None, right=None, is_operator=False, operator_class=None):
        self.value = value
        self.left_node = left
        self.right_node = right
        self.is_operator = is_operator
        self.operator_class = operator_class

    def __str__(self):
        return f"[A node with a value of {self.value}. It is {'NOT' if not self.is_operator else ''} an operator. " \
               f"Right node = '{self.right_node}', Left node = '{self.left_node}']"

    def has_both_children(self):
        """
        :return: True if both left and right nodes are not None
        """
        return self.left_node and self.right_node

    def is_an_operator(self):
        """
        :return: True if the node is an operator
        """
        return self.is_operator

    def has_any_child_operator(self):
        """
        :return: True if there is any operator in child or left node
        """
        if self.left_node and self.left_node.is_an_operator():
            return True

        if self.right_node and self.right_node.is_an_operator():
            return True

    def get_precedence(self):
        """
        :return: The precedence of the node, if it's an operator.
        """
        if not self.is_an_operator():
            return None
        if not self.operator_class:
            raise ValueError(
                f"An operator must have always an operator class")
        return self.operator_class.precedence
