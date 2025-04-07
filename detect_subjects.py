import cv2
import numpy as np
import os
import sys
from glob import glob

def non_max_suppression_fast(boxes, overlapThresh=0.5):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    pick = []

    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    scores = boxes[:,4]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(scores)[::-1]

    while len(idxs) > 0:
        i = idxs[0]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[1:]])
        yy1 = np.maximum(y1[i], y1[idxs[1:]])
        xx2 = np.minimum(x2[i], x2[idxs[1:]])
        yy2 = np.minimum(y2[i], y2[idxs[1:]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[1:]]

        idxs = idxs[np.where(overlap <= overlapThresh)[0] + 1]

    return pick

def find_subjects_in_image(test_img, subject_imgs, threshold=0.9, nms_thresh=0.3):
    matches = []
    subject_found_flags = {}

    for subject_id, (subject_name, subject) in enumerate(subject_imgs):
        h, w = subject.shape[:2]
        result = cv2.matchTemplate(test_img, subject, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        boxes = []
        for pt in zip(*loc[::-1]):
            score = result[pt[1], pt[0]]
            boxes.append([pt[0], pt[1], pt[0] + w, pt[1] + h, score])

        keep = non_max_suppression_fast(boxes, overlapThresh=nms_thresh)

        found_any = False
        for i in keep:
            found_any = True
            x1, y1, x2, y2, score = boxes[i]
            matches.append({
                'subject_id': subject_id,
                'subject_name': os.path.basename(subject_name),
                'top_left': (int(x1), int(y1)),
                'bottom_right': (int(x2), int(y2)),
                'center': (int((x1 + x2) // 2), int((y1 + y2) // 2)),
                'score': float(score)
            })

        subject_found_flags[os.path.basename(subject_name)] = found_any

    return matches, subject_found_flags

def load_subject_images(folder):
    image_paths = sorted(glob(os.path.join(folder, "*.*")))
    valid_exts = {'.png', '.jpg', '.jpeg', '.bmp'}
    subject_imgs = []
    for path in image_paths:
        if os.path.splitext(path)[1].lower() in valid_exts:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                subject_imgs.append((path, img))
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

    matches, subject_found_flags = find_subjects_in_image(test_img, subject_imgs)

    print("\nDetected subject positions:")
    for match in matches:
        print(f"{match['subject_name']} at {match['top_left']} to {match['bottom_right']} "
              f"(center: {match['center']}, score: {match['score']:.2f})")

    missing_subjects = [name for name, found in subject_found_flags.items() if not found]
    if missing_subjects:
        print("\n⚠️ Templates NOT found in the test image:")
        for name in missing_subjects:
            print(f"- {name}")
    else:
        print("\n✅ All templates found in the test image.")

if __name__ == "__main__":
    main()
