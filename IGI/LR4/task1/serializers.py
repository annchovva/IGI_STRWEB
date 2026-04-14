"""
Program Purpose: Data serialization (CSV and Pickle) for Teacher objects
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""
import csv
import pickle
import os
from typing import List
from .models import Teacher  

class BaseSerializer:
    """Abstract base class for serialization."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, records: List[Teacher]) -> None:
        """Saves records to a file."""
        raise NotImplementedError("Subclasses must implement save() method")

    def load(self) -> List[Teacher]:
        """Loads records from a file. """
        raise NotImplementedError("Subclasses must implement load() method")


class CSVSerializer(BaseSerializer):
    """Serializer for CSV format. Inherits from BaseSerializer."""
    def __init__(self, filepath: str):
        super().__init__(filepath) 

    def save(self, records: List[Teacher]) -> None:
        """Saves Teacher objects to a CSV file."""
        try:
            with open(self.filepath, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['teacher_name', 'school_class', 'hours'])
                for record in records:
                    writer.writerow([record.teacher_name, record.school_class, record.hours])
            print(f"Successfully saved to CSV: {self.filepath}")
        except IOError as e:
            print(f"Error saving to CSV: {e}")

    def load(self) -> List[Teacher]:
        """Loads Teacher objects from a CSV file."""
        if not os.path.exists(self.filepath):
            return []
        
        records = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    record = Teacher(
                        teacher_name=row['teacher_name'],
                        school_class=row['school_class'],
                        hours=int(row['hours'])
                    )
                    records.append(record)
        except (IOError, ValueError, KeyError) as e:
            print(f"Error loading CSV: {e}")
        return records


class PickleSerializer(BaseSerializer):
    """Serializer for Pickle format."""
    def __init__(self, filepath: str):
        super().__init__(filepath)

    def save(self, records: List[Teacher]) -> None:
        """Saves Teacher objects using pickle."""
        try:
            with open(self.filepath, mode='wb') as file:
                pickle.dump(records, file)
            print(f"Successfully saved to Pickle: {self.filepath}")
        except IOError as e:
            print(f"Error saving to Pickle: {e}")

    def load(self) -> List[Teacher]:
        """Loads Teacher objects using pickle."""
        if not os.path.exists(self.filepath):
            return []
            
        try:
            with open(self.filepath, mode='rb') as file:
                return pickle.load(file)
        except (IOError, pickle.PickleError) as e:
            print(f"Error loading Pickle: {e}")
            return []
