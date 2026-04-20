"""
generate_sample_images.py — Create sample test images for the OCR pipeline.

This script generates two sample images:
  1. A simple document with text paragraphs
  2. A table with rows and columns

These can be used to test the pipeline without needing external images.

Usage:
    python generate_sample_images.py
"""

import os
import numpy as np
import cv2

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_images")


def create_document_image(path: str):
    """Generate a simple document image with printed text."""
    width, height = 800, 600
    img = np.ones((height, width, 3), dtype=np.uint8) * 255  # white background

    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 0, 0)  # black text

    lines = [
        ("OCR Pipeline Test Document", 50, 1.0, 2),
        ("", 0, 0, 0),
        ("This is a sample document created for testing the", 100, 0.6, 1),
        ("Optical Character Recognition pipeline. The system", 135, 0.6, 1),
        ("uses PaddleOCR as the primary engine with Tesseract", 170, 0.6, 1),
        ("as a fallback for low-confidence results.", 205, 0.6, 1),
        ("", 0, 0, 0),
        ("Key Features:", 260, 0.7, 2),
        ("1. Preprocessing with OpenCV", 300, 0.55, 1),
        ("2. Text region detection", 335, 0.55, 1),
        ("3. Table structure extraction", 370, 0.55, 1),
        ("4. Multi-language support (English, Hindi)", 405, 0.55, 1),
        ("5. CSV and Excel output", 440, 0.55, 1),
        ("", 0, 0, 0),
        ("Date: 2025-04-20   Author: OCR Pipeline", 500, 0.5, 1),
    ]

    for text, y, scale, thickness in lines:
        if text:
            cv2.putText(img, text, (30, y), font, scale, color, thickness, cv2.LINE_AA)

    cv2.imwrite(path, img)
    print(f"  Created: {path}")


def create_table_image(path: str):
    """Generate a simple table image with grid lines and cell text."""
    width, height = 700, 400
    img = np.ones((height, width, 3), dtype=np.uint8) * 255  # white background

    # Table parameters
    x_start, y_start = 50, 50
    col_widths = [150, 150, 120, 130]
    row_height = 50
    num_rows = 5

    # Table data
    data = [
        ["Name", "Subject", "Score", "Grade"],
        ["Alice", "Math", "95", "A+"],
        ["Bob", "Science", "87", "A"],
        ["Charlie", "English", "76", "B+"],
        ["Diana", "History", "91", "A"],
    ]

    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (0, 0, 0)
    line_color = (0, 0, 0)
    header_bg = (220, 220, 220)

    # Draw header background
    total_width = sum(col_widths)
    cv2.rectangle(
        img,
        (x_start, y_start),
        (x_start + total_width, y_start + row_height),
        header_bg, -1,
    )

    # Draw cells and text
    for row_idx in range(num_rows):
        y = y_start + row_idx * row_height
        x = x_start

        for col_idx, col_w in enumerate(col_widths):
            # Draw cell border
            cv2.rectangle(img, (x, y), (x + col_w, y + row_height), line_color, 2)

            # Draw text
            if row_idx < len(data) and col_idx < len(data[row_idx]):
                text = data[row_idx][col_idx]
                scale = 0.5 if row_idx == 0 else 0.45
                thickness = 2 if row_idx == 0 else 1
                text_size = cv2.getTextSize(text, font, scale, thickness)[0]
                text_x = x + (col_w - text_size[0]) // 2
                text_y = y + (row_height + text_size[1]) // 2
                cv2.putText(img, text, (text_x, text_y), font, scale, text_color, thickness, cv2.LINE_AA)

            x += col_w

    cv2.imwrite(path, img)
    print(f"  Created: {path}")


def main():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    print("Generating sample images...")
    create_document_image(os.path.join(SAMPLE_DIR, "sample_document.png"))
    create_table_image(os.path.join(SAMPLE_DIR, "sample_table.png"))
    print("Done!")


if __name__ == "__main__":
    main()
