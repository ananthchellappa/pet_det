import sys
import re
from dataclasses import dataclass
from typing import Tuple, List

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

def center_inside_box(center: Tuple[int, int], box1: ObjectBox, box2: ObjectBox, direction: str):
    x, y = center
    if direction == 'vertical':
        left = max(box1.bounds()[0], box2.bounds()[0])
        right = min(box1.bounds()[2], box2.bounds()[2])
        top = min(box1.bounds()[1], box2.bounds()[1])
        bottom = max(box1.bounds()[3], box2.bounds()[3])
        return left <= x <= right and top <= y <= bottom
    elif direction == 'horizontal':
        top = max(box1.bounds()[1], box2.bounds()[1])
        bottom = min(box1.bounds()[3], box2.bounds()[3])
        left = min(box1.bounds()[0], box2.bounds()[0])
        right = max(box1.bounds()[2], box2.bounds()[2])
        return left <= x <= right and top <= y <= bottom
    return False

def is_valid_connection(obj1: ObjectBox, obj2: ObjectBox, roads: List[Road], objects: List[ObjectBox]):
    dir = None
    if abs(obj1.center[1] - obj2.center[1]) < 30:
        dir = 'horizontal'
    elif abs(obj1.center[0] - obj2.center[0]) < 30:
        dir = 'vertical'
    else:
        return False

    valid = any(center_inside_box(road.center, obj1, obj2, dir) for road in roads)
    if not valid:
        return False

    for obj in objects:
        if obj.name in (obj1.name, obj2.name):
            continue
        if center_inside_box(obj.center, obj1, obj2, dir):
            return False

    return True

def main():
    objects = []
    roads = []
    lines = []

    for line in sys.stdin:
        line = line.strip()
        if 'center' not in line:
            continue
        print(line)  # Echo valid line to stdout
        lines.append(line)

    for line in lines:
        parsed = parse_line(line)
        if parsed:
            name, tl, br, center = parsed
            if 'road' in name:
                roads.append(Road(center=center))
            else:
                objects.append(ObjectBox(name=name, top_left=tl, bottom_right=br, center=center))

    print("\nConnections:")
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i >= j:
                continue
            if is_valid_connection(obj1, obj2, roads, objects):
                print(f"{obj1.name} <--> {obj2.name}")

if __name__ == "__main__":
    main()
