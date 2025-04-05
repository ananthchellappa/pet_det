import sys
import re

def average_min_separation(values):
    """Compute average of minimum separations between sorted unique values."""
    sorted_vals = sorted(set(values))
    diffs = [b - a for a, b in zip(sorted_vals[:-1], sorted_vals[1:])]
    return sum(diffs) / len(diffs) if diffs else 1

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
    grid_x_unit = average_min_separation(xs)
    grid_y_unit = average_min_separation(ys)

    for x, y in pixel_coords:
        gx = round((x - min_x) / grid_x_unit)
        gy = round((y - min_y) / grid_y_unit)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
