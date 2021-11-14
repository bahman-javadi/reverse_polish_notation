import logging
from collections import deque
from functools import lru_cache
from helpers.operators import OperatorsHelper
from binary_expression_tree import binary_exp_tree_node

logger = logging.getLogger(__name__)


class ExpressionTree:
    def __init__(self):
        self._stack = deque()
        # We use this to avoid re-processing every time.
        # If it's already evaluated, we just return the cached results
        self._alreadyConstructed = False
        self._cachedResult = None
        self._cachedInfixExpression = None
        self._originalPostfixExpression = None

    def _get_root(self):
        # Root is the last item in the stack
        if not self._stack:
            return None

        return self._stack[-1]

    # References: I got the ideas from the following references:
    # https://www.geeksforgeeks.org/stack-set-4-evaluation-postfix-expression/
    # https://ttzztt.gitbooks.io/lc/content/quant-dev/postfixto-infix.html
    def _construct_from_postfix(self, expression: str, delimiter=',') -> None:
        logger.debug(f"Constructing binary tree expression from {expression}. Delimiter is set to '{delimiter}'")
        self._stack.clear()
        self._alreadyConstructed = False
        self._cachedResult = None
        self._cachedInfixExpression = None

        # The final evaluated result will be kept in result_stack
        result_stack = deque()
        # The final infix expression will be kept in infix_stack
        infix_stack = deque()

        # Considering empty expression is considered valid
        expression = expression.strip()
        self._originalPostfixExpression = expression
        if not expression:
            self._cachedInfixExpression = ''
            self._alreadyConstructed = True
            return

        # traverse the postfix expression
        for token in expression.split(delimiter):
            token = token.strip()
            if not token:
                raise ValueError(
                    f"The expression '{expression}' is not valid and contains empty operand(s)/operator(s).")

            # if the current token is an operator
            current_operator = OperatorsHelper.get_operator(token)
            if current_operator:
                # pop two operands `operand2` and `operand1` from the stack
                operand2 = self._stack.pop()
                if not operand2:
                    raise ValueError(
                        f"The second operand in '{expression}' is not valid.")
                operand1 = self._stack.pop()
                if not operand1:
                    raise ValueError(f"The first operand in '{expression}' is not valid.")

                # construct a new binary tree whose root is the operator and whose
                # left and right children point to `operand1` and `operand2`, respectively
                node = binary_exp_tree_node.ExpressionTreeNode(token, operand1, operand2, is_operator=True,
                                                               operator_class=current_operator)
                # push the current node into the stack
                self._stack.append(node)

                operand2_string = infix_stack.pop()
                operand1_string = infix_stack.pop()
                if operand1.is_an_operator() and \
                        (operand1.get_precedence() < current_operator.precedence):
                    operand1_string = f"({operand1_string})"

                if operand2.is_an_operator() and \
                        (operand2.get_precedence() <= current_operator.precedence):
                    operand2_string = f"({operand2_string})"

                infix_stack.append(f"{operand1_string} {current_operator.string} {operand2_string}")
                operand2_result = result_stack.pop()
                if not operand2_result:
                    raise ValueError(
                        f"The expression '{expression}' is not valid.")

                operand1_result = result_stack.pop()
                if not operand2:
                    raise ValueError(
                        f"The expression '{expression}' is not valid.")

                result_stack.append(current_operator.operator_callable(operand1_result, operand2_result))

            else:
                # if the current token is an operand, create a new binary tree node
                # whose root is the operand and push it into the stack
                OperatorsHelper.validate_operand(token)
                self._stack.append(binary_exp_tree_node.ExpressionTreeNode(token))
                result_stack.append(int(token))
                infix_stack.append(token)

        # the evaluated result must be in the operand_stack now. we check if there is
        # only a single result on the stack
        if len(result_stack) != 1:
            raise ValueError(
                f"The expression '{expression}' cannot be evaluated.")

        self._cachedResult = result_stack.pop()
        self._cachedInfixExpression = infix_stack.pop()

    # Todo: This needs to be checked for maxsize
    @lru_cache(maxsize=1000)
    def process(self, postfix_expression):
        self._construct_from_postfix(postfix_expression)
        return self._cachedResult, self._cachedInfixExpression
