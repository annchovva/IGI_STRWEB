"""
Purpose: Function for executing Task 1
Lab 3 Task 1, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

import services.math_logic as calc
import services.validate_input as input
from modules.menu_logic import menu_for_tasks

def print_table(all_data):
    """Print the collected results in table"""
    print("\n" + "="*80)
    print(f"| {'x':^12} | {'n':^6} | {'F(x)':^16} | {'Math F(x)':^16} | {'eps':^10} |")
    print("-"*80)

    for row in all_data:
        print(f"| {row[0]:12.4f} | {row[1]:6d} | {row[2]:16.8f} | {row[3]:16.8f} | {row[4]:10.1e} |")
        print("="*80 + "\n")

@menu_for_tasks
def task1():
    """Main business function for Task 2: Calculating sin(x) when entering x and epsilon""" 
    x = input.get_float("Please enter x = ")
    epsilon = input.get_float("Please enter eps = ", 0.1)
    res = calc.calculate_sin_taylor(x, epsilon)
    results_to_show = [res]
    print_table(results_to_show)      




