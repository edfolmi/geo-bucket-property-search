import re
from typing import List


class LocationNormalizer:
    """
    Handles location name normalization for consistent matching.
    Removes noise, standardizes format, and handles common variations.
    """
    
    # Common location suffixes to remove (Nigerian context)
    COMMON_SUFFIXES = {
        'lagos', 'nigeria', 'ng',
        'lga', 'state', 'area'
    }
    
    # Location name replacements for standardization
    REPLACEMENTS = {
        'str': 'street',
        'rd': 'road',
        'ave': 'avenue',
        'st': 'street',
    }

    @classmethod
    def normalize(cls, name: str) -> str:
        """
        Normalize a location name for consistent matching.
        
        Process:
        1. Convert to lowercase
        2. Remove special characters
        3. Remove common suffixes
        4. Collapse whitespace
        5. Apply standardizations
        
        Args:
            name: Original location name
            
        Returns:
            Normalized location name
            
        Examples:
            "Sangotedo, Ajah" -> "sangotedo ajah"
            "sangotedo lagos" -> "sangotedo"
            "Sangotedo" -> "sangotedo"
        """
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove special characters, keep alphanumeric and spaces
        normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
        
        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common suffixes
        words = normalized.split()
        filtered_words = [w for w in words if w not in cls.COMMON_SUFFIXES]
        
        # If we filtered out everything, keep the original
        if not filtered_words:
            filtered_words = normalized.split()[:2]  # Keep first 2 words
        
        normalized = ' '.join(filtered_words)
        
        # Apply replacements
        for old, new in cls.REPLACEMENTS.items():
            normalized = normalized.replace(f' {old} ', f' {new} ')
        
        return normalized.strip()

    @classmethod
    def generate_trigrams(cls, text: str) -> List[str]:
        """
        Generate trigrams from text for fuzzy matching.
        
        Args:
            text: Input text
            
        Returns:
            List of trigrams
            
        Example:
            "sangotedo" -> ["san", "ang", "ngo", "got", "ote", "ted", "edo"]
        """
        if not text or len(text) < 3:
            return []
        
        text = text.lower().replace(' ', '')
        trigrams = []
        
        for i in range(len(text) - 2):
            trigrams.append(text[i:i+3])
        
        return trigrams

    @classmethod
    def generate_variants(cls, name: str) -> List[str]:
        """
        Generate common variants of a location name.
        
        Args:
            name: Original location name
            
        Returns:
            List of possible variants
            
        Example:
            "Sangotedo" -> ["sangotedo", "sangotedo lagos", "sangotedo ajah"]
        """
        normalized = cls.normalize(name)
        variants = {normalized}
        
        # Add original (case-insensitive)
        variants.add(name.lower().strip())
        
        # Add with common area suffixes (Nigerian context)
        common_areas = ['lagos', 'ajah', 'lekki']
        for area in common_areas:
            if area not in normalized:
                variants.add(f"{normalized} {area}")
        
        return list(variants)

    @classmethod
    def metaphone_simple(cls, text: str) -> str:
        """
        Simple phonetic encoding (metaphone-like).
        Helps match similar-sounding names.
        
        Args:
            text: Input text
            
        Returns:
            Phonetic encoding
            
        Example:
            "sangotedo" -> "SNKTD"
        """
        if not text:
            return ""
        
        text = text.upper()
        
        # Remove vowels except at start
        if len(text) > 1:
            result = text[0] + re.sub(r'[AEIOU]', '', text[1:])
        else:
            result = text
        
        # Remove duplicate consonants
        result = re.sub(r'(.)\1+', r'\1', result)
        
        # Common phonetic replacements
        replacements = {
            'PH': 'F',
            'CK': 'K',
            'SH': 'X',
            'CH': 'X',
        }
        
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result[:10]  # Limit length

    @classmethod
    def calculate_similarity(cls, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using trigram overlap.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not str1 or not str2:
            return 0.0
        
        trigrams1 = set(cls.generate_trigrams(str1))
        trigrams2 = set(cls.generate_trigrams(str2))
        
        if not trigrams1 or not trigrams2:
            return 1.0 if str1.lower() == str2.lower() else 0.0
        
        intersection = len(trigrams1 & trigrams2)
        union = len(trigrams1 | trigrams2)
        
        return intersection / union if union > 0 else 0.0
