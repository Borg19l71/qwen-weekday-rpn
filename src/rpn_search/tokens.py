"""
Token definitions for RPN expressions.

This module defines the token types and Token class used to represent
elements in Reverse Polish Notation expressions.
"""

from dataclasses import dataclass
from typing import Optional, Union


class TokenType:
    """Enumeration of token types for RPN expressions."""
    
    CONST = 'CONST'           # Integer constant 0..20
    VAR_YY = 'VAR_YY'         # Variable yy (input value 0-99)
    VAR_A = 'VAR_A'           # Variable a (tens digit of yy)
    VAR_B = 'VAR_B'           # Variable b (ones digit of yy)
    UNARY_MINUS = 'UNARY_MINUS'  # Unary negation operator
    BINARY_OP = 'BINARY_OP'   # Binary arithmetic operator (+, -, *, //, %)
    IF_THEN_ELSE = 'IF_THEN_ELSE'  # Conditional with both branches
    IF_THEN = 'IF_THEN'       # Conditional without ELSE branch


@dataclass
class Token:
    """
    Represents a single token in an RPN expression.
    
    Attributes:
        token_type: The type of token (from TokenType)
        value: Optional value associated with the token
        
    Examples:
        >>> Token(TokenType.CONST, 5)
        Token(token_type='CONST', value=5)
        >>> Token(TokenType.VAR_YY)
        Token(token_type='VAR_YY', value=None)
        >>> Token(TokenType.BINARY_OP, '+')
        Token(token_type='BINARY_OP', value='+')
    """
    
    token_type: str
    value: Optional[Union[str, int, tuple]] = None
    
    def __repr__(self) -> str:
        """Return a string representation of the token."""
        if self.value is not None:
            return f"Token({self.token_type}, {self.value})"
        return f"Token({self.token_type})"


# Pre-created token instances for efficiency (Flyweight pattern)
TOKEN_CACHE = {}

# Initialize cache with constants
for i in range(21):
    TOKEN_CACHE[(TokenType.CONST, i)] = Token(TokenType.CONST, i)

# Initialize cache with variables
TOKEN_CACHE[(TokenType.VAR_YY, None)] = Token(TokenType.VAR_YY)
TOKEN_CACHE[(TokenType.VAR_A, None)] = Token(TokenType.VAR_A)
TOKEN_CACHE[(TokenType.VAR_B, None)] = Token(TokenType.VAR_B)

# Initialize cache with unary operator
TOKEN_CACHE[(TokenType.UNARY_MINUS, None)] = Token(TokenType.UNARY_MINUS)

# Initialize cache with binary operators
for op in ['+', '-', '*', '//', '%']:
    TOKEN_CACHE[(TokenType.BINARY_OP, op)] = Token(TokenType.BINARY_OP, op)


def get_cached_token(token_type: str, value: Optional[Union[str, int]] = None) -> Token:
    """
    Get a cached token instance or create a new one if not in cache.
    
    Args:
        token_type: The type of token (from TokenType)
        value: Optional value associated with the token
        
    Returns:
        A Token instance (may be shared with other callers)
        
    Examples:
        >>> t1 = get_cached_token(TokenType.CONST, 5)
        >>> t2 = get_cached_token(TokenType.CONST, 5)
        >>> t1 is t2  # Same instance due to caching
        True
    """
    key = (token_type, value)
    if key not in TOKEN_CACHE:
        TOKEN_CACHE[key] = Token(token_type, value)
    return TOKEN_CACHE[key]
