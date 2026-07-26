import os
import terratorch

root = os.path.dirname(terratorch.__file__)

print("\nTerratorch Root:")
print(root)

print("\nSearching for interesting files...\n")

keywords = [
    "worldcover",
    "dynamicworld",
    "landcover",
    "prithvi",
    "checkpoint",
    "pretrain",
    "segmentation",
]

for folder, _, files in os.walk(root):
    for file in files:

        name = file.lower()

        for keyword in keywords:
            if keyword in name:
                print(os.path.join(folder, file))
                break