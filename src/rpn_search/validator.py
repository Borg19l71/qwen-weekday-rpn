"""
RPN Expression Validator

This module provides functions for validating RPN expression structures,
checking stack effects, and ensuring syntactic correctness.
"""

from typing import List, Optional
from .tokens import Token, TokenType


def get_stack_effect(tokens: List[Token]) -> Optional[int]:
    """
    Calculate the net stack effect of a token sequence.
    
    The stack effect is the number of values left on the stack after
    executing the token sequence, starting from an empty stack.
    
    Args:
        tokens: List of tokens to analyze
        
    Returns:
        Net stack effect (positive = values pushed, negative = values popped),
        or None if the sequence is invalid (stack underflow)
        
    Examples:
        >>> from .tokens import Token, TokenType
        >>> # CONST pushes 1 value
        >>> get_stack_effect([Token(TokenType.CONST, 5)])
        1
        >>> # Binary op consumes 2, produces 1, net -1
        >>> tokens = [Token(TokenType.CONST, 5), Token(TokenType.CONST, 3), Token(TokenType.BINARY_OP, '+')]
        >>> get_stack_effect(tokens)
        1
    """
    stack_size = 0
    
    for token in tokens:
        if token.token_type in [TokenType.CONST, TokenType.VAR_YY, TokenType.VAR_A, TokenType.VAR_B]:
            stack_size += 1
        elif token.token_type == TokenType.UNARY_MINUS:
            if stack_size < 1:
                return None
            # Consumes 1, produces 1, net effect 0
        elif token.token_type == TokenType.BINARY_OP:
            if stack_size < 2:
                return None
            stack_size -= 1  # Consumes 2, produces 1, net effect -1
        elif token.token_type == TokenType.IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = token.value
            cond_effect = get_stack_effect(cond_tokens)
            then_effect = get_stack_effect(then_tokens)
            else_effect = get_stack_effect(else_tokens)
            
            if cond_effect is None or then_effect is None or else_effect is None:
                return None
            
            # Condition must leave exactly one value on stack
            if cond_effect != 1:
                return None
            
            # THEN and ELSE must have the same stack effect
            if then_effect != else_effect:
                return None
            
            stack_size += then_effect
        elif token.token_type == TokenType.IF_THEN:
            cond_tokens, then_tokens = token.value
            cond_effect = get_stack_effect(cond_tokens)
            then_effect = get_stack_effect(then_tokens)
            
            if cond_effect is None or then_effect is None:
                return None
            
            # Condition must leave exactly one value on stack
            if cond_effect != 1:
                return None
            
            # IF-THEN doesn't have a fixed stack effect (depends on condition)
            # We just validate structure here
    
    return stack_size


def is_valid_rpn_sequence(tokens: List[Token], allow_multi_result: bool = False) -> bool:
    """
    Check if a token sequence can form a valid RPN expression.
    
    Uses stack-based validation to ensure the expression doesn't cause
    stack underflow and produces the expected result.
    
    Args:
        tokens: List of tokens to validate
        allow_multi_result: If True, allows final stack size > 1.
                           Used for validating IF branches internally.
                           
    Returns:
        True if the sequence is a valid RPN expression, False otherwise
        
    Rules:
        - Simple expressions (no IF-THEN): final stack must be exactly 1
        - IF-THEN expressions: final stack depends on runtime condition
        - IF branches being validated: any non-negative stack size allowed
        
    Examples:
        >>> from .tokens import Token, TokenType
        >>> # Valid: single constant
        >>> is_valid_rpn_sequence([Token(TokenType.CONST, 5)])
        True
        >>> # Invalid: binary op with only one operand
        >>> is_valid_rpn_sequence([Token(TokenType.CONST, 5), Token(TokenType.BINARY_OP, '+')])
        False
    """
    stack_size = 0
    
    for token in tokens:
        if token.token_type in [TokenType.CONST, TokenType.VAR_YY, TokenType.VAR_A, TokenType.VAR_B]:
            stack_size += 1
        elif token.token_type == TokenType.UNARY_MINUS:
            if stack_size < 1:
                return False
            # Consumes 1, produces 1
        elif token.token_type == TokenType.BINARY_OP:
            if stack_size < 2:
                return False
            stack_size -= 1  # Consumes 2, produces 1
        elif token.token_type == TokenType.IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = token.value
            if not is_valid_rpn_sequence(cond_tokens):
                return False
            if not is_valid_rpn_sequence(then_tokens, allow_multi_result=True):
                return False
            if not is_valid_rpn_sequence(else_tokens, allow_multi_result=True):
                return False
            
            then_effect = get_stack_effect(then_tokens)
            else_effect = get_stack_effect(else_tokens)
            
            if then_effect is None or else_effect is None:
                return False
            if then_effect != else_effect:
                return False
            if then_effect < 1:
                return False
                
            stack_size += then_effect
        elif token.token_type == TokenType.IF_THEN:
            cond_tokens, then_tokens = token.value
            if not is_valid_rpn_sequence(cond_tokens):
                return False
            if not is_valid_rpn_sequence(then_tokens, allow_multi_result=True):
                return False
            
            cond_effect = get_stack_effect(cond_tokens)
            if cond_effect is None or cond_effect != 1:
                return False
            
            then_effect = get_stack_effect(then_tokens)
            if then_effect is None or then_effect < 0:
                return False
            
            # IF-THEN doesn't guarantee fixed stack size
            pass
    
    # Check final stack state
    has_if_then = any(t.token_type == TokenType.IF_THEN for t in tokens)
    has_if_then_else = any(t.token_type == TokenType.IF_THEN_ELSE for t in tokens)
    
    if has_if_then or has_if_then_else:
        # IF expressions are valid if they don't underflow
        return True
    elif allow_multi_result:
        return stack_size >= 0
    else:
        return stack_size == 1
