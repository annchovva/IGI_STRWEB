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

def run_task():
    """Main entry point for Task 1."""
    teachers_list = []
    
    csv_path = os.path.join("task1", "data.csv")
    pickle_path = os.path.join("task1", "data.pkl")

    while True:
        print("\n ---- TASK 1: SCHOOL WORKLOAD MANAGEMENT ----")
        print("| 1. Add new workload record                 |")
        print("| 2. Show all records                        |") 
        print("| 3. Show workload statistics (Max/Min/Total)|")
        print("| 4. Find workload by teacher name           |")
        print("| 5. Save data (CSV/Pickle)                  |")
        print("| 6. Load data (CSV/Pickle)                  |")
        print("| 0. Back to main menu                       |")
        print(" --------------------------------------------")

        choice = get_integer_input("Choose an option: ", 0)

        if choice == 1:
            name = get_string_input("Enter teacher name: ")
            s_class = get_class_input("Enter school class (e.g. 10A): ")
            hours = get_integer_input("Enter hours: ", 0)
            
            new_record = Teacher(name, s_class, hours)
            teachers_list.append(new_record)
            print("Record added successfully!")

        elif choice == 2:
            if not teachers_list:
                print("No records found.")
            else:
                print("\nAll Records:")
                for record in teachers_list:
                    print(record)
                print(f"Total objects created in this session: {Teacher.total_records}")

        elif choice == 3:
            if not teachers_list:
                print("List is empty.")
                continue
            
            calc = WorkloadCalculator(teachers_list)
            
            print("\nTotal workload per teacher:")
            workloads = calc.get_total_workload_per_teacher()
            for t_name, t_hours in workloads.items():
                print(f"- {t_name}: {t_hours} hours")

            max_t, max_h = calc.get_max_workload_teacher()
            min_t, min_h = calc.get_min_workload_teacher()
            print(f"\nHighest workload: {max_t} ({max_h} hours)")
            print(f"Lowest workload: {min_t} ({min_h} hours)")

        elif choice == 4:
            search_name = get_string_input("Enter teacher name to search: ")
            calc = WorkloadCalculator(teachers_list)
            h = calc.get_teacher_workload(search_name)
            print(f"Total workload for {search_name}: {h} hours.")

        elif choice == 5:
            print("Select format: 1. CSV  2. Pickle")
            fmt = get_integer_input("Choice: ", 1)
            serializer = CSVSerializer(csv_path) if fmt == 1 else PickleSerializer(pickle_path)
            serializer.save(teachers_list)
            print("Successful saving to a file!")

        elif choice == 6:
            print("Select format: 1. CSV  2. Pickle")
            fmt = get_integer_input("Choice: ", 1)
            serializer = CSVSerializer(csv_path) if fmt == 1 else PickleSerializer(pickle_path)
            teachers_list = serializer.load()
            print(f"Loaded {len(teachers_list)} records.")

        elif choice == 0:
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Try again.")