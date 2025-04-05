import sys
import re

# Hardcoded grid step and origin
GRID_DX = 102
GRID_DY = 100

# These are based on your lowest coordinates
MIN_X = 35
MIN_Y = 39

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

    for x, y in pixel_coords:
        gx = round((x - MIN_X) / GRID_DX)
        gy = round((y - MIN_Y) / GRID_DY)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grid_transform.py <input_file>")
    else:
        main(sys.argv[1])
