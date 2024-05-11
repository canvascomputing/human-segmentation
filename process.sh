#!/bin/bash

backgrounds_dir="backgrounds"
overlays_dir="data"

main() {
    for overlay in "$overlays_dir"/*
    do
        if [ -f "$overlay" ]; then
            background=$(find "$backgrounds_dir" -type f | shuf -n 1)
            python3 merge_images.py -b "$background" -o "$overlay"
        fi
    done
}

main