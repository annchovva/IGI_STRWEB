"""
Program Purpose: Main entry point for Task1
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""
import os
from .models import Teacher, WorkloadCalculator
from .serializers import CSVSerializer, PickleSerializer
from services.validators import get_string_input, get_integer_input, get_class_input

def print_all_records(records):
    """Print all teacher records."""
    if not records:
        print("No records in memory.")
        return

    print("\nTeacher records:")
    for record in records:
        print(record)

def print_statistics(records):
    """Print workload statistics."""
    if not records:
        print("No data for statistics.")
        return

    calc = WorkloadCalculator(records)
    totals = calc.total_by_teacher()

    print("\nTotal workload by teacher:")
    for name, hours in totals.items():
        print(f"{name}: {hours} hours")

    max_name, max_hours = calc.max_teacher()
    min_name, min_hours = calc.min_teacher()

    print(f"\nHighest workload: {max_name} ({max_hours} hours)")
    print(f"Lowest workload: {min_name} ({min_hours} hours)")  

def print_sorted_data(records):
    """Show sorting options and print sorted records."""
    if not records:
        print("No records to sort.")
        return

    calc = WorkloadCalculator(records)

    print("\nSorting options:")
    print("1. Sort by teacher name")
    print("2. Sort by hours")
    choice = get_integer_input("Choose option: ", 1, 2)

    if choice == 1:
        sorted_records = calc.sort_by_name()
    else:
        sorted_records = calc.sort_by_hours()

    print("\nSorted records:")
    for record in sorted_records:
        print(record)    

def choose_handler():
    """Let the user choose the file format."""
    print("\nChoose file format:")
    print("1. CSV")
    print("2. Pickle")
    choice = get_integer_input("Your choice: ", 1, 2)

    if choice == 1:
        return CSVSerializer()
    return PickleSerializer()              

def run_task1():
    """Main entry point for Task 1."""  

    initial_data = {
        "Ivanov": [("5A", 10), ("6B", 8)],
        "Petrov": [("7A", 12), ("8B", 6)],
        "Sidorova": [("9A", 14)]
    }

    records = []
    for teacher_name, items in initial_data.items():
        for school_class, hours in items:
            records.append(Teacher(teacher_name, school_class, hours))

    while True:
        print("\n ---- TASK 1: SCHOOL WORKLOAD MANAGEMENT ----")
        print("| 1. Add new workload record                 |")
        print("| 2. Show all records                        |") 
        print("| 3. Show workload statistics (Max/Min/Total)|")
        print("| 4. Find workload by teacher name           |")
        print("| 5. Sort data                               |")
        print("| 6. Save data (CSV/Pickle)                  |")
        print("| 7. Load data (CSV/Pickle)                  |")
        print("| 0. Back to main menu                       |")
        print(" --------------------------------------------")

        choice = get_integer_input("Choose an option: ", 0, 7)

        if choice == 1:
            try: 
                name = get_string_input("Enter teacher name: ")
                school_class = get_class_input("Enter class (for example 10A): ")
                hours = get_integer_input("Enter hours: ", 0)

                records.append(Teacher(name, school_class, hours))
                print("Record added successfully.")
            except (TypeError, ValueError) as error:
                print(f"Error: {error}")    

        elif choice == 2:
            print_all_records(records)

        elif choice == 3:
            print_statistics(records)

        elif choice == 4: 
            search_name = get_string_input("Enter teacher name to search: ")
            if search_name.lower() in initial_data.keys().lower():
                calc = WorkloadCalculator(records)
                h = calc.teacher_workload(search_name)    
                print(f"Total workload for {search_name}: {h} hours.")
            else:
                print(f"Teacher {search_name} not found.")    
                

        elif choice == 5:
            print_sorted_data(records)

        elif choice == 6:
            try:
                handler = choose_handler()
                handler.save(records)
                print("Data saved successfully.")
            except OSError as error:
                print(error)

        elif choice == 7:
            try:
                handler = choose_handler()
                records = handler.load()
                print(f"Loaded {len(records)} records.")
            except ValueError as error:
                print(error)    


        elif choice == 0:
            print("Returning to main menu...")
            break