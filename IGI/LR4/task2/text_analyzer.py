"""
Program Purpose: Text analysis using Regular Expressions
Lab4, Task2, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import re
from typing import List, Tuple


class TextAnalyzerMixin:
    """Mixin providing utility methods for text processing."""
    
    def clean_whitespaces(self, text: str) -> str:
        """Remove extra whitespaces from text."""
        return re.sub(r'\s+', ' ', text).strip()


class BaseAnalyzer:
    """Base class for text analysis."""   
    def __init__(self, raw_text: str):
        self._raw_text = raw_text

    @property
    def raw_text(self) -> str:
        """Getter for raw text."""
        return self._raw_text

    @raw_text.setter
    def raw_text(self, value: str) -> None:
        """Setter for raw text with validation."""
        if not value:
            raise ValueError("Text cannot be empty")
        self._raw_text = value

    def get_summary(self) -> str:
        """Method for analysis summary."""
        return "Base Analysis Summary"


class WordAnalyzer(BaseAnalyzer, TextAnalyzerMixin):
    """Analyzes word-level patterns."""
    WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)?")
    LOWERCASE_RE = re.compile(r"\b[a-z][A-Za-z'-]*\b")
    PUNCTUATION_RE = re.compile(r'[^\w\s]')
    LETTER_PATTERN = re.compile(r"[A-Za-z]")
    WORD_PATTERN = re.compile(r"\b[A-Za-z]+\b")

    def __init__(self, raw_text: str):
        super().__init__(raw_text)
        self._text = self.clean_whitespaces(raw_text)
        self._words = self.WORD_RE.findall(self._text)

    def __len__(self) -> int:
        """Method returns number of words."""
        return len(self._words)

    def __str__(self) -> str:
        """Method string representation."""
        return f"WordAnalyzer with {len(self)} words"

    def get_summary(self) -> str:
        """Method for counting the number of words."""
        return f"Word count: {len(self)}"

    def get_lowercase_words(self) -> List[str]:
        """Return all words starting with lowercase letter."""
        return self.LOWERCASE_RE.findall(self._text)

    def get_punctuation(self) -> List[str]:
        """Return all punctuation marks in text."""
        return self.PUNCTUATION_RE.findall(self._text)

    def get_longest_word_info(self) -> Tuple[str, int]:
        """Get longest word and its position."""
        if not self._words:
            return ("", 0)
        longest = max(self._words, key=len)
        position = self._words.index(longest) + 1
        return longest, position

    def get_odd_words(self) -> List[str]:
        """Return words at odd positions."""
        return self._words[::2]

    def count_avg_len_word(self) -> float:
        """Count average word length in characters."""
        words = self.WORD_PATTERN.findall(self._text)
        if not words:
            return 0.0
        letters_count = len(self.LETTER_PATTERN.findall(self._text))
        return letters_count / len(words)


class SentenceAnalyzer(BaseAnalyzer):
    """Analyzes sentence types and statistics."""
    total_sentences_processed = 0
    SENTENCE_PATTERN = re.compile(r"[.!?]")
    QUESTION_PATTERN = re.compile(r"\?")
    EXCLAMATION_PATTERN = re.compile(r"!")
    DECLARATIVE_PATTERN = re.compile(r"\.")
    LETTER_PATTERN = re.compile(r"[A-Za-z]")

    def __init__(self, raw_text: str):
        super().__init__(raw_text)
        SentenceAnalyzer.total_sentences_processed += self.count_all_sentences()

    def __len__(self) -> int:
        """Method returns number of sentences."""
        return self.count_all_sentences()

    def get_summary(self) -> str:
        """Method for counting the number of sentences."""
        return f"Sentence count: {len(self)}"

    def count_all_sentences(self):
        """Count all sentences in the text."""
        return len(self.SENTENCE_PATTERN.findall(self.raw_text))

    def count_question_sentences(self):
        """Count question sentences."""
        return len(self.QUESTION_PATTERN.findall(self.raw_text))

    def count_exclamation_sentences(self):
        """Count exclamation sentences."""
        return len(self.EXCLAMATION_PATTERN.findall(self.raw_text))

    def count_declarative_sentences(self):
        """Count declarative sentences."""
        return len(self.DECLARATIVE_PATTERN.findall(self.raw_text))

    def count_avg_len_sentence(self):
        """Count average sentence length in characters."""
        sentence_count = self.count_all_sentences()
        if sentence_count == 0:
            return 0.0
        letters_count = len(self.LETTER_PATTERN.findall(self.raw_text))
        return letters_count / sentence_count


class SpecialPatternAnalyzer:
    """Utility class for MAC addresses and smileys."""   
    MAC_PATTERN = re.compile(r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$')
    MAC_FIND_PATTERN = re.compile(r'[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}')
    SMILEY_PATTERN = re.compile(r'[:;]-*(?:\(+|\)+|\[+|\]+)')
    
    def __init__(self, text: str = ""):
        self.text = text
    
    @classmethod
    def is_valid_mac(cls, mac: str) -> bool:
        """Check if string is a valid MAC address."""
        return bool(cls.MAC_PATTERN.match(mac.strip()))
    
    @classmethod
    def find_mac_addresses(cls, text: str) -> List[str]:
        """Find all MAC addresses in text."""
        return [match.group() for match in cls.MAC_FIND_PATTERN.finditer(text)]
    
    @classmethod
    def find_smileys(cls, text: str) -> List[str]:
        """Find all smileys in text."""
        return [match.group() for match in cls.SMILEY_PATTERN.finditer(text)]

    def count_smiles(self):
        """Count smileys in the text."""
        return len(self.SMILEY_PATTERN.findall(self.text))
