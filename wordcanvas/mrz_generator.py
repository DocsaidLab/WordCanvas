import random
from typing import List, Tuple, Union

from capybara import get_curdir

from .word_canvas import RandomWordCanvas

DIR = get_curdir(__file__)


class MRZGenerator:

    def __init__(
        self,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        background_color: Tuple[int, int, int] = (255, 255, 255),
        spacing: int = None,
        **kwargs
    ):

        if spacing is None:
            interval_settings = {
                'random_spacing': True,
                'min_random_spacing': 8,
                'max_random_spacing': 64
            }
        else:
            interval_settings = {
                'spacing': spacing
            }

        self.spacing = spacing
        self.background_color = background_color
        self.gen = RandomWordCanvas(
            font_path=DIR / 'fonts' / 'OcrB-Regular.ttf',
            text_color=text_color,
            background_color=background_color,
            return_infos=True,
            **interval_settings,
            **kwargs
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
        mrz_text: Union[str, List[str]] = None,
    ):
        if mrz_type is None:
            mrz_type = random.choice(['TD1', 'TD2', 'TD3'])

        if mrz_text is None:
            # Using random MRZ text
            n = 3 if mrz_type == 'TD1' else 2
            length = self.mrz_l[mrz_type]
            mrz_text = '\n'.join(
                [self.gen_random_mrz(length) for _ in range(n)])
        else:
            if isinstance(mrz_text, str):
                lines = mrz_text.split('\n')
                if mrz_type == 'TD1' and (len(lines) != 3 or any(len(line) != 30 for line in lines)):
                    raise ValueError(
                        'For TD1, mrz_text must contain exactly 3 lines with 30 characters each.')
                if mrz_type in ['TD2', 'TD3'] and (len(lines) != 2 or any(len(line) != self.mrz_l[mrz_type] for line in lines)):
                    raise ValueError(
                        f'For {mrz_type}, mrz_text must contain exactly 2 lines with {self.mrz_l[mrz_type]} characters each.')
            elif isinstance(mrz_text, list):
                if mrz_type == 'TD1' and (len(mrz_text) != 3 or any(len(line) != 30 for line in mrz_text)):
                    raise ValueError(
                        'For TD1, mrz_text must be a list of 3 strings with 30 characters each.')
                if mrz_type in ['TD2', 'TD3'] and (len(mrz_text) != 2 or any(len(line) != self.mrz_l[mrz_type] for line in mrz_text)):
                    raise ValueError(
                        f'For {mrz_type}, mrz_text must be a list of 2 strings with {self.mrz_l[mrz_type]} characters each.')
                mrz_text = '\n'.join(mrz_text)
            else:
                raise ValueError(
                    'mrz_text must be either a string or a list of strings.')

        if mrz_type == 'TD1':

            # Generate MRZ image
            mrz_image, infos = self.gen(mrz_text)
            spacing = infos['spacing']

            # Generate coordinates for each character
            point_x_interval = mrz_image.shape[1] / self.mrz_l[mrz_type]
            point_x = [int(point_x_interval / 2 + point_x_interval * i)
                       for i in range(self.mrz_l[mrz_type])]

            base_h = (mrz_image.shape[0] - 2 * spacing) // 3
            point_y1 = [0.5 * base_h] * self.mrz_l[mrz_type]
            point_y2 = [1.5 * base_h + spacing] * self.mrz_l[mrz_type]
            point_y3 = [2.5 * base_h + spacing * 2] * self.mrz_l[mrz_type]

            points = list(zip(*[point_x, point_y1])) + \
                list(zip(*[point_x, point_y2])) + \
                list(zip(*[point_x, point_y3]))

        else:

            # Generate MRZ image
            mrz_image, infos = self.gen(mrz_text)
            spacing = infos['spacing']

            # Generate coordinates for each character
            point_x_interval = mrz_image.shape[1] / self.mrz_l[mrz_type]
            point_x = [int(point_x_interval / 2 + point_x_interval * i)
                       for i in range(self.mrz_l[mrz_type])]

            base_h = (mrz_image.shape[0] - spacing) // 2
            point_y1 = [0.5 * base_h] * self.mrz_l[mrz_type]
            point_y2 = [1.5 * base_h + spacing] * self.mrz_l[mrz_type]

            points = list(zip(*[point_x, point_y1])) + \
                list(zip(*[point_x, point_y2]))

        return {
            'typ': mrz_type,
            'text': mrz_text,
            'points': points,
            'image': mrz_image
        }


# if __name__ == '__main__':

#     import capybara as cb

#     mrz_gen = MRZGenerator(
#         random_background_color=True,
#         random_text_color=True,
#     )

#     mrz = mrz_gen(
#         mrz_type='TD2',
#         mrz_text=[
#             "ABCDEFGHIJKLMNOPQRSTUVWXY01234500000",
#             "ZYXWVUTSRQPONMLKJIHGFEDCBA0987650000"
#         ]
#     )

#     cb.imwrite(mrz['image'])
#     print(mrz['text'])
#     print(mrz['points'])
#     print(mrz['typ'])

#     points_img = cb.draw_points(mrz['image'], mrz['points'], scales=5)
#     cb.imwrite(points_img)
