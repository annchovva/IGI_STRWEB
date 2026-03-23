"""
Purpose: Decorator for executing all individual tasks,
Lab 3, Version 1.1,
Author: Gorbachova Anna,
Date: 21.03.2026.
"""
import services.validate_input as input

def menu_for_tasks(func):
    """Decorator for re-executing the task."""
    def wrapper(*args, **kwargs):
        while True:
            print("1. Start")
            print("2. Exit")
            choice = input.get_int("Choose an option: ", 0)
            if choice == 1:
                func(*args, **kwargs)
            elif choice == 2:
                print("Exit program...")
                break
            else:
                print("Invalid choice, try again. ")
    return wrapper
    