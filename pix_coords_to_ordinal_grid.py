import sys
import re
from collections import Counter

def most_common_step(values):
    """Find most common step between sorted unique values as grid unit."""
    sorted_vals = sorted(set(values))
    diffs = [b - a for a, b in zip(sorted_vals[:-1], sorted_vals[1:])]
    count = Counter(diffs)
    most_common = count.most_common(1)
    if most_common:
        return most_common[0][0]
    return 1

def parse_file(filename):
    coords = []
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'\s*(\d+)\s*,\s*(\d+)\s*', line)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                coords.append((x, y))
    return coords

def main(filename):
    pixel_coords = parse_file(filename)
    if not pixel_coords:
        print("No valid coordinates found.")
        return

    xs, ys = zip(*pixel_coords)
    min_x, min_y = min(xs), min(ys)

    dx = most_common_step(xs)
    dy = most_common_step(ys)

    print(f"# Grid step detected: dx={dx}, dy={dy}\n")

    for x, y in pixel_coords:
        gx = round((x - min_x) / dx)
        gy = round((y - min_y) / dy)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
