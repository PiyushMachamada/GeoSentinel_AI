from backend.models.changeformer.changeformer_model import ChangeFormerModel

model = ChangeFormerModel()

result = model.analyze_images(
"datasets/change_detection/before.jpg",
"datasets/change_detection/after.jpg"
)

print(result)
