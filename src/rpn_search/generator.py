"""
RPN Expression Generator

This module provides functions for generating RPN expressions with
increasing complexity (number of tokens).
"""

from typing import List, Tuple, Generator, Dict
from functools import lru_cache
from .tokens import Token, TokenType, get_cached_token


def generate_simple_tokens() -> List[Token]:
    """
    Generate simple tokens (constants and variables).
    
    Returns:
        List of all constant tokens (0-20) and variable tokens (yy, a, b)
    """
    tokens = []
    
    # Constants 0..20
    for i in range(21):
        tokens.append(get_cached_token(TokenType.CONST, i))
    
    # Variables
    tokens.append(get_cached_token(TokenType.VAR_YY))
    tokens.append(get_cached_token(TokenType.VAR_A))
    tokens.append(get_cached_token(TokenType.VAR_B))
    
    return tokens


def generate_unary_tokens() -> List[Token]:
    """
    Generate unary operation tokens.
    
    Returns:
        List containing the unary minus token
    """
    return [get_cached_token(TokenType.UNARY_MINUS)]


def generate_binary_ops() -> List[Token]:
    """
    Generate binary operation tokens.
    
    Returns:
        List of binary operator tokens (+, -, *, //, %)
    """
    ops = ['+', '-', '*', '//', '%']
    return [get_cached_token(TokenType.BINARY_OP, op) for op in ops]


def can_use_div_mod_operator(last_token: Token) -> bool:
    """
    Check if // or % operator can be used based on the last token.
    
    The // and % operators are only valid when the token immediately 
    before them is a constant >= 2.
    
    Args:
        last_token: The last token before the // or % operator
        
    Returns:
        True if // or % can be used, False otherwise
    """
    if last_token is None:
        return False
    
    # Only allow if last token is a constant >= 2
    if last_token.token_type == TokenType.CONST and last_token.value >= 2:
        return True
    
    return False


def get_last_terminal_token(tokens: List[Token]) -> Token:
    """
    Get the last terminal token (rightmost leaf) in an expression.
    
    For simple tokens, returns the token itself.
    For IF-THEN-ELSE tokens, recursively finds the last token in the else branch.
    
    Args:
        tokens: List of tokens representing an expression
        
    Returns:
        The last terminal token, or None if not found
    """
    if not tokens:
        return None
    
    # Start from the last token
    token = tokens[-1]
    
    # If it's a simple token (CONST, VAR, BINARY_OP, UNARY_MINUS), we need to look deeper
    # Actually, for RPN, the last token in the list IS the operator for binary ops
    # We need to find the rightmost operand
    
    # For IF_THEN_ELSE, the structure is [IF_token] where IF_token.value = (cond, then, else)
    if token.token_type == TokenType.IF_THEN_ELSE:
        cond_expr, then_expr, else_expr = token.value
        # Recursively get last token from else branch (it's evaluated last)
        return get_last_terminal_token(else_expr)
    
    if token.token_type == TokenType.IF_THEN:
        cond_expr, then_expr = token.value
        return get_last_terminal_token(then_expr)
    
    # For BINARY_OP, the last token in the flat list is the operator itself
    # We need to find the last token of the second operand
    # But since we're working with a flat RPN list, we need to evaluate which tokens form E2
    # This is complex, so let's use a simpler approach: scan backwards to find first non-operator
    
    # Scan backwards to find the last operand token
    for t in reversed(tokens):
        if t.token_type in [TokenType.CONST, TokenType.VAR_YY, TokenType.VAR_A, TokenType.VAR_B]:
            return t
        elif t.token_type == TokenType.UNARY_MINUS:
            continue  # Skip unary minus, keep looking
        elif t.token_type in [TokenType.BINARY_OP, TokenType.IF_THEN_ELSE, TokenType.IF_THEN]:
            # Operators don't count as terminal tokens
            continue
    
    return None


