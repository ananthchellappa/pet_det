import sys
import re
import math

def average_min_separation(values):
    """Average of smallest differences between sorted unique values."""
    sorted_vals = sorted(set(values))
    if len(sorted_vals) < 2:
        return 1  # avoid division by zero
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

    # 👉 Compute average minimum spacing as you originally intended
    dx = average_min_separation(xs)
    dy = average_min_separation(ys)

    print(f"# Estimated grid size: dx = {dx:.2f}, dy = {dy:.2f}\n")

    for x, y in pixel_coords:
        gx = round((x - min_x) / dx)
        gy = round((y - min_y) / dy)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
