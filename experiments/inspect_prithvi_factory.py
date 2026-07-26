from terratorch.models import PrithviModelFactory

print("\n=== PrithviModelFactory ===\n")

factory = PrithviModelFactory()

print(type(factory))

print("\nFactory Methods:\n")

for item in dir(factory):
    if not item.startswith("_"):
        print(item)