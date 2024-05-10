import cv2
import argparse
import albumentations as A


def apply_transformations(image):
    height, width = image.shape[
        :2
    ]  # Extracting the height and width from the overlay image
    transform = A.Compose(
        [
            A.ShiftScaleRotate(
                shift_limit_x=(0.2, 0.2),
                shift_limit_y=(0, 0),
                scale_limit=0.0,
                rotate_limit=0,
                p=1.0,
            )
        ]
    )
    return transform(image=image)["image"]


def merge_images(background_path, overlay_path, output_path, width, height):
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
    overlay = apply_transformations(overlay)

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
    cv2.imwrite(output_path, resized_background)


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

    args = parser.parse_args()

    merge_images(args.background, args.overlay, args.output, args.width, args.height)


if __name__ == "__main__":
    main()
