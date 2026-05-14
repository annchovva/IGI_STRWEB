"""
Program Purpose: Data visualization module (Matplotlib).
Lab4, Task3, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import matplotlib.pyplot as plt
import os

class ChartManager:
    """Handles plotting logic and file export."""
    
    @staticmethod
    def plot_taylor_results(x_list, y_taylor, y_math, filename="output_chart.png"):
        """Creates a colored plot with legends and annotations."""
        plt.figure(figsize=(10, 5))
        
        plt.plot(x_list, y_taylor, color='red', marker='o', linestyle='-', label='Taylor Expansion')
        plt.plot(x_list, y_math, color='blue', linestyle='--', label='Math.sin(x)')
        
        plt.title("Taylor Series vs Math Library Sin(x)")
        plt.xlabel("X values")
        plt.ylabel("Function results")
        plt.axhline(0, color='black', linewidth=0.8)
        plt.axvline(0, color='black', linewidth=0.8)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.annotate("Сравнение ряда и функции", xy=(0.3, 0.3), xytext=(0.1, 0.8))

        folder = "task3"
        save_path = os.path.join(folder, filename)
        plt.savefig(save_path)
        print(f"Chart saved to: {save_path}")
        plt.show()
