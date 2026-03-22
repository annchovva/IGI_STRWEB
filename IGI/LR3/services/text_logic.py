"""
Purpose: Text analysis functions
Lab 3, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

def count_non_whilespace_chars(text):
    """Counts non-whitespace characters in a string"""
    return sum(1 for char in text if not char.isspace())

def get_clean_words(text):
    """Getting text without punctuation marks"""
    for char in ",.":
        text = text.replace(char, " " if char == "-" else "")
    return text.split()

def count_vowel_enders(words):
    """Counting words ending with a vowel"""
    vowels = "aeiouy"
    count = 0
    for word in words:
        if word[-1].lower() in vowels:
            count += 1
    return count
        
def get_average_length_words(words):
    """Calculating the average word length and diaplaying such words"""
    total_len = sum(len(word) for word in words)
    avg_res = round(total_len / len(words))

    target_words = []
    for word in words:
        if len(word) == avg_res:
            if word.lower() not in [w.lower() for w in target_words]:
                target_words.append(word)
    return avg_res, target_words  

def get_every_fifth(words):
    """Displaying every fifth word"""
    return words[4::5]
          