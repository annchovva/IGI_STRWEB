"""
Program Purpose: Manage teacher workload data and calculate statistics.
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import re

class ConsoleMixin:
    """Mixin for printing simple messages to the console."""

    def log(self, message):
        """Prints a message to the console."""
        print(f"[INFO]: {message}")

class Person:
    """Base class for a person."""

    def __init__(self, name):
        """Create a person with name."""
        self.name = name

    @property
    def name(self):
        """Get the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the person's name with validation."""
        if not isinstance(value, str):
            raise TypeError("Name must be a string.")

        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty.")

        self._name = value      

class Teacher(Person, ConsoleMixin):
    """Class for one teacher workload record."""

    def __init__(self, teacher_name, school_class, hours):
        """Create a teacher record."""
        super().__init__(teacher_name)
        self.school_class = school_class
        self.hours = hours 
        
        self.log(f"Teacher record created: {self.teacher_name}")
        
    @property
    def teacher_name(self):
        """Get teacher name."""
        return self.name

    @teacher_name.setter
    def teacher_name(self, value):
        """Set teacher name."""
        self.name = value

    @property    
    def school_class(self):
        """Get school class."""
        return self._school_class
    
    @school_class.setter
    def school_class(self, value):
        """Set school class with checking format."""
        if not isinstance(value, str):
            raise TypeError("School class must be a string.")
        
        value = value.strip().upper()

        if not value:
            raise ValueError("Class cannot be empty.")
        
        pattern = r'^([1-9]|10|11)[A-Z]$'
        if not re.fullmatch(pattern, value):
            raise ValueError("Class must be in format 'Number(1-11)+Letter'.")  
          
        self._school_class = value

    @property
    def hours(self):
        """Get workload hours.."""
        return self._hours

    @hours.setter
    def hours(self, value):
        """Set workload hours."""
        if not isinstance(value, int):
            raise TypeError("Hours must be an integer.")
        if value < 0:
            raise ValueError("Hours cannot be negative.")
        self._hours = value  

    def to_dict(self):
        """Convert object data to a dictionary."""
        return {
            "teacher_name": self.teacher_name,
            "school_class": self.school_class,
            "hours": self.hours
        }  

    def __str__(self):
        """String representation for users."""
        return f"Teacher: {self.teacher_name:15} | Class: {self.school_class:5} | Hours: {self.hours}"

    def __repr__(self):
        """Official string representation."""
        return f"Teacher('{self.teacher_name}', '{self.school_class}', {self.hours})"  


class WorkloadCalculator:
    """Class for calculating teacher workload.."""

    def __init__(self, records):
        """Store a list of teacher records."""
        self.records = list(records)

    def total_by_teacher(self):
        """Calculates total workload for each teacher."""
        result = {}

        for record in self.records:
            result[record.teacher_name] = result.get(record.teacher_name, 0) + record.hours

        return result    

    def max_teacher(self):
        """Find teacher with the biggest workload."""
        totals = self.total_by_teacher()

        if not totals:
            return None, 0
        
        name = max(totals, key=totals.get)
        return (name, totals[name])

    def min_teacher(self):
        """Finds teacher with the smallest workload."""
        totals = self.total_by_teacher()

        if not totals:
            return None, 0
        
        name = min(totals, key=totals.get)
        return (name, totals[name])
    
    def teacher_workload(self, teacher_name):
        """Return workload for one teacher."""
        totals = self.total_by_teacher()
        target = teacher_name.strip().lower()

        for name, hours in totals.items():
            if name.lower() == target:
                return hours
        return 0

    def sort_by_name(self):
        """Sort records by teacher name."""
        return sorted(self.records, key=lambda item: item.teacher_name.lower())

    def sort_by_hours(self):
        """Sort records by hours (from biggest to smallest)."""
        return sorted(self.records, key=lambda item: item.hours, reverse=True)