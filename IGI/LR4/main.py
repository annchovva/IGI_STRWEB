"""
Program Purpose: Main entry point for LabWork 4.
Lab4, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import sys
from services.validators import get_integer_input
from task1.task1_main import run_task

def main_menu():
    """Main menu of the application."""
    while True:
        print("\n" + "="*40)
        print("   LABORATORY WORK №4: OBJECT-ORIENTED PROGRAMMING")
        print("   Developer: Gorbachova Anna")
        print("="*40)
        print("1. Task 1: School Workload (Models, Serializers, OOP)")
        print("2. Task 2: (To be implemented...)")
        print("0. Exit")
        print("="*40)

        choice = get_integer_input("Select task number: ", 0, 2)

        if choice == 1:
            run_task()
        elif choice == 2:
            print("Task 2 is not implemented yet. Come back later!")
        elif choice == 0:
            print("Exiting the program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"An unexpected error occurred in the main module: {e}")
