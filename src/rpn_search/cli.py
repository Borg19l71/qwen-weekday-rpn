#!/usr/bin/env python3
"""
RPN Expression Search - Command Line Interface

Searches for Reverse Polish Notation (RPN) expressions that produce the same
result as (yy + yy//4) % 7 for all yy in range 0..99.
"""

import argparse
import logging
import sys
from typing import List, Tuple, Optional

# Add src to path for imports
sys.path.insert(0, '/workspace/src')

from rpn_search import (
    generate_all_rpn_with_if,
    check_expression,
    tokens_to_string,
    evaluate_rpn,
    target_function,
)


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=level, format=format_str)


def verify_solution(tokens: List, sample_values: List[int] = None) -> None:
    """Print verification results for a solution."""
    if sample_values is None:
        sample_values = [0, 1, 10, 25, 50, 99]
    
    print("  Verification:")
    for yy in sample_values:
        result = evaluate_rpn(tokens, yy) % 7
        expected = target_function(yy)
        match = result == expected
        print(f"    yy={yy:2d}: result={result}, expected={expected}, match={match}")


def search_expressions(
    max_tokens: int,
    max_solutions: int = 10,
    verbose: bool = False
) -> List[Tuple[int, str, List]]:
    """
    Search for RPN expressions matching the target function.
    
    Args:
        max_tokens: Maximum number of tokens to search
        max_solutions: Maximum number of solutions to find at minimum complexity
        verbose: Enable verbose logging
        
    Returns:
        List of found solutions as (num_tokens, expression_string, tokens)
    """
    logger = logging.getLogger(__name__)
    found_solutions = []
    min_solution_tokens = None
    
    logger.info(f"Starting search with max_tokens={max_tokens}")
    
    for num_tokens, tokens in generate_all_rpn_with_if(max_tokens):
        # If we've found solutions and this is significantly larger, stop
        if min_solution_tokens is not None and num_tokens > min_solution_tokens + 2:
            logger.info(f"Stopping search at {num_tokens} tokens (found solutions at {min_solution_tokens})")
            break
        
        if verbose and num_tokens % 5 == 0:
            logger.debug(f"Checking expressions with {num_tokens} tokens...")
        
        if check_expression(tokens):
            expr_str = tokens_to_string(tokens)
            found_solutions.append((num_tokens, expr_str, tokens))
            
            if min_solution_tokens is None:
                min_solution_tokens = num_tokens
                logger.info(f"First solution found with {num_tokens} tokens!")
            
            print(f"\n✓ Found solution with {num_tokens} tokens:")
            print(f"  {expr_str}")
            
            verify_solution(tokens)
            
            # Stop after finding enough solutions at minimum complexity
            if num_tokens == min_solution_tokens:
                count_at_min = len([s for s in found_solutions if s[0] == min_solution_tokens])
                if count_at_min >= max_solutions:
                    logger.info(f"Found {max_solutions} solutions at minimum complexity, stopping")
                    break
    
    return found_solutions


def print_summary(found_solutions: List[Tuple[int, str, List]]) -> None:
    """Print a summary of found solutions."""
    if not found_solutions:
        print("\nNo solutions found.")
        return
    
    print("\n" + "=" * 70)
    print(f"Found {len(found_solutions)} solution(s)")
    
    min_tokens = min(s[0] for s in found_solutions)
    best_solutions = [s for s in found_solutions if s[0] == min_tokens]
    
    print(f"\nBest solutions (minimum {min_tokens} tokens):")
    for num_tok, expr_str, _ in best_solutions[:10]:
        print(f"  [{num_tok} tokens] {expr_str}")
    
    if len(best_solutions) > 10:
        print(f"  ... and {len(best_solutions) - 10} more solutions with {min_tokens} tokens")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Search for RPN expressions equivalent to (yy + yy//4) % 7',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--max-tokens', 
        type=int, 
        default=10,
        help='Maximum number of tokens to search'
    )
    parser.add_argument(
        '--max-solutions',
        type=int,
        default=10,
        help='Maximum number of solutions to find at minimum complexity'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file to save solutions (optional)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    print("Searching for RPN expressions equivalent to (yy + yy//4) % 7")
    print("=" * 70)
    
    found_solutions = search_expressions(
        max_tokens=args.max_tokens,
        max_solutions=args.max_solutions,
        verbose=args.verbose
    )
    
    print_summary(found_solutions)
    
    # Save to file if requested
    if args.output and found_solutions:
        with open(args.output, 'w') as f:
            f.write(f"Found {len(found_solutions)} solution(s)\n\n")
            min_tokens = min(s[0] for s in found_solutions)
            for num_tok, expr_str, _ in found_solutions:
                marker = " [BEST]" if num_tok == min_tokens else ""
                f.write(f"[{num_tok} tokens]{marker} {expr_str}\n")
        print(f"\nSolutions saved to {args.output}")
    
    return 0 if found_solutions else 1


if __name__ == "__main__":
    sys.exit(main())
