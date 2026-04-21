import time
from paddleocr import PaddleOCR
import cv2

print("Initializing...")
ocr = PaddleOCR(use_angle_cls=False, lang='en', show_log=False, cpu_threads=1)
img = cv2.imread('sample_images/test.png')
print(f"Image shape: {img.shape}")
start = time.time()
res = ocr.ocr(img, cls=False)
print(f"Time taken: {time.time() - start:.2f}s")
