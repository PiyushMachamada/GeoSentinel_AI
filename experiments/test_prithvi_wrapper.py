from backend.models.prithvi.prithvi_model import PrithviModel

model = PrithviModel()

stats = model.segment("datasets/geotiff/rgb2.tif")

print(stats)