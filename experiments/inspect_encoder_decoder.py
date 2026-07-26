from terratorch.models import EncoderDecoderFactory

factory = EncoderDecoderFactory()

print("\n=== EncoderDecoderFactory ===\n")

for item in dir(factory):
    if not item.startswith("_"):
        print(item)