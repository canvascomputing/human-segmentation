#!/bin/bash

merge() {
    local backgrounds_dir="backgrounds"
    local segmentations_dir="humans"

    background=$(find "$backgrounds_dir" -type f | shuf -n 1)
    segmentation=$(find "$segmentations_dir" -type f | shuf -n 1)

    echo "Iteration $i: $segmentation + $background"

    python3 "util/merge_images.py" \
        -b "$background" -s "$segmentation" \
        -im "$1" -gt "$2"
}

main() {
    local max_iterations=2000
    local train_gt_path="dataset/training/gt"
    local train_image_path="dataset/training/im"
    local validation_gt_path="dataset/validation/gt"
    local validation_image_path="dataset/validation/im"
    for ((i = 0 ; i <= $max_iterations ; i++)); do
        # For quicker creation some parallelization
        # Notice: last iteration is for validation set
        {
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$train_image_path" "$train_gt_path" &
            merge "$validation_image_path" "$validation_gt_path" &
        }
        wait
    done
}

main