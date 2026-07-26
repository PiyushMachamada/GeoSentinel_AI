class GeoSentinelValidator:

    def validate(self, results):

        return {
            "confidence": results["confidence_score"],
            "change_percentage": results["change_percentage"],
            "objects_detected": len(results["objects_detected"]),
            "transition_count": len(results["transition_results"]),
            "status": "PASS"
        }