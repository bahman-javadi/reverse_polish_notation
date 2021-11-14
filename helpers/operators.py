import operator


class RPNOperator:
    """
    This class represents each operator in the RPN
    """
    def __init__(self, string, precedence, operator_callable, associativity='l'):
        """
        :param string: The string representation of the operator
        :param precedence: The operator precedence
        :param operator_callable: The callable object for the operand
        :param associativity: 'l' for left associativity and 'r' for right associativity
        """
        self.string = string
        self.precedence = precedence
        self.operator_callable = operator_callable
        self.associativity = associativity

    def __str__(self):
        return f"An operator with string representation '{self.string}'. Precedence = {self.precedence}, " \
               f"Associativity = {self.associativity}"


class OperatorsHelper:
    @staticmethod
    def get_operator(token):
        """
        A utility function to check if the token is a valid operator and returns it's operator class.
        Currently, these operators ['+', '-', '*', '/'] are accepted.
        Associativity of all supported operands is left to right.
        :param token: is a string containing zero or more characters
        :return: The operator's object if the string is a valid operator, else None
        """
        operators = {'+': (1, operator.add), '-': (1, operator.sub), '*': (2, operator.mul), '/': (2, operator.truediv)}

        token = token.strip()
        if not (token and isinstance(token, str) and len(token) == 1):
            return None

        if not (token in operators.keys()):
            return None

        precedence_operator_tuple = operators[token]
        return RPNOperator(token, precedence_operator_tuple[0], precedence_operator_tuple[1])


    @staticmethod
    def validate_operand(token: str) -> int:
        """
        # A utility function to check if the token is a valid operand
        :param token: is a string containing zero or more characters
        :return: converted operand
        """
        token = token.strip()
        if not (token and isinstance(token, str) and token.isnumeric()):
            raise ValueError(f"'{token}' is an invalid operand !")

        # This check would helpful to detect arithmetic overflow
        return int(token)