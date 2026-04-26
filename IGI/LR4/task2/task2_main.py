"""
Program Purpose: Main entry point for Task2
Lab4, Task2, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import os

from task2.text_analyzer import WordAnalyzer, SentenceAnalyzer, SpecialPatternAnalyzer
from task2.file_manager import TextFileHandler, ArchiveHandler
from services.validators import get_integer_input

def run_analysis() -> None:
    """Run text analysis with user input."""
    filename = "task2/text.txt"
    
    try:
        file_handler = TextFileHandler(filename)
        content = file_handler.read()
        print(f"\nLoaded {len(content)} characters from {filename}")
        
        word_analyzer = WordAnalyzer(content)
        sentence_analyzer = SentenceAnalyzer(content)
        pattern_analyzer = SpecialPatternAnalyzer(content)
        
        longest_word, longest_pos = word_analyzer.get_longest_word_info()
        lowercase_words = word_analyzer.get_lowercase_words()
        punctuation = word_analyzer.get_punctuation()
        smileys = pattern_analyzer.find_smileys(content)
        mac_addresses = pattern_analyzer.find_mac_addresses(content)
        
        report_lines = []
        report_lines.append("TEXT ANALYSIS REPORT")
        
        report_lines.append("\n--- SENTENCE STATISTICS ---")
        report_lines.append(f"Total sentences: {sentence_analyzer.count_all_sentences()}")
        report_lines.append(f"  - Declarative (ending with '.'): {sentence_analyzer.count_declarative_sentences()}")
        report_lines.append(f"  - Interrogative (ending with '?'): {sentence_analyzer.count_question_sentences()}")
        report_lines.append(f"  - Imperative (ending with '!'): {sentence_analyzer.count_exclamation_sentences()}")
        report_lines.append(f"Average sentence length (word characters): {sentence_analyzer.count_avg_len_sentence():.2f}")
        
        report_lines.append("\n--- WORD STATISTICS ---")
        report_lines.append(f"Total words: {len(word_analyzer)}")
        report_lines.append(f"Average word length: {word_analyzer.count_avg_len_word():.2f} characters")
        report_lines.append(f"Longest word: '{longest_word}' at position {longest_pos}")
        
        odd_words = word_analyzer.get_odd_words()
        report_lines.append(f"Every odd word: {odd_words}")
        
        report_lines.append(f"\nWords starting with lowercase: {lowercase_words}")
        report_lines.append(f"\nPunctuation marks: {punctuation}")
        
        report_lines.append("\n--- SMILEY ANALYSIS ---")
        report_lines.append(f"Smileys found: {pattern_analyzer.count_smiles()}")
        if smileys:
            report_lines.append(f"Smileys: {smileys}")
        
        report_lines.append("\n--- MAC ADDRESS ANALYSIS ---")
        report_lines.append(f"MAC addresses found: {len(mac_addresses)}")
        if mac_addresses:
            for mac in mac_addresses:
                report_lines.append(f"  - {mac} (valid: {pattern_analyzer.is_valid_mac(mac)})")
        
        final_report = "\n".join(report_lines)
        print("\n" + final_report)
        
        result_file = "task2/analysis_result.txt"
        result_handler = TextFileHandler(result_file)
        result_handler.write(final_report)
        
        archive_name = "task2/result.zip"
        
        archiver = ArchiveHandler(result_file, archive_name)
        archiver.create_zip()
        archiver.print_archive_info()
        
        print(f"\nAnalysis complete!")
        print(f"  - Report saved to: {result_file}")
        print(f"  - Archive saved to: {archive_name}")
        
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except ValueError as e:
        print(f"Data error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def run_task2():
    """Main entry point for Task 2."""
    while True:
        print("\n" + "=" * 40)
        print(" ---- TASK 2: TEXT ANALYSIS SYSTEM ----")
        print("| 1. Run Text Analysis                |")
        print("| 0. Back to Main Menu                |")
        print(" -------------------------------------")
        
        choice = get_integer_input("Choose an option: ", 0)

        if choice == 1:
            run_analysis()

        elif choice == 0:
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Try again.")    
