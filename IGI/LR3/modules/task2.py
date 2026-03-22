"""
Purpose: Function for executing Task 2
Lab 3 Task 2, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

import services.math_logic as calc
from modules.menu_logic import menu_for_tasks

@menu_for_tasks
def task2():
    """Main business function for Task 2: Calculating the average value until 0 is entered"""   
    average = calc.run_average()
    print(f"Average = {average}")