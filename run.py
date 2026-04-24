#!/usr/bin/env python3
"""
RPN Expression Search - Entry Point

This script serves as the main entry point for running the RPN expression search.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rpn_search.cli import main

if __name__ == "__main__":
    sys.exit(main())
