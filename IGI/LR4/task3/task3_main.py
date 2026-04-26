"""
Program Purpose: Orchestrator for Task 3 execution.
Lab Number: 4
Task Number: 3
Program Version: 1.0
Developer: Gorbachova Anna 453504
Date: 12.04.2026
"""

from .models import TaylorCalculator, SequenceAnalyzer
from .visualizer import ChartManager
from services.validators import get_string_input, get_float_input

def run_task3():
    """Main entry point for Task 3."""
    while True:
        print("\n--- TASK 3: MATHEMATICAL ANALYSIS ---")
        
        try:
            # Inputs
            x_start = get_float_input("Enter Start X: ")
            x_end = get_float_input("Enter End X: ", x_start)
            step = get_float_input("Enter Step: ", 0, x_end - x_start)
            epsilon = get_float_input("Enter Epsilon (0 < eps <= 0.1): ")

            calc = TaylorCalculator(epsilon)
            print(calc.get_info()) # Mixin call

            results = []
            current_x = x_start
            while current_x <= x_end:
                results.append(calc.compute(current_x))
                current_x += step

            print("\n" + "="*80)
            print(f"| {'X':^12} | {'N':^6} | {'Taylor F(x)':^16} | {'Math F(x)':^16} | {'eps':^10} |")
            print("-" * 80)
            for r in results:
                print(f"| {r[0]:12.4f} | {r[1]:6d} | {r[2]:16.8f} | {r[3]:16.8f} | {epsilon:10.1e} |")
            print("=" * 80)

            y_data = [r[2] for r in results]
            analyzer = SequenceAnalyzer(y_data)
            print(analyzer) 

            x_coords = [r[0] for r in results]
            y_math = [r[3] for r in results]
            ChartManager.plot_taylor_results(x_coords, y_data, y_math)

        except ValueError as e:
            print(f"Calculation Error: {e}")
        except Exception as e:
            print(f"Critical Error: {e}")

        repeat = get_string_input("Execute Task 3 again? (y/n): ").lower()
        if repeat != 'y':
            break
