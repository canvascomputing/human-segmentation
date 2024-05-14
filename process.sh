#!/bin/bash

backgrounds_dir="backgrounds"
overlays_dir="data"

main() {
    local count=0  # Initialize a counter variable
    for overlay in "$overlays_dir"/*
    do
        count=$((count + 1))  # Increment the counter
        if [ -f "$overlay" ]; then
            echo "Processing iteration $count with overlay: $overlay"
            background=$(find "$backgrounds_dir" -type f | shuf -n 1)
            python3 merge_images.py -b "$background" -o "$overlay"
        fi
    done
}

main