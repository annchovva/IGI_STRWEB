"""
Purpose: Function for executing Task 3
Lab 3 Task 3, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

import services.text_logic as text
from modules.menu_logic import menu_for_tasks

@menu_for_tasks
def task3():
    """Main business function for Task 3: Analysis of the string entered by the user"""        
    user_input = input("Input string: ")
    print(f"Non-space count: {text.count_non_whilespace_chars(user_input)}")


