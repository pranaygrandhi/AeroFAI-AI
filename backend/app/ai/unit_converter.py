from typing import Optional


class UnitConverter:
    """Convert engineering dimension values between imperial and metric units."""

    IN_TO_MM = 25.4
    MM_TO_IN = 1.0 / IN_TO_MM

    @staticmethod
    def normalize_unit(unit: str) -> str:
        if not unit:
            return ""
        unit = unit.strip().lower()
        if unit in ("mm", "millimeter", "millimetre"):
            return "mm"
        if unit in ("in", "inch", "inches"):
            return "in"
        if unit in ("cm", "centimeter", "centimetre"):
            return "cm"
        return unit

    @classmethod
    def to_mm(cls, value: float, unit: Optional[str] = None) -> Optional[float]:
        unit = cls.normalize_unit(unit or "")
        if value is None:
            return None
        if unit == "mm":
            return value
        if unit == "in":
            return round(value * cls.IN_TO_MM, 6)
        if unit == "cm":
            return round(value * 10.0, 6)
        return None

    @classmethod
    def to_in(cls, value: float, unit: Optional[str] = None) -> Optional[float]:
        unit = cls.normalize_unit(unit or "")
        if value is None:
            return None
        if unit == "in":
            return value
        if unit == "mm":
            return round(value * cls.MM_TO_IN, 6)
        if unit == "cm":
            return round(value * 0.3937007874, 6)
        return None

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        from_unit = cls.normalize_unit(from_unit)
        to_unit = cls.normalize_unit(to_unit)
        if value is None:
            return None
        if from_unit == to_unit:
            return value
        if to_unit == "mm":
            return cls.to_mm(value, from_unit)
        if to_unit == "in":
            return cls.to_in(value, from_unit)
        if to_unit == "cm":
            mm_value = cls.to_mm(value, from_unit)
            return round(mm_value / 10.0, 6) if mm_value is not None else None
        return None
