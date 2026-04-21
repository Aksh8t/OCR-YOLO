import easyocr
import time
import numpy as np
print("Init...")
reader = easyocr.Reader(['en'], gpu=False)
img = np.zeros((800, 620, 3), dtype=np.uint8)
print("Inferencing...")
start = time.time()
res = reader.readtext(img)
print("Done. Time:", time.time() - start)
