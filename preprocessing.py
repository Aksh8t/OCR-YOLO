"""
preprocessing.py — Image preprocessing utilities using OpenCV.

Steps:
  1. Load image
  2. Resize (proportional)
  3. Convert to grayscale
  4. Apply thresholding (Otsu / adaptive)
  5. Remove noise (Gaussian / median blur)
  6. Optional: Canny edge detection
"""

import cv2
import numpy as np

from config import (
    MAX_IMAGE_WIDTH,
    THRESHOLD_METHOD,
    NOISE_REMOVAL_METHOD,
    BLUR_KERNEL_SIZE,
    CANNY_LOW,
    CANNY_HIGH,
)


def load_image(path: str) -> np.ndarray:
    """Load an image from disk. Raises FileNotFoundError if missing."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return img


def resize_image(img: np.ndarray, max_width: int = MAX_IMAGE_WIDTH) -> np.ndarray:
    """Resize image proportionally so that width ≤ max_width."""
    h, w = img.shape[:2]
    if w <= max_width:
        return img
    scale = max_width / w
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convert a BGR image to grayscale."""
    if len(img.shape) == 2:
        return img  # already grayscale
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def apply_threshold(img_gray: np.ndarray, method: str = THRESHOLD_METHOD) -> np.ndarray:
    """
    Apply thresholding to a grayscale image.
    Methods: 'otsu' (default), 'adaptive'.
    """
    if method == "otsu":
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == "adaptive":
        thresh = cv2.adaptiveThreshold(
            img_gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )
    else:
        raise ValueError(f"Unknown threshold method: {method}")
    return thresh


def remove_noise(img: np.ndarray, method: str = NOISE_REMOVAL_METHOD) -> np.ndarray:
    """
    Remove noise from an image.
    Methods: 'gaussian' (default), 'median'.
    """
    k = BLUR_KERNEL_SIZE
    if method == "gaussian":
        return cv2.GaussianBlur(img, (k, k), 0)
    elif method == "median":
        return cv2.medianBlur(img, k)
    else:
        raise ValueError(f"Unknown noise removal method: {method}")


def detect_edges(img_gray: np.ndarray) -> np.ndarray:
    """Apply Canny edge detection to a grayscale image."""
    return cv2.Canny(img_gray, CANNY_LOW, CANNY_HIGH)


def preprocess(
    image_path: str,
    do_threshold: bool = True,
    do_noise_removal: bool = True,
    do_edge_detection: bool = False,
) -> dict:
    """
    Full preprocessing pipeline.

    Returns a dict with:
        - 'original':   original loaded image (resized)
        - 'gray':       grayscale version
        - 'processed':  thresholded / denoised version
        - 'edges':      edge map (if requested)
    """
    img = load_image(image_path)
    img = resize_image(img)
    gray = to_grayscale(img)

    processed = gray.copy()
    if do_noise_removal:
        processed = remove_noise(processed)
    if do_threshold:
        processed = apply_threshold(processed)

    result = {
        "original": img,
        "gray": gray,
        "processed": processed,
    }

    if do_edge_detection:
        result["edges"] = detect_edges(gray)

    return result
