from ultralytics import YOLO


class YOLODetector:

    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect(self, image_path):
        print("Running YOLO Detection...")

        results = self.model(
            image_path,
            save=True
        )

        print("YOLO Detection Complete")

        return results