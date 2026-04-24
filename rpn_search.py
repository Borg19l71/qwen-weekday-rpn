#!/usr/bin/env python3
"""
RPN Expression Search Program
Searches for RPN expressions that produce the same result as (yy + yy//4) % 7
for all yy in range 0..99, using increasing complexity (number of tokens).
Optimized for performance with caching, early termination, and efficient data structures.
"""

from itertools import product
from typing import List, Tuple, Optional, Union, Callable
import sys
import time
from functools import lru_cache

# Target function: (yy + yy//4) % 7 - precompute all values
TARGET_VALUES = tuple((yy + yy // 4) % 7 for yy in range(100))

# Critical test values for early rejection (indices into TARGET_VALUES)
CRITICAL_INDICES = (0, 3, 4, 7, 8, 11, 15, 19, 20, 39, 40, 59, 60, 79, 80, 99)

# Precompute variable values for all yy
YY_VALUES = tuple(range(100))
A_VALUES = tuple(yy // 10 for yy in range(100))
B_VALUES = tuple(yy % 10 for yy in range(100))

# Token types - use integers for faster comparison
CONST = 0
VAR_YY = 1
VAR_A = 2
VAR_B = 3
UNARY_MINUS = 4
BINARY_OP = 5
IF_THEN_ELSE = 6
IF_THEN = 7

# Binary operations as integer codes for faster dispatch
OP_ADD = 0
OP_SUB = 1
OP_MUL = 2
OP_DIV = 3
OP_MOD = 4

def get_variables(yy: int) -> Tuple[int, int, int]:
    """Extract yy, a, b from yy value."""
    return YY_VALUES[yy], A_VALUES[yy], B_VALUES[yy]

# Use simple tuple-based tokens for performance: (type, value)
# This avoids object overhead during evaluation

def create_token(token_type: int, value=None):
    """Create a token as a simple tuple."""
    return (token_type, value)

def token_type(token):
    """Get token type."""
    return token[0]

def token_value(token):
    """Get token value."""
    return token[1]

def evaluate_rpn(tokens, yy: int) -> Optional[int]:
    """
    Evaluate RPN expression for given yy value using tuple-based tokens.
    Returns None if evaluation fails (stack underflow, division by zero, etc.)
    or if final stack doesn't have exactly one value.
    Optimized for speed with direct tuple unpacking and precomputed values.
    """
    stack = []
    yy_val = YY_VALUES[yy]
    a = A_VALUES[yy]
    b = B_VALUES[yy]
    
    for ttype, tval in tokens:
        if ttype == CONST:
            stack.append(tval)
        elif ttype == VAR_YY:
            stack.append(yy_val)
        elif ttype == VAR_A:
            stack.append(a)
        elif ttype == VAR_B:
            stack.append(b)
        elif ttype == UNARY_MINUS:
            if not stack:
                return None
            stack[-1] = -stack[-1]
        elif ttype == BINARY_OP:
            if len(stack) < 2:
                return None
            b_val = stack.pop()
            a_val = stack.pop()
            
            if tval == OP_ADD:
                stack.append(a_val + b_val)
            elif tval == OP_SUB:
                stack.append(a_val - b_val)
            elif tval == OP_MUL:
                stack.append(a_val * b_val)
            elif tval == OP_DIV:
                if b_val == 0:
                    return None
                stack.append(a_val // b_val)
            elif tval == OP_MOD:
                if b_val == 0:
                    return None
                stack.append(a_val % b_val)
        elif ttype == IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = tval
            cond_result = _eval_fast(cond_tokens, yy, stack.copy())
            if cond_result is None:
                return None
            if cond_result != 0:
                result = _eval_fast(then_tokens, yy, stack)
            else:
                result = _eval_fast(else_tokens, yy, stack)
            if result is None:
                return None
        elif ttype == IF_THEN:
            cond_tokens, then_tokens = tval
            cond_result = _eval_fast(cond_tokens, yy, stack.copy())
            if cond_result is None:
                return None
            if cond_result != 0:
                result = _eval_fast(then_tokens, yy, stack)
                if result is None:
                    return None
    
    if len(stack) != 1:
        return None
    
    return stack[0]

def _eval_fast(tokens, yy: int, stack: list) -> Optional[int]:
    """
    Fast internal RPN evaluation that works on an existing stack.
    Uses tuple-based tokens and precomputed variable values.
    Returns the top of stack after evaluation, or None if failed.
    """
    yy_val = YY_VALUES[yy]
    a = A_VALUES[yy]
    b = B_VALUES[yy]
    
    for ttype, tval in tokens:
        if ttype == CONST:
            stack.append(tval)
        elif ttype == VAR_YY:
            stack.append(yy_val)
        elif ttype == VAR_A:
            stack.append(a)
        elif ttype == VAR_B:
            stack.append(b)
        elif ttype == UNARY_MINUS:
            if not stack:
                return None
            stack.append(-stack.pop())
        elif ttype == BINARY_OP:
            if len(stack) < 2:
                return None
            b_val = stack.pop()
            a_val = stack.pop()
            
            if tval == OP_ADD:
                stack.append(a_val + b_val)
            elif tval == OP_SUB:
                stack.append(a_val - b_val)
            elif tval == OP_MUL:
                stack.append(a_val * b_val)
            elif tval == OP_DIV:
                if b_val == 0:
                    return None
                stack.append(a_val // b_val)
            elif tval == OP_MOD:
                if b_val == 0:
                    return None
                stack.append(a_val % b_val)
        elif ttype == IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = tval
            cond_result = _eval_fast(cond_tokens, yy, stack)
            if cond_result is None:
                return None
            if cond_result != 0:
                result = _eval_fast(then_tokens, yy, stack)
            else:
                result = _eval_fast(else_tokens, yy, stack)
            if result is None:
                return None
        elif ttype == IF_THEN:
            cond_tokens, then_tokens = tval
            saved_len = len(stack)
            cond_result = _eval_fast(cond_tokens, yy, stack)
            if cond_result is None:
                return None
            if cond_result != 0:
                result = _eval_fast(then_tokens, yy, stack)
                if result is None:
                    return None
            else:
                # Restore stack to state before condition evaluation
                while len(stack) > saved_len:
                    stack.pop()
    
    if not stack:
        return None
    
    return stack[-1]

def generate_simple_tokens():
    """Generate simple tokens (constants and variables) as tuples."""
    # Constants 0..20
    tokens = [(CONST, i) for i in range(21)]
    # Variables
    tokens.append((VAR_YY, None))
    tokens.append((VAR_A, None))
    tokens.append((VAR_B, None))
    return tokens

def generate_unary_tokens():
    """Generate unary minus token as tuple."""
    return [(UNARY_MINUS, None)]

def generate_binary_ops():
    """Generate binary operation tokens as tuples with integer codes."""
    return [(BINARY_OP, op) for op in range(5)]  # OP_ADD=0, OP_SUB=1, OP_MUL=2, OP_DIV=3, OP_MOD=4

def get_stack_effect(tokens) -> Optional[int]:
    """
    Calculate the net stack effect of a token sequence.
    Returns None if the sequence is invalid.
    Positive means values pushed, negative means values popped.
    Uses tuple-based tokens for performance.
    """
    stack_size = 0
    
    for ttype, tval in tokens:
        if ttype in (CONST, VAR_YY, VAR_A, VAR_B):
            stack_size += 1
        elif ttype == UNARY_MINUS:
            if stack_size < 1:
                return None
        elif ttype == BINARY_OP:
            if stack_size < 2:
                return None
            stack_size -= 1
        elif ttype == IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = tval
            cond_effect = get_stack_effect(cond_tokens)
            then_effect = get_stack_effect(then_tokens)
            else_effect = get_stack_effect(else_tokens)
            
            if cond_effect is None or then_effect is None or else_effect is None:
                return None
            if cond_effect != 1:
                return None
            if then_effect != else_effect:
                return None
            stack_size += then_effect
        elif ttype == IF_THEN:
            cond_tokens, then_tokens = tval
            cond_effect = get_stack_effect(cond_tokens)
            then_effect = get_stack_effect(then_tokens)
            
            if cond_effect is None or then_effect is None:
                return None
            if cond_effect != 1:
                return None
    
    return stack_size

def is_valid_rpn_sequence(tokens, allow_multi_result: bool = False) -> bool:
    """
    Check if a token sequence can form a valid RPN expression.
    Uses stack-based validation with tuple-based tokens.
    """
    stack_size = 0
    
    for ttype, tval in tokens:
        if ttype in (CONST, VAR_YY, VAR_A, VAR_B):
            stack_size += 1
        elif ttype == UNARY_MINUS:
            if stack_size < 1:
                return False
        elif ttype == BINARY_OP:
            if stack_size < 2:
                return False
            stack_size -= 1
        elif ttype == IF_THEN_ELSE:
            cond_tokens, then_tokens, else_tokens = tval
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
        elif ttype == IF_THEN:
            cond_tokens, then_tokens = tval
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
    
    has_if_then = any(t[0] == IF_THEN for t in tokens)
    has_if_then_else = any(t[0] == IF_THEN_ELSE for t in tokens)
    
    if has_if_then or has_if_then_else:
        return True
    elif allow_multi_result:
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
    Uses iterative generation to avoid memory issues.
    Optimized with precomputed token lists and efficient evaluation.
    """
    simple_tokens = generate_simple_tokens()
    unary_tokens = generate_unary_tokens()
    binary_ops = generate_binary_ops()
    
    # Cache expressions by token count - but clear older levels to save memory
    cache = {}
    
    def get_expressions(n: int, allow_if: bool):
        key = (n, allow_if)
        if key in cache:
            return cache[key]
        
        exprs = []
        
        if n == 1:
            exprs = [[t] for t in simple_tokens]
        elif n == 2:
            exprs = [[simple, unary] for simple in simple_tokens for unary in unary_tokens]
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
            if allow_if and n >= 5:
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
                                    exprs.append([(IF_THEN_ELSE, (ce, te, ee))])
            
            # IF-THEN (without ELSE) structures
            if allow_if and n >= 4:
                for cond_size in range(1, n - 1):
                    then_size = n - 1 - cond_size
                    if then_size < 1:
                        continue
                    
                    cond_exprs = get_expressions(cond_size, False)
                    then_exprs = get_expressions(then_size, False)
                    
                    for ce in cond_exprs:
                        for te in then_exprs:
                            exprs.append([(IF_THEN, (ce, te))])
        
        cache[key] = exprs
        return exprs
    
    for n in range(1, max_tokens + 1):
        allow_if = (n >= 5)
        exprs = get_expressions(n, allow_if)
        total_exprs = len(exprs)
        
        print(f"\nSearching {total_exprs:,} expressions with {n} token(s)...", end='', flush=True)
        
        for i, expr in enumerate(exprs, 1):
            print(f'\r  Progress: {i:,}/{total_exprs:,} ({100*i//total_exprs}%)', end='', flush=True)
            yield n, expr
        
        # Clear cache for this level to free memory (keep only current and next level)
        old_key = (n, False)
        if old_key in cache:
            del cache[old_key]
        old_key = (n, True)
        if old_key in cache:
            del cache[old_key]
        
        print('\r' + ' ' * 60 + '\r', end='', flush=True)

def check_expression(tokens) -> bool:
    """Check if expression matches target for all yy in 0..99.
    
    Uses two-phase verification with precomputed target values:
    1. First check critical boundary values (quick rejection)
    2. If samples pass, check all values 0..99
    """
    # Phase 1: Quick check with critical boundary values
    for yy in CRITICAL_INDICES:
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        if (result % 7) != TARGET_VALUES[yy]:
            return False
    
    # Phase 2: Full check with all values 0..99
    for yy in YY_VALUES:
        result = evaluate_rpn(tokens, yy)
        if result is None:
            return False
        if (result % 7) != TARGET_VALUES[yy]:
            return False
    
    return True

def tokens_to_string(tokens) -> str:
    """Convert tokens to human-readable string."""
    op_names = ['+', '-', '*', '//', '%']
    parts = []
    for ttype, tval in tokens:
        if ttype == CONST:
            parts.append(str(tval))
        elif ttype == VAR_YY:
            parts.append('yy')
        elif ttype == VAR_A:
            parts.append('a')
        elif ttype == VAR_B:
            parts.append('b')
        elif ttype == UNARY_MINUS:
            parts.append('neg')
        elif ttype == BINARY_OP:
            parts.append(op_names[tval])
        elif ttype == IF_THEN_ELSE:
            cond, then_b, else_b = tval
            parts.append(f'IF({tokens_to_string(cond)})THEN({tokens_to_string(then_b)})ELSE({tokens_to_string(else_b)})')
        elif ttype == IF_THEN:
            cond, then_b = tval
            parts.append(f'IF({tokens_to_string(cond)})THEN({tokens_to_string(then_b)})')
    return ' '.join(parts)

def main():
    print("Searching for RPN expressions equivalent to (yy + yy//4) % 7")
    print("=" * 70)
    
    found_solutions = []
    max_tokens = 10
    min_solution_tokens = None
    
    start_time = time.time()
    
    for num_tokens, tokens in generate_all_rpn_with_if(max_tokens):
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
            
            # Verify a few values using precomputed target values
            print("  Verification:")
            for yy in [0, 1, 10, 25, 50, 99]:
                result = evaluate_rpn(tokens, yy) % 7
                expected = TARGET_VALUES[yy]
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
        for num_tok, expr_str, _ in best_solutions[:10]:
            print(f"  [{num_tok} tokens] {expr_str}")
        
        if len(best_solutions) > 10:
            print(f"  ... and {len(best_solutions) - 10} more solutions with {min_tokens} tokens")

if __name__ == "__main__":
    main()
