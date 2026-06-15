from typing import Any


class FairGenerator:
    def generate_form_1(self, drawing: dict[str, Any]) -> dict[str, Any]:
        return {"form": 1, "drawing_id": drawing.get("drawing_id")}

    def generate_form_2(self, drawing: dict[str, Any]) -> dict[str, Any]:
        return {"form": 2, "drawing_id": drawing.get("drawing_id")}

    def generate_form_3(self, drawing: dict[str, Any]) -> dict[str, Any]:
        return {"form": 3, "drawing_id": drawing.get("drawing_id")}
