from ultralytics import YOLO
import cv2


class YOLODetector:

    def __init__(self):

        self.model = YOLO("yolov8n.pt")

    def detect(
        self,
        image_path,
        output_path=None,
    ):

        print(f"\nRunning YOLO Detection: {image_path}")

        results = self.model(
            image_path,
            save=False,
        )

        detected_objects = {}

        for result in results:

            for cls in result.boxes.cls:

                class_id = int(cls)

                class_name = self.model.names[class_id]

                detected_objects[class_name] = (
                    detected_objects.get(class_name, 0) + 1
                )

        annotated_frame = results[0].plot()

        if output_path is not None:

            cv2.imwrite(
                str(output_path),
                annotated_frame,
            )

        print("Detected Objects:")
        print(detected_objects)

        return detected_objects

    # =====================================
    # Compare Before vs After
    # =====================================

    def compare_images(
        self,
        before_image,
        after_image,
        output_paths,
    ):

        print("\nComparing YOLO Results...")

        before_objects = self.detect(
            before_image,
            output_paths["yolo_before"],
        )

        after_objects = self.detect(
            after_image,
            output_paths["yolo_after"],
        )

        all_classes = (
            set(before_objects.keys())
            .union(after_objects.keys())
        )

        comparison = {}

        for cls in all_classes:

            before_count = before_objects.get(
                cls,
                0,
            )

            after_count = after_objects.get(
                cls,
                0,
            )

            comparison[cls] = {
                "before": before_count,
                "after": after_count,
                "difference": (
                    after_count - before_count
                ),
            }

        print("\nYOLO Comparison Results:")

        for cls, values in comparison.items():

            print(
                f"{cls}: "
                f"{values['before']} -> "
                f"{values['after']} "
                f"(Δ {values['difference']})"
            )

        return comparison