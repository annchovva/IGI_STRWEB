"""
Program Purpose: Main entry point for Task2
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import os
import sys
from typing import List

from task2.text_analyzer import WordAnalyzer, SentenceAnalyzer, SpecialPatternAnalyzer
from task2.file_manager import TextFileHandler, ArchiveHandler


def ensure_default_file(filename: str) -> None:
    """
    Create default text file if it doesn't exist.
    
    Args:
        filename: Path to the file
    """
    if not os.path.exists(filename):
        default_text = """Hello! How are you today? I'm doing great, thank you!
        
Check these MAC addresses: aE:dC:cA:56:76:54 and 01:23:45:67:89:Az.
The weather is wonderful. Is it not? Wow! 

Smileys examples: :-) ;-) ;--------[[[[[[[[ :-]]]] :(((
        
Here are some words: lowercase words like python and code. UPPERCASE words like PYTHON.
Punctuation marks: commas, periods, exclamation marks!
"""
        # Create directory if needed
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(default_text)
        print(f"[Info] Created default file: {filename}")


def run_analysis() -> None:
    """
    Run text analysis with user input.
    Implements Requirement 8 (repeatable execution, input validation).
    """
    # Default filename
    default_file = "task2/text.txt"
    filename = input(f"Enter input filename (default: {default_file}): ").strip()
    if not filename:
        filename = default_file
    
    # Ensure file exists
    ensure_default_file(filename)
    
    try:
        # 1. Read text from file
        file_handler = TextFileHandler(filename)
        content = file_handler.read()
        print(f"\n[OK] Loaded {len(content)} characters from {filename}")
        
        # 2. Initialize analyzers
        word_analyzer = WordAnalyzer(content)
        sentence_analyzer = SentenceAnalyzer(content)
        pattern_analyzer = SpecialPatternAnalyzer()
        
        # 3. Collect analysis results
        sentence_types = sentence_analyzer.get_counts_by_type()
        longest_word, longest_pos = word_analyzer.get_longest_word_info()
        lowercase_words = word_analyzer.get_lowercase_words()
        punctuation = word_analyzer.get_punctuation()
        smileys = pattern_analyzer.find_smileys(content)
        mac_addresses = pattern_analyzer.find_mac_addresses(content)
        
        # 4. Build report
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("TEXT ANALYSIS REPORT")
        report_lines.append("=" * 60)
        
        # Sentence statistics
        report_lines.append("\n--- SENTENCE STATISTICS ---")
        report_lines.append(f"Total sentences: {len(sentence_analyzer)}")
        report_lines.append(f"  - Declarative (ending with '.'): {sentence_types['decl']}")
        report_lines.append(f"  - Interrogative (ending with '?'): {sentence_types['int']}")
        report_lines.append(f"  - Imperative (ending with '!'): {sentence_types['imp']}")
        report_lines.append(f"Average sentence length (word characters): {sentence_analyzer.get_avg_sentence_length(word_analyzer._words):.2f}")
        
        # Word statistics
        report_lines.append("\n--- WORD STATISTICS ---")
        report_lines.append(f"Total words: {len(word_analyzer)}")
        report_lines.append(f"Average word length: {word_analyzer.get_avg_word_length():.2f} characters")
        report_lines.append(f"Longest word: '{longest_word}' at position {longest_pos}")
        
        # Odd position words
        odd_words = word_analyzer.get_odd_words()
        report_lines.append(f"Every odd word: {odd_words[:10]}{'...' if len(odd_words) > 10 else ''}")
        
        # Lowercase words
        report_lines.append(f"\nWords starting with lowercase: {lowercase_words[:20]}{'...' if len(lowercase_words) > 20 else ''}")
        
        # Punctuation marks
        report_lines.append(f"\nPunctuation marks: {punctuation[:30]}{'...' if len(punctuation) > 30 else ''}")
        
        # Smileys
        report_lines.append("\n--- SMILEY ANALYSIS ---")
        report_lines.append(f"Smileys found: {len(smileys)}")
        if smileys:
            report_lines.append(f"Smileys: {smileys}")
        
        # MAC addresses
        report_lines.append("\n--- MAC ADDRESS ANALYSIS ---")
        report_lines.append(f"MAC addresses found: {len(mac_addresses)}")
        if mac_addresses:
            for mac in mac_addresses:
                report_lines.append(f"  - {mac} (valid: {pattern_analyzer.is_valid_mac(mac)})")
        
        # Individual MAC validation (as per task)
        report_lines.append("\n--- MAC VALIDATION (user input) ---")
        mac_test = input("\nEnter MAC address to validate (default: aE:dC:cA:56:76:54): ").strip()
        if not mac_test:
            mac_test = "aE:dC:cA:56:76:54"
        is_valid = pattern_analyzer.is_valid_mac(mac_test)
        report_lines.append(f"MAC '{mac_test}' is {'VALID' if is_valid else 'INVALID'}")
        
        report_lines.append("\n" + "=" * 60)
        
        # 5. Print report
        final_report = "\n".join(report_lines)
        print("\n" + final_report)
        
        # 6. Save report to file
        result_file = "analysis_result.txt"
        result_handler = TextFileHandler(result_file)
        result_handler.write(final_report)
        
        # 7. Archive the result file
        archive_name = input("\nEnter archive name (default: result.zip): ").strip()
        if not archive_name:
            archive_name = "result.zip"
        
        archiver = ArchiveHandler(result_file, archive_name)
        archiver.create_zip()
        archiver.print_archive_info()
        
        print(f"\n[SUCCESS] Analysis complete!")
        print(f"  - Report saved to: {result_file}")
        print(f"  - Archive saved to: {archive_name}")
        
    except FileNotFoundError as e:
        print(f"[ERROR] File error: {e}")
    except ValueError as e:
        print(f"[ERROR] Data error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


def main() -> None:
    """
    Main program loop (Requirement 8).
    Provides repeatable execution without exiting.
    """
    while True:
        print("\n" + "=" * 40)
        print("    TEXT ANALYSIS SYSTEM (LAB 2)")
        print("=" * 40)
        print("1. Run Text Analysis")
        print("2. Back to Main Menu")
        print("-" * 40)
        
        choice = input("Your choice: ").strip()
        
        if choice == '1':
            run_analysis()
            input("\nPress Enter to continue...")
        elif choice == '2':
            print("Returning to main menu...")
            break
        else:
            print("[ERROR] Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()