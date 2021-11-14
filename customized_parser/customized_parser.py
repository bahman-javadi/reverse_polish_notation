import argparse
import sys


class CustomizedParser(argparse.ArgumentParser):
    """
    CustomizedParser is a subclass from ArgumentParser
    It is implemented to customize parser error messages.
    The error message would be a simple error starting with 'Error-' prefix.
    """

    def error(self, message):
        print(f'ERROR- Invalid Argument(s) - {message}', file=sys.stdout)
        exit(-1)
