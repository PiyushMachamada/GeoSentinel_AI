from terratorch.models.backbones import BACKBONE_REGISTRY

print("\nAvailable Backbones:\n")

for name in BACKBONE_REGISTRY:
    print(name)