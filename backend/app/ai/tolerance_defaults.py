from typing import Any
import re


class ToleranceDefaults:
    """Apply ISO 2768 and other tolerance standards to dimensions."""
    
    # ISO 2768 coarse (c), medium (m), fine (f) tolerances for linear dimensions
    ISO2768_LINEAR = {
        "coarse": {
            (0.5, 3): (0.2, 0.3),
            (3, 6): (0.3, 0.5),
            (6, 30): (0.5, 0.8),
            (30, 120): (1.2, 1.5),
            (120, 315): (2, 2.5),
            (315, 1000): (3, 4),
            (1000, 2000): (4, 5),
            (2000, float('inf')): (5, 8),
        },
        "medium": {
            (0.5, 3): (0.1, 0.15),
            (3, 6): (0.15, 0.2),
            (6, 30): (0.2, 0.3),
            (30, 120): (0.5, 0.8),
            (120, 315): (1, 1.2),
            (315, 1000): (1.5, 2),
            (1000, 2000): (2.5, 3),
            (2000, float('inf')): (3, 4),
        },
        "fine": {
            (0.5, 3): (0.05, 0.1),
            (3, 6): (0.1, 0.15),
            (6, 30): (0.15, 0.2),
            (30, 120): (0.2, 0.3),
            (120, 315): (0.3, 0.5),
            (315, 1000): (0.5, 1),
            (1000, 2000): (1, 1.5),
            (2000, float('inf')): (1.5, 2),
        },
    }
    
    # ISO 2768 tolerances for angular dimensions (all grades)
    ISO2768_ANGULAR = {
        "coarse": {"<10": 1, "10-50": 0.5, "50-120": 0.3, "120-315": 0.2, ">=315": 0.1},
        "medium": {"<10": 0.5, "10-50": 0.3, "50-120": 0.2, "120-315": 0.15, ">=315": 0.1},
        "fine": {"<10": 0.3, "10-50": 0.2, "50-120": 0.1, "120-315": 0.1, ">=315": 0.05},
    }
    
    def apply_defaults(
        self, dimensions: list[dict[str, Any]], tolerance_grade: str = "medium", unit: str = "mm"
    ) -> list[dict[str, Any]]:
        """Apply default tolerances to dimensions without explicit tolerances.
        
        Args:
            dimensions: List of dimension dicts from DimensionParser
            tolerance_grade: 'coarse', 'medium', or 'fine' (ISO 2768)
            unit: 'mm' or 'in'
        
        Returns:
            Enhanced dimensions with tolerance defaults applied
        """
        result = []
        
        for dim in dimensions:
            # Skip if already has tolerance or is basic/reference
            if dim.get("tolerance") or dim.get("class") in ["basic", "reference"]:
                result.append(dim)
                continue
            
            value = float(dim.get("value", 0))
            dim_type = dim.get("type", "length")
            
            # Apply appropriate default tolerance
            if dim_type == "angle":
                tolerance = self._get_angular_tolerance(value, tolerance_grade)
            else:
                tolerance = self._get_linear_tolerance(value, tolerance_grade, unit)
            
            # Add tolerance to dimension
            dim_copy = dim.copy()
            if tolerance:
                dim_copy["tolerance"] = f"±{tolerance}"
                dim_copy["tolerance_source"] = "iso2768"
            result.append(dim_copy)
        
        return result
    
    def _get_linear_tolerance(self, value: float, grade: str = "medium", unit: str = "mm") -> float:
        """Get ISO 2768 linear tolerance for a dimension value."""
        if unit == "in":
            value *= 25.4  # Convert to mm for lookup
        
        tolerances = self.ISO2768_LINEAR.get(grade, self.ISO2768_LINEAR["medium"])
        
        for range_tuple, (lower, upper) in tolerances.items():
            if range_tuple[0] <= value < range_tuple[1]:
                return lower  # Return lower bound (more permissive)
        
        return None
    
    def _get_angular_tolerance(self, value: float, grade: str = "medium") -> float:
        """Get ISO 2768 angular tolerance for an angle value."""
        tolerances = self.ISO2768_ANGULAR.get(grade, self.ISO2768_ANGULAR["medium"])
        
        if value < 10:
            return tolerances["<10"]
        elif value < 50:
            return tolerances["10-50"]
        elif value < 120:
            return tolerances["50-120"]
        elif value < 315:
            return tolerances["120-315"]
        else:
            return tolerances[">=315"]
    
    def get_tolerance_info(self, value: float, dim_type: str, grade: str = "medium") -> dict:
        """Get detailed tolerance information for a dimension."""
        if dim_type == "angle":
            tol = self._get_angular_tolerance(value, grade)
        else:
            tol = self._get_linear_tolerance(value, grade, "mm")
        
        return {
            "value": value,
            "type": dim_type,
            "standard": "ISO 2768",
            "grade": grade,
            "tolerance": tol,
            "tolerance_text": f"±{tol}" if tol else "Check drawing",
        }
