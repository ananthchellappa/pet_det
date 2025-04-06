import sys
import re
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def parse_file(filename):
    coords = []
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'\s*(\d+)\s*,\s*(\d+)\s*', line)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                coords.append((x, y))
    return coords

def cluster_1d(values, distance_threshold=50):
    """Cluster 1D values using agglomerative clustering."""
    values_array = np.array(values).reshape(-1, 1)
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=distance_threshold)
    labels = clustering.fit_predict(values_array)
    
    # Find the average of each cluster
    clusters = {}
    for val, label in zip(values, labels):
        clusters.setdefault(label, []).append(val)

    centers = sorted([np.mean(v) for v in clusters.values()])
    return centers

def find_nearest_index(centers, value):
    """Return index of closest center to the value."""
    return min(range(len(centers)), key=lambda i: abs(centers[i] - value))

def main(filename):
    coords = parse_file(filename)
    if not coords:
        print("No valid coordinates found.")
        return

    xs, ys = zip(*coords)

    # Auto-detect clusters in X and Y with good spacing
    x_centers = cluster_1d(xs, distance_threshold=60)
    y_centers = cluster_1d(ys, distance_threshold=60)

    print(f"# Detected columns: {x_centers}")
    print(f"# Detected rows   : {y_centers}\n")

    for x, y in coords:
        gx = find_nearest_index(x_centers, x)
        gy = find_nearest_index(y_centers, y)
        print(f"{x}, {y} -> {gx},{gy}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clustered_grid.py <input_file>")
    else:
        main(sys.argv[1])
