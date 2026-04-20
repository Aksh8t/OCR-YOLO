"""
detection.py — Text-region and table-cell detection.

Two strategies:
  1. PaddleOCR-based text detection (for documents)
  2. Contour-based table/cell detection (for tables)
"""

import cv2
import numpy as np

from config import MIN_CONTOUR_AREA, MIN_CELL_WIDTH, MIN_CELL_HEIGHT


def detect_text_regions_paddle(img: np.ndarray, ocr_instance) -> list:
    """
    Use PaddleOCR's detector to find text bounding boxes.

    Args:
        img: Original BGR image.
        ocr_instance: An initialised PaddleOCR object.

    Returns:
        List of dicts: { "bbox": [x1, y1, x2, y2], "type": "text" }
    """
    results = ocr_instance.ocr(img, cls=True)
    regions = []
    if results and results[0]:
        for line in results[0]:
            box = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            x1, y1 = int(min(xs)), int(min(ys))
            x2, y2 = int(max(xs)), int(max(ys))
            regions.append({
                "bbox": [x1, y1, x2, y2],
                "type": "text",
                "text": line[1][0],
                "confidence": line[1][1],
            })
    return regions


def detect_table_contours(img_processed: np.ndarray) -> list:
    """
    Detect table cells using morphological operations and contour detection.

    Args:
        img_processed: Preprocessed (thresholded) grayscale image.

    Returns:
        List of dicts: { "bbox": [x1, y1, x2, y2], "type": "table_cell" }
    """
    # Invert so that lines are white on black
    inverted = cv2.bitwise_not(img_processed)

    # Detect horizontal lines
    h_kernel_len = max(img_processed.shape[1] // 30, 10)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
    horizontal = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, h_kernel, iterations=2)

    # Detect vertical lines
    v_kernel_len = max(img_processed.shape[0] // 30, 10)
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))
    vertical = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, v_kernel, iterations=2)

    # Combine horizontal + vertical to get grid
    table_mask = cv2.add(horizontal, vertical)

    # Dilate slightly to close small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    table_mask = cv2.dilate(table_mask, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < MIN_CONTOUR_AREA:
            continue
        if w < MIN_CELL_WIDTH or h < MIN_CELL_HEIGHT:
            continue
        # Skip the outermost bounding box (whole table)
        if w > img_processed.shape[1] * 0.95 and h > img_processed.shape[0] * 0.95:
            continue
        cells.append({
            "bbox": [x, y, x + w, y + h],
            "type": "table_cell",
        })

    return cells


def detect_regions(img_original: np.ndarray, img_processed: np.ndarray,
                   ocr_instance=None, mode: str = "auto") -> dict:
    """
    Unified detection dispatcher.

    Args:
        img_original:  Original BGR image (for PaddleOCR).
        img_processed: Preprocessed threshold image (for contour detection).
        ocr_instance:  PaddleOCR instance (can be None if mode='table').
        mode:          'auto', 'document', or 'table'.

    Returns:
        dict with keys:
            - "text_regions":  list of text-region dicts
            - "table_cells":   list of table-cell dicts
            - "is_table":      bool — whether a table was detected
    """
    text_regions = []
    table_cells = []

    if mode in ("auto", "table"):
        table_cells = detect_table_contours(img_processed)

    if mode in ("auto", "document"):
        if ocr_instance is not None:
            text_regions = detect_text_regions_paddle(img_original, ocr_instance)

    is_table = len(table_cells) >= 4 

    return {
        "text_regions": text_regions,
        "table_cells": table_cells,
        "is_table": is_table,
    }
