"""
Purpose: Function for executing Task 4,
Lab 3 Task 4, Version 1.1,
Author: Gorbachova Anna,
Date: 21.03.2026.
"""

import services.text_logic as ta
from modules.menu_logic import menu_for_tasks

@menu_for_tasks
def task4():
    """Main business function for Task 4: Text analysis."""
    text = "So she was considering in her own mind, as well as she could, " \
    "for the hot day made her feel very sleepy and stupid, whether the pleasure " \
    "of making a daisy-chain would be worth the trouble of getting up and " \
    "picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her."
    print("Text analysis")
    words = ta.get_clean_words(text)
    print(f"а) Words ending with a vowel: {ta.count_vowel_enders(words)}")
    avg_val, avg_words = ta.get_average_length_words(words)
    print(f"b) Average length: {avg_val}")
    if avg_words:
        print(f"   Words this length: {', '.join(avg_words)}")
    else:
        print(f"   No words of length {avg_val} ")
    fifth_words = ta.get_every_fifth(words)
    print(f"c) Every fifth words: {', '.join(fifth_words)}")