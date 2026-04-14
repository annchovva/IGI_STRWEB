"""
Program Purpose: Text analysis using Regular Expressions
Lab4, Task1, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import re
from typing import List, Dict, Tuple, Any


class TextAnalyzerMixin:
    """Mixin providing utility methods for text processing."""
    
    def clean_whitespaces(self, text: str) -> str:
        """Remove extra whitespaces from text."""
        return re.sub(r'\s+', ' ', text).strip()


class BaseAnalyzer:
    """Base class demonstrating inheritance and polymorphism."""
    
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
        """Method for polymorphism - to be overridden."""
        return "Base Analysis Summary"


class WordAnalyzer(BaseAnalyzer, TextAnalyzerMixin):
    """Analyzes word-level patterns."""
    
    # Pattern for words (supports apostrophes and hyphens)
    WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:['-][A-Za-zА-Яа-яЁё]+)?")
    # Pattern for words starting with lowercase letter
    LOWERCASE_RE = re.compile(r"\b[a-zа-яё][A-Za-zА-Яа-яЁё']*\b")
    # Pattern for punctuation marks
    PUNCTUATION_RE = re.compile(r'[^\w\s]')

    def __init__(self, raw_text: str):
        super().__init__(raw_text)
        self._text = self.clean_whitespaces(raw_text)
        self._words = self.WORD_RE.findall(self._text)

    def __len__(self) -> int:
        """Magic method: returns number of words."""
        return len(self._words)

    def __str__(self) -> str:
        """Magic method: string representation."""
        return f"WordAnalyzer with {len(self)} words"

    def get_summary(self) -> str:
        """Polymorphism: overriding base method."""
        return f"Word count: {len(self)}"

    def get_lowercase_words(self) -> List[str]:
        """Return all words starting with lowercase letter."""
        return self.LOWERCASE_RE.findall(self._text)

    def get_punctuation(self) -> List[str]:
        """Return all punctuation marks in text."""
        return self.PUNCTUATION_RE.findall(self._text)

    def get_longest_word_info(self) -> Tuple[str, int]:
        """
        Get longest word and its position (1-based index).
        
        Returns:
            Tuple of (longest_word, position)
        """
        if not self._words:
            return ("", 0)
        longest = max(self._words, key=len)
        position = self._words.index(longest) + 1
        return longest, position

    def get_odd_words(self) -> List[str]:
        """Return words at odd positions (1st, 3rd, 5th, ...)."""
        return self._words[::2]

    def get_avg_word_length(self) -> float:
        """Calculate average word length in characters."""
        if not self._words:
            return 0.0
        return sum(len(w) for w in self._words) / len(self._words)


class SentenceAnalyzer(BaseAnalyzer):
    """Analyzes sentence types and statistics."""
    
    # Static attribute (Requirement 4)
    total_sentences_processed = 0

    def __init__(self, raw_text: str):
        super().__init__(raw_text)
        # Split sentences by . ! ? followed by space or end of string
        self._sentences = re.split(r'(?<=[.!?])\s+', raw_text.strip())
        SentenceAnalyzer.total_sentences_processed += len(self._sentences)

    def __len__(self) -> int:
        """Magic method: returns number of sentences."""
        return len(self._sentences)

    def get_summary(self) -> str:
        """Polymorphism: overriding base method."""
        return f"Sentence count: {len(self)}"

    def get_counts_by_type(self) -> Dict[str, int]:
        """
        Count sentences by type.
        
        Returns:
            Dictionary with 'decl' (declarative), 'int' (interrogative), 'imp' (imperative)
        """
        types = {"decl": 0, "int": 0, "imp": 0}
        for s in self._sentences:
            if s.endswith('?'):
                types["int"] += 1
            elif s.endswith('!'):
                types["imp"] += 1
            else:
                types["decl"] += 1
        return types

    def get_avg_sentence_length(self, words: List[str]) -> float:
        """
        Calculate average sentence length in characters (word characters only).
        
        Args:
            words: List of words from WordAnalyzer
            
        Returns:
            Average sentence length
        """
        if not self._sentences:
            return 0.0
        total_word_chars = sum(len(w) for w in words)
        return total_word_chars / len(self._sentences)


class SpecialPatternAnalyzer:
    """Utility class for MAC addresses and Smileys."""
    
    # Pattern for MAC address (case-insensitive)
    MAC_PATTERN = re.compile(r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$')
    
    # Pattern for finding MAC addresses in text
    MAC_FIND_PATTERN = re.compile(r'[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}', re.IGNORECASE)
    
    # Pattern for smileys: : or ;, then 0+ hyphens, then 1+ identical brackets
    SMILEY_PATTERN = re.compile(r'[:;]-*([\(\)\[\]])\1*')
    
    @classmethod
    def is_valid_mac(cls, mac: str) -> bool:
        """
        Check if string is a valid MAC address.
        
        Args:
            mac: MAC address string
            
        Returns:
            True if valid, False otherwise
        """
        return bool(cls.MAC_PATTERN.match(mac.strip()))
    
    @classmethod
    def find_mac_addresses(cls, text: str) -> List[str]:
        """
        Find all MAC addresses in text.
        
        Args:
            text: Text to search
            
        Returns:
            List of found MAC addresses
        """
        return cls.MAC_FIND_PATTERN.findall(text)
    
    @classmethod
    def count_smileys(cls, text: str) -> int:
        """
        Count smileys in text.
        
        Args:
            text: Text to search
            
        Returns:
            Number of smileys
        """
        return len(cls.SMILEY_PATTERN.findall(text))
    
    @classmethod
    def find_smileys(cls, text: str) -> List[str]:
        """
        Find all smileys in text.
        
        Args:
            text: Text to search
            
        Returns:
            List of found smileys
        """
        return [match.group() for match in cls.SMILEY_PATTERN.finditer(text)]