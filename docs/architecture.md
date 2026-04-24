# RPN Search Architecture

## Overview

The RPN Search project is structured as a modular Python package that searches for Reverse Polish Notation (RPN) expressions matching a target function.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                        (cli.py)                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Generator   │   │    Checker    │   │   Formatter   │
│  (generator)  │──▶│   (checker)   │──▶│  (formatter)  │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   Validator   │   │   Evaluator   │
│  (validator)  │   │  (evaluator)  │
└───────┬───────┘   └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
         ┌───────────────┐
         │    Tokens     │
         │   (tokens)    │
         └───────────────┘
```

## Module Responsibilities

### `tokens.py`
- Defines `TokenType` enumeration
- Implements `Token` dataclass
- Provides token caching (Flyweight pattern) for efficiency

### `evaluator.py`
- Core RPN expression evaluation logic
- Unified evaluation with optional initial stack
- Handles all token types: constants, variables, operators, conditionals
- Error handling for stack underflow and division by zero

### `validator.py`
- Stack-based RPN validation
- Stack effect calculation
- Structural correctness checking

### `generator.py`
- Recursive expression generation
- Caching for performance (memoization)
- Supports binary ops, unary ops, and IF-THEN-ELSE structures
- Yields expressions in increasing complexity order

### `checker.py`
- Target function definition
- Two-phase verification (sample + full)
- Configuration constants

### `formatter.py`
- Human-readable string conversion
- Recursive formatting for nested structures

### `cli.py`
- Command-line argument parsing
- Search orchestration
- Progress reporting and output formatting

## Data Flow

1. **Generation**: `generate_all_rpn_with_if(max_tokens)` yields (count, tokens)
2. **Validation**: Expressions are structurally valid by construction
3. **Checking**: `check_expression(tokens)` verifies against target function
4. **Formatting**: `tokens_to_string(tokens)` creates readable output

## Design Decisions

### 1. Unified Evaluation Function
**Decision**: Single `_evaluate_rpn_core()` function with optional initial stack

**Rationale**: Eliminates ~90% code duplication between `evaluate_rpn()` and `evaluate_rpn_internal()`

### 2. Token Caching (Flyweight Pattern)
**Decision**: Pre-create and reuse common tokens

**Rationale**: Reduces memory allocation during massive expression generation

### 3. Two-Phase Verification
**Decision**: Quick sample check before full verification

**Rationale**: Fast rejection of non-matching expressions saves computation

### 4. Iterative Deepening
**Decision**: Generate expressions by increasing token count

**Rationale**: Finds minimal-complexity solutions first

### 5. Generator Pattern
**Decision**: Use generators instead of returning lists

**Rationale**: Memory efficient for large search spaces

## Extension Points

### Adding New Token Types
1. Add to `TokenType` class
2. Update `evaluate_rpn_core()` handling
3. Update `get_stack_effect()` 
4. Update `is_valid_rpn_sequence()`
5. Update `tokens_to_string()`

### Adding New Operations
1. Add operator to relevant token generation
2. Implement operation in evaluator
3. Define stack effect

### Custom Target Functions
Modify `checker.py`:
```python
def target_function(yy: int) -> int:
    return your_custom_formula(yy)
```

Update configuration constants as needed.

## Performance Considerations

### Time Complexity
- Expression generation: O(k^n) where k = avg branching factor, n = token count
- Evaluation: O(n) per expression per yy value
- Overall: O(k^n * 100) for full verification

### Space Complexity
- Cache: O(total unique expressions by token count)
- Per-expression: O(n) for token list

### Optimizations Applied
1. Memoization in generator
2. Token flyweight caching
3. Early termination on solution found
4. Two-phase verification

## Testing Strategy

- Unit tests for each module
- Property-based testing opportunities (Hypothesis)
- Integration tests for full search pipeline
- Performance benchmarks for regression detection
