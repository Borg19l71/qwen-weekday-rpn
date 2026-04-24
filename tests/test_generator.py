"""Tests for RPN expression generator."""

import pytest
from rpn_search import Token, TokenType, generate_all_rpn_with_if


class TestGenerateAllRPNWithIf:
    """Test cases for generate_all_rpn_with_if function."""
    
    def test_generates_expressions(self):
        """Test that generator produces expressions."""
        expressions = list(generate_all_rpn_with_if(3))
        assert len(expressions) > 0
    
    def test_yields_token_count(self):
        """Test that generator yields token count with expression."""
        for num_tokens, expr in generate_all_rpn_with_if(5):
            assert isinstance(num_tokens, int)
            assert isinstance(expr, list)
            assert len(expr) == num_tokens
    
    def test_increasing_token_count(self):
        """Test that expressions are generated in increasing token count order."""
        prev_count = 0
        for num_tokens, _ in generate_all_rpn_with_if(5):
            assert num_tokens >= prev_count
            prev_count = num_tokens
    
    def test_single_token_expressions(self):
        """Test that single token expressions include constants and variables."""
        found_const = False
        found_var = False
        
        for num_tokens, expr in generate_all_rpn_with_if(1):
            if num_tokens == 1 and len(expr) == 1:
                token = expr[0]
                if token.token_type == TokenType.CONST:
                    found_const = True
                elif token.token_type == TokenType.VAR_YY:
                    found_var = True
        
        assert found_const, "Should generate constant tokens"
        assert found_var, "Should generate variable tokens"
    
    def test_two_token_expressions(self):
        """Test two token expressions (constant + unary)."""
        found_unary = False
        
        for num_tokens, expr in generate_all_rpn_with_if(2):
            if num_tokens == 2:
                # Should have a value token followed by unary minus
                if len(expr) == 2 and expr[1].token_type == TokenType.UNARY_MINUS:
                    found_unary = True
                    break
        
        assert found_unary, "Should generate expressions with unary minus"
    
    def test_binary_operation_expressions(self):
        """Test that binary operation expressions are generated."""
        found_binary = False
        
        for num_tokens, expr in generate_all_rpn_with_if(3):
            if num_tokens == 3:
                # Look for pattern: CONST CONST BINARY_OP
                if (len(expr) == 3 and 
                    expr[0].token_type == TokenType.CONST and
                    expr[1].token_type == TokenType.CONST and
                    expr[2].token_type == TokenType.BINARY_OP):
                    found_binary = True
                    break
        
        assert found_binary, "Should generate binary operation expressions"
    
    def test_max_tokens_limit(self):
        """Test that generator respects max_tokens limit."""
        max_found = 0
        for num_tokens, _ in generate_all_rpn_with_if(4):
            assert num_tokens <= 4
            max_found = max(max_found, num_tokens)
        
        assert max_found == 4
