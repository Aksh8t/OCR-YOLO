"""
pipeline.py — Main orchestrator that ties all modules together.
"""

import os
import time

from preprocessing import preprocess
from detection import detect_regions
from ocr_engine import (
    get_paddle_ocr,
    extract_text,
    extract_text_from_region,
    PADDLE_AVAILABLE,
)
from table_extractor import extract_table, normalize_table
from postprocessing import postprocess, postprocess_table
from output_handler import save_csv, save_excel, save_text
from config import OUTPUT_DIR


def run_pipeline(
    image_path: str,
    mode: str = "auto",
    lang: str = "en",
    output_dir: str = OUTPUT_DIR,
    save_formats: list = None,
) -> dict:
    """
    Execute the full OCR pipeline.

    Args:
        image_path:   Path to the input image.
        mode:         'auto', 'document', or 'table'.
        lang:         Language code ('en', 'hi', 'ch', etc.).
        output_dir:   Directory for output files.
        save_formats: List of formats to save: ['csv', 'excel', 'text'].
                      Defaults to ['csv', 'text'].

    Returns:
        dict with:
            - "mode_used":     'document' or 'table'
            - "text":          extracted text (for document mode)
            - "table_data":    2D list (for table mode)
            - "output_files":  list of saved file paths
            - "engine":        OCR engine used
            - "confidence":    average confidence
            - "time_seconds":  total processing time
    """
    if save_formats is None:
        save_formats = ["csv", "text"]

    start_time = time.time()
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # ── Step 1: Preprocess ────────────────────────────────────────────────
    print(f"[1/6] Preprocessing: {image_path}")
    images = preprocess(image_path)
    img_original = images["original"]
    img_processed = images["processed"]

    # ── Step 2: Detection ─────────────────────────────────────────────────
    print("[2/6] Detecting regions...")
    ocr_instance = get_paddle_ocr(lang) if PADDLE_AVAILABLE else None
    detection = detect_regions(img_original, img_processed, ocr_instance, mode)

    is_table = detection["is_table"]
    mode_used = "table" if (mode == "table" or (mode == "auto" and is_table)) else "document"

    result = {
        "mode_used": mode_used,
        "text": "",
        "table_data": [],
        "output_files": [],
        "engine": "",
        "confidence": None,
        "time_seconds": 0,
    }

    # ── Step 3 & 4: OCR + Table Extraction ────────────────────────────────
    if mode_used == "table":
        print(f"[3/6] Table detected ({len(detection['table_cells'])} cells). Extracting...")
        table_raw = extract_table(
            img_original,
            detection["table_cells"],
            extract_text_from_region,
            lang,
        )
        table_raw = normalize_table(table_raw)

        # ── Step 5: Post-process ──────────────────────────────────────────
        print("[4/6] Post-processing table data...")
        table_data = postprocess_table(table_raw)

        # Filter out completely empty rows
        table_data = [row for row in table_data if any(cell.strip() for cell in row)]

        result["table_data"] = table_data
        result["engine"] = "paddleocr" if PADDLE_AVAILABLE else "tesseract"

        # ── Step 6: Output ────────────────────────────────────────────────
        print("[5/6] Saving outputs...")
        if "csv" in save_formats:
            path = save_csv(table_data, f"{base_name}_table.csv", output_dir)
            result["output_files"].append(path)
            print(f"       → CSV: {path}")

        if "excel" in save_formats:
            path = save_excel(table_data, f"{base_name}_table.xlsx", output_dir)
            result["output_files"].append(path)
            print(f"       → Excel: {path}")

        if "text" in save_formats:
            # Also save a text representation
            text_repr = "\n".join(["\t".join(row) for row in table_data])
            path = save_text(text_repr, f"{base_name}_table.txt", output_dir)
            result["output_files"].append(path)
            print(f"       → Text: {path}")

    else:
        # Document mode
        print("[3/6] Extracting text from document...")

        # If PaddleOCR detection already found text regions, combine them
        if detection["text_regions"]:
            all_text = []
            confidences = []
            for region in detection["text_regions"]:
                all_text.append(region["text"])
                confidences.append(region["confidence"])
            combined = "\n".join(all_text)
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            result["engine"] = "paddleocr"
            result["confidence"] = round(avg_conf, 4)
        else:
            # Full-image OCR
            ocr_result = extract_text(img_original, lang)
            combined = ocr_result["text"]
            result["engine"] = ocr_result["engine"]
            result["confidence"] = ocr_result["confidence"]

        # ── Step 5: Post-process ──────────────────────────────────────────
        print("[4/6] Post-processing text...")
        cleaned = postprocess(combined)
        result["text"] = cleaned

        # ── Step 6: Output ────────────────────────────────────────────────
        print("[5/6] Saving outputs...")
        if "text" in save_formats:
            path = save_text(cleaned, f"{base_name}_text.txt", output_dir)
            result["output_files"].append(path)
            print(f"       → Text: {path}")

        if "csv" in save_formats:
            # Save each line as a row
            lines = [[line] for line in cleaned.split("\n") if line.strip()]
            path = save_csv(lines, f"{base_name}_text.csv", output_dir)
            result["output_files"].append(path)
            print(f"       → CSV: {path}")

    elapsed = round(time.time() - start_time, 2)
    result["time_seconds"] = elapsed
    print(f"[6/6] Done! ({elapsed}s)")

    return result
