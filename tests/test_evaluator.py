"""Tests for RPN expression evaluator."""

import pytest
from rpn_search import Token, TokenType, evaluate_rpn


class TestEvaluateRPN:
    """Test cases for the evaluate_rpn function."""
    
    def test_single_constant(self):
        """Test evaluation of a single constant."""
        tokens = [Token(TokenType.CONST, 42)]
        assert evaluate_rpn(tokens, 0) == 42
    
    def test_single_variable_yy(self):
        """Test evaluation of yy variable."""
        tokens = [Token(TokenType.VAR_YY)]
        assert evaluate_rpn(tokens, 50) == 50
    
    def test_single_variable_a(self):
        """Test evaluation of a (tens digit) variable."""
        tokens = [Token(TokenType.VAR_A)]
        assert evaluate_rpn(tokens, 42) == 4
    
    def test_single_variable_b(self):
        """Test evaluation of b (ones digit) variable."""
        tokens = [Token(TokenType.VAR_B)]
        assert evaluate_rpn(tokens, 42) == 2
    
    def test_addition(self):
        """Test binary addition."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert evaluate_rpn(tokens, 0) == 8
    
    def test_subtraction(self):
        """Test binary subtraction."""
        tokens = [
            Token(TokenType.CONST, 10),
            Token(TokenType.CONST, 4),
            Token(TokenType.BINARY_OP, '-'),
        ]
        assert evaluate_rpn(tokens, 0) == 6
    
    def test_multiplication(self):
        """Test binary multiplication."""
        tokens = [
            Token(TokenType.CONST, 6),
            Token(TokenType.CONST, 7),
            Token(TokenType.BINARY_OP, '*'),
        ]
        assert evaluate_rpn(tokens, 0) == 42
    
    def test_integer_division(self):
        """Test integer division."""
        tokens = [
            Token(TokenType.CONST, 20),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '//'),
        ]
        assert evaluate_rpn(tokens, 0) == 6
    
    def test_modulo(self):
        """Test modulo operation."""
        tokens = [
            Token(TokenType.CONST, 20),
            Token(TokenType.CONST, 7),
            Token(TokenType.BINARY_OP, '%'),
        ]
        assert evaluate_rpn(tokens, 0) == 6
    
    def test_division_by_zero(self):
        """Test that division by zero returns None."""
        tokens = [
            Token(TokenType.CONST, 10),
            Token(TokenType.CONST, 0),
            Token(TokenType.BINARY_OP, '//'),
        ]
        assert evaluate_rpn(tokens, 0) is None
    
    def test_modulo_by_zero(self):
        """Test that modulo by zero returns None."""
        tokens = [
            Token(TokenType.CONST, 10),
            Token(TokenType.CONST, 0),
            Token(TokenType.BINARY_OP, '%'),
        ]
        assert evaluate_rpn(tokens, 0) is None
    
    def test_stack_underflow_binary_op(self):
        """Test that stack underflow returns None."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert evaluate_rpn(tokens, 0) is None
    
    def test_unary_minus(self):
        """Test unary negation."""
        tokens = [
            Token(TokenType.CONST, 42),
            Token(TokenType.UNARY_MINUS),
        ]
        assert evaluate_rpn(tokens, 0) == -42
    
    def test_unary_minus_stack_underflow(self):
        """Test unary minus with empty stack."""
        tokens = [Token(TokenType.UNARY_MINUS)]
        assert evaluate_rpn(tokens, 0) is None
    
    def test_complex_expression(self):
        """Test a more complex expression."""
        # (5 + 3) * 2 = 16
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
            Token(TokenType.BINARY_OP, '+'),
            Token(TokenType.CONST, 2),
            Token(TokenType.BINARY_OP, '*'),
        ]
        assert evaluate_rpn(tokens, 0) == 16
    
    def test_expression_with_variable(self):
        """Test expression using yy variable."""
        # yy + 10
        tokens = [
            Token(TokenType.VAR_YY),
            Token(TokenType.CONST, 10),
            Token(TokenType.BINARY_OP, '+'),
        ]
        assert evaluate_rpn(tokens, 25) == 35
    
    def test_final_stack_not_one(self):
        """Test that multiple values on stack returns None."""
        tokens = [
            Token(TokenType.CONST, 5),
            Token(TokenType.CONST, 3),
        ]
        assert evaluate_rpn(tokens, 0) is None
    
    def test_empty_tokens(self):
        """Test empty token list."""
        tokens = []
        assert evaluate_rpn(tokens, 0) is None
