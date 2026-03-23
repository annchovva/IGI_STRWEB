"""
Purpose: List processing logic and sequence, 
Lab 3, Version 1.1,
Author: Gorbachova Anna,
Date: 21.03.2026.
"""
import random
import services.validate_input as i

def list_generator(size):
    """Generates a list of random floats."""
    return [round(random.uniform(-10, 10), 2) for _ in range(size)]

def input_list(size):
    """Initializes list with user input."""
    lst = []
    for i in range(size):
        lst.append(i.get_float(f"Enter element №{i}: "))
    return lst    

def max_element(lst):
    """Returns the index of the maximum absolute element."""
    if not lst:
        return None
    max_idx = 0
    for i in range(1, len(lst)):
        if abs(lst[i]) > abs(lst[max_idx]):
            max_idx = i
    return max_idx        

def sum_after_positive(lst):
    """Calculates sum of elements after the first positive value."""
    if not lst:
        return None
    first_pos = -1
    for i, val in enumerate(lst):
        if val > 0:
            first_pos = i
            break
    if first_pos == -1 or first_pos == len(lst) - 1:
        return None
    return sum(lst[first_pos + 1:])       
