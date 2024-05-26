import cv2
from merge_images import augment_and_match_size


if __name__ == "__main__":
    image = cv2.imread("humans/example01.png", cv2.IMREAD_UNCHANGED)
    result = augment_and_match_size(image, 600, 1000)
    cv2.imwrite("dataset/test.png", result)
