#!/bin/bash

random_merge() {
    local backgrounds_dir="backgrounds"
    local overlays_dir="humans"
    
    local image_path="$1"
    local groundtruth_path="$2"
    
    background=$(find "$backgrounds_dir" -type f | shuf -n 1)
    overlay=$(find "$overlays_dir" -type f | shuf -n 1)
    echo "Processing iteration $i: $overlay + $background"
    python3 "util/merge_images.py" \
        -b "$background" -o "$overlay" \
        -gt "$groundtruth_path" -im "$image_path"
}

main() {
    local max_iterations=2000
    for ((i = 0 ; i <= $max_iterations ; i++)); do
        # For quicker creation some parallelization
        # Notice: last iteration if for validation set
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/training/im dataset/training/gt &
        random_merge dataset/validation/im dataset/validation/g
    done
}

main