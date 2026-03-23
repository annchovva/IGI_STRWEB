"""
Purpose: Function for executing Task 5,
Lab 3 Task 5, Version 1.1,
Author: Gorbachova Anna,
Date: 21.03.2026.
"""

import services.validate_input as i
import services.list_logic as ls
from modules.menu_logic import menu_for_tasks

@menu_for_tasks
def task5():
    """Main business function for Task 5: Max element and Sum logic."""
    my_list = input_method()
    print_list(my_list)
    max_idx = ls.max_element(my_list)
    if max_idx is None:
        print("List is empty.")
        return
    print(f"Maximum element {my_list[max_idx]} with index {max_idx}")
    sum_after = ls.sum_after_positive(my_list) 
    if sum_after is None:
        print("There are no positive elements or list is empty.")
    else:
        print(f"Sum after positive: {sum_after}")

def input_method():
    """Selecting a method for entering the list (manual input or generator)."""
    size = i.get_int("List size: ", 1)
    print("1. Manual Input | 2. Generator")
    while True:
        m = i.get_int("Choice: ")
        if m == 1:
            return ls.input_list(size)
        elif m == 2:  
            return ls.list_generator(size)
        else:
            print("Enter choice! (1 or 2): ")
            continue

def print_list(lst):
    """Displaying the list."""
    print("\nList: ")
    formatted = [f"{x:g}" for x in lst] 
    print(f"[{', '.join(formatted)}]")
 