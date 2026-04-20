"""
ocr_engine.py — OCR extraction using PaddleOCR (primary) and Tesseract (fallback).
"""

import cv2
import numpy as np

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

try:
    import pytesseract
    # Check if the Tesseract binary is actually accessible
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
    except pytesseract.TesseractNotFoundError:
        TESSERACT_AVAILABLE = False
except ImportError:
    TESSERACT_AVAILABLE = False

from config import OCR_CONFIDENCE_THRESHOLD, LANG_MAP


# ─── PaddleOCR Singleton ─────────────────────────────────────────────────────

_paddle_instances: dict = {}


def get_paddle_ocr(lang: str = "en") -> "PaddleOCR":
    """
    Return a cached PaddleOCR instance for the given language.
    Models are downloaded on first use (~150 MB).
    """
    if not PADDLE_AVAILABLE:
        raise ImportError("paddleocr is not installed. Run: pip install paddleocr paddlepaddle")

    paddle_lang = LANG_MAP.get(lang, {}).get("paddle", "en")
    if paddle_lang not in _paddle_instances:
        _paddle_instances[paddle_lang] = PaddleOCR(
            use_angle_cls=True,
            lang=paddle_lang,
            show_log=False,
        )
    return _paddle_instances[paddle_lang]


# ─── PaddleOCR ────────────────────────────────────────────────────────────────

def ocr_paddleocr(img: np.ndarray, lang: str = "en") -> list:
    """
    Run PaddleOCR on an image (full or cropped region).

    Returns:
        List of dicts: { "text": str, "confidence": float, "bbox": [...] }
    """
    ocr = get_paddle_ocr(lang)
    results = ocr.ocr(img, cls=True)
    extracted = []
    if results and results[0]:
        for line in results[0]:
            box = line[0]
            text = line[1][0]
            conf = line[1][1]
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            extracted.append({
                "text": text,
                "confidence": conf,
                "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
            })
    return extracted


# ─── Tesseract ────────────────────────────────────────────────────────────────

def ocr_tesseract(img: np.ndarray, lang: str = "en") -> str:
    """
    Run Tesseract OCR on an image.

    Returns:
        Extracted text string.
    """
    if not TESSERACT_AVAILABLE:
        return ""

    tess_lang = LANG_MAP.get(lang, {}).get("tesseract", "eng")

    # Convert to grayscale if needed
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(img, lang=tess_lang)
    return text.strip()


# ─── Unified Extraction ──────────────────────────────────────────────────────

def extract_text(
    img: np.ndarray,
    lang: str = "en",
    use_tesseract_fallback: bool = True,
) -> dict:
    """
    Extract text from an image using PaddleOCR, with optional Tesseract fallback.

    Returns:
        dict with:
            - "text":       combined text string
            - "details":    list of per-line results from PaddleOCR
            - "engine":     "paddleocr" or "tesseract"
            - "confidence": average confidence score
    """
    # Try PaddleOCR first
    if PADDLE_AVAILABLE:
        try:
            details = ocr_paddleocr(img, lang)
        except Exception:
            details = []
        if details:
            avg_conf = sum(d["confidence"] for d in details) / len(details)
            combined = "\n".join(d["text"] for d in details)

            if avg_conf >= OCR_CONFIDENCE_THRESHOLD:
                return {
                    "text": combined,
                    "details": details,
                    "engine": "paddleocr",
                    "confidence": round(avg_conf, 4),
                }

            # Low confidence — try Tesseract as alternative
            if use_tesseract_fallback and TESSERACT_AVAILABLE:
                tess_text = ocr_tesseract(img, lang)
                # Simple heuristic: prefer longer output (more content captured)
                if tess_text and len(tess_text) > len(combined) * 0.8:
                    return {
                        "text": tess_text,
                        "details": [],
                        "engine": "tesseract",
                        "confidence": None,
                    }

            # Return PaddleOCR result anyway
            return {
                "text": combined,
                "details": details,
                "engine": "paddleocr",
                "confidence": round(avg_conf, 4),
            }

    # PaddleOCR unavailable or returned nothing — use Tesseract
    if TESSERACT_AVAILABLE:
        tess_text = ocr_tesseract(img, lang)
        if tess_text:
            return {
                "text": tess_text,
                "details": [],
                "engine": "tesseract",
                "confidence": None,
            }

    # No engine produced results — return empty instead of crashing
    return {"text": "", "details": [], "engine": "none", "confidence": 0.0}


def extract_text_from_region(
    img: np.ndarray,
    bbox: list,
    lang: str = "en",
    padding: int = 2,
) -> dict:
    """
    Crop a region from the image and run OCR on it.

    Args:
        img:     Full image (BGR).
        bbox:    [x1, y1, x2, y2].
        lang:    Language code.
        padding: Extra pixels around the crop.

    Returns:
        Same dict as extract_text().
    """
    h, w = img.shape[:2]
    x1 = max(0, bbox[0] - padding)
    y1 = max(0, bbox[1] - padding)
    x2 = min(w, bbox[2] + padding)
    y2 = min(h, bbox[3] + padding)
    crop = img[y1:y2, x1:x2]

    if crop.size == 0:
        return {"text": "", "details": [], "engine": "none", "confidence": 0.0}

    return extract_text(crop, lang, use_tesseract_fallback=True)
