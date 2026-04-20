"""
output_handler.py — Save extracted data to CSV, Excel, or plain text.
"""

import os
import csv

import pandas as pd

from config import OUTPUT_DIR


def _ensure_output_dir(output_dir: str = OUTPUT_DIR):
    """Create the output directory if it does not exist."""
    os.makedirs(output_dir, exist_ok=True)


def save_csv(data: list, filename: str = "output.csv", output_dir: str = OUTPUT_DIR) -> str:
    """
    Save a 2D list to a CSV file.

    Args:
        data:       2D list of strings (rows × cols).
        filename:   Output filename.
        output_dir: Directory to write to.

    Returns:
        Absolute path to the saved file.
    """
    _ensure_output_dir(output_dir)
    path = os.path.join(output_dir, filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

    return path


def save_excel(data: list, filename: str = "output.xlsx", output_dir: str = OUTPUT_DIR) -> str:
    """
    Save a 2D list to an Excel (.xlsx) file using pandas + openpyxl.

    Args:
        data:       2D list of strings (rows × cols).
        filename:   Output filename.
        output_dir: Directory to write to.

    Returns:
        Absolute path to the saved file.
    """
    _ensure_output_dir(output_dir)
    path = os.path.join(output_dir, filename)

    df = pd.DataFrame(data)
    # Use first row as header if it looks like one (optional)
    df.to_excel(path, index=False, header=False, engine="openpyxl")

    return path


def save_text(text: str, filename: str = "output.txt", output_dir: str = OUTPUT_DIR) -> str:
    """
    Save plain text to a .txt file.

    Args:
        text:       Extracted text content.
        filename:   Output filename.
        output_dir: Directory to write to.

    Returns:
        Absolute path to the saved file.
    """
    _ensure_output_dir(output_dir)
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return path
