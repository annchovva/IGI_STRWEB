"""
Program Purpose: Testing geometric figure classes with visualization.
Lab4, Task4, Version 1.1
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import math
import matplotlib.pyplot as plt
from task4.figures import Triangle
from services.validators import get_float_input, get_string_input, get_color_input

def build_triangle_vertices(triangle):
    """Logic for vertex calculation separated into a function."""
    a = triangle.a
    B_rad = math.radians(triangle.angle_b)
    C_rad = math.radians(triangle.angle_c)
    A_rad = math.pi - (B_rad + C_rad)
    
    c = (a * math.sin(C_rad)) / math.sin(A_rad)
    
    x = [0, a, c * math.cos(B_rad), 0]
    y = [0, 0, c * math.sin(B_rad), 0]
    return x, y

def display_info(figures):
    """Demonstrates polymorphism by calling __str__ on any shape."""
    for figure in figures:
        print(figure)

def run_task4():
    """Main function with a loop for repeated execution."""
    while True:
        print("\n--- Triangle Builder ---")
        
        try:
            a = get_float_input("Enter side a: ", 0.0001, 10000.0)
            angle_b = get_float_input("Enter angle B (degrees): ", 0.0001, 179.999)
            angle_c = get_float_input("Enter angle C (degrees): ", 0.0001, 179.999)
            color = get_color_input("Enter color (e.g., 'blue', 'red'): ")
            label = get_string_input("Enter text label for the triangle: ")

            tri = Triangle(a, angle_b, angle_c, color, label)

            display_info([tri])

            # использование миксина
            tri.save_to_file("task4\output_info.txt")

            x, y = build_triangle_vertices(tri)
            plt.figure(figsize=(6, 5))
            plt.fill(x, y, color=tri.color, alpha=0.5, label=f"Area: {tri.area():.2f}")
            plt.plot(x, y, color='black', linewidth=2)
            plt.text(sum(x[:3])/3, sum(y[:3])/3, tri.label, ha='center')
            plt.title(f"{tri.figure_name()}: {tri.label}")
            plt.axis('equal')
            plt.grid(True)
            
            print("Displaying figure window...")
            plt.savefig("task4\output_figure.png")
            plt.show()

        except ValueError as e:
            print(f"Geometry Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        choice = input("\nDo you want to build another figure? (y/n): ").lower()
        if choice != 'y':
            print("Thank you for using the program. Goodbye!")
            break
