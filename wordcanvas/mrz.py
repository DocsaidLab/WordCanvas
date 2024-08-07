import random
from typing import List, Tuple

import docsaidkit as D
import numpy as np

from .base import WordCanvas

DIR = D.get_curdir(__file__)


class MRZGenerator:

    def __init__(
        self,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        background_color: Tuple[int, int, int] = (255, 255, 255),
        interval: int = None,
        delimiter: str = '&',
    ):
        self.delimiter = delimiter
        self.interval = interval
        self.background_color = background_color
        self.gen = WordCanvas(
            font_path=DIR / 'fonts' / 'OcrB-Regular.ttf',
            text_color=text_color,
            background_color=background_color
        )

    def gen_random_mrz(self, l: int):
        candidate = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
        return ''.join(random.choices(candidate, k=l))

    @property
    def mrz_l(self):
        return {
            'TD1': 30,
            'TD2': 36,
            'TD3': 44
        }

    def __call__(
        self,
        mrz_type: str = None,
        mrz_text: List[str] = None,
    ):
        if mrz_type is None:
            mrz_type = random.choice(['TD1', 'TD2', 'TD3'])

        if mrz_text is None:
            # Using random MRZ text
            n = 3 if mrz_type == 'TD1' else 2
            length = self.mrz_l[mrz_type]
            mrz_text = [self.gen_random_mrz(length) for _ in range(n)]
        else:
            if not isinstance(mrz_text, list):
                raise ValueError('mrz_text should be a list of mrz strings')
            if mrz_type == 'TD1' and len(mrz_text) != 3:
                raise ValueError(
                    'mrz_text should have 3 elements for TD1 mrz_typee')
            if mrz_type != 'TD1' and len(mrz_text) != 2:
                raise ValueError(
                    'mrz_text should have 2 elements for TD2 and TD3 mrz_typees')
            for i, mrz in enumerate(mrz_text):
                if not isinstance(mrz, str):
                    raise ValueError(f'mrz_text[{i}] should be a string')
                if len(mrz) != self.mrz_l[mrz_type]:
                    raise ValueError(
                        f'mrz_text[{i}] should have {self.mrz_l[mrz_type]} characters')

        if mrz_type == 'TD1':

            # Generate MRZ image
            mrz_image = [self.gen(mrz_text[i])[0] for i in range(3)]

            # Generate random interval
            if self.interval is not None:
                rnd_interval = self.interval
            else:
                rnd_interval = random.randint(8, 24)

            interval = np.zeros(
                (rnd_interval, mrz_image[0].shape[1], 3), dtype=np.uint8) + self.background_color
            img_concat = np.concatenate([
                mrz_image[0], interval, mrz_image[1], interval, mrz_image[2]], axis=0)

            # Generate coordinates for each character
            point_x_interval = img_concat.shape[1] / self.mrz_l[mrz_type]
            point_x = [int(point_x_interval / 2 + point_x_interval * i)
                       for i in range(self.mrz_l[mrz_type])]
            point_y1 = [mrz_image[0].shape[0] // 2] * self.mrz_l[mrz_type]
            point_y2 = [mrz_image[0].shape[0] + rnd_interval +
                        mrz_image[1].shape[0] // 2] * self.mrz_l[mrz_type]
            point_y3 = [img_concat.shape[0] -
                        mrz_image[0].shape[0] // 2] * self.mrz_l[mrz_type]

            points = list(zip(*[point_x, point_y1])) + \
                list(zip(*[point_x, point_y2])) + \
                list(zip(*[point_x, point_y3]))

        else:

            # Generate MRZ image
            mrz_image = [self.gen(mrz_text[i])[0] for i in range(2)]

            # Generate random interval
            if self.interval is not None:
                rnd_interval = self.interval
            else:
                rnd_interval = random.randint(8, 64)

            interval = np.zeros(
                (rnd_interval, mrz_image[0].shape[1], 3), dtype=np.uint8) + self.background_color
            img_concat = np.concatenate([
                mrz_image[0], interval, mrz_image[1]], axis=0)

            # Generate coordinates for each character
            point_x_interval = img_concat.shape[1] / self.mrz_l[mrz_type]
            point_x = [int(point_x_interval / 2 + point_x_interval * i)
                       for i in range(self.mrz_l[mrz_type])]
            point_y1 = [mrz_image[0].shape[0] // 2] * self.mrz_l[mrz_type]
            point_y2 = [img_concat.shape[0] -
                        mrz_image[0].shape[0] // 2] * self.mrz_l[mrz_type]

            points = list(zip(*[point_x, point_y1])) + \
                list(zip(*[point_x, point_y2]))

        return {
            'typ': mrz_type,
            'text': f'{self.delimiter}'.join(mrz_text),
            'points': points,
            'image': np.uint8(img_concat)
        }
