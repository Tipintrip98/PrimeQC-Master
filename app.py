"""
PrimeQC Master - Application Launcher.
Root entry point for standalone packaging and local execution.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.main import main

if __name__ == "__main__":
    main()
