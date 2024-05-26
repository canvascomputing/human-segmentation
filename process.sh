#!/bin/bash

random_merge() {
    local backgrounds_dir="backgrounds"
    local overlays_dir="data"
    background=$(find "$backgrounds_dir" -type f | shuf -n 1)
    overlay=$(find "$overlays_dir" -type f | shuf -n 1)
    echo "Processing iteration $i: $overlay + $background"
    python3 merge_images.py -b "$background" -o "$overlay"
}

main() {
    local count=0
    local max_iterations=4000
    for ((i = 0 ; i <= $max_iterations ; i++)); do
        random_merge &
        random_merge &
        random_merge &
        random_merge &
        random_merge
    done
}

main