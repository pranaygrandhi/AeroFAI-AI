from typing import Any, Optional
import math


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


class BalloonEngine:
    def generate(
        self,
        dimensions: list[dict[str, Any]],
        gdts: list[dict[str, Any]],
        datums: list[dict[str, Any]],
        notes: list[dict[str, Any]],
        pages: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """Auto-balloon inspection characteristics with collision-safe layout metadata."""
        balloons = []
        page = (pages or [{}])[0] if pages else {}
        width = int(page.get("width", 1024))
        height = int(page.get("height", 768))

        anchors = []
        if pages:
            seen_targets = set()
            for page_data in pages:
                page_w = int(page_data.get("width", width))
                page_h = int(page_data.get("height", height))

                for shape in page_data.get("shapes", []):
                    center = shape.get("center")
                    if center and len(center) == 2:
                        target = (int(center[0]), int(center[1]))
                        if target not in seen_targets:
                            seen_targets.add(target)
                            anchors.append({
                                "target": [target[0], target[1]],
                                "page_width": page_w,
                                "page_height": page_h,
                                "page_data": page_data,
                            })

                for detection in page_data.get("detections", []):
                    center = detection.get("center")
                    if center and len(center) == 2:
                        target = (int(center[0]), int(center[1]))
                        if target not in seen_targets:
                            seen_targets.add(target)
                            anchors.append({
                                "target": [target[0], target[1]],
                                "page_width": page_w,
                                "page_height": page_h,
                                "page_data": page_data,
                            })

                for text_item in page_data.get("text_items", []):
                    center = text_item.get("center")
                    if center and len(center) == 2:
                        target = (int(center[0]), int(center[1]))
                        if target not in seen_targets:
                            seen_targets.add(target)
                            anchors.append({
                                "target": [target[0], target[1]],
                                "page_width": page_w,
                                "page_height": page_h,
                                "page_data": page_data,
                            })

        def get_target(item: dict[str, Any], default_target: list[int]) -> list[int]:
            if isinstance(item, dict):
                target = item.get("target") or item.get("value", {}).get("target")
                if target and isinstance(target, list) and len(target) == 2:
                    return [int(target[0]), int(target[1])]
            return default_target

        def find_nearest_feature(point: list[int], page_data: dict[str, Any], max_dist: int = 120) -> Optional[list[int]]:
            best = None
            best_dist = max_dist
            for shape in page_data.get("shapes", []):
                center = shape.get("center")
                if center and len(center) == 2:
                    dx = center[0] - point[0]
                    dy = center[1] - point[1]
                    dist = math.hypot(dx, dy)
                    if dist < best_dist:
                        best_dist = dist
                        best = [int(center[0]), int(center[1])]
            for detection in page_data.get("detections", []):
                center = detection.get("center")
                if center and len(center) == 2:
                    dx = center[0] - point[0]
                    dy = center[1] - point[1]
                    dist = math.hypot(dx, dy)
                    if dist < best_dist:
                        best_dist = dist
                        best = [int(center[0]), int(center[1])]
            return best

        def find_nearest_text(point: list[int], page_data: dict[str, Any], max_dist: int = 120) -> Optional[list[int]]:
            best = None
            best_dist = max_dist
            for text_item in page_data.get("text_items", []):
                center = text_item.get("center")
                if center and len(center) == 2:
                    dx = center[0] - point[0]
                    dy = center[1] - point[1]
                    dist = math.hypot(dx, dy)
                    if dist < best_dist:
                        best_dist = dist
                        best = [int(center[0]), int(center[1])]
            return best

        def choose_target(item: dict[str, Any], page_data: dict[str, Any], default_target: list[int]) -> list[int]:
            target = get_target(item, default_target)
            if page_data:
                if target != default_target:
                    feature_target = find_nearest_feature(target, page_data)
                    if feature_target is not None:
                        return feature_target
                    text_target = find_nearest_text(target, page_data)
                    if text_target is not None:
                        return text_target
                else:
                    text_target = find_nearest_text(target, page_data)
                    if text_target is not None:
                        return text_target
                    feature_target = find_nearest_feature(target, page_data)
                    if feature_target is not None:
                        return feature_target
            return target

        def label_position(target: list[int], index: int, page_w: int, page_h: int) -> list[int]:
            dx = -1 if target[0] > page_w / 2 else 1
            dy = -1 if target[1] > page_h / 2 else 1
            offset = 110
            x = int(target[0] + dx * offset)
            y = int(target[1] + dy * offset)
            x = clamp(x, 24, page_w - 24)
            y = clamp(y, 24, page_h - 24)
            return [x, y]

        def next_anchor(index: int, item: dict[str, Any]) -> dict[str, Any]:
            target = get_target(item, [width // 2, height // 2])
            if anchors:
                best_anchor = None
                best_dist = 999999
                for anchor in anchors:
                    dx = anchor["target"][0] - target[0]
                    dy = anchor["target"][1] - target[1]
                    dist = math.hypot(dx, dy)
                    if dist < best_dist:
                        best_dist = dist
                        best_anchor = anchor
                if best_anchor and best_dist < 160:
                    return best_anchor
                return anchors[index % len(anchors)]
            return {"target": target, "page_width": width, "page_height": height, "page_data": None}

        balloon_id = 1
        for idx, dim in enumerate(dimensions):
            anchor = next_anchor(idx, dim)
            target = choose_target(dim, anchor.get("page_data"), anchor["target"])
            position = label_position(target, idx, anchor["page_width"], anchor["page_height"])
            balloons.append({
                "id": balloon_id,
                "type": "dimension",
                "label": str(balloon_id),
                "value": {
                    "position": position,
                    "target": target,
                    "label": str(balloon_id),
                    "text": dim.get("text") or dim.get("value"),
                },
            })
            balloon_id += 1

        for idx, gdt in enumerate(gdts):
            anchor = next_anchor(len(dimensions) + idx, gdt)
            target = choose_target(gdt, anchor.get("page_data"), anchor["target"])
            position = label_position(target, len(dimensions) + idx, anchor["page_width"], anchor["page_height"])
            balloons.append({
                "id": balloon_id,
                "type": "gdt",
                "label": str(balloon_id),
                "value": {
                    "position": position,
                    "target": target,
                    "label": str(balloon_id),
                    "text": gdt.get("text") or gdt.get("symbol"),
                },
            })
            balloon_id += 1

        for idx, datum in enumerate(datums):
            anchor = next_anchor(len(dimensions) + len(gdts) + idx, datum)
            target = choose_target(datum, anchor.get("page_data"), anchor["target"])
            position = label_position(target, len(dimensions) + len(gdts) + idx, anchor["page_width"], anchor["page_height"])
            balloons.append({
                "id": balloon_id,
                "type": "datum",
                "label": str(balloon_id),
                "value": {
                    "position": position,
                    "target": target,
                    "label": str(balloon_id),
                    "text": datum.get("text") or datum.get("datum"),
                },
            })
            balloon_id += 1

        for idx, note in enumerate(notes):
            anchor = next_anchor(len(dimensions) + len(gdts) + len(datums) + idx, note)
            target = choose_target(note, anchor.get("page_data"), anchor["target"])
            position = label_position(target, len(dimensions) + len(gdts) + len(datums) + idx, anchor["page_width"], anchor["page_height"])
            balloons.append({
                "id": balloon_id,
                "type": "note",
                "label": str(balloon_id),
                "value": {
                    "position": position,
                    "target": target,
                    "label": str(balloon_id),
                    "text": note.get("note") or note.get("text"),
                },
            })
            balloon_id += 1

        return balloons
