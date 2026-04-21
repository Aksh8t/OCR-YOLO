"""
table_extractor.py - Reconstruct table structure from detected cell bounding boxes.
"""

import numpy as np

from config import ROW_Y_TOLERANCE


def sort_boxes(boxes):
    """
    Sort bounding boxes top-to-bottom, then left-to-right.
    Each box is a dict with key "bbox": [x1, y1, x2, y2].
    """
    return sorted(boxes, key=lambda b: (b["bbox"][1], b["bbox"][0]))


def group_into_rows(boxes, y_tolerance=ROW_Y_TOLERANCE):
    """
    Group sorted bounding boxes into rows based on Y-coordinate proximity.

    Returns:
        List of rows, where each row is a list of box dicts sorted left-to-right.
    """
    if not boxes:
        return []

    sorted_boxes = sort_boxes(boxes)
    rows = []
    current_row = [sorted_boxes[0]]
    current_y = sorted_boxes[0]["bbox"][1]

    for box in sorted_boxes[1:]:
        y = box["bbox"][1]
        if abs(y - current_y) <= y_tolerance:
            current_row.append(box)
        else:
            current_row.sort(key=lambda b: b["bbox"][0])
            rows.append(current_row)
            current_row = [box]
            current_y = y

    current_row.sort(key=lambda b: b["bbox"][0])
    rows.append(current_row)

    return rows


def extract_table(img, boxes, ocr_fn, lang="en", text_regions=None):
    """
    Extract a table as a 2D list of strings.

    Args:
        img:          Original BGR image.
        boxes:        List of table-cell bounding box dicts.
        ocr_fn:       Function(img, bbox, lang) -> dict with "text" key.
        lang:         Language code.
        text_regions: Pre-detected text regions to map to cells for speed.

    Returns:
        2D list (rows x cols) of cell text values.
    """
    rows = group_into_rows(boxes)
    table_data = []

    # Map text regions to cells if available for huge speedup
    if text_regions:
        for row in rows:
            row_data = []
            for cell in row:
                cx1, cy1, cx2, cy2 = cell["bbox"]
                cell_text = []
                for tr in text_regions:
                    if "bbox" not in tr: continue
                    tx1, ty1, tx2, ty2 = tr["bbox"]
                    center_x, center_y = (tx1 + tx2) / 2, (ty1 + ty2) / 2
                    if (cx1 - 2) <= center_x <= (cx2 + 2) and (cy1 - 2) <= center_y <= (cy2 + 2):
                        cell_text.append((center_y, center_x, tr.get("text", "")))
                
                cell_text.sort()
                text = " ".join([t[2] for t in cell_text]).strip()
                row_data.append(text)
            table_data.append(row_data)
        return table_data

    for row in rows:
        row_data = []
        for cell in row:
            result = ocr_fn(img, cell["bbox"], lang)
            text = result.get("text", "").strip()
            row_data.append(text)
        table_data.append(row_data)

    return table_data


def normalize_table(table_data):
    """
    Ensure all rows have the same number of columns by padding with empty strings.
    """
    if not table_data:
        return table_data

    max_cols = max(len(row) for row in table_data)
    for row in table_data:
        while len(row) < max_cols:
            row.append("")

    return table_data
