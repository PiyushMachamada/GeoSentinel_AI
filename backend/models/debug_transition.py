import numpy as np

before = np.load(
    "backend/outputs/segmask_before.npy"
)

after = np.load(
    "backend/outputs/segmask_after.npy"
)

print(
    "Different Pixels:",
    np.sum(before != after)
)

print(
    "Total Pixels:",
    before.size
)