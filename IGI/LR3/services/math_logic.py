"""
Purpose: Mathrmatical calculations (Taylor and average)
Lab 3, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

import math
import services.validate_input as input

def calculate_decorator(func):
    """Simple decorator that print massage before and after calculation"""
    def wrapper(*args, **kwargs):
        print(f"\n--- Starting calculation for x = {args[0]} ---")
        result = func(*args, **kwargs)
        print("--- Calculation finished ----")
        return result
    return wrapper

@calculate_decorator
def calculate_sin_taylor(x, eps):
    """Calculate sin(x) using Taylor series"""
    max_iter = 500
    x_norm = x % (2 * math.pi)
    term = x_norm
    series_sum = term
    n = 1
    while abs(term) >= eps and n < max_iter:
        multiplier = -(x_norm**2) / ((2 * n) * (2 * n + 1))
        term *= multiplier
        series_sum += term
        n += 1
    return [x, n, series_sum, math.sin(x), eps]

def run_average():
    """Calculates average of numbers until 0 is entered"""
    total_sum = 0
    count = 0
    while True:
        num = input.get_int("Input integer number: ")
        if num == 0:
            break
        total_sum += num
        count += 1
    if count == 0:
        return 0
    return total_sum / count

