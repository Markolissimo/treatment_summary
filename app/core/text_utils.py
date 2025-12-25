"""Text normalization utilities for ensuring ASCII-safe output."""

import unicodedata


def normalize_to_ascii(text: str) -> str:
    """
    Normalize unicode text to ASCII-safe equivalents.
    
    Replaces common unicode characters with ASCII equivalents:
    - En-dash (–) → hyphen (-)
    - Em-dash (—) → double hyphen (--)
    - Curly quotes (" " ' ') → straight quotes (" ')
    - Ellipsis (…) → three dots (...)
    - Other unicode → closest ASCII equivalent
    
    Args:
        text: Input text that may contain unicode characters
        
    Returns:
        ASCII-normalized text
    """
    if not text:
        return text
    
    # Replace common unicode punctuation with ASCII equivalents
    replacements = {
        '\u2013': '-',      # en-dash
        '\u2014': '--',     # em-dash
        '\u2018': "'",      # left single quote
        '\u2019': "'",      # right single quote
        '\u201c': '"',      # left double quote
        '\u201d': '"',      # right double quote
        '\u2026': '...',    # ellipsis
        '\u00a0': ' ',      # non-breaking space
        '\u2022': '*',      # bullet
        '\u00b0': ' deg',   # degree symbol
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # Normalize remaining unicode to closest ASCII equivalent
    # NFD = decompose, then filter out combining marks
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    return text


def normalize_treatment_output(output: dict) -> dict:
    """
    Normalize all text fields in a treatment summary output to ASCII.
    
    Args:
        output: Dictionary containing treatment summary fields
        
    Returns:
        Dictionary with normalized text fields
    """
    if isinstance(output, dict):
        normalized = {}
        for key, value in output.items():
            if isinstance(value, str):
                normalized[key] = normalize_to_ascii(value)
            elif isinstance(value, list):
                normalized[key] = [
                    normalize_to_ascii(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                normalized[key] = value
        return normalized
    return output
