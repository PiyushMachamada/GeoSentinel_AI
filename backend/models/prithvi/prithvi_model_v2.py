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


class PrithviModelV2:

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

                print("\nGeoTIFF Information")
                print("-" * 40)
                print("Shape :", image.shape)
                print("Bands :", image.shape[0])
                print("dtype :", image.dtype)
                print("Min   :", image.min())
                print("Max   :", image.max())

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
        # Remove useless alpha band if present
        # --------------------------------------------------

        if image.shape[0] == 4:
            image = image[:3]

        # --------------------------------------------------
        # Normalize
        # --------------------------------------------------

        image = image.astype(np.float32)

        if image.max() > 1:
            image = image / 255.0

        # --------------------------------------------------
        # Pad to 6 channels
        # --------------------------------------------------

        if image.shape[0] < 6:

            extra = np.zeros(
                (
                    6 - image.shape[0],
                    image.shape[1],
                    image.shape[2]
                ),
                dtype=np.float32
            )

            image = np.concatenate(
                (
                    image,
                    extra
                ),
                axis=0
            )

        elif image.shape[0] > 6:

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
        tile_size = 1024
    ):

        tiles = []

        height = image.shape[1]
        width = image.shape[2]

        stride = 768  # 25% overlap

        for y in range(0, height, stride):
            for x in range(0, width, stride):

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
                        mode="reflect"
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
        tile_size=1024
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

            existing = full_mask[y:y+h, x:x+w]

            new = prediction[:h, :w]

            mask = existing == 0

            existing[mask] = new[mask]

            full_mask[y:y+h, x:x+w] = existing

        return full_mask
    
    # ======================================================
# TILE INFERENCE
# ======================================================

    def predict_large_image(
        self,
        image,
        tile_size=1024,
    ):
        """
        Segment large Sentinel images using tiled inference.
        """

        import time

        print("\nCreating image tiles...")

        tiles = self.create_tiles(
            image,
            tile_size=tile_size,
        )

        total_tiles = len(tiles)

        print(f"Tile Size   : {tile_size} x {tile_size}")
        print(f"Total Tiles : {total_tiles}\n")

        predictions = []

        start_time = time.time()

        for i, (tile, y, x) in enumerate(tiles, start=1):

            tile_start = time.time()

            tensor = self.preprocess_image(tile)

            prediction = self.predict(tensor)

            prediction = cv2.resize(
                prediction.astype(np.uint8),
                (tile_size, tile_size),
                interpolation=cv2.INTER_NEAREST,
            )

            predictions.append(
                (
                    prediction,
                    y,
                    x,
                )
            )

            tile_time = time.time() - tile_start

        if i == 1 or i % 10 == 0 or i == total_tiles:
            print(
                f"[{i}/{total_tiles}] "
                f"{100*i/total_tiles:.1f}% complete "
                f"({tile_time:.2f}s)"
            )

        total_time = time.time() - start_time

        print(f"\nFinished inference on {total_tiles} tiles.")
        print(f"Total Time : {total_time:.2f} seconds")

        print("\nMerging tiles...")

        merged = self.merge_tiles(
            predictions,
            image.shape[1],
            image.shape[2],
            tile_size=tile_size,
        )

        print("Merge complete.\n")

        return merged

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

        print("\nPrediction Debug")
        print("-" * 40)
        print("Unique Classes :", np.unique(prediction))
        print("Min Class      :", prediction.min())
        print("Max Class      :", prediction.max())

        unique, counts = np.unique(prediction, return_counts=True)

        for cls, count in zip(unique, counts):
            print(f"Class {cls}: {count} pixels")

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
        image_path,
        output_paths,
    ):
        filename = os.path.basename(image_path).lower()

        if "before" in filename:

            mask_path = output_paths["segmask_before"]

            overlay_path = output_paths["prithvi_before"]

        else:

            mask_path = output_paths["segmask_after"]

            overlay_path = output_paths["prithvi_after"]

        np.save(
            mask_path,
            prediction,
        )

        cv2.imwrite(
            str(overlay_path),
            overlay,
        )

        print(f"Segmentation mask saved: {mask_path}")
        print(f"Segmentation visualization saved: {overlay_path}")

        return overlay_path


    # ======================================================
    # MAIN SEGMENTATION FUNCTION
    # ======================================================

    def segment(
        self,
        image_path,
        output_paths,
    ):

        import time

        overall_start = time.time()

        print("\n" + "=" * 60)
        print("Running Prithvi Segmentation")
        print("=" * 60)

        # --------------------------------------------------
        # LOAD IMAGE
        # --------------------------------------------------

        (
            image,
            original_height,
            original_width,
            original_rgb
        ) = self.load_image(image_path)

        print(f"Original Image Size : {original_width} x {original_height}")
        print(f"Image Shape         : {image.shape}")

        # --------------------------------------------------
        # RUN TILED INFERENCE
        # --------------------------------------------------

        print("\nStarting tiled segmentation...")

        prediction = self.predict_large_image(
            image,
            tile_size=1024,
        )

        print("\nPrediction Shape:", prediction.shape)

        print(
            f"Segmentation Time : "
            f"{time.time() - overall_start:.2f} seconds"
        )

        # --------------------------------------------------
        # RESTORE ORIGINAL SIZE
        # --------------------------------------------------

        prediction = self.resize_prediction(
            prediction,
            original_width,
            original_height,
        )

        print("Prediction resized to original resolution.")

        # --------------------------------------------------
        # LAND COVER STATISTICS
        # --------------------------------------------------

        class_stats = self.calculate_statistics(
            prediction
        )

        # --------------------------------------------------
        # CREATE COLOR MASK
        # --------------------------------------------------

        color_mask = self.create_color_mask(
            prediction
        )

        # --------------------------------------------------
        # CREATE OVERLAY
        # --------------------------------------------------

        overlay = self.create_overlay(
            original_rgb,
            color_mask,
        )

        # --------------------------------------------------
        # SAVE OUTPUTS
        # --------------------------------------------------

        output_path = self.save_outputs(
            prediction,
            overlay,
            image_path,
            output_paths,
        )

        print(f"\nOutput saved to: {output_path}")

        print("=" * 60)
        print("Prithvi Segmentation Complete")
        print("=" * 60)

        print(
            f"Total Execution Time : "
            f"{time.time() - overall_start:.2f} seconds"
        )

        return class_stats