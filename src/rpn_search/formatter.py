"""
Token Formatter

This module provides functions for converting RPN token lists
into human-readable string representations.
"""

from typing import List
from .tokens import Token, TokenType


def tokens_to_string(tokens: List[Token]) -> str:
    """
    Convert tokens to a human-readable string representation.
    
    Args:
        tokens: List of RPN tokens to format
        
    Returns:
        Space-separated string representation of the expression
        
    Examples:
        >>> from .tokens import Token, TokenType
        >>> tokens = [Token(TokenType.CONST, 5), Token(TokenType.CONST, 3), Token(TokenType.BINARY_OP, '+')]
        >>> tokens_to_string(tokens)
        '5 3 +'
        >>> tokens_to_string([Token(TokenType.VAR_YY)])
        'yy'
    """
    parts = []
    for token in tokens:
        if token.token_type == TokenType.CONST:
            parts.append(str(token.value))
        elif token.token_type == TokenType.VAR_YY:
            parts.append('yy')
        elif token.token_type == TokenType.VAR_A:
            parts.append('a')
        elif token.token_type == TokenType.VAR_B:
            parts.append('b')
        elif token.token_type == TokenType.UNARY_MINUS:
            parts.append('neg')
        elif token.token_type == TokenType.BINARY_OP:
            parts.append(str(token.value))
        elif token.token_type == TokenType.IF_THEN_ELSE:
            cond, then_b, else_b = token.value
            cond_str = tokens_to_string(cond)
            then_str = tokens_to_string(then_b)
            else_str = tokens_to_string(else_b)
            parts.append(f'IF({cond_str})THEN({then_str})ELSE({else_str})')
        elif token.token_type == TokenType.IF_THEN:
            cond, then_b = token.value
            cond_str = tokens_to_string(cond)
            then_str = tokens_to_string(then_b)
            parts.append(f'IF({cond_str})THEN({then_str})')
    
    return ' '.join(parts)
