from terratorch.models import MODEL_FACTORY_REGISTRY

print("\nAvailable Model Factories:\n")

for name in MODEL_FACTORY_REGISTRY:
    print(name)