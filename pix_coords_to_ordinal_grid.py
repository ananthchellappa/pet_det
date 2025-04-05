import sys
import re
import math

def estimate_grid_unit(values):
    """Estimate grid spacing using average nearest neighbor distance."""
    sorted_vals = sorted(set(values))
    if len(sorted_vals) < 2:
        return 1
    diffs = [b - a for a, b in zip(sorted_vals[:-1], sorted_vals[1:])]
    return sum(diffs) / len(diffs)

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

    grid_x_unit = estimate_grid_unit(xs)
    grid_y_unit = estimate_grid_unit(ys)

    print(f"# Estimated grid unit: dx = {grid_x_unit:.2f}, dy = {grid_y_unit:.2f}\n")

    for x, y in pixel_coords:
        grid_x = round((x - min_x) / grid_x_unit)
        grid_y = round((y - min_y) / grid_y_unit)
        print(f"{x}, {y} -> {grid_x},{grid_y}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
