"""
RPN Expression Evaluator

This module provides functions for evaluating Reverse Polish Notation (RPN)
expressions given a set of tokens and input values.
"""

from typing import List, Optional, Tuple
from .tokens import Token, TokenType


def get_variables(yy: int) -> Tuple[int, int, int]:
    """
    Extract yy, a (tens digit), and b (ones digit) from yy value.
    
    Args:
        yy: Input value (typically 0-99)
        
    Returns:
        Tuple of (yy, a, b) where a = yy // 10 and b = yy % 10
        
    Examples:
        >>> get_variables(42)
        (42, 4, 2)
        >>> get_variables(7)
        (7, 0, 7)
        >>> get_variables(99)
        (99, 9, 9)
    """
    a = yy // 10
    b = yy % 10
    return yy, a, b


def evaluate_rpn(tokens: List[Token], yy: int) -> Optional[int]:
    """
    Evaluate RPN expression for given yy value.
    
    This is the main entry point for evaluating an RPN expression. It starts
    with an empty stack and processes all tokens.
    
    Args:
        tokens: List of RPN tokens to evaluate
        yy: Input value (0-99) representing the variable
        
    Returns:
        The computed integer result, or None if evaluation fails due to:
        - Stack underflow
        - Division by zero
        - Final stack doesn't have exactly one value
        
    Examples:
        >>> from .tokens import Token, TokenType
        >>> tokens = [Token(TokenType.CONST, 5), Token(TokenType.CONST, 3), Token(TokenType.BINARY_OP, '+')]
        >>> evaluate_rpn(tokens, 0)
        8
    """
    return _evaluate_rpn_core(tokens, yy, initial_stack=[])


def evaluate_rpn_internal(tokens: List[Token], yy: int, stack: List[int]) -> Optional[int]:
    """
    Internal RPN evaluation that works on an existing stack.
    
    This function continues evaluation from a given stack state, useful for
    evaluating nested expressions within IF-THEN-ELSE constructs.
    
    Args:
        tokens: List of RPN tokens to evaluate
        yy: Input value (0-99) representing the variable
        stack: Initial stack state to continue from
        
    Returns:
        The top of stack after evaluation, or None if failed
        
    Note:
        This function modifies the stack in-place.
    """
    return _evaluate_rpn_core(tokens, yy, initial_stack=stack)


def _evaluate_rpn_core(
    tokens: List[Token], 
    yy: int, 
    initial_stack: Optional[List[int]] = None
) -> Optional[int]:
    """
    Core RPN evaluation logic with optional initial stack.
    
    This unified function handles both fresh evaluation (empty stack) and
    internal evaluation (existing stack), eliminating code duplication.
    
    Args:
        tokens: List of RPN tokens to evaluate
        yy: Input value (0-99) representing the variable
        initial_stack: Starting stack state (empty list if None)
        
    Returns:
        For empty initial stack: final single value or None
        For non-empty initial stack: top of stack after evaluation or None
    """
    stack = initial_stack if initial_stack is not None else []
    yy_val, a, b = get_variables(yy)
    
    is_returning_top = (initial_stack is not None)
    
    for token in tokens:
        if token.token_type == TokenType.CONST:
            stack.append(token.value)
        elif token.token_type == TokenType.VAR_YY:
            stack.append(yy_val)
        elif token.token_type == TokenType.VAR_A:
            stack.append(a)
        elif token.token_type == TokenType.VAR_B:
            stack.append(b)
        elif token.token_type == TokenType.UNARY_MINUS:
            if len(stack) < 1:
                return None
            val = stack.pop()
            stack.append(-val)
        elif token.token_type == TokenType.BINARY_OP:
            if len(stack) < 2:
                return None
            b_val = stack.pop()
            a_val = stack.pop()
            op = token.value
            
            try:
                if op == '+':
                    stack.append(a_val + b_val)
                elif op == '-':
                    stack.append(a_val - b_val)
                elif op == '*':
                    stack.append(a_val * b_val)
                elif op == '//':
                    if b_val == 0:
                        return None
                    stack.append(a_val // b_val)
                elif op == '%':
                    if b_val == 0:
                        return None
                    stack.append(a_val % b_val)
            except (ZeroDivisionError, OverflowError):
                return None
        elif token.token_type == TokenType.IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = token.value
            
            # Evaluate condition on a copy
            cond_stack = stack.copy()
            cond_result = _evaluate_rpn_core(cond_tokens, yy, cond_stack)
            if cond_result is None:
                return None
            
            if cond_result != 0:
                branch_result = _evaluate_rpn_core(then_tokens, yy, stack)
            else:
                branch_result = _evaluate_rpn_core(else_tokens, yy, stack)
            
            if branch_result is None:
                return None
                
        elif token.token_type == TokenType.IF_THEN:
            cond_tokens, then_tokens = token.value
            
            # Evaluate condition on a copy
            cond_stack = stack.copy()
            cond_result = _evaluate_rpn_core(cond_tokens, yy, cond_stack)
            if cond_result is None:
                return None
            
            if cond_result != 0:
                branch_result = _evaluate_rpn_core(then_tokens, yy, stack)
                if branch_result is None:
                    return None
            # else: condition is false - no stack change
    
    if is_returning_top:
        # Internal evaluation: return top of stack
        if len(stack) < 1:
            return None
        return stack[-1]
    else:
        # Fresh evaluation: must have exactly one value
        if len(stack) != 1:
            return None
        return stack[0]
