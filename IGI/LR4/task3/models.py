"""
Program Purpose: OOP models for Taylor series and sequence analysis.
Lab4, Task3, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import math
import statistics

class InfoMixin:
    """Mixin to provide descriptive info about the object."""
    def get_info(self):
        return f"[INFO] Object of type: {self.__class__.__name__}"

class BaseCalculator:
    """Base class for all math tools."""
    execution_count = 0 

    def __init__(self):
        BaseCalculator.execution_count += 1

    def compute(self, *args):
        """Method for polymorphism."""
        raise NotImplementedError("Subclasses must implement compute()")

class TaylorCalculator(BaseCalculator, InfoMixin):
    """Calculates Sin(x) using Taylor series."""
    def __init__(self, epsilon):
        super().__init__()
        self.epsilon = epsilon 

    @property
    def epsilon(self):
        """Getter for epsilon property."""
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value):
        """Setter with validation (Requirement #9 - Exception handling)."""
        if value <= 0 or value > 0.1:
            raise ValueError("Epsilon must be between 0 and 0.1 for precision.")
        self._epsilon = value

    def compute(self, x):
        """Taylor series calculation."""
        max_iter = 500
        x_norm = x % (2 * math.pi)
        term = x_norm
        series_sum = term
        n = 1
        
        while abs(term) >= self.epsilon and n < max_iter:
            multiplier = -(x_norm**2) / ((2 * n) * (2 * n + 1))
            term *= multiplier
            series_sum += term
            n += 1
        return (x, n, series_sum, math.sin(x))

class SequenceAnalyzer:
    """Analyzes sequences for stats."""
    def __init__(self, data):
        self.data = data

    def __len__(self):
        """Magic method: returns number of items in sequence."""
        return len(self.data)

    def __str__(self):
        """Magic method: user-friendly statistics output."""
        if not self.data:
            return "Sequence is empty."
        
        mean_val = statistics.mean(self.data)
        median_val = statistics.median(self.data)
        try:
            mode_val = statistics.mode(self.data)
        except statistics.StatisticsError:
            mode_val = "No unique mode"
        
        variance_val = statistics.variance(self.data) if len(self.data) > 1 else 0
        std_dev = statistics.stdev(self.data) if len(self.data) > 1 else 0

        return (f"--- Sequence Statistics ---\n"
                f"Elements: {len(self)}\n"
                f"Mean: {mean_val:.6f}\n"
                f"Median: {median_val:.6f}\n"
                f"Mode: {mode_val}\n"
                f"Variance: {variance_val:.6f}\n"
                f"Std Deviation: {std_dev:.6f}")
