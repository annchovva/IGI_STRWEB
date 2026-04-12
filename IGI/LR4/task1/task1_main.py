"""
Program Purpose: Main entry point for Task1
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import sys
from models import Teacher, TeacherStatistics
from data_manager import CSVDataManager, PickleDataManager

def get_valid_input(prompt: str, type_func, min_val=None):
    """Generic input protection function."""
    while True:
        try:
            val = type_func(input(prompt))
            if min_val is not None and val < min_val:
                print(f"Value must be at least {min_val}")
                continue
            return val
        except ValueError:
            print("Invalid input format. Please try again.")

def main():
    """Main program loop."""
    teachers = [
        Teacher("Ivanov", 20.0, ["10A"]),
        Teacher("Petrova", 35.5, ["11B", "9A"])
    ]
    
    while True:
        print("\n--- TEACHER MANAGEMENT SYSTEM ---")
        print("1. Display All | 2. Find | 3. Max Load | 4. Min Load")
        print("5. Summary     | 6. Add  | 7. Save CSV  | 8. Load CSV")
        print("9. Save Pickle | 10. Load Pickle | 11. Sort | 12. Exit")
        
        choice = get_valid_input("Select (1-12): ", int, 1)
        stats = TeacherStatistics(teachers)

        try:
            if choice == 1:
                for t in teachers: print(t)
            
            elif choice == 2:
                name = input("Enter surname: ")
                print(stats.find_by_surname(name))
            
            elif choice == 3:
                print(f"Max load: {stats.get_max_load()}")
                
            elif choice == 4:
                print(f"Min load: {stats.get_min_load()}")
            
            elif choice == 5:
                res = stats.get_summary()
                print(f"Avg hours: {res['avg_hours']:.2f}, Total: {res['total_hours']}")
            
            elif choice == 6:
                s = input("Surname: ")
                h = get_valid_input("Hours: ", float, 0)
                teachers.append(Teacher(s, h))
            
            elif choice == 7:
                CSVDataManager(input("Filename: ")).save(teachers)
            
            elif choice == 8:
                teachers = CSVDataManager(input("Filename: ")).load()
            
            elif choice == 9:
                PickleDataManager(input("Filename: ")).save(teachers)
                
            elif choice == 10:
                teachers = PickleDataManager(input("Filename: ")).load()
            
            elif choice == 11:
                for t in stats.get_all_sorted(): print(t)
                
            elif choice == 12:
                print(f"Instances created: {Teacher.get_instance_count()}")
                break
                
        except (ValueError, FileNotFoundError, IOError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()            
