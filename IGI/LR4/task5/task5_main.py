"""
Program Purpose: Testing NumPy matrix processing tools.
Lab4, Task5, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

from pathlib import Path
from services.validators import get_integer_input, get_optional_int_input
from task5.matrix_tools import MatrixProcessor

def run_task5():
    """Main entry point."""
    while True:
        print("\n" + "=" * 50)
        print("TASK 5: NUMPY MATRIX ANALYSIS")
        print("=" * 50)

        try:
            rows = get_integer_input("Enter number of rows n: ", 1)
            cols = get_integer_input("Enter number of columns m: ", 1)
            low = get_integer_input("Enter minimum random value: ")
            high = get_integer_input("Enter maximum random value: ", low)

            seed = get_optional_int_input("Enter random seed (or press Enter): ")

            processor = MatrixProcessor(rows, cols, low, high, seed)
            processor.create_matrix()

            print("\nGenerated matrix:")
            print(processor.matrix)

            print("\nAdditional info:")
            print(processor.build_report())

        except (TypeError, ValueError) as error:
            print(f"Input error: {error}")
        except Exception as error:
            print(f"Unexpected error: {error}")

        repeat = input("\nRun Task 5 again? (y/n): ").strip().lower()
        if repeat != "y":
            print("Exiting Task 5...")
            break

