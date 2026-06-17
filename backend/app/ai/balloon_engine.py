from typing import Any, Optional, List, Dict, Tuple
import math


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


class BalloonEngine:
    def __init__(self):
        self.MIN_BALLOON_DISTANCE = 50  # Minimum distance between balloons
        self.MIN_FEATURE_DISTANCE = 30  # Minimum distance from feature to balloon
        self.LABEL_OFFSET_INITIAL = 80  # Starting offset distance
        self.LABEL_OFFSET_MAX = 200  # Max offset to try
        
    def _calculate_feature_density(self, page_data: Dict[str, Any], grid_size: int = 100) -> List[List[float]]:
        """Calculate feature density map by dividing page into grid cells."""
        page_w = int(page_data.get("width", 1024))
        page_h = int(page_data.get("height", 768))
        
        grid_w = (page_w + grid_size - 1) // grid_size
        grid_h = (page_h + grid_size - 1) // grid_size
        density = [[0.0 for _ in range(grid_w)] for _ in range(grid_h)]
        
        # Add shapes
        for shape in page_data.get("shapes", []):
            center = shape.get("center")
            if center and len(center) == 2:
                gx = min(int(center[0]) // grid_size, grid_w - 1)
                gy = min(int(center[1]) // grid_size, grid_h - 1)
                if 0 <= gx < grid_w and 0 <= gy < grid_h:
                    density[gy][gx] += 1.0
                    # Spread to adjacent cells
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < grid_w and 0 <= ny < grid_h:
                                density[ny][nx] += 0.3
        
        # Add detections
        for detection in page_data.get("detections", []):
            center = detection.get("center")
            if center and len(center) == 2:
                gx = min(int(center[0]) // grid_size, grid_w - 1)
                gy = min(int(center[1]) // grid_size, grid_h - 1)
                if 0 <= gx < grid_w and 0 <= gy < grid_h:
                    density[gy][gx] += 0.8
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < grid_w and 0 <= ny < grid_h:
                                density[ny][nx] += 0.2
        
        return density
    
    def _get_local_density(self, density: List[List[float]], x: int, y: int, page_w: int, page_h: int, grid_size: int = 100) -> float:
        if not density:
            return 0.0
        gx = min(max(int(x) // grid_size, 0), len(density[0]) - 1)
        gy = min(max(int(y) // grid_size, 0), len(density) - 1)
        return density[gy][gx]

    def _find_low_density_direction(self, target: List[int], page_data: Dict[str, Any], page_w: int, page_h: int) -> Tuple[int, int]:
        """Find the best local direction for label placement."""
        density = self._calculate_feature_density(page_data)
        directions = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
            (1, -1),
            (1, 1),
            (-1, 1),
            (-1, -1),
        ]

        best_direction = (1, 1)
        best_score = float("inf")
        for dx, dy in directions:
            x = clamp(target[0] + dx * self.LABEL_OFFSET_INITIAL, 24, page_w - 24)
            y = clamp(target[1] + dy * self.LABEL_OFFSET_INITIAL, 24, page_h - 24)
            local_density = self._get_local_density(density, x, y, page_w, page_h)
            target_dist = math.hypot(x - target[0], y - target[1])
            score = local_density * 10 + target_dist / 10
            if score < best_score:
                best_score = score
                best_direction = (dx, dy)

        return best_direction

    def generate(
        self,
        dimensions: List[Dict[str, Any]],
        gdts: List[Dict[str, Any]],
        datums: List[Dict[str, Any]],
        notes: List[Dict[str, Any]],
        pages: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Auto-balloon inspection characteristics with improved accuracy and collision detection."""
        balloons = []
        page = (pages or [{}])[0] if pages else {}
        width = int(page.get("width", 1024))
        height = int(page.get("height", 768))

        anchors = []
        placed_positions = []  # Track placed balloon positions for collision detection
        
        if pages:
            seen_targets = set()
            for page_data in pages:
                page_w = int(page_data.get("width", width))
                page_h = int(page_data.get("height", height))

                # Extract all diagram features
                for shape in page_data.get("shapes", []):
                    center = shape.get("center")
                    if center and len(center) == 2:
                        radius = shape.get("radius", 0)
                        rect = shape.get("rect", [])
                        if radius and radius > max(page_w, page_h) * 0.45:
                            continue
                        if rect and len(rect) == 4 and ((rect[2] - rect[0]) > page_w * 0.8 or (rect[3] - rect[1]) > page_h * 0.8):
                            continue
                        target = (int(center[0]), int(center[1]))
                        if target not in seen_targets:
                            seen_targets.add(target)
                            anchors.append({
                                "target": [target[0], target[1]],
                                "page_width": page_w,
                                "page_height": page_h,
                                "page_data": page_data,
                                "type": "shape",
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
                                "type": "detection",
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
                                "type": "text",
                            })

        def get_target(item: Dict[str, Any], default_target: List[int]) -> List[int]:
            if isinstance(item, dict):
                target = item.get("target") or item.get("value", {}).get("target")
                if target and isinstance(target, list) and len(target) == 2:
                    return [int(target[0]), int(target[1])]
            return default_target

        def find_nearest_feature(point: List[int], page_data: Dict[str, Any], max_dist: int = 150) -> Optional[List[int]]:
            """Find nearest feature to point, expanding search radius intelligently."""
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

        def find_nearest_text(point: List[int], page_data: Dict[str, Any], max_dist: int = 150) -> Optional[List[int]]:
            """Find nearest text element to point."""
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

        def choose_target(item: Dict[str, Any], page_data: Dict[str, Any], default_target: List[int]) -> List[int]:
            """Choose the best target for a balloon by analyzing nearby features."""
            target = get_target(item, default_target)
            if page_data:
                feature_target = find_nearest_feature(target, page_data, max_dist=200)
                if feature_target is not None:
                    return feature_target
                text_target = find_nearest_text(target, page_data, max_dist=200)
                if text_target is not None:
                    return text_target
            return target

        def find_best_label_position(target: List[int], index: int, page_w: int, page_h: int, 
                                    page_data: Dict[str, Any], occupied: List[Tuple[int, int]]) -> List[int]:
            """Find best position for balloon label with collision avoidance."""
            if not page_data:
                # Fallback to simple logic
                dx = -1 if target[0] > page_w / 2 else 1
                dy = -1 if target[1] > page_h / 2 else 1
                offset = self.LABEL_OFFSET_INITIAL
                x = int(target[0] + dx * offset)
                y = int(target[1] + dy * offset)
                return [clamp(x, 24, page_w - 24), clamp(y, 24, page_h - 24)]
            
            # Find low-density direction and try a range of offsets.
            dx_sign, dy_sign = self._find_low_density_direction(target, page_data, page_w, page_h)

            # Try offsets in both the best low-density direction and a few backup directions
            candidate_directions = [(dx_sign, dy_sign), (-dx_sign, -dy_sign), (dx_sign, 0), (0, dy_sign), (1, -1), (-1, 1)]
            tried_positions = []

            for direction in candidate_directions:
                dx, dy = direction
                for offset in range(self.LABEL_OFFSET_INITIAL, self.LABEL_OFFSET_MAX + 1, 20):
                    x = int(target[0] + dx * offset)
                    y = int(target[1] + dy * offset)

                    x = clamp(x, 24, page_w - 24)
                    y = clamp(y, 24, page_h - 24)

                    if (x, y) in tried_positions:
                        continue
                    tried_positions.append((x, y))

                    collision = False
                    for ox, oy in occupied:
                        if math.hypot(x - ox, y - oy) < self.MIN_BALLOON_DISTANCE:
                            collision = True
                            break

                    if collision:
                        continue

                    target_dist = math.hypot(x - target[0], y - target[1])
                    if target_dist < self.MIN_FEATURE_DISTANCE:
                        continue

                    return [x, y]

            # If no clear spot found, place label at a safe offset in the least congested direction.
            x = int(target[0] + dx_sign * self.LABEL_OFFSET_MAX)
            y = int(target[1] + dy_sign * self.LABEL_OFFSET_MAX)
            return [clamp(x, 24, page_w - 24), clamp(y, 24, page_h - 24)]

        def next_anchor(index: int, item: Dict[str, Any]) -> Dict[str, Any]:
            """Find best anchor point for item."""
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
                # Prefer anchors that are actual shapes or nearby text; otherwise fallback
                if best_anchor and best_dist < max(200, min(width, height) * 0.25):
                    return best_anchor
                # otherwise choose nearest shape anchor if present
                for anchor in anchors:
                    if anchor.get("type") == "shape":
                        return anchor
                return anchors[index % len(anchors)] if anchors else {"target": target, "page_width": width, "page_height": height, "page_data": None}
            return {"target": target, "page_width": width, "page_height": height, "page_data": None}

        balloon_id = 1
        for idx, dim in enumerate(dimensions):
            anchor = next_anchor(idx, dim)
            target = choose_target(dim, anchor.get("page_data"), anchor["target"])
            position = find_best_label_position(target, idx, anchor["page_width"], anchor["page_height"], 
                                              anchor.get("page_data"), placed_positions)
            placed_positions.append((position[0], position[1]))
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
            position = find_best_label_position(target, len(dimensions) + idx, anchor["page_width"], anchor["page_height"],
                                              anchor.get("page_data"), placed_positions)
            placed_positions.append((position[0], position[1]))
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
            position = find_best_label_position(target, len(dimensions) + len(gdts) + idx, anchor["page_width"], anchor["page_height"],
                                              anchor.get("page_data"), placed_positions)
            placed_positions.append((position[0], position[1]))
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
            position = find_best_label_position(target, len(dimensions) + len(gdts) + len(datums) + idx, anchor["page_width"], anchor["page_height"],
                                              anchor.get("page_data"), placed_positions)
            placed_positions.append((position[0], position[1]))
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
