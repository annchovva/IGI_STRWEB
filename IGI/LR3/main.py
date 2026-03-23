"""
Purpose: Function for executing program,
Lab 3, Version 1.1,
Author: Gorbachova Anna,
Date: 21.03.2026.
"""
import services.validate_input as input
import modules.task1 as t1
import modules.task2 as t2
import modules.task3 as t3
import modules.task4 as t4
import modules.task5 as t5

def main():
    """Main application loop."""
    while True:
        print("-------Lab 3-------")
        print("| 1. Task1        |")
        print("| 2. Task2        |")
        print("| 3. Task3        |")
        print("| 4. Task4        |")
        print("| 5. Task5        |")
        print("| 0. Exit program |")
        print("-------------------")

        choice = input.get_int("\n Choose an option: ", -1)

        if choice == 1:
            t1.task1()     
        elif choice == 2:
            t2.task2() 
        elif choice == 3:
            t3.task3() 
        elif choice == 4:
            t4.task4() 
        elif choice == 5:
            t5.task5() 
        elif choice == 0:
            print("Exit program...")
            break
        else:
            print("Invalid choice, try again.")

main()