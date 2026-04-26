"""
Program Purpose: NumPy matrix generation and statistical analysis.
Lab4, Task5, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

from abc import ABC, abstractmethod
import numpy as np


class InfoMixin:
    """Mixin providing info about the object."""
    def get_info(self):
        return f"Object type: {self.__class__.__name__}"

class BaseMatrixProcessor(ABC):
    """Abstract base class for matrix processors."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    @abstractmethod
    def create_matrix(self):
        """Create matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze(self):
        """Analyze matrix."""
        raise NotImplementedError


class MatrixProcessor(BaseMatrixProcessor, InfoMixin):
    """Class for generating and analyzing NumPy matrices."""

    created_objects = 0

    def __init__(self, rows, cols, low= 0, high= 9, seed= None):
        super().__init__(rows, cols)
        self.low = low
        self.high = high
        self.seed = seed
        self._matrix = None
        
        MatrixProcessor.created_objects += 1

    @property
    def rows(self):
        """Get number of rows."""
        return self._rows

    @rows.setter
    def rows(self, value):
        """Set number of rows."""
        if not isinstance(value, int):
            raise TypeError("Rows must be an integer.")
        if value <= 0:
            raise ValueError("Rows must be positive.")
        self._rows = value

    @property
    def cols(self):
        """Get number of columns."""
        return self._cols

    @cols.setter
    def cols(self, value):
        """Set number of columns."""
        if not isinstance(value, int):
            raise TypeError("Columns must be an integer.")
        if value <= 0:
            raise ValueError("Columns must be positive.")
        self._cols = value

    @property
    def matrix(self):
        """Get matrix."""
        if self._matrix is None:
            raise ValueError("Matrix has not been created yet.")
        return self._matrix

    def create_matrix(self):
        """Create a random integer matrix."""
        if self.seed is not None:
            np.random.seed(self.seed)

        self._matrix = np.random.randint(self.low, self.high + 1, size=(self.rows, self.cols))
        return self._matrix

    def create_from_array(self, values):
        """Create 1D NumPy array using array()."""
        return np.array(values)

    def create_zeros(self):
        """Create matrix filled with zeros."""
        return np.zeros((self.rows, self.cols), dtype=int)

    def create_ones(self):
        """Create matrix filled with ones."""
        return np.ones((self.rows, self.cols), dtype=int)

    def create_full(self, value):
        """Create matrix filled with a specific value."""
        return np.full((self.rows, self.cols), value, dtype=int)

    def create_arange(self):
        """Create array with arange()."""
        return np.arange(self.rows * self.cols)

    def create_values(self, *values):
        """Create array from values, similar to values()."""
        return np.array(values)

    def get_last_row(self):
        """Return the last row of the matrix."""
        return self.matrix[-1]

    def sort_last_row(self):
        """Sort last row in ascending order."""
        sorted_row = np.sort(self.matrix[-1])
        self._matrix[-1] = sorted_row
        return sorted_row

    def last_row_median_builtin(self):
        """Median of last row using NumPy function."""
        return float(np.median(self.get_last_row()))

    def last_row_median_manual(self):
        """Median of last row using manual formula."""
        row = np.sort(self.get_last_row())
        n = len(row)
        mid = n // 2

        if n % 2 == 1:
            return float(row[mid])
        return float((row[mid - 1] + row[mid]) / 2)

    def analyze(self):
        """Return statistics for matrix and its last row."""
        mat = self.matrix
        last_row = self.get_last_row()

        stats = {
            "mean": float(np.mean(mat)),
            "median": float(np.median(mat)),
            "variance": float(np.var(mat)),
            "std": float(np.std(mat)),
            "last_row_builtin_median": self.last_row_median_builtin(),
            "last_row_manual_median": self.last_row_median_manual(),
        }

        if self.rows > 1:
            stats["corrcoef"] = np.corrcoef(mat, rowvar=False)
        else:
            stats["corrcoef"] = None

        return stats

    def __len__(self):
        """Return number of matrix elements."""
        return self.rows * self.cols

    def __getitem__(self, item):
        """Allow indexing and slicing."""
        return self.matrix[item]

    def __str__(self):
        """String representation of matrix."""
        return f"MatrixProcessor({self.rows}x{self.cols})"

    def build_report(self):
        """Build full report string."""
        stats = self.analyze()

        report_lines = []
        report_lines.append("NUMPY MATRIX ANALYSIS REPORT")
        report_lines.append(f"Class info: {self.get_info()}")
        report_lines.append(f"Created objects: {MatrixProcessor.created_objects}")
        report_lines.append("")
        report_lines.append("Matrix:")
        report_lines.append(str(self.matrix))
        report_lines.append("")
        report_lines.append(f"Shape: {self.matrix.shape}")
        report_lines.append(f"Size: {self.matrix.size}")
        report_lines.append(f"Length by __len__: {len(self)}")
        report_lines.append("")
        report_lines.append("Basic statistics:")
        report_lines.append(f"Mean: {stats['mean']:.4f}")
        report_lines.append(f"Median: {stats['median']:.4f}")
        report_lines.append(f"Variance: {stats['variance']:.4f}")
        report_lines.append(f"Std deviation: {stats['std']:.4f}")

        if stats["corrcoef"] is not None:
            report_lines.append("")
            report_lines.append("Correlation matrix:")
            report_lines.append(str(stats["corrcoef"]))

        report_lines.append("")
        report_lines.append("Last row:")
        report_lines.append(str(self.get_last_row()))
        report_lines.append(f"Sorted last row: {self.sort_last_row()}")
        report_lines.append(f"Median of last row by NumPy: {stats['last_row_builtin_median']:.4f}")
        report_lines.append(f"Median of last row manually: {stats['last_row_manual_median']:.4f}")

        report_lines.append("")
        report_lines.append("Examples of indexing and slicing:")
        report_lines.append(f"First row: {self[0]}")
        report_lines.append(f"First column: {self.matrix[:, 0]}")
        report_lines.append(f"Top-left 2x2 block: {self.matrix[:2, :2]}")

        report_lines.append("")
        report_lines.append("Ufunc examples:")
        report_lines.append(f"Matrix + 1:\n{np.add(self.matrix, 1)}")
        report_lines.append(f"Matrix * 2:\n{np.multiply(self.matrix, 2)}")
        report_lines.append(f"Square root of matrix elements:\n{np.sqrt(self.matrix)}")

        report_lines.append("")
        report_lines.append("Arrays created by NumPy:")
        report_lines.append(f"array(): {self.create_from_array([1, 2, 3, 4])}")
        report_lines.append(f"values(): {self.create_values(5, 6, 7, 8)}")
        report_lines.append(f"zeros():\n{self.create_zeros()}")
        report_lines.append(f"ones():\n{self.create_ones()}")
        report_lines.append(f"full(7):\n{self.create_full(7)}")
        report_lines.append(f"arange(): {self.create_arange()}")

        return "\n".join(report_lines)
