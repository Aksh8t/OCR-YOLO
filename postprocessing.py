"""
postprocessing.py — Text cleaning and merging utilities.
"""

import re


def clean_text(text: str) -> str:
    """
    Clean extracted text:
      - Remove non-printable characters
      - Collapse multiple spaces / tabs into one
      - Strip leading/trailing whitespace per line
    """
    # Remove non-printable chars (keep newlines, tabs, normal chars)
    text = re.sub(r'[^\x20-\x7E\n\t\u0900-\u097F\u0980-\u09FF\u00C0-\u024F]', '', text)
    # Collapse multiple spaces/tabs
    text = re.sub(r'[ \t]+', ' ', text)
    # Strip each line
    lines = [line.strip() for line in text.split('\n')]
    # Remove empty lines that are consecutive
    cleaned = []
    prev_empty = False
    for line in lines:
        if line == '':
            if not prev_empty:
                cleaned.append(line)
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    return '\n'.join(cleaned).strip()


def merge_broken_words(text: str) -> str:
    """
    Rejoin words broken by hyphens at line breaks.
    E.g., 'docu-\\nment' → 'document'
    """
    text = re.sub(r'-\s*\n\s*', '', text)
    return text


def handle_multiline_cells(text: str) -> str:
    """
    Collapse multi-line cell content into a single line.
    Replaces internal newlines with spaces.
    """
    return re.sub(r'\n+', ' ', text).strip()


def postprocess(text: str, is_cell: bool = False) -> str:
    """
    Full post-processing pipeline for extracted text.

    Args:
        text:    Raw extracted text.
        is_cell: If True, collapse multi-line content (for table cells).

    Returns:
        Cleaned text string.
    """
    text = merge_broken_words(text)
    text = clean_text(text)
    if is_cell:
        text = handle_multiline_cells(text)
    return text


def postprocess_table(table_data: list) -> list:
    """
    Apply post-processing to every cell in a 2D table.
    """
    return [
        [postprocess(cell, is_cell=True) for cell in row]
        for row in table_data
    ]
