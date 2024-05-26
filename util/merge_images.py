import os
import cv2
import argparse
import random
import string
import albumentations as A


def augment_final_image(image):
    transform = A.Compose(
        [
            A.MotionBlur(blur_limit=(5, 11), p=1.0),
            A.GaussNoise(var_limit=(10, 150), p=1.0),
            A.ColorJitter(
                brightness=(0.6, 1.0),
                contrast=(0.6, 1.0),
                saturation=(0.3, 1),
                hue=(0.0, 0.1),
                p=0.5,
            ),
            A.RandomFog(
                fog_coef_lower=0.05,
                fog_coef_upper=0.2,
                alpha_coef=0.08,
                always_apply=False,
                p=0.5,
            ),
            A.RandomShadow(
                shadow_roi=(0, 0.5, 1, 1),
                num_shadows_limit=(1, 2),
                num_shadows_lower=None,
                num_shadows_upper=None,
                shadow_dimension=5,
                always_apply=False,
                p=0.5,
            ),
            A.RandomToneCurve(scale=0.1, always_apply=False, p=0.5),
        ]
    )
    return transform(image=image)["image"]


def remove_alpha_threshold(image, alpha_threshold=160):
    # This function removes artifacts created by LayerDiffusion
    mask = image[:, :, 3] < alpha_threshold
    image[mask] = [0, 0, 0, 0]
    return image


def create_ground_truth_mask(image):
    image = remove_alpha_threshold(image.copy())
    return image[:, :, 3]


def create_random_filename_from_filepath(path):
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(13))
    return random_string + "_" + os.path.basename(path)


def scale_image(image, factor=1.5):
    width = int(image.shape[1] * factor)
    height = int(image.shape[0] * factor)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)


def augment_and_match_size(image, target_width, target_height):

    random_scale = random.uniform(1, 1.5)
    image = scale_image(image, random_scale)

    transform = A.Compose(
        [
            A.HorizontalFlip(p=0.5),
            A.ShiftScaleRotate(
                shift_limit_x=(-0.3, 0.3),
                shift_limit_y=(0.0, 0.4),
                scale_limit=(0, 0),
                border_mode=cv2.BORDER_CONSTANT,
                rotate_limit=(-5, 5),
                p=0.7,
            ),
        ]
    )
    image = transform(image=image)["image"]

    # Ensure the image matches the target dimensions
    current_height, current_width = image.shape[:2]

    # Crop if the image is larger than the target size
    if current_height > target_height or current_width > target_width:
        # Calculating the top-left point to crop the image
        start_x = max(0, (current_width - target_width) // 2)
        start_y = max(0, (current_height - target_height) // 2)
        image = image[
            start_y : start_y + target_height, start_x : start_x + target_width
        ]

    # Pad if the image is smaller than the target size
    if current_height < target_height or current_width < target_width:
        delta_w = max(0, target_width - current_width)
        delta_h = max(0, target_height - current_height)
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)
        color = [0, 0, 0, 0]
        image = cv2.copyMakeBorder(
            image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )

    return image


def merge_images(background, foreground, position=(0, 0)):

    x, y = position

    fh, fw = foreground.shape[:2]

    if x + fw > background.shape[1]:
        fw = background.shape[1] - x
        foreground = foreground[:, :fw]
    if y + fh > background.shape[0]:
        fh = background.shape[0] - y
        foreground = foreground[:fh, :]

    # Region of Interest (ROI) in the background where the foreground will be placed
    roi = background[y : y + fh, x : x + fw]

    # Split the foreground image into its color and alpha channels
    foreground_color = foreground[:, :, :3]
    alpha = foreground[:, :, 3] / 255.0

    # Blend the images based on the alpha channel
    for c in range(0, 3):
        roi[:, :, c] = (1.0 - alpha) * roi[:, :, c] + alpha * foreground_color[:, :, c]

    # Place the modified ROI back into the original image
    background[y : y + fh, x : x + fw] = roi

    return background


def create_training_data(
    background_path, segmentation_path, image_path, ground_truth_path
):
    background = cv2.imread(background_path, cv2.IMREAD_COLOR)
    segmentation = cv2.imread(segmentation_path, cv2.IMREAD_UNCHANGED)

    if segmentation.shape[2] < 4:
        raise Exception(f"Image does not have an alpha channel: {segmentation_path}")

    file_name = create_random_filename_from_filepath(segmentation_path)
    image_path = os.path.join(image_path, file_name)
    ground_truth_path = os.path.join(ground_truth_path, file_name)

    bg_height, bg_width = background.shape[:2]
    segmentation = augment_and_match_size(
        segmentation, target_height=bg_height, target_width=bg_width
    )
    ground_truth = create_ground_truth_mask(segmentation)

    result = merge_images(background, segmentation)
    result = augment_final_image(result)

    assert ground_truth.shape[0] == result.shape[0]
    assert ground_truth.shape[1] == result.shape[1]

    cv2.imwrite(ground_truth_path, ground_truth)
    cv2.imwrite(image_path, result)


def main():
    parser = argparse.ArgumentParser(
        description="Merge two images with one image having transparency."
    )
    parser.add_argument(
        "-b", "--background", required=True, help="Path to the background image"
    )
    parser.add_argument(
        "-s", "--segmentation", required=True, help="Path to the segmentation image"
    )
    parser.add_argument(
        "-im",
        "--image-path",
        type=str,
        default="im",
        help="Path where the merged image will be saved",
    )
    parser.add_argument(
        "-gt",
        "--groundtruth-path",
        type=str,
        default="gt",
        help="Ground truth folder",
    )
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        os.makedirs(args.image_path)
    if not os.path.exists(args.groundtruth_path):
        os.makedirs(args.groundtruth_path)

    create_training_data(
        background_path=args.background,
        segmentation_path=args.segmentation,
        image_path=args.image_path,
        ground_truth_path=args.groundtruth_path,
    )


if __name__ == "__main__":
    main()
