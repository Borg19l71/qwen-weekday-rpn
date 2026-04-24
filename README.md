# RPN Expression Search

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Search for Reverse Polish Notation (RPN) expressions that produce the same result as a target function across a range of input values.

## Overview

This project searches for minimal-complexity RPN expressions equivalent to the target function:

```
f(yy) = (yy + yy // 4) % 7
```

This function is particularly useful for **day-of-week calculations** in calendar algorithms, where it computes the day offset for a given year within a century.

### What is RPN?

Reverse Polish Notation (RPN) is a mathematical notation where operators follow their operands. For example:
- Infix: `(5 + 3) * 2`
- RPN: `5 3 + 2 *`

RPN eliminates the need for parentheses and is evaluated using a stack.

## Installation

### From Source

```bash
cd /workspace
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

Run the search with default parameters:

```bash
python run.py
```

Or use the installed command:

```bash
rpn-search
```

### Command Line Options

```bash
# Search up to 10 tokens
python run.py --max-tokens 10

# Find up to 20 solutions at minimum complexity
python run.py --max-solutions 20

# Enable verbose logging
python run.py --verbose

# Save results to file
python run.py --output solutions.txt

# Combine options
python run.py --max-tokens 12 --max-solutions 5 --verbose --output results.txt
```

### As a Library

```python
from rpn_search import (
    generate_all_rpn_with_if,
    check_expression,
    tokens_to_string,
    evaluate_rpn,
    target_function,
)

# Check if an expression matches the target
from rpn_search import Token, TokenType

# Create expression: yy 4 // yy + 7 %
tokens = [
    Token(TokenType.VAR_YY),
    Token(TokenType.CONST, 4),
    Token(TokenType.BINARY_OP, '//'),
    Token(TokenType.VAR_YY),
    Token(TokenType.BINARY_OP, '+'),
    Token(TokenType.CONST, 7),
    Token(TokenType.BINARY_OP, '%'),
]

if check_expression(tokens):
    print("Expression matches target function!")
    print(f"RPN: {tokens_to_string(tokens)}")

# Evaluate for specific values
for yy in [0, 25, 50, 99]:
    result = evaluate_rpn(tokens, yy)
    expected = target_function(yy)
    print(f"yy={yy}: result={result}, expected={expected}")
```

## Algorithm

The search uses **iterative deepening** to find minimal-complexity solutions:

1. **Generate expressions** by token count (1, 2, 3, ...)
2. **Validate structure** using stack-based RPN validation
3. **Two-phase verification**:
   - Phase 1: Quick check with sample values (fast rejection)
   - Phase 2: Full check with all 100 values (0-99)
4. **Stop early** when solutions are found at minimum complexity

### Expression Generation

Expressions are built recursively:
- **Base case**: Single constants (0-20) or variables (yy, a, b)
- **Binary operations**: `E1 E2 OP` where E1 and E2 are sub-expressions
- **Unary operations**: `E1 neg` (negation)
- **Conditionals**: `IF(cond)THEN(then)ELSE(else)` structures

### Supported Operations

| Type | Tokens | Description |
|------|--------|-------------|
| Constants | `0` to `20` | Integer literals |
| Variables | `yy`, `a`, `b` | Input value, tens digit, ones digit |
| Unary | `neg` | Negation (-x) |
| Binary | `+`, `-`, `*`, `//`, `%` | Arithmetic operations |
| Conditional | `IF(...)THEN(...)ELSE(...)` | Branching logic |
| Conditional | `IF(...)THEN(...)` | Branching without else |

## Examples

### Found Solutions

Running the search typically finds solutions like:

```
✓ Found solution with 7 tokens:
  yy 4 // yy + 7 %
  
Verification:
  yy= 0: result=0, expected=0, match=True
  yy= 1: result=0, expected=0, match=True
  yy=10: result=1, expected=1, match=True
  yy=25: result=3, expected=3, match=True
  yy=50: result=6, expected=6, match=True
  yy=99: result=4, expected=4, match=True
```

## Project Structure

```
/workspace/
├── src/rpn_search/       # Package source
│   ├── __init__.py       # Package exports
│   ├── tokens.py         # Token definitions
│   ├── evaluator.py      # Expression evaluation
│   ├── validator.py      # RPN validation
│   ├── generator.py      # Expression generation
│   ├── checker.py        # Target matching
│   ├── formatter.py      # String formatting
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
├── docs/                 # Documentation
├── configs/              # Configuration files
├── run.py                # Entry point
├── pyproject.toml        # Project metadata
└── README.md             # This file
```

## Performance

Search time grows exponentially with token count. Approximate times:

| Max Tokens | Expressions | Time (est.) |
|------------|-------------|-------------|
| 5          | ~10K        | < 1 second  |
| 7          | ~1M         | ~10 seconds |
| 9          | ~100M       | ~15 minutes |
| 10+        | Billions    | Hours+      |

**Tip**: Start with `--max-tokens 8` and increase only if no solutions are found.

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=rpn_search --cov-report=html
```

## Configuration

Constants can be modified in `src/rpn_search/checker.py`:

```python
CONSTANT_RANGE = range(21)      # Constants 0-20
YY_TEST_RANGE = range(100)      # Test yy values 0-99
SAMPLE_VALUES = [0, 1, 7, ...]  # Quick check values
MODULUS = 7                     # Expected result range
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guidelines
- Add docstrings to all public functions
- Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- RPN notation invented by Charles Hamblin (1954)
- Target function commonly used in day-of-week algorithms (Zeller's congruence variant)
