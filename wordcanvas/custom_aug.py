import math
import random

import albumentations as A
import cv2
import numpy as np
from capybara import imresize
from PIL import Image


class Shear:

    def __init__(
        self,
        max_shear_left: int = 20,
        max_shear_right: int = 20,
        p: float = 0.5
    ):
        self.probability = p
        self.max_shear_left = max_shear_left
        self.max_shear_right = max_shear_right

    def __call__(self, image):
        if np.random.rand() <= self.probability:

            height, width = image.shape[0:2]
            image = Image.fromarray(image)

            angle_to_shear = int(np.random.uniform(
                (abs(self.max_shear_left)*-1) - 1, self.max_shear_right + 1))
            if angle_to_shear != -1:
                angle_to_shear += 1

            phi = math.tan(math.radians(angle_to_shear))
            shift_in_pixels = phi * height

            if shift_in_pixels > 0:
                shift_in_pixels = math.ceil(shift_in_pixels)
            else:
                shift_in_pixels = math.floor(shift_in_pixels)

            matrix_offset = shift_in_pixels
            if angle_to_shear <= 0:
                shift_in_pixels = abs(shift_in_pixels)
                matrix_offset = 0
                phi = abs(phi) * -1

            transform_matrix = (1, phi, -matrix_offset, 0, 1, 0)
            image = image.transform(
                (int(round(width + shift_in_pixels)), height),
                Image.AFFINE,
                transform_matrix,
                Image.BICUBIC
            )

            image = image.crop((abs(shift_in_pixels), 0, width, height))
            image.resize((width, height), resample=Image.BICUBIC)
            image = imresize(np.array(image), size=(height, width))

        return image


class ExampleAug:

    def __init__(self, p: float = 0.5, max_width: int = 256):
        self.shear = Shear(p=p)
        self.shift_scale = A.ShiftScaleRotate(
            shift_limit_x=0,
            shift_limit_y=0.1,
            scale_limit=[-0.2, 0],
            rotate_limit=0,
            p=1
        )
        self.safe_rotate = A.SafeRotate(limit=10, p=1)

        self.aug = A.Compose([

            A.OneOf([
                A.ChannelShuffle(),
                A.ChannelDropout(),
                A.RGBShift(),
            ]),

            A.OneOf([
                A.MotionBlur(),
                A.GaussianBlur(),
                A.Downscale(scale_range=(0.5, 0.9))
            ]),

            A.OneOf([
                A.GaussNoise(),
                A.MultiplicativeNoise(),
                A.ISONoise(),
            ], p=p),

        ])

    def __call__(self, img, background_color=(255, 255, 255)):
        img = self.shear(img)

        self.shift_scale.border_mode = random.choice([
            cv2.BORDER_CONSTANT,
            cv2.BORDER_REPLICATE,
        ])
        self.shift_scale.value = background_color
        img = self.shift_scale(image=img)['image']

        self.safe_rotate.border_mode = random.choice([
            cv2.BORDER_CONSTANT,
            cv2.BORDER_REFLECT_101,
        ])
        self.safe_rotate.value = background_color
        img = self.aug(image=img)['image']
        return img
