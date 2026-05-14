"""
Program Purpose: Save and load teacher workload data in CSV and Pickle formats.
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import csv
import pickle
import os
from abc import ABC, abstractmethod
from task1.models import Teacher  

class BaseSerializer(ABC):
    """Abstract base class for serialization."""

    @abstractmethod
    def save(self, records):
        """Save records to a file."""
        pass

    @abstractmethod    
    def load(self):
        """Load records from a file."""
        pass

class CSVSerializer(BaseSerializer):
    """Serializer for CSV format."""
    filepath = "task1\data.csv"

    def save(self, records):
        """Save records to CSV file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8', newline="") as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["teacher_name", "school_class", "hours"])
                for record in records:
                    writer.writerow([record.teacher_name, record.school_class, record.hours])
            print(f"Successfully saved to CSV: {self.filepath}")
        except IOError as e:
            print(f"Error saving to CSV: {e}")

    def load(self):
        """Load records from CSV file."""
        if not os.path.exists(self.filepath):
            return []
        
        records = []
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline="") as file:
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
    filepath = "task1\data.pkl"

    def save(self, records):
        """Save RECORDS to Pickle."""
        try:
            with open(self.filepath, 'wb') as file:
                pickle.dump(records, file)
            print(f"Successfully saved to Pickle: {self.filepath}")
        except IOError as e:
            print(f"Error saving to Pickle: {e}")

    def load(self):
        """Load records from Pickle."""
        if not os.path.exists(self.filepath):
            return []
            
        try:
            with open(self.filepath, 'rb') as file:
                return pickle.load(file)
        except (IOError, pickle.PickleError) as e:
            print(f"Error loading Pickle: {e}")
            return []
