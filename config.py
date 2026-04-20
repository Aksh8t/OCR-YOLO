"""
config.py — Shared constants and configuration for the OCR pipeline.
"""

import os

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
SAMPLE_DIR = os.path.join(PROJECT_ROOT, "sample_images")

# ─── Preprocessing ────────────────────────────────────────────────────────────
MAX_IMAGE_WIDTH = 1024          # Resize to this width (maintains aspect ratio)
THRESHOLD_METHOD = "otsu"       # "otsu" or "adaptive"
NOISE_REMOVAL_METHOD = "gaussian"  # "gaussian" or "median"
BLUR_KERNEL_SIZE = 5            # Must be odd
CANNY_LOW = 50
CANNY_HIGH = 150

# ─── Detection ────────────────────────────────────────────────────────────────
MIN_CONTOUR_AREA = 500          # Minimum area for a valid table-cell contour
MIN_CELL_WIDTH = 20             # Minimum width (px) for a table cell
MIN_CELL_HEIGHT = 10            # Minimum height (px) for a table cell

# ─── OCR ──────────────────────────────────────────────────────────────────────
PADDLE_LANG = "en"              # Default PaddleOCR language
TESSERACT_LANG = "eng"          # Default Tesseract language
OCR_CONFIDENCE_THRESHOLD = 0.5  # Fall back to Tesseract below this confidence

# Language mapping: user-friendly → PaddleOCR / Tesseract codes
LANG_MAP = {
    "en":  {"paddle": "en",  "tesseract": "eng"},
    "hi":  {"paddle": "hi",  "tesseract": "hin"},
    "ch":  {"paddle": "ch",  "tesseract": "chi_sim"},
    "fr":  {"paddle": "fr",  "tesseract": "fra"},
    "de":  {"paddle": "german", "tesseract": "deu"},
}

# ─── Table Extraction ────────────────────────────────────────────────────────
ROW_Y_TOLERANCE = 15            # Pixel tolerance for grouping boxes into rows

# ─── Output ───────────────────────────────────────────────────────────────────
DEFAULT_OUTPUT_FORMAT = "csv"   # "csv", "excel", or "text"
