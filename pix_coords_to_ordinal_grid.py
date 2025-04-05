import sys
import re
import numpy as np

def average_nearest_neighbor_distance(values):
    """Estimate grid spacing by averaging the nearest neighbor distance."""
    values = sorted(set(values))
    if len(values) < 2:
        return 1  # avoid divide-by-zero
    diffs = np.diff(values)
    return np.min(diffs) if len(diffs) == 1 else np.mean(np.minimum(diffs[:-1], diffs[1:]))

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

    # Updated estimation using nearest-neighbor average spacing
    grid_x_unit = average_nearest_neighbor_distance(xs)
    grid_y_unit = average_nearest_neighbor_distance(ys)

    print(f"# Grid units estimated: dx={grid_x_unit:.2f}, dy={grid_y_unit:.2f}\n")

    for x, y in pixel_coords:
        gx = round((x - min_x) / grid_x_unit)
        gy = round((y - min_y) / grid_y_unit)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
