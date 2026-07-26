from terratorch.models.encoder_decoder_factory import EncoderDecoderFactory

factory = EncoderDecoderFactory()

model = factory.build_model(
    task="segmentation",
    backbone="terratorch_prithvi_eo_v2_300",
    decoder="FCNDecoder",
    num_classes=7
)

print(type(model))
print()

print("Backbone:")
print(model.encoder)

print("\nModel attributes:")
for attr in dir(model):
    if "transform" in attr.lower() or "preprocess" in attr.lower() or "normalize" in attr.lower():
        print(attr)