"""
Program Purpose: Data analysis of Wine Reviews using Pandas.
Lab4, Task6, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import pandas as pd
from abc import ABC, abstractmethod

class DataSummaryMixin:
    """Mixin to provide high-level summary of any DataFrame."""
    
    def show_basic_info(self, df):
        print("\n--- General DataFrame Info ---")
        print(f"Columns: {', '.join(df.columns)}")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print("------------------------------")

class AbstractDataProcessor(ABC):
    """Abstract base class for data processors."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self._df = None

    @abstractmethod
    def load_data(self):
        """Method to load data from source."""
        pass

    @abstractmethod
    def run_analysis(self):
        """Method to perform specific analysis."""
        pass

class WineReviewProcessor(AbstractDataProcessor, DataSummaryMixin):
    """Concrete class for processing Wine Reviews dataset."""

    DATA_SOURCE = "Kaggle: Wine Reviews"

    def __init__(self, file_path):
        super().__init__(file_path)
        self.analysis_results = {} 
        self.load_data()

    @property
    def df(self):
        """Getter for the dataframe."""
        if self._df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self._df

    @df.setter
    def df(self, value):
        """Setter for the dataframe with basic type validation."""
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Value must be a pandas DataFrame.")
        self._df = value

    def load_data(self):
        """Loads CSV data into a DataFrame."""
        try:
            self.df = pd.read_csv(self.file_path, index_col=0)
            print(f"Successfully loaded {self.DATA_SOURCE}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File not found at {self.file_path}")
        except Exception as e:
            raise Exception(f"Failed to load data: {e}")

    def task_a_series_operations(self):
        """
        Task A: Working with Series.
        Creates a Series of countries, extracts first 8 elements, and converts to list.
        """
        print("\n--- Task A: Series Operations ---")
        
        countries = self.df['country']
        print(f"Object type: {type(countries)}")

        # 2. Extract first 8 elements using .iloc
        first_8_iloc = countries.iloc[:8]
        print("First 8 via .iloc:")
        print(first_8_iloc)

        indices = countries.index[:8]
        first_8_loc = countries.loc[indices]
        print("\nFirst 8 via .loc:")
        print(first_8_loc)     

        # 3. Convert to list
        first_8_list = first_8_iloc.tolist()
        
        print("First 8 countries (as list):")
        print(first_8_list)
        
        return first_8_list

    def task_b_statistical_analysis(self):
        """
        Task B: Statistical analysis.
        Calculates the ratio of average prices between highest and lowest rated wines.
        """
        print("\n--- Task B: Statistical Analysis ---")
        
        # 1. Get info about dataframe
        self.show_basic_info(self.df)

        # 2. Find max and min points (ignoring zero points if any)
        max_points = self.df['points'].max()
        min_points = self.df[self.df['points'] > 0]['points'].min()

        print(f"Max points found: {max_points}")
        print(f"Min points found: {min_points}")

        # 3. Calculate average price for max points
        # We dropna() to ensure mean is calculated only on valid price data
        avg_price_max = self.df[self.df['points'] == max_points]['price'].dropna().mean()
        
        # 4. Calculate average price for min points
        avg_price_min = self.df[self.df['points'] == min_points]['price'].dropna().mean()

        if avg_price_min == 0 or pd.isna(avg_price_min):
            return "Calculation impossible: division by zero or no price data for min points."

        ratio = avg_price_max / avg_price_min
        
        result = round(ratio, 2)
        print(f"Average price for {max_points} pts: {avg_price_max:.2f}")
        print(f"Average price for {min_points} pts: {avg_price_min:.2f}")
        print(f"The ratio is: {result}")
        
        return result

    def run_analysis(self):
        """Polymorphic method to run all tasks."""
        self.task_a_series_operations()
        self.task_b_statistical_analysis()

    # Magic Methods
    def __len__(self):
        """Returns the number of rows in the dataset."""
        return len(self.df)

    def __getitem__(self, index):
        """Allows access to rows by index: processor[5]."""
        return self.df.iloc[index]

    def __str__(self):
        """String representation of the object."""
        return f"WineReviewProcessor for {self.file_path} ({len(self)} records)"
