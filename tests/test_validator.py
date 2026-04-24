"""Tests for RPN expression validator."""

import pytest
from rpn_search import Token, TokenType, is_valid_rpn_sequence, get_stack_effect


class TestGetStackEffect:
    """Test cases for get_stack_effect function."""
    
    def test_single_constant(self):
        """Test stack effect of single constant."""
        tokens = [Token(TokenType.CONST, 5)]
        assert get_stack_effect(tokens) == 1
    
    def test_single_variable(self):
        """Test stack effect of single variable."""
        tokens = [Token(TokenType.VAR_YY)]
        assert get_stack_effect(tokens) == 1
    
    def test_binary_operation(self):
        """Test stack effect of binary operation."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert get_stack_effect(tokens) == 1
    
    def test_unary_operation(self):
        """Test stack effect of unary operation."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.UNARY_MINUS),
        ]
        assert get_stack_effect(tokens) == 1
    
    def test_stack_underflow(self):
        """Test that underflow returns None."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert get_stack_effect(tokens) is None


class TestIsValidRPNSequence:
    """Test cases for is_valid_rpn_sequence function."""
    
    def test_valid_single_token(self):
        """Test valid single token expressions."""
        assert is_valid_rpn_sequence([Token(TokenType.CONST, 5)]) is True
        assert is_valid_rpn_sequence([Token(TokenType.VAR_YY)]) is True
    
    def test_valid_binary_expression(self):
        """Test valid binary expression."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert is_valid_rpn_sequence(tokens) is True
    
    def test_invalid_stack_underflow(self):
        """Test invalid expression with stack underflow."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert is_valid_rpn_sequence(tokens) is False
    
    def test_invalid_multiple_values(self):
        """Test expression leaving multiple values on stack."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
        ]
        assert is_valid_rpn_sequence(tokens) is False
    
    def test_valid_unary_expression(self):
        """Test valid unary expression."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.UNARY_MINUS),
        ]
        assert is_valid_rpn_sequence(tokens) is True
    
    def test_complex_valid_expression(self):
        """Test complex valid expression."""
        # (5 + 3) * 2
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '+'),
            Token(TokenType.CONST, 2),
            Token(TokenType.BINARY_OP, '*'),
        ]
        assert is_valid_rpn_sequence(tokens) is True
    
    def test_allow_multi_result(self):
        """Test allow_multi_result parameter."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
        ]
        # Without allow_multi_result
        assert is_valid_rpn_sequence(tokens, allow_multi_result=False) is False
        # With allow_multi_result
        assert is_valid_rpn_sequence(tokens, allow_multi_result=True) is True
