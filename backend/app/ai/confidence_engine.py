from typing import Any


class ConfidenceEngine:
    def calculate(self, dimensions: list[dict[str, Any]], gdts: list[dict[str, Any]], datums: list[dict[str, Any]], notes: list[dict[str, Any]], balloons: list[dict[str, Any]]) -> float:
        """Compute a composite confidence score across all extracted characteristics."""
        # Mock implementation: return higher confidence when more features are found
        total_features = len(dimensions) + len(gdts) + len(datums) + len(notes) + len(balloons)
        # Max confidence 0.95 to indicate this is a mock/demo
        return min(0.95, 0.3 + (total_features * 0.1))
