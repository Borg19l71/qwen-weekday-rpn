"""
Expression Checker and Target Function

This module provides functions for checking if RPN expressions match
a target function across a range of input values.
"""

from typing import List

from .evaluator import evaluate_rpn
from .tokens import Token


# Configuration constants
CONSTANT_RANGE = range(21)  # Constants 0-20
YY_TEST_RANGE = range(100)  # Test yy values 0-99
SAMPLE_VALUES = [0, 1, 7, 15, 23, 50, 77, 99]  # Quick check values
MODULUS = 7  # Expected result range


def target_function(yy: int) -> int:
    """
    Target function that RPN expressions should match.
    
    Computes (yy + yy//4) % 7, which is useful for day-of-week calculations.
    
    Args:
        yy: Input value (typically 0-99 representing years)
        
    Returns:
        Result in range [0, 6]
        
    Examples:
        >>> target_function(0)
        0
        >>> target_function(7)
        1
        >>> target_function(99)
        4
    """
    return (yy + yy // 4) % 7


def check_expression(tokens: List[Token]) -> bool:
    """
    Check if expression matches target for all yy in 0..99.
    
    Uses two-phase verification:
    1. First check sample values (quick rejection)
    2. If samples pass, check all values 0..99
    
    Args:
        tokens: List of RPN tokens to verify
        
    Returns:
        True if the expression produces the same result as target_function
        for all yy in 0..99, False otherwise
        
    Note:
        Returns False if evaluation fails for any yy value (returns None).
        Results are normalized modulo 7 before comparison.
    """
    # Phase 1: Quick check with sample values
    for yy in SAMPLE_VALUES:
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        expected = target_function(yy)
        result_mod = result % MODULUS
        if result_mod != expected:
            return False
    
    # Phase 2: Full check with all values 0..99
    for yy in YY_TEST_RANGE:
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        expected = target_function(yy)
        result_mod = result % MODULUS
        if result_mod != expected:
            return False
    
    return True
