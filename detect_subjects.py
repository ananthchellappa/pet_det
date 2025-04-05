import cv2
import numpy as np
import os
import sys
from glob import glob

def find_subjects_in_image(test_img, subject_imgs, threshold=0.9):
    matches = []

    for subject_id, (subject_name, subject) in enumerate(subject_imgs):
        h, w = subject.shape[:2]
        result = cv2.matchTemplate(test_img, subject, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            matches.append({
                'subject_id': subject_id,
                'subject_name': os.path.basename(subject_name),
                'top_left': pt,
                'bottom_right': (pt[0] + w, pt[1] + h),
                'center': (pt[0] + w // 2, pt[1] + h // 2),
                'score': result[pt[1], pt[0]]
            })

    return matches

def load_subject_images(folder):
    image_paths = sorted(glob(os.path.join(folder, "*.*")))  # all file types
    valid_exts = {'.png', '.jpg', '.jpeg', '.bmp'}

    subject_imgs = []
    for path in image_paths:
        if os.path.splitext(path)[1].lower() in valid_exts:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                subject_imgs.append((path, img))
            else:
                print(f"Warning: Failed to load {path}")
    return subject_imgs

def main():
    if len(sys.argv) != 3:
        print("Usage: python detect_subjects.py <test_image_path> <subject_folder>")
        sys.exit(1)

    test_image_path = sys.argv[1]
    subject_folder = sys.argv[2]

    test_img = cv2.imread(test_image_path, cv2.IMREAD_GRAYSCALE)
    if test_img is None:
        print(f"Error: Could not load test image: {test_image_path}")
        sys.exit(1)

    subject_imgs = load_subject_images(subject_folder)
    if not subject_imgs:
        print(f"Error: No valid subject images found in folder: {subject_folder}")
        sys.exit(1)

    matches = find_subjects_in_image(test_img, subject_imgs)

    print("\nDetected subject positions:")
    for match in matches:
        print(f"{match['subject_name']} at {match['top_left']} to {match['bottom_right']} "
              f"(center: {match['center']}, score: {match['score']:.2f})")

if __name__ == "__main__":
    main()
