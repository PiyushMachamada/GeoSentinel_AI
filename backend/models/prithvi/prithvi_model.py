from terratorch.models.encoder_decoder_factory import EncoderDecoderFactory

import torch
import rasterio
import numpy as np
import cv2
import os

from PIL import Image

from .class_mapping import (
    CLASS_NAMES,
    CLASS_COLORS
)


class PrithviModel:

    def __init__(self):

        print("=" * 60)
        print("Loading Prithvi EO 2.0 Model...")
        print("=" * 60)

        # --------------------------------------------------
        # DEVICE
        # --------------------------------------------------

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(f"Using device: {self.device}")

        # --------------------------------------------------
        # CREATE FACTORY
        # --------------------------------------------------

        self.factory = EncoderDecoderFactory()

        # --------------------------------------------------
        # BUILD MODEL
        # --------------------------------------------------

        self.model = self.factory.build_model(
            task="segmentation",
            backbone="terratorch_prithvi_eo_v2_300",
            decoder="FCNDecoder",
            num_classes=7
        )

        self.model.to(self.device)

        self.model.eval()

        print("\nPrithvi Model Loaded Successfully.")

        print("\nConfiguration")
        print("-" * 40)
        print("Backbone : terratorch_prithvi_eo_v2_300")
        print("Decoder  : FCNDecoder")
        print("Classes  :", len(CLASS_NAMES))

        print("\nClass Mapping")
        print("-" * 40)

        for idx, name in CLASS_NAMES.items():
            print(f"{idx} : {name}")

        print("=" * 60)

    # ======================================================
    # IMAGE LOADER
    # ======================================================

    def load_image(self, image_path):

        """
        Reads either:

        • GeoTIFF
        • PNG
        • JPG
        • JPEG

        Returns

        image
        original_height
        original_width
        original_rgb
        """

        extension = os.path.splitext(
            image_path
        )[1].lower()

        # ---------------------------------------------
        # GEOTIFF
        # ---------------------------------------------

        if extension in [
            ".tif",
            ".tiff"
        ]:

            with rasterio.open(image_path) as src:

                image = src.read().astype(
                    np.float32
                )

            original_height = image.shape[1]
            original_width = image.shape[2]

            rgb = image[:3]

            rgb = np.moveaxis(
                rgb,
                0,
                -1
            )

            rgb = np.clip(
                rgb,
                0,
                255
            ).astype(np.uint8)

            return (
                image,
                original_height,
                original_width,
                rgb
            )

        # ---------------------------------------------
        # NORMAL IMAGE
        # ---------------------------------------------

        image = Image.open(
            image_path
        ).convert("RGB")

        rgb = np.array(image)

        image = rgb.astype(
            np.float32
        )

        image = np.transpose(
            image,
            (
                2,
                0,
                1
            )
        )

        original_height = image.shape[1]
        original_width = image.shape[2]

        return (
            image,
            original_height,
            original_width,
            rgb
        )
        
            # ======================================================
    # PREPROCESS IMAGE
    # ======================================================

    def preprocess_image(self, image):
        """
        Prepare image for Prithvi EO 2.0.

        Input:
            (C, H, W)

        Output:
            (1, 6, 1, 224, 224)
        """

        # --------------------------------------------------
        # Keep all available spectral bands
        # --------------------------------------------------

        image = image.astype(np.float32)

        # --------------------------------------------------
        # Reflectance normalization
        # --------------------------------------------------

        if image.max() > 10000:
            image = image / 65535.0

        elif image.max() > 1:
            image = image / 10000.0

        image = np.clip(image, 0.0, 1.0)

        # --------------------------------------------------
        # Match Prithvi's expected 6-channel input
        # --------------------------------------------------

        channels = image.shape[0]

        if channels < 6:

            padded = np.zeros(
                (
                    6,
                    image.shape[1],
                    image.shape[2]
                ),
                dtype=np.float32
            )

            padded[:channels] = image
            image = padded

        elif channels > 6:

            image = image[:6]

        # --------------------------------------------------
        # Tensor
        # --------------------------------------------------

        tensor = torch.from_numpy(image).float()

        # --------------------------------------------------
        # Resize
        # --------------------------------------------------

        tensor = torch.nn.functional.interpolate(
            tensor.unsqueeze(0),
            size=(224, 224),
            mode="bilinear",
            align_corners=False
        )

        # --------------------------------------------------
        # Temporal dimension
        # --------------------------------------------------

        tensor = tensor.unsqueeze(2)

        tensor = tensor.to(self.device)

        return tensor
    
    # ======================================================
# SPLIT IMAGE INTO TILES
# ======================================================

    def create_tiles(
        self,
        image,
        tile_size=224
    ):

        tiles = []

        height = image.shape[1]
        width = image.shape[2]

        for y in range(0, height, tile_size):

            for x in range(0, width, tile_size):

                tile = image[
                    :,
                    y:min(y + tile_size, height),
                    x:min(x + tile_size, width)
                ]

                pad_h = tile_size - tile.shape[1]
                pad_w = tile_size - tile.shape[2]

                if pad_h > 0 or pad_w > 0:

                    tile = np.pad(
                        tile,
                        (
                            (0, 0),
                            (0, pad_h),
                            (0, pad_w)
                        ),
                        mode="constant"
                    )

                tiles.append(
                    (
                        tile,
                        y,
                        x
                    )
                )

        return tiles
    
    # ======================================================
