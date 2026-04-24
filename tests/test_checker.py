"""Tests for expression checker and target function."""

import pytest
from rpn_search import (
    Token, 
    TokenType, 
    check_expression, 
    target_function,
    SAMPLE_VALUES,
    YY_TEST_RANGE,
    MODULUS,
)


class TestTargetFunction:
    """Test cases for target_function."""
    
    def test_known_values(self):
        """Test target function with known values."""
        assert target_function(0) == 0
        assert target_function(1) == 0
        assert target_function(4) == 1
        assert target_function(7) == 1
        assert target_function(99) == 4
    
    def test_range(self):
        """Test that results are always in range [0, 6]."""
        for yy in range(100):
            result = target_function(yy)
            assert 0 <= result < 7
    
    def test_formula(self):
        """Test the formula implementation."""
        for yy in range(100):
            expected = (yy + yy // 4) % 7
            assert target_function(yy) == expected


class TestCheckExpression:
    """Test cases for check_expression function."""
    
    def test_matching_expression(self):
        """Test expression that matches target function."""
        # yy 4 // yy + 7 % should match (yy + yy//4) % 7
        tokens = [
            Token(TokenType.VAR_YY),
            Token(TokenType.CONST, 4),
            Token(TokenType.BINARY_OP, '//'),
            Token(TokenType.VAR_YY),
            Token(TokenType.BINARY_OP, '+'),
            Token(TokenType.CONST, 7),
            Token(TokenType.BINARY_OP, '%'),
        ]
        assert check_expression(tokens) is True
    
    def test_non_matching_expression(self):
        """Test expression that doesn't match target function."""
        # Just yy - doesn't match
        tokens = [Token(TokenType.VAR_YY)]
        assert check_expression(tokens) is False
    
    def test_constant_expression(self):
        """Test constant expression (doesn't match)."""
        tokens = [Token(TokenType.CONST, 0)]
        assert check_expression(tokens) is False
    
    def test_simple_addition(self):
        """Test simple addition (doesn't match)."""
        tokens = [
            Token(TokenType.VAR_YY),
            Token(TokenType.CONST, 1),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert check_expression(tokens) is False
    
    def test_evaluation_failure(self):
        """Test that expressions failing evaluation return False."""
        # Division by zero for some inputs
        tokens = [
            Token(TokenType.VAR_YY),
            Token(TokenType.CONST, 0),
            Token(TokenType.BINARY_OP, '//'),
        ]
        assert check_expression(tokens) is False


class TestConfigurationConstants:
    """Test configuration constants."""
    
    def test_sample_values_in_range(self):
        """Test that sample values are within test range."""
        for value in SAMPLE_VALUES:
            assert value in YY_TEST_RANGE
    
    def test_modulus_is_seven(self):
        """Test that modulus is 7."""
        assert MODULUS == 7
    
    def test_yy_test_range_size(self):
        """Test that YY_TEST_RANGE has 100 values."""
        assert len(list(YY_TEST_RANGE)) == 100
