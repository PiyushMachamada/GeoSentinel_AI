import ever as er
import torch

from torchange.models.changen2 import (
    s1_init_s1c1_changestar_vitb_1x256
)

print("Loading ChangeStar model...")

model = s1_init_s1c1_changestar_vitb_1x256()

print("Model loaded successfully!")

model.eval()

print("Device:", er.auto_device())

print("\n================ MODEL =================")
print(model)

print("\n================ DUMMY TEST ================")

x = torch.randn(1, 6, 256, 256)

with torch.no_grad():
    out = model(x)

print(type(out))
print(out.change_prediction.shape)
print(out.t1_semantic_prediction.shape)
print(out.t2_semantic_prediction.shape)

print(type(out))
print(out.change_prediction.shape)