# MERGE TILES
# ======================================================

    def merge_tiles(
        self,
        predictions,
        height,
        width,
        tile_size=224
    ):

        full_mask = np.zeros(
            (
                height,
                width
            ),
            dtype=np.uint8
        )

        for prediction, y, x in predictions:

            h = min(tile_size, height - y)
            w = min(tile_size, width - x)

            full_mask[
                y:y+h,
                x:x+w
            ] = prediction[
                :h,
                :w
            ]

        return full_mask
    
    # ======================================================
# TILE INFERENCE
# ======================================================

    def predict_large_image(
        self,
        image
    ):

        tiles = self.create_tiles(image)

        predictions = []

        for tile, y, x in tiles:

            tensor = self.preprocess_image(tile)

            prediction = self.predict(tensor)

            predictions.append(
                (
                    prediction,
                    y,
                    x
                )
            )

        return self.merge_tiles(
            predictions,
            image.shape[1],
            image.shape[2]
        )

    # ======================================================
    # RUN MODEL
    # ======================================================

    def predict(
        self,
        tensor
    ):
        """
        Performs Prithvi inference.

        Returns:
            prediction mask
            (224 x 224)
        """

        with torch.no_grad():

            output = self.model(
                tensor
            )

        prediction = output.output.argmax(
            dim=1
        )

        prediction = prediction.squeeze()

        prediction = prediction.cpu().numpy()

        return prediction

    # ======================================================
    # RESIZE TO ORIGINAL IMAGE
    # ======================================================

    def resize_prediction(
        self,
        prediction,
        width,
        height
    ):

        prediction = cv2.resize(
            prediction.astype(np.uint8),
            (
                width,
                height
            ),
            interpolation=cv2.INTER_NEAREST
        )

        return prediction
    
        # ======================================================
    # LAND COVER STATISTICS
    # ======================================================

    def calculate_statistics(
        self,
        prediction
    ):

        unique, counts = np.unique(
            prediction,
            return_counts=True
        )

        total_pixels = prediction.size

        class_stats = {}

        print("\nLand Cover Statistics")
        print("-" * 40)

        for cls, count in zip(unique, counts):

            percentage = (
                count / total_pixels
            ) * 100

            class_name = CLASS_NAMES.get(
                int(cls),
                f"class_{cls}"
            )

            class_stats[class_name] = round(
                percentage,
                2
            )

            print(
                f"{class_name}: {percentage:.2f}%"
            )

        return class_stats


    # ======================================================
    # CREATE COLORED SEGMENTATION
    # ======================================================

    def create_color_mask(
        self,
        prediction
    ):

        color_mask = np.zeros(
            (
                prediction.shape[0],
                prediction.shape[1],
                3
            ),
            dtype=np.uint8
        )

        for class_id, color in CLASS_COLORS.items():

            color_mask[
                prediction == class_id
            ] = color

        return color_mask


    # ======================================================
    # CREATE OVERLAY
    # ======================================================

    def create_overlay(
        self,
        original_rgb,
        color_mask
    ):

        original_bgr = cv2.cvtColor(
            original_rgb,
            cv2.COLOR_RGB2BGR
        )

        overlay = cv2.addWeighted(
            original_bgr,
            0.6,
            color_mask,
            0.4,
            0
        )

        return overlay
    
        # ======================================================
    # SAVE OUTPUTS
    # ======================================================

    def save_outputs(
        self,
        prediction,
        overlay,
        image_path
    ):

        filename = os.path.basename(image_path)

        name = os.path.splitext(filename)[0]

        os.makedirs(
            "backend/outputs",
            exist_ok=True
        )

        mask_path = (
            f"backend/outputs/segmask_{name}.npy"
        )

        np.save(
            mask_path,
            prediction
        )

        print(
            f"Segmentation mask saved: {mask_path}"
        )

        output_path = (
            f"backend/outputs/prithvi_{name}.png"
        )

        cv2.imwrite(
            output_path,
            overlay
        )

        print(
            f"Segmentation visualization saved: {output_path}"
        )

        return output_path


    # ======================================================
    # MAIN SEGMENTATION FUNCTION
    # ======================================================

    def segment(
        self,
        image_path
    ):

        print("\n" + "=" * 60)
        print("Running Prithvi Segmentation")
        print("=" * 60)

        # ---------------------------------------------
        # LOAD IMAGE
        # ---------------------------------------------

        (
            image,
            original_height,
            original_width,
            original_rgb
        ) = self.load_image(image_path)

        print(
            f"Original Image Size: "
            f"{original_width} x {original_height}"
        )

        # ---------------------------------------------
        # PREPROCESS
        # ---------------------------------------------

        prediction = self.predict_large_image(
            image
        )

        print(
            "Prediction Shape:",
            prediction.shape
        )

        # ---------------------------------------------
        # RESTORE ORIGINAL SIZE
        # ---------------------------------------------

        prediction = self.resize_prediction(
            prediction,
            original_width,
            original_height
        )

        # ---------------------------------------------
        # STATISTICS
        # ---------------------------------------------

        class_stats = self.calculate_statistics(
            prediction
        )

        # ---------------------------------------------
        # COLOR MASK
        # ---------------------------------------------

        color_mask = self.create_color_mask(
            prediction
        )

        # ---------------------------------------------
        # OVERLAY
        # ---------------------------------------------

        overlay = self.create_overlay(
            original_rgb,
            color_mask
        )

        # ---------------------------------------------
        # SAVE OUTPUTS
        # ---------------------------------------------

        self.save_outputs(
            prediction,
            overlay,
            image_path
        )

        print("=" * 60)
        print("Prithvi Segmentation Complete")
        print("=" * 60)

        return class_stats