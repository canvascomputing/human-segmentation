import os
import cv2
import argparse
from pathlib import Path
import albumentations as A


def apply_scale_and_move(image):
    transform = A.Compose(
        [
            A.ShiftScaleRotate(
                shift_limit_x=(-0.3, 0.3),
                shift_limit_y=(0, 0),
                scale_limit=(0.0, 0.2),
                border_mode=cv2.BORDER_CONSTANT,
                rotate_limit=(-10, 10),
                p=0.7,
            )
        ]
    )
    return transform(image=image)["image"]


def apply_noise(image):
    transform = A.Compose(
        [
            A.MotionBlur(blur_limit=(3, 15), p=0.5),
            A.GaussNoise(var_limit=(10, 50), p=0.5),
        ]
    )
    return transform(image=image)["image"]


def merge_images(
    background_path, overlay_path, output_path, groundtruth_path, width, height
):
    # Read the background image and resize it to the specified dimensions
    background = cv2.imread(background_path, cv2.IMREAD_COLOR)
    resized_background = cv2.resize(
        background, (width, height), interpolation=cv2.INTER_AREA
    )

    # Read the overlay image with alpha channel
    overlay = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)

    # Ensure overlay has an alpha channel
    if overlay.shape[2] < 4:
        raise Exception("Overlay image does not have an alpha channel.")

    # Apply transformations to the overlay
    overlay = expand_image_borders_rgba(overlay, width, height)
    overlay = apply_scale_and_move(overlay)

    # store ground truth
    extract_alpha_channel_as_bw(
        overlay, os.path.join(groundtruth_path, os.path.basename(overlay_path))
    )

    overlay = apply_noise(overlay)

    # Overlay placement on the resized background
    x_offset = (width - overlay.shape[1]) // 2
    y_offset = (height - overlay.shape[0]) // 2

    # Preventing overlay from exceeding the background dimensions
    x_offset = max(0, x_offset)
    y_offset = max(0, y_offset)

    # Calculate the normalized alpha mask
    alpha_overlay = overlay[..., 3] / 255.0
    region_of_interest = resized_background[
        y_offset : y_offset + overlay.shape[0],
        x_offset : x_offset + overlay.shape[1],
        :,
    ]

    # Blend the images
    for c in range(0, 3):
        region_of_interest[..., c] = (
            alpha_overlay * overlay[..., c]
            + (1 - alpha_overlay) * region_of_interest[..., c]
        )

    resized_background[
        y_offset : y_offset + overlay.shape[0], x_offset : x_offset + overlay.shape[1]
    ] = region_of_interest

    # Save the result
    cv2.imwrite(
        os.path.join(output_path, os.path.basename(overlay_path)), resized_background
    )


def expand_image_borders_rgba(
    image, final_width, final_height, border_color=(0, 0, 0, 0)
):
    # Check if image has an alpha channel
    if image.shape[2] < 4:
        raise ValueError(
            "Loaded image does not contain an alpha channel. Make sure the input image is RGBA."
        )

    # Current dimensions
    height, width = image.shape[:2]

    # Calculate padding needed
    top = bottom = (final_height - height) // 2
    left = right = (final_width - width) // 2

    # To handle cases where the new dimensions are odd and original dimensions are even (or vice versa)
    if (final_height - height) % 2 != 0:
        bottom += 1
    if (final_width - width) % 2 != 0:
        right += 1

    # Apply make border with an RGBA color
    new_image = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=border_color
    )

    return new_image


def extract_alpha_channel_as_bw(image, output_path):
    # Check if the image has an alpha channel
    if image.shape[2] < 4:
        raise ValueError(
            "Loaded image does not contain an alpha channel. Make sure the input image is in PNG format with an alpha channel."
        )

    # Extract the alpha channel
    alpha_channel = image[:, :, 3]

    # Save or display the alpha channel as a black and white image
    cv2.imwrite(output_path, alpha_channel)


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
        type=str,
        default="im",
        help="Path where the merged image will be saved",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Width to which the background image will be resized",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Height to which the background image will be resized",
    )
    parser.add_argument(
        "-gt",
        "--groundtruth",
        type=str,
        default="gt",
        help="Ground truth folder",
    )
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)
    if not os.path.exists(args.groundtruth):
        os.makedirs(args.groundtruth)

    merge_images(
        args.background,
        args.overlay,
        args.output,
        args.groundtruth,
        args.width,
        args.height,
    )


if __name__ == "__main__":
    main()