def generate_all_rpn_with_if(max_tokens: int) -> Generator[Tuple[int, List[Token]], None, None]:
    """
    Generate RPN expressions including IF-THEN-ELSE structures.
    
    This generator yields expressions in order of increasing token count,
    making it suitable for finding minimal-complexity solutions.
    
    Args:
        max_tokens: Maximum number of tokens to generate
        
    Yields:
        Tuples of (num_tokens, expression_tokens)
        
    Example:
        >>> for num_tokens, expr in generate_all_rpn_with_if(5):
        ...     print(f"{num_tokens} tokens: {expr}")
    """
    simple_tokens = generate_simple_tokens()
    unary_tokens = generate_unary_tokens()
    binary_ops = generate_binary_ops()
    
    # Cache expressions by token count and allow_if flag
    cache: Dict[Tuple[int, bool], List[List[Token]]] = {}
    
    def get_expressions(n: int, allow_if: bool) -> List[List[Token]]:
        """Get or compute all expressions with n tokens."""
        cache_key = (n, allow_if)
        if cache_key in cache:
            return cache[cache_key]
        
        exprs = []
        
        if n == 1:
            # Only simple tokens can form a valid 1-token expression
            for token in simple_tokens:
                exprs.append([token])
                
        elif n == 2:
            # Simple token + unary minus
            for simple in simple_tokens:
                for unary in unary_tokens:
                    exprs.append([simple, unary])
                    
        else:
            # Binary operations: E = E1 E2 OP
            for k in range(1, n):
                remaining = n - k - 1
                if remaining < 1:
                    continue
                
                exprs1 = get_expressions(k, allow_if)
                exprs2 = get_expressions(remaining, allow_if)
                
                for e1 in exprs1:
                    for e2 in exprs2:
                        # Check if we can use // or % operators based on the last token of E2
                        last_token_of_e2 = get_last_terminal_token(e2)
                        allow_div_mod = can_use_div_mod_operator(last_token_of_e2)
                        
                        for op in binary_ops:
                            # Skip // and % if not allowed
                            if op.value in ['//', '%'] and not allow_div_mod:
                                continue
                            exprs.append(e1 + e2 + [op])
            
            # Unary operations: E = E1 UNARY_MINUS
            for expr in get_expressions(n - 1, allow_if):
                for unary in unary_tokens:
                    exprs.append(expr + [unary])
            
            # IF-THEN-ELSE structures (only if enabled and enough tokens)
            if allow_if and n >= 5:
                # Total = cond_tokens + then_tokens + else_tokens + 1 (IF token)
                for cond_size in range(1, n - 2):
                    for then_size in range(1, n - cond_size - 1):
                        else_size = n - 1 - cond_size - then_size
                        if else_size < 1:
                            continue
                        
                        cond_exprs = get_expressions(cond_size, False)
                        then_exprs = get_expressions(then_size, False)
                        else_exprs = get_expressions(else_size, False)
                        
                        for ce in cond_exprs:
                            for te in then_exprs:
                                for ee in else_exprs:
                                    if_token = Token(TokenType.IF_THEN_ELSE, (ce, te, ee))
                                    exprs.append([if_token])
            
            # IF-THEN (without ELSE) structures
            if allow_if and n >= 4:
                # Total = cond_tokens + then_tokens + 1 (IF token)
                for cond_size in range(1, n - 1):
                    then_size = n - 1 - cond_size
                    if then_size < 1:
                        continue
                    
                    cond_exprs = get_expressions(cond_size, False)
                    then_exprs = get_expressions(then_size, False)
                    
                    for ce in cond_exprs:
                        for te in then_exprs:
                            if_token = Token(TokenType.IF_THEN, (ce, te))
                            exprs.append([if_token])
        
        cache[cache_key] = exprs
        return exprs
    
    for n in range(1, max_tokens + 1):
        allow_if = (n >= 5)
        exprs = get_expressions(n, allow_if)
        for expr in exprs:
            yield n, expr
