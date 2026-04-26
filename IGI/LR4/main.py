"""
Program Purpose: Main entry point for LabWork 4.
Lab4, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import sys
from services.validators import get_integer_input
from task1.task1_main import run_task1
from task2.task2_main import run_task2
from task3.task3_main import run_task3
from task4.task4_main import run_task4
from task5.task5_main import run_task5
from task6.task6_main import run_task6

def main_menu():
    """Main menu of the application."""
    while True:
        print("\n" + "="*40)
        print("   LABORATORY WORK 4")
        print("   Developer: Gorbachova Anna")
        print("="*40)
        print("1. Task 1: School Workload")
        print("2. Task 2: Text analysis")
        print("3. Task 3: Math")
        print("4. Task 4.")
        print("5. Task 5.")
        print("6. Task 6.")
        print("0. Exit")
        print("="*40)

        choice = get_integer_input("Select task number: ", 0, 6)

        if choice == 1:
            run_task1()
        elif choice == 2:
            run_task2()
        elif choice == 3:
            run_task3()  
        elif choice == 4:
            run_task4()   
        elif choice == 5:
            run_task5() 
        elif choice == 6:
            run_task6()                        
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
