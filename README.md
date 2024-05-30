---
license: apache-2.0
tags:
  - art
pretty_name: Human Segmentation Dataset
---

# Human Segmentation Dataset

[>>> Download Here <<<](https://drive.google.com/drive/folders/1K1lK6nSoaQ7PLta-bcfol3XSGZA1b9nt?usp=drive_link)

This dataset was created **for developing the best fully open-source background remover** of images with humans. It was crafted with [LayerDiffuse](https://github.com/layerdiffusion/LayerDiffuse), a Stable Diffusion extension for generating transparent images.

The dataset covers a diverse set of segmented humans: various skin tones, clothes, hair styles etc. Since Stable Diffusion is not perfect, the dataset contains images with flaws. Still the dataset is good enough for training background remover models.

It contains transparent images of humans (`/humans`) which are randomly combined with backgrounds (`/backgrounds`) with an augmentation script.

I created more than 5.000 images with people and more than 5.000 diverse backgrounds.

# Create Training Dataset

1. [Download human segmentations and backgrounds](https://drive.google.com/drive/folders/1K1lK6nSoaQ7PLta-bcfol3XSGZA1b9nt?usp=drive_link)

2. Execute the following script for creating training and validation data:

```
./create_dataset.sh
```

# Examples

Here you can see an augmented image and the resulting ground truth:

![](example_image.png)
![](example_ground_truth.png)

# Support

If you identify weaknesses in the data, please contact me.

I had some trouble with the Hugging Face file upload. This is why you can find the data here: [Google Drive](https://drive.google.com/drive/folders/1K1lK6nSoaQ7PLta-bcfol3XSGZA1b9nt?usp=drive_link).

# Research

Synthetic datasets have limitations for achieving great segmentation results. This is because artificial lighting, occlusion, scale or backgrounds create a gap between synthetic and real images. A "model trained solely on synthetic data generated with naïve domain randomization struggles to generalize on the real domain", see [PEOPLESANSPEOPLE: A Synthetic Data Generator for Human-Centric Computer Vision (2022)](https://arxiv.org/pdf/2112.09290). However, hybrid training approaches seem to be promising and can even improve segmentation results.

Currently I am doing research how to close this gap with the resources I have. There are approaches like considering the pose of humans for improving segmentation results, see [Cross-Domain Complementary Learning Using Pose for Multi-Person Part Segmentation (2019)](https://arxiv.org/pdf/1907.05193).

# Changelog

### 28.05.2024

- Reduced blur, because it leads to blurred edges in results

### 26.05.2024

- Added more diverse backgrounds (natural landscapes, streets, houses)
- Added more close-up images
- Added shadow augmentation
