import sys
import re
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict


@dataclass
class ObjectBox:
    name: str
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]
    center: Tuple[int, int]

    def bounds(self):
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


@dataclass
class Road:
    name: str
    center: Tuple[int, int]


def parse_line(line: str):
    match = re.match(r"(\S+\.png) at \((\d+), (\d+)\) to \((\d+), (\d+)\).*center: \((\d+), (\d+)\)", line)
    if match:
        name = match.group(1).replace('.png', '')
        tl = (int(match.group(2)), int(match.group(3)))
        br = (int(match.group(4)), int(match.group(5)))
        center = (int(match.group(6)), int(match.group(7)))
        return name, tl, br, center
    return None


def center_inside_box(center: Tuple[int, int], box1: ObjectBox, box2: ObjectBox, direction: str) -> bool:
    x, y = center
    if direction in ('north', 'south'):
        left = max(box1.bounds()[0], box2.bounds()[0])
        right = min(box1.bounds()[2], box2.bounds()[2])
        top = min(box1.bounds()[1], box2.bounds()[1])
        bottom = max(box1.bounds()[3], box2.bounds()[3])
        return left <= x <= right and top <= y <= bottom
    elif direction in ('east', 'west'):
        top = max(box1.bounds()[1], box2.bounds()[1])
        bottom = min(box1.bounds()[3], box2.bounds()[3])
        left = min(box1.bounds()[0], box2.bounds()[0])
        right = max(box1.bounds()[2], box2.bounds()[2])
        return left <= x <= right and top <= y <= bottom
    return False


def determine_direction(from_obj: ObjectBox, to_obj: ObjectBox) -> Optional[str]:
    dx = to_obj.center[0] - from_obj.center[0]
    dy = to_obj.center[1] - from_obj.center[1]
    if abs(dx) > abs(dy):
        if abs(dy) < 30:  # y is nearly same
            return 'east' if dx > 0 else 'west'
    else:
        if abs(dx) < 30:  # x is nearly same
            return 'south' if dy > 0 else 'north'
    return None


def road_connects(obj1: ObjectBox, obj2: ObjectBox, roads: List[Road], direction: str, all_objects: List[ObjectBox]) -> Optional[Tuple[str, Tuple[int, int]]]:
    for road in roads:
        if center_inside_box(road.center, obj1, obj2, direction):
            # Check that no other object center is in the region
            blocked = any(
                center_inside_box(o.center, obj1, obj2, direction)
                for o in all_objects if o.name not in (obj1.name, obj2.name)
            )
            if not blocked:
                return road.name, road.center
    return None


def find_nearest_neighbors(objects: List[ObjectBox], roads: List[Road]) -> List[Tuple[str, str, str, Tuple[int, int]]]:
    connections = []

    for obj in objects:
        # Group potential neighbors by direction
        neighbors_by_dir: Dict[str, Tuple[ObjectBox, float]] = {}

        for other in objects:
            if obj.name == other.name:
                continue
            direction = determine_direction(obj, other)
            if not direction:
                continue
            dist = (
                abs(obj.center[0] - other.center[0]) +
                abs(obj.center[1] - other.center[1])
            )
            if direction not in neighbors_by_dir or dist < neighbors_by_dir[direction][1]:
                neighbors_by_dir[direction] = (other, dist)

        # Try to connect to one neighbor per direction
        for direction, (neighbor, _) in neighbors_by_dir.items():
            road_info = road_connects(obj, neighbor, roads, direction, objects)
            if road_info:
                road_name, road_center = road_info
                # Report only once per pair (avoid duplicates)
                if obj.name < neighbor.name:
                    connections.append((obj.name, neighbor.name, road_name, road_center))

    return connections


def main():
    objects = []
    roads = []
    lines = []

    for line in sys.stdin:
        line = line.strip()
        if 'center' not in line:
            continue
        print(line)
        lines.append(line)

    for line in lines:
        parsed = parse_line(line)
        if parsed:
            name, tl, br, center = parsed
            if 'road' in name:
                roads.append(Road(name=name, center=center))
            else:
                objects.append(ObjectBox(name=name, top_left=tl, bottom_right=br, center=center))

    print("\nConnections:")
    for obj1_name, obj2_name, road_name, road_center in find_nearest_neighbors(objects, roads):
        print(f"{obj1_name} <--> {obj2_name} [via {road_name} at {road_center}]")


if __name__ == "__main__":
    main()
