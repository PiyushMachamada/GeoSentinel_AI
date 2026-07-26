import cv2
import numpy as np

mask = cv2.imread(
    "backend/outputs/changeformer_result.png",
    cv2.IMREAD_GRAYSCALE
)

print(
    "Shape:",
    mask.shape
)

print(
    "Unique values:",
    np.unique(mask)
)

print(
    "White pixels:",
    np.sum(mask > 0)
)

print(
    "Total pixels:",
    mask.size
)