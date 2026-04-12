"""
Program Purpose: Define classes for teacher data management and statistics
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

from typing import List, Dict, Any

class TeacherLoadMixin:
    """Mixin for teacher load calculations."""

    def calculate_total_load(self) -> float:
        """Calculate total hours for a teacher."""
        if hasattr(self, 'hours'):
            return float(self.hours)
        return 0.0

class Teacher(TeacherLoadMixin):
    """Teacher class representing a teachers with their workload."""

    _instances_count = 0

    def __init__(self, surname: str, hours: float, classes: List[str] = None):
        """Initialize a Teacher instance."""
        self._surname = surname
        self._hours = hours
        self._classes = classes if classes is not None else []
        Teacher._instances_count += 1

    @staticmethod
    def get_instance_count() -> int:
        """Return number of created instances."""
        return Teacher._instances_count    

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Teacher':
        """Create Teacher instance from dictionary."""
        return cls(data['surname'], data['hours'], data.get('classes', []))

    @property
    def surname(self) -> str:
        """Getter for teacher's surname."""
        return self._surname
    
    @surname.setter
    def surname(self, value: str) -> None:
        """Setter for surname with validation."""
        if not value or not value.strip():
            raise ValueError("Surname cannot be empty")
        self._surname = value.strip()

    @property
    def hours(self) -> float:
        """Getter for teacher's hours."""
        return self._hours
    
    @hours.setter
    def hours(self, value: float) -> None:
        """Setter for hours with validation."""
        if value < 0:
            raise ValueError("Hours cannot be negative")
        self._hours = float(value)

    @property
    def classes(self) -> List[str]:
        """Getter for list of classes."""
        return self._classes.copy()
    
    def add_class(self, class_name: str) -> None:
        """Add a class to the teacher's list."""
        if class_name and class_name.strip():
            self._classes.append(class_name.strip())

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Teacher: {self._surname}, Load: {self.calculate_total_load()}h" 

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Teacher(surname='{self._surname}', hours={self._hours}, classes={self._classes})"

    def __eq__(self, other: object) -> bool:
        """Compare teachers by surname."""
        if not isinstance(other, Teacher):
            return NotImplemented
        return self._surname.lower() == other._surname.lower()

    def __lt__(self, other: 'Teacher') -> bool:
        """Compare teachers by load for sorting."""
        return self.calculate_total_load() < other.calculate_total_load()

class TeacherStatistics:
    """Class for statistical operations on teacher lists."""

    def __init__(self, teachers: List[Teacher]):
        """Initialize with a list of Teacher objects."""
        self._teachers = teachers

    def get_max_load(self) -> Teacher:
        """Return teacher with maximum load."""
        if not self._teachers:
            raise ValueError("No teachers available")
        return max(self._teachers, key=lambda t: t.calculate_total_load())
       
    def get_min_load(self) -> Teacher:
        """Return teacher with minimum load."""
        if not self._teachers:
            raise ValueError("No teachers available")
        return min(self._teachers, key=lambda t: t.calculate_total_load())   
    
    def find_by_surname(self, surname: str) -> Teacher:
        """Search teacher by surname."""
        surname_lower = surname.lower().strip()
        for teacher in self._teachers:
            if teacher.surname.lower() == surname_lower:
                return teacher
        raise ValueError(f"Teacher '{surname}' not found")
    
    def get_all_sorted(self) -> List[Teacher]:
        """Return teachers sorted by load descending."""
        return sorted(self._teachers, reverse=True)
    
    def get_summary(self) -> Dict[str, Any]:
        """Return summary statistics using Mixin calculations."""
        if not self._teachers:
            return {"count": 0, "total_hours": 0, "avg_hours": 0}
        
        total = sum(t.calculate_total_load() for t in self._teachers)
        return {
            "count": len(self._teachers),
            "total_hours": total,
            "avg_hours": total / len(self._teachers)
        }
