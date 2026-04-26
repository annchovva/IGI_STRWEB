"""
Program Purpose: Geometric figure modeling and visualization.
Lab4, Task4, Version 1.1
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

from abc import ABC, abstractmethod
import math

class FileOutputMixin:
    """Mixin to provide file output functionality for figures."""

    def save_to_file(self, filename):
        """Saves the string representation of the object to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.__str__())
            print(f"Text data successfully saved to {filename}")
        except OSError as e:
            print(f"Error saving to file: {e}")    

class ShapeColor:
    """Class for storing and validating figure color."""

    ALLOWED_COLORS = ['red', 'green', 'blue', 'yellow', 'purple',
                      'orange', 'pink', 'brown', 'black', 'white']

    def __init__(self, color):
        self.color = color

    @property
    def color(self):
        """Get figure color."""
        return self._color

    @color.setter
    def color(self, value):
        """Set figure color with validation."""
        if not isinstance(value, str):
            raise TypeError("Color must be a string.")
        value = value.strip().lower()
        if not value:
            raise ValueError("Color cannot be empty.")
        if value not in self.ALLOWED_COLORS:
            raise ValueError(f"Color must be one of: {', '.join(self.ALLOWED_COLORS)}")
        self._color = value


class GeometricFigure(ABC):
    """Abstract base class for geometric figures."""

    is_geometric_shape = True

    def __init__(self):
        """Base constructor."""
        pass

    @abstractmethod
    def area(self):
        """Return area of the figure."""
        pass

    @classmethod
    @abstractmethod
    def figure_name(cls):
        """Return figure name."""
        pass


class Triangle(GeometricFigure, FileOutputMixin):
    """Triangle built by side a and two adjacent angles B and C."""

    figure_type = "Triangle"

    def __init__(self, a, angle_b, angle_c, color, label):
        super().__init__()
        
        self.a = a
        self.angle_b = angle_b
        self.angle_c = angle_c
        self.color_obj = ShapeColor(color)
        self.label = label

        self._validate_geometry()

    @property
    def a(self):
        """Get side a."""
        return self._a

    @a.setter
    def a(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Side a must be a number.")
        if value <= 0:
            raise ValueError("Side a must be positive.")
        self._a = float(value)

    @property
    def angle_b(self):
        return self._angle_b

    @angle_b.setter
    def angle_b(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Angle B must be a number.")
        if not (0 < value < 180):
            raise ValueError("Angle B must be between 0 and 180 degrees.")
        self._angle_b = float(value)

    @property
    def angle_c(self):
        return self._angle_c

    @angle_c.setter
    def angle_c(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Angle C must be a number.")
        if not (0 < value < 180):
            raise ValueError("Angle C must be between 0 and 180 degrees.")
        self._angle_c = float(value)

    @property
    def color(self):
        return self.color_obj.color

    @color.setter
    def color(self, value):
        self.color_obj.color = value

    @classmethod
    def figure_name(cls):
        return cls.figure_type

    def _validate_geometry(self):
        """Validate if triangle with these angles can exist."""
        if self.angle_b + self.angle_c >= 180:
            raise ValueError("Sum of angles B and C must be less than 180 degrees.")

    def area(self):
        """Calculate triangle area using the formula: S = (a^2 * sinB * sinC) / (2 * sin(B+C))."""
        b_rad = math.radians(self.angle_b)
        c_rad = math.radians(self.angle_c)
        bc_sum_rad = math.radians(self.angle_b + self.angle_c)
        return (self.a**2 * math.sin(b_rad) * math.sin(c_rad)) / (2 * math.sin(bc_sum_rad))

    def description(self):
        """Return string with main parameters, color and area."""
        return (
            "--- {0} ---\n"
            "Side a: {1:.2f}\n"
            "Angle B: {2:.2f}°\n"
            "Angle C: {3:.2f}°\n"
            "Color: {4}\n"
            "Area: {5:.2f}\n"
            "Label: {6}\n"
            "Static Check (Is Shape): {7}"
        ).format(
            self.figure_name(), self.a, self.angle_b, self.angle_c,
            self.color, self.area(), self.label, self.is_geometric_shape
        )

    def __str__(self):
        """Special magic method."""
        return self.description()
