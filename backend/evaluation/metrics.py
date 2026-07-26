import json
from datetime import datetime


class EvaluationMetrics:

    def __init__(self):

        self.metrics = {}

    def add(self, key, value):

        self.metrics[key] = value

    def get(self):

        return self.metrics

    def print(self):

        print("\n")
        print("=" * 60)
        print("GeoSentinel Evaluation")
        print("=" * 60)

        for key, value in self.metrics.items():

            print(f"{key:25}: {value}")

        print("=" * 60)

    def save(self, path):

        with open(path, "w") as f:

            json.dump(
                self.metrics,
                f,
                indent=4
            )   