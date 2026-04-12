"""
Program Purpose: Data serialization (CSV and Pickle) for Teacher objects
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import csv
import pickle
from typing import List
from models import Teacher

class DataManager:
    """Base class for data management."""
    
    def __init__(self, filename: str):
        """Initialize with a filename."""
        self._filename = filename
    
    @property
    def filename(self) -> str:
        """Get filename."""
        return self._filename
    
    def save(self, teachers: List[Teacher]) -> None:
        """Abstract save method."""
        raise NotImplementedError("Subclasses must implement save()")
    
    def load(self) -> List[Teacher]:
        """Abstract load method."""
        raise NotImplementedError("Subclasses must implement load()")

class CSVDataManager(DataManager):
    """CSV implementation."""
    
    def __init__(self, filename: str):
        super().__init__(filename)
        if not self._filename.lower().endswith('.csv'):
            self._filename += '.csv'

    def save(self, teachers: List[Teacher]) -> None:
        """Save teachers to CSV file."""
        try:
            with open(self._filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Surname', 'Hours', 'Classes'])
                for t in teachers:
                    writer.writerow([t.surname, t.hours, ';'.join(t.classes)])
            print(f"Successfully saved to {self._filename}")
        except Exception as e:
            raise IOError(f"CSV save error: {e}")
        
    def load(self) -> List[Teacher]:
        """Load teachers from CSV file with validation."""
        teachers = []
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        classes = row[2].split(';') if len(row) > 2 and row[2] else []
                        teachers.append(Teacher(row[0], float(row[1]), classes))
            return teachers
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self._filename} not found.")
        except Exception as e:
            raise ValueError(f"CSV load error: {e}")    

class PickleDataManager(DataManager):
    """Pickle implementation."""
    
    def __init__(self, filename: str):
        super().__init__(filename)
        if not self._filename.lower().endswith('.pkl'):
            self._filename += '.pkl'

    def save(self, teachers: List[Teacher]) -> None:
        """Save objects using pickle."""
        try:
            with open(self._filename, 'wb') as f:
                pickle.dump(teachers, f)
            print(f"Objects saved to {self._filename}")
        except Exception as e:
            raise IOError(f"Pickle save error: {e}")
    
    def load(self) -> List[Teacher]:
        """Load objects using pickle with specific exception handling."""
        try:
            with open(self._filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self._filename} not found.")
        except (pickle.UnpicklingError, EOFError):
            raise ValueError("Pickle file is corrupted.")
