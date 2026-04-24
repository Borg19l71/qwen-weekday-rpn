"""
RPN Expression Search Package

A package for searching Reverse Polish Notation (RPN) expressions that match
a target function across a range of input values.
"""

from .tokens import Token, TokenType
from .evaluator import evaluate_rpn
from .validator import is_valid_rpn_sequence, get_stack_effect
from .generator import generate_all_rpn_with_if
from .checker import check_expression, target_function, SAMPLE_VALUES, YY_TEST_RANGE, MODULUS
from .formatter import tokens_to_string

__version__ = "1.0.0"
__all__ = [
    "Token",
    "TokenType",
    "evaluate_rpn",
    "is_valid_rpn_sequence",
    "get_stack_effect",
    "generate_all_rpn_with_if",
    "check_expression",
    "target_function",
    "tokens_to_string",
    "SAMPLE_VALUES",
    "YY_TEST_RANGE",
    "MODULUS",
]
