import numpy as np
import time
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=False, lang='en', show_log=False)
img = np.zeros((100, 100, 3), dtype=np.uint8)
print("starting inference")
start = time.perf_counter()
res = ocr.ocr(img, cls=False)
print("inference done. time:", time.perf_counter()-start)
