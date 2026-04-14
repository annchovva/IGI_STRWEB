"""
Program Purpose: Define classes for teacher data management and statistics
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

class ConsoleLoggerMixin:
    """A mixin class to provide logging capabilities."""
    def log(self, message: str) -> None:
        """Prints a log message to the console."""
        print(f"[LOG]: {message}")

class Teacher(ConsoleLoggerMixin):
    """Class representing a single teacher's workload record.""" 
    total_records = 0

    def __init__(self, teacher_name: str, school_class: str, hours: int):
        """Constructor. Initializes dynamic attributes."""
        self.teacher_name = teacher_name
        self.school_class = school_class
        self.hours = hours 
        
        Teacher.total_records += 1
        
        self.log(f"Created record for teacher {self.teacher_name}")      

    @property
    def hours(self) -> int:
        """Getter for hours."""
        return self._hours

    @hours.setter
    def hours(self, value: int) -> None:
        """Setter for hours. Protects against invalid data."""
        if not isinstance(value, int):
            raise TypeError("Hours must be an integer.")
        if value < 0:
            raise ValueError("Hours cannot be negative.")
        self._hours = value   

    def __str__(self) -> str:
        """String representation for users."""
        return f"Teacher: {self.teacher_name:15} | Class: {self.school_class:5} | Hours: {self.hours}"

    def __repr__(self) -> str:
        """Magic method. Official string representation."""
        return f"Teacher('{self.teacher_name}', '{self.school_class}', {self.hours})"  

class WorkloadCalculator:
    """Class to perform calculations on a list of Teacher objects."""
    def __init__(self, records: list[Teacher]):
        self.records = records

    def get_total_workload_per_teacher(self) -> dict[str, int]:
        """Calculates total hours for each teacher."""
        workload = {} 
        for record in self.records: #Утиная типизация
            workload[record.teacher_name] = workload.get(record.teacher_name, 0) + record.hours
        return workload

    def get_max_workload_teacher(self) -> tuple[str, int]:
        """Finds the teacher with the highest workload."""
        workloads = self.get_total_workload_per_teacher()
        if not workloads:
            return ("None", 0)
        max_teacher = max(workloads, key=workloads.get)
        return (max_teacher, workloads[max_teacher])

    def get_min_workload_teacher(self) -> tuple[str, int]:
        """Finds the teacher with the lowest workload."""
        workloads = self.get_total_workload_per_teacher()
        if not workloads:
            return ("None", 0)
        min_teacher = min(workloads, key=workloads.get)
        return (min_teacher, workloads[min_teacher])

    def get_teacher_workload(self, teacher_name: str) -> int:
        """Returns workload for a specific teacher."""
        workloads = self.get_total_workload_per_teacher()
        return workloads.get(teacher_name, 0)