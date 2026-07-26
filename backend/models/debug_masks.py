import numpy as np

before = np.load(
    "backend/outputs/segmask_before.npy"
)

after = np.load(
    "backend/outputs/segmask_after.npy"
)

print(
    "Unique BEFORE classes:",
    np.unique(before)
)

print(
    "Unique AFTER classes:",
    np.unique(after)
)