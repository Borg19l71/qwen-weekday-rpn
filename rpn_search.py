#!/usr/bin/env python3
"""
RPN Expression Search Program
Searches for RPN expressions that produce the same result as (yy + yy//4) % 7
for all yy in range 0..99, using increasing complexity (number of tokens).
"""

from itertools import product
from typing import List, Tuple, Optional, Union, Callable
import sys
import time

# Target function: (yy + yy//4) % 7
def target_function(yy: int) -> int:
    return (yy + yy // 4) % 7

# Token types
class TokenType:
    CONST = 'CONST'      # Integer constant 0..20
    VAR_YY = 'VAR_YY'    # Variable yy
    VAR_A = 'VAR_A'      # Variable a (tens digit)
    VAR_B = 'VAR_B'      # Variable b (ones digit)
    UNARY_MINUS = 'UNARY_MINUS'
    BINARY_OP = 'BINARY_OP'
    IF_THEN_ELSE = 'IF_THEN_ELSE'
    IF_THEN = 'IF_THEN'  # IF-THEN without ELSE (returns 0 if condition is false)

class Token:
    def __init__(self, token_type: str, value: Optional[Union[str, int]] = None):
        self.token_type = token_type
        self.value = value
    
    def __repr__(self):
        if self.value is not None:
            return f"Token({self.token_type}, {self.value})"
        return f"Token({self.token_type})"

def get_variables(yy: int) -> Tuple[int, int, int]:
    """Extract yy, a, b from yy value."""
    a = yy // 10
    b = yy % 10
    return yy, a, b

def evaluate_rpn(tokens: List[Token], yy: int) -> Optional[int]:
    """
    Evaluate RPN expression for given yy value.
    Returns None if evaluation fails (stack underflow, division by zero, etc.)
    or if final stack doesn't have exactly one value.
    Optimized for speed with local variable caching and minimal lookups.
    """
    stack = []
    yy_val, a, b = get_variables(yy)
    
    # Cache token attributes to avoid repeated attribute lookups
    for token in tokens:
        ttype = token.token_type
        tval = token.value
        
        if ttype == 'CONST':
            stack.append(tval)
        elif ttype == 'VAR_YY':
            stack.append(yy_val)
        elif ttype == 'VAR_A':
            stack.append(a)
        elif ttype == 'VAR_B':
            stack.append(b)
        elif ttype == 'UNARY_MINUS':
            if len(stack) < 1:
                return None
            stack[-1] = -stack[-1]
        elif ttype == 'BINARY_OP':
            if len(stack) < 2:
                return None
            b_val = stack.pop()
            a_val = stack.pop()
            
            if tval == '+':
                stack.append(a_val + b_val)
            elif tval == '-':
                stack.append(a_val - b_val)
            elif tval == '*':
                stack.append(a_val * b_val)
            elif tval == '//':
                if b_val == 0:
                    return None
                stack.append(a_val // b_val)
            elif tval == '%':
                if b_val == 0:
                    return None
                stack.append(a_val % b_val)
        elif ttype == 'IF_THEN_ELSE':
            # Format: IF (condition_tokens) THEN (then_tokens) ELSE (else_tokens)
            # The token value contains nested token lists
            cond_tokens, then_tokens, else_tokens = token.value
            
            # Evaluate condition (must produce exactly one value)
            cond_stack = stack.copy()
            cond_result = evaluate_rpn_internal(cond_tokens, yy, cond_stack)
            if cond_result is None:
                return None
            
            # In Python, any non-zero value is truthy
            if cond_result != 0:
                branch_result = evaluate_rpn_internal(then_tokens, yy, stack)
            else:
                branch_result = evaluate_rpn_internal(else_tokens, yy, stack)
            
            if branch_result is None:
                return None
            # Branch result should be the top of stack after evaluation
            # The branch replaces the condition value(s) with its own output
        elif ttype == 'IF_THEN':
            # Format: IF (condition_tokens) THEN (then_tokens)
            # If condition is true: execute then_branch
            # If condition is false: do NOTHING (no stack change)
            cond_tokens, then_tokens = token.value
            
            # Save current stack state
            saved_stack = stack.copy()
            
            # Evaluate condition on a copy to check validity
            cond_stack = stack.copy()
            cond_result = evaluate_rpn_internal(cond_tokens, yy, cond_stack)
            if cond_result is None:
                return None
            
            # In Python, any non-zero value is truthy
            if cond_result != 0:
                # Condition is true - execute then branch
                # Restore original stack before executing then branch
                branch_result = evaluate_rpn_internal(then_tokens, yy, stack)
                if branch_result is None:
                    return None
                # Then branch result is now on stack
            # else: condition is false - restore original stack (already there)
    
    if len(stack) != 1:
        return None
    
    return stack[0]

def evaluate_rpn_internal(tokens: List[Token], yy: int, stack: List[int]) -> Optional[int]:
    """
    Internal RPN evaluation that works on an existing stack.
    Returns the top of stack after evaluation, or None if failed.
    """
    yy_val, a, b = get_variables(yy)
    
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
            
            cond_result = evaluate_rpn_internal(cond_tokens, yy, stack)
            if cond_result is None:
                return None
            
            if cond_result != 0:
                branch_result = evaluate_rpn_internal(then_tokens, yy, stack)
            else:
                branch_result = evaluate_rpn_internal(else_tokens, yy, stack)
            
            if branch_result is None:
                return None
        elif token.token_type == TokenType.IF_THEN:
            cond_tokens, then_tokens = token.value
            
            saved_stack = stack.copy()
            cond_result = evaluate_rpn_internal(cond_tokens, yy, stack)
            if cond_result is None:
                return None
            
            if cond_result != 0:
                branch_result = evaluate_rpn_internal(then_tokens, yy, stack)
                if branch_result is None:
                    return None
            # else: false - stack already restored conceptually (we didn't modify it yet)
    
    if len(stack) < 1:
        return None
    
    return stack[-1]

def generate_simple_tokens():
    """Generate simple tokens (constants and variables)."""
    tokens = []
    
    # Constants 0..20
    for i in range(21):
        tokens.append(Token(TokenType.CONST, i))
    
    # Variables
    tokens.append(Token(TokenType.VAR_YY))
    tokens.append(Token(TokenType.VAR_A))
    tokens.append(Token(TokenType.VAR_B))
    
    return tokens

def generate_unary_tokens():
    """Generate unary minus token."""
    return [Token(TokenType.UNARY_MINUS)]

def generate_binary_ops():
    """Generate binary operation tokens."""
    ops = ['+', '-', '*', '//', '%']
    return [Token(TokenType.BINARY_OP, op) for op in ops]

def get_stack_effect(tokens: List[Token]) -> Optional[int]:
    """
    Calculate the net stack effect of a token sequence.
    Returns None if the sequence is invalid.
    Positive means values pushed, negative means values popped.
    """
    stack_size = 0
    min_stack_size = 0
    
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
            
            # Net effect: condition consumes nothing from outer, produces 1
            # Then branch replaces that 1 with then_effect values
            # So net effect is then_effect
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
            
            # IF-THEN: if true, pushes then_effect values; if false, no change (effect 0)
            # For validation, we consider the maximum possible effect
            # But actually we need to ensure the expression is valid in both cases
            # The net effect when true is then_effect, when false is 0
            # We'll track this specially - for now just check validity
            pass  # IF-THEN doesn't have a fixed stack effect
    
    return stack_size

def is_valid_rpn_sequence(tokens: List[Token], allow_multi_result: bool = False) -> bool:
    """
    Check if a token sequence can form a valid RPN expression.
    Uses stack-based validation.
    
    Args:
        tokens: List of tokens to validate
        allow_multi_result: If True, allows final stack size > 1 (used for IF branch validation)
    
    For simple expressions (no IF-THEN), final stack must be exactly 1.
    For IF-THEN expressions, final stack can be >= 0 depending on condition.
    For IF branches being validated internally, any stack size >= 0 is allowed.
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
            # IF THEN ELSE consumes nothing from outer stack, produces result of branches
            cond_tokens, then_tokens, else_tokens = token.value
            if not is_valid_rpn_sequence(cond_tokens):
                return False
            # Branches can have multi-result
            if not is_valid_rpn_sequence(then_tokens, allow_multi_result=True):
                return False
            if not is_valid_rpn_sequence(else_tokens, allow_multi_result=True):
                return False
            
            # Get stack effects of branches
            then_effect = get_stack_effect(then_tokens)
            else_effect = get_stack_effect(else_tokens)
            
            # Both branches must be valid and have same effect
            if then_effect is None or else_effect is None:
                return False
            if then_effect != else_effect:
                return False
            
            # Each branch must leave at least one value (for the overall expression to produce output)
            if then_effect < 1:
                return False
                
            stack_size += then_effect
        elif token.token_type == TokenType.IF_THEN:
            # IF THEN (without ELSE)
            cond_tokens, then_tokens = token.value
            if not is_valid_rpn_sequence(cond_tokens):
                return False
            # Then branch can have multi-result
            if not is_valid_rpn_sequence(then_tokens, allow_multi_result=True):
                return False
            
            # Condition must produce exactly one value
            cond_effect = get_stack_effect(cond_tokens)
            if cond_effect is None or cond_effect != 1:
                return False
            
            # Then branch can have any non-negative effect
            then_effect = get_stack_effect(then_tokens)
            if then_effect is None or then_effect < 0:
                return False
            
            # IF-THEN doesn't guarantee a fixed stack size since false case = no change
            # We don't add anything to stack_size here
            pass
    
    # For expressions without IF-THEN, must end with exactly 1 value (unless allow_multi_result)
    # For expressions with IF-THEN or IF-THEN-ELSE, we need special handling
    has_if_then = any(t.token_type == TokenType.IF_THEN for t in tokens)
    has_if_then_else = any(t.token_type == TokenType.IF_THEN_ELSE for t in tokens)
    
    if has_if_then or has_if_then_else:
        # IF expressions are valid if they don't underflow
        # The actual result depends on runtime condition
        return True
    elif allow_multi_result:
        # Allow any non-negative stack size
        return stack_size >= 0
    else:
        return stack_size == 1

def generate_rpn_expressions(num_tokens: int, use_if_then_else: bool = False):
    """
    Generate all valid RPN expressions with exactly num_tokens tokens.
    This is a recursive generator that builds expressions token by token.
    """
    if num_tokens == 0:
        return
    
    simple_tokens = generate_simple_tokens()
    unary_tokens = generate_unary_tokens()
    binary_ops = generate_binary_ops()
    
    if num_tokens == 1:
        # Only simple tokens can form a valid 1-token expression
        for token in simple_tokens:
            yield [token]
    elif num_tokens == 2:
        # Simple + unary minus
        for simple in simple_tokens:
            for unary in unary_tokens:
                yield [simple, unary]
    else:
        # For larger expressions, we need to build them recursively
        # An RPN expression is either:
        # 1. A simple token (base case)
        # 2. A unary operation applied to an expression
        # 3. A binary operation applied to two expressions
        # 4. An IF-THEN-ELSE structure
        
        # Case 1: Binary operation on two sub-expressions
        # E = E1 E2 OP where E1 has k tokens, E2 has (num_tokens - k - 1) tokens
        for k in range(1, num_tokens):
            remaining = num_tokens - k - 1
            if remaining < 1:
                continue
            
            for expr1 in generate_rpn_expressions(k, use_if_then_else=False):
                for expr2 in generate_rpn_expressions(remaining, use_if_then_else=False):
                    for op in binary_ops:
                        yield expr1 + expr2 + [op]
        
        # Case 2: Unary operation on an expression
        # E = E1 UNARY_MINUS where E1 has (num_tokens - 1) tokens
        if num_tokens > 1:
            for expr in generate_rpn_expressions(num_tokens - 1, use_if_then_else=False):
                for unary in unary_tokens:
                    yield expr + [unary]
        
        # Case 3: IF-THEN-ELSE (only if enabled and enough tokens)
        if use_if_then_else and num_tokens >= 4:
            # Minimum: IF(cond) THEN(val1) ELSE(val2) = at least 4 tokens for the structure
            # Actually more like: cond_tokens + then_tokens + else_tokens + IF_THEN_ELSE marker
            # For simplicity, we'll handle this separately
            pass

def generate_all_rpn_with_if(max_tokens: int):
    """
    Generate RPN expressions including IF-THEN-ELSE structures.
    Uses a different approach: generate base expressions first, then combine with IF.
    """
    simple_tokens = generate_simple_tokens()
    unary_tokens = generate_unary_tokens()
    binary_ops = generate_binary_ops()
    
    # Cache expressions by token count
    cache = {}
    
    def get_expressions(n: int, allow_if: bool) -> List[List[Token]]:
        if n in cache and cache[n][0] == allow_if:
            return cache[n][1]
        
        exprs = []
        
        if n == 1:
            for token in simple_tokens:
                exprs.append([token])
        elif n == 2:
            # Simple + unary
            for simple in simple_tokens:
                for unary in unary_tokens:
                    exprs.append([simple, unary])
            # Also check binary with constants (but need 3 tokens minimum for binary)
        else:
            # Binary operations
            for k in range(1, n):
                remaining = n - k - 1
                if remaining < 1:
                    continue
                
                exprs1 = get_expressions(k, allow_if)
                exprs2 = get_expressions(remaining, allow_if)
                
                for e1 in exprs1:
                    for e2 in exprs2:
                        for op in binary_ops:
                            exprs.append(e1 + e2 + [op])
            
            # Unary operations
            for expr in get_expressions(n - 1, allow_if):
                for unary in unary_tokens:
                    exprs.append(expr + [unary])
            
            # IF-THEN-ELSE structures
            if allow_if and n >= 5:  # Minimum: 1 cond + 1 then + 1 else + structure overhead
                # IF THEN ELSE takes 1 token itself, plus tokens for each branch
                # Total = cond_tokens + then_tokens + else_tokens + 1 (for IF token)
                # So: cond + then + else = n - 1
                for cond_size in range(1, n - 2):
                    for then_size in range(1, n - cond_size - 1):
                        else_size = n - 1 - cond_size - then_size
                        if else_size < 1:
                            continue
                        
                        cond_exprs = get_expressions(cond_size, False)  # No nesting for now
                        then_exprs = get_expressions(then_size, False)
                        else_exprs = get_expressions(else_size, False)
                        
                        for ce in cond_exprs:
                            for te in then_exprs:
                                for ee in else_exprs:
                                    if_token = Token(TokenType.IF_THEN_ELSE, (ce, te, ee))
                                    exprs.append([if_token])
            
            # IF-THEN (without ELSE) structures
            if allow_if and n >= 4:  # Minimum: 1 cond + 1 then + structure overhead
                # IF THEN takes 1 token itself, plus tokens for condition and then branch
                # Total = cond_tokens + then_tokens + 1 (for IF token)
                # So: cond + then = n - 1
                for cond_size in range(1, n - 1):
                    then_size = n - 1 - cond_size
                    if then_size < 1:
                        continue
                    
                    cond_exprs = get_expressions(cond_size, False)  # No nesting for now
                    then_exprs = get_expressions(then_size, False)
                    
                    for ce in cond_exprs:
                        for te in then_exprs:
                            if_token = Token(TokenType.IF_THEN, (ce, te))
                            exprs.append([if_token])
        
        if n not in cache or cache[n][0] != allow_if:
            cache[n] = (allow_if, exprs)
        
        return exprs
    
    for n in range(1, max_tokens + 1):
        allow_if = (n >= 5)
        exprs = get_expressions(n, allow_if)
        total_exprs = len(exprs)
        
        # Print header for this token count
        print(f"\nSearching {total_exprs:,} expressions with {n} token(s)...", end='', flush=True)
        
        for i, expr in enumerate(exprs, 1):
            # Update progress on same line
            print(f'\r  Progress: {i:,}/{total_exprs:,} ({100*i//total_exprs}%)', end='', flush=True)
            yield n, expr
        
        # Clear the progress line after completing this token count
        print('\r' + ' ' * 60 + '\r', end='', flush=True)

def check_expression(tokens: List[Token]) -> bool:
    """Check if expression matches target for all yy in 0..99.
    
    Uses two-phase verification:
    1. First check a few sample values (quick rejection)
    2. If samples pass, check all values 0..99
    """
    # Phase 1: Quick check with critical boundary values only
    critical_values = [0, 3, 4, 7, 8, 11, 15, 19, 20, 39, 40, 59, 60, 79, 80, 99]
    
    for yy in critical_values:
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        expected = target_function(yy)
        # Normalize result to be in range [0, 6]
        result_mod = result % 7
        if result_mod != expected:
            return False
    
    # Phase 2: Full check with all values 0..99
    for yy in range(100):
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        expected = target_function(yy)
        # Normalize result to be in range [0, 6]
        result_mod = result % 7
        if result_mod != expected:
            return False
    
    return True

def tokens_to_string(tokens: List[Token]) -> str:
    """Convert tokens to human-readable string."""
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

def main():
    print("Searching for RPN expressions equivalent to (yy + yy//4) % 7")
    print("=" * 70)
    
    found_solutions = []
    max_tokens = 10  # Search up to this many tokens
    min_solution_tokens = None  # Track minimum token count for found solutions
    
    start_time = time.time()
    
    for num_tokens, tokens in generate_all_rpn_with_if(max_tokens):
        # If we've found solutions and this is significantly larger, stop
        if min_solution_tokens is not None and num_tokens > min_solution_tokens + 2:
            break
        
        if check_expression(tokens):
            expr_str = tokens_to_string(tokens)
            found_solutions.append((num_tokens, expr_str, tokens))
            
            if min_solution_tokens is None:
                min_solution_tokens = num_tokens
            
            elapsed = time.time() - start_time
            print(f"\n✓ Found solution with {num_tokens} tokens (in {elapsed:.1f}s):")
            print(f"  {expr_str}")
            
            # Verify a few values
            print("  Verification:")
            for yy in [0, 1, 10, 25, 50, 99]:
                result = evaluate_rpn(tokens, yy) % 7
                expected = target_function(yy)
                print(f"    yy={yy:2d}: result={result}, expected={expected}, match={result==expected}")
            
            # Stop after finding first 10 solutions at minimum complexity
            if min_solution_tokens is not None and num_tokens == min_solution_tokens:
                if len([s for s in found_solutions if s[0] == min_solution_tokens]) >= 10:
                    break
    
    total_time = time.time() - start_time
    
    if not found_solutions:
        print("\nNo solutions found up to", max_tokens, "tokens.")
        print("Try increasing max_tokens or checking the search logic.")
    else:
        print("\n" + "=" * 70)
        print(f"Found {len(found_solutions)} solution(s) in {total_time:.1f} seconds")
        print("\nBest solutions (minimum tokens):")
        min_tokens = min(s[0] for s in found_solutions)
        best_solutions = [s for s in found_solutions if s[0] == min_tokens]
        for num_tok, expr_str, _ in best_solutions[:10]:  # Show up to 10 best
            print(f"  [{num_tok} tokens] {expr_str}")
        
        if len(best_solutions) > 10:
            print(f"  ... and {len(best_solutions) - 10} more solutions with {min_tokens} tokens")

if __name__ == "__main__":
    main()
