import random

import numpy as np
import cv2
from PIL import Image

canvas = np.full((200, 200), 255, dtype=np.uint8)

random_points = [
    [random.randint(0, 199), random.randint(0, 199)],
    [random.randint(0, 199), random.randint(0, 199)],
    [random.randint(0, 199), random.randint(0, 199)],
]
contours = np.array(random_points, dtype=np.uint8)


cv2.fillPoly(canvas, pts=np.int32([contours]), color=0)

img = Image.fromarray(canvas)
img.show("test")

if __name__ == "__main__":
    pass
