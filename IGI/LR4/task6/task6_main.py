"""
Program Purpose: Testing Pandas Wine Review Analysis.
Lab4, Task6, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import os
from task6.data_analysis import WineReviewProcessor

def run_task6():
    """Main execution loop for Task 6."""
    while True:
        print("--- PANDAS DATA ANALYSIS: WINE REVIEWS ---")

        file_path = "task6\winemag-data-130k-v2.csv"

        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
        else:
            try:
                processor = WineReviewProcessor(file_path)
                
                print(f"Processing object: {processor}")
                print(f"Total entries via __len__: {len(processor)}")
                
                processor.run_analysis()
                
                print("\nExample: Data of the 10th row in dataset:")
                print(processor[9])

            except Exception as e:
                print(f"An error occurred during processing: {e}")

        repeat = input("\nAnalyze another file? (y/n): ").lower()
        if repeat != 'y':
            break