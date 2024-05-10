import cv2
import argparse
import numpy as np


def merge_images(background_path, overlay_path, output_path):
    background = cv2.imread(background_path, cv2.IMREAD_UNCHANGED)
    overlay = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)

    if overlay.shape[2] < 4:
        raise Exception("Overlay image does not have an alpha channel.")

    if background.shape[:2] != overlay.shape[:2]:
        overlay = cv2.resize(overlay, (background.shape[1], background.shape[0]))

    overlay_img = overlay[..., :3]  # Color channels
    overlay_mask = overlay[..., 3]  # Alpha channel only

    background_img = background

    alpha_overlay = overlay_mask / 255.0

    for c in range(0, 3):
        background_img[..., c] = (
            alpha_overlay * overlay_img[..., c]
            + (1 - alpha_overlay) * background_img[..., c]
        )

    cv2.imwrite(output_path, background_img)


def main():
    parser = argparse.ArgumentParser(
        description="Merge two images with one image having transparency."
    )
    parser.add_argument(
        "-b", "--background", required=True, help="Path to the background image"
    )
    parser.add_argument(
        "-o", "--overlay", required=True, help="Path to the overlay image"
    )
    parser.add_argument(
        "-out",
        "--output",
        required=True,
        help="Path where the merged image will be saved",
    )

    args = parser.parse_args()

    merge_images(args.background, args.overlay, args.output)


if __name__ == "__main__":
    main()
