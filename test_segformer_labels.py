from transformers import (
    SegformerForSemanticSegmentation
)

model = SegformerForSemanticSegmentation.from_pretrained(
    "Pranilllllll/segformer-satellite-segementation"
)

print("\nClass Labels:\n")

for k, v in model.config.id2label.items():
    print(k, ":", v)