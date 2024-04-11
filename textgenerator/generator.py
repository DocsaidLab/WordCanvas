from enum import IntEnum
from pathlib import Path
from pprint import pprint
from typing import Tuple, Union

import docsaidkit as D
import numpy as np
import regex

from .text2image import text2image
from .utils import get_supported_characters, load_truetype_font

DIR = D.get_curdir(__file__)

__all__ = [
    'TextGenerator', 'AlignMode', 'OutputDirection',
]


class AlignMode(D.EnumCheckMixin, IntEnum):
    Default = 0
    Left = 0
    Right = 1
    Center = 2
    Scatter = 3


class OutputDirection(D.EnumCheckMixin, IntEnum):
    Default = 0
    Remain = 0
    Horizontal = 1
    Vertical = 2


class TextGenerator:

    DEFAULT_FONT_BANK = DIR / 'fonts'
    DEFAULT_FONT_PATH = DIR / 'fonts' / 'NotoSans' / 'NotoSansTC-Regular.otf'

    def __init__(
        self,
        font_path: Union[str, Path] = DEFAULT_FONT_PATH,
        text_size: int = 64,
        direction: str = 'ltr',
        text_color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (0, 0, 0),
        text_ascept_ratio: float = 1.0,
        align_mode: str = AlignMode.Default,
        output_size: Tuple[int, int] = None,
        output_direction: str = OutputDirection.Default,
        *,
        enable_all_random: bool = False,
        font_bonk: Union[str, Path] = DEFAULT_FONT_BANK,
        random_font: bool = False,
        random_text: bool = False,
        min_random_text_length: int = 1,
        max_random_text_length: int = 7,
        random_direction: bool = False,
        random_text_color: bool = False,
        random_align_mode: bool = False,
        random_background_color: bool = False,
    ):
        self.font_path = font_path
        self.font = load_truetype_font(font_path, size=text_size)
        self.font_chars_tables = {
            Path(font_path).stem: get_supported_characters(font_path)
        }

        self.text_size = text_size
        self.direction = direction
        self.text_color = text_color
        self.background_color = background_color
        self.text_ascept_ratio = text_ascept_ratio
        self.align_mode = AlignMode.obj_to_enum(align_mode)
        self.output_size = output_size
        self.output_direction = OutputDirection.obj_to_enum(output_direction)
        self.min_random_text_length = min_random_text_length
        self.max_random_text_length = max_random_text_length

        self.enable_all_random = enable_all_random
        self.random_text = random_text or enable_all_random
        self.random_font = random_font or enable_all_random
        self.random_align_mode = random_align_mode or enable_all_random
        self.random_direction = random_direction or enable_all_random
        self.random_text_color = random_text_color or enable_all_random
        self.random_background_color = random_background_color or enable_all_random

        if random_font or enable_all_random:
            print('Loading all fonts from bank...')
            font_bonk = D.get_files(font_bonk, suffix=['.ttf', '.otf'])
            self.font_bank = [
                load_truetype_font(font, size=text_size)
                for font in D.Tqdm(font_bonk)
            ]

            if random_text:
                # Overwrite font_chars_tables settings
                print('Building character tables...')
                self.font_chars_tables = {
                    font.stem: get_supported_characters(font)
                    for font in D.Tqdm(font_bonk)
                }

    def __repr__(self):
        return f'{self.__class__.__name__}(\n\t' + ',\n\t'.join([
            f'font_path={self.font_path.stem!r}',
            f'text_size={self.text_size!r}',
            f'direction={self.direction!r}',
            f'text_color={self.text_color!r}',
            f'background_color={self.background_color!r}',
            f'align_mode={self.align_mode!r}',
            f'output_size={self.output_size!r}',
            f'output_direction={self.output_direction!r}',
            f'enable_all_random={self.enable_all_random!r}',
            f'random_font={self.random_font!r}',
            f'random_text={self.random_text!r}',
            f'random_direction={self.random_direction!r}',
            f'random_text_color={self.random_text_color!r}',
            f'random_background_color={self.random_background_color!r}',
            f'random_align_mode={self.random_align_mode!r}',
            f'min_random_text_length={self.min_random_text_length!r}',
            f'max_random_text_length={self.max_random_text_length!r}',
        ]) + '\n)'

    def regularize_image(self, img, direction, background_color) -> np.ndarray:
        h, w = self.output_size
        if direction == 'ltr':
            img = D.imresize(
                img,
                (img.shape[0], int(img.shape[1] // self.text_ascept_ratio))
            )
            img = D.imresize(img, (h, None))
            img_w = img.shape[1]
            if img_w > w:
                img = D.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if self.align_mode == AlignMode.Left:
                    pad_size = (0, 0, 0, w - img_w)
                elif self.align_mode == AlignMode.Right:
                    pad_size = (0, 0, w - img_w, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = (0, 0, (w - img_w) // 2, (w - img_w) // 2)
                img = D.pad(img, pad_size, fill_value=background_color)
        elif direction == 'ttb':
            h, w = w, h

            if self.align_mode != AlignMode.Scatter:
                img = D.imresize(
                    img,
                    (img.shape[0], int(img.shape[1] // self.text_ascept_ratio))
                )

            img = D.imresize(img, (None, w))
            img_h = img.shape[0]
            if img_h > h:
                img = D.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if self.align_mode == AlignMode.Left:
                    pad_size = (0, h - img_h, 0, 0)
                elif self.align_mode == AlignMode.Right:
                    pad_size = (h - img_h, 0, 0, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = ((h - img_h) // 2, (h - img_h) // 2, 0, 0)
                img = D.pad(img, pad_size, fill_value=background_color)
        return img

    def gen_scatter_image(self, text, font, direction, text_color, background_color) -> np.ndarray:

        def split_text(text: str):
            """ Split text into a list of characters. """
            pattern = r"[a-zA-Z0-9<]+|."
            matches = regex.findall(pattern, text)
            # If the text is a single character, split it into a list
            if len(matches) == 1:
                matches = list(text)
            return matches

        texts = split_text(text)

        imgs = [
            text2image(
                text=t,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
            )[0] for t in texts if t != ' '  # Skip space
        ]

        # If there is only one image, return it directly
        if len(imgs) == 1:
            return imgs[0]

        if direction == 'ltr':

            # For `self.text_ascept_ratio` is not 1.0
            if self.text_ascept_ratio != 1.0:
                imgs = [
                    D.imresize(
                        img, (img.shape[0], int(
                            img.shape[1] // self.text_ascept_ratio))
                    ) for img in imgs
                ]

            align_h = max([img.shape[0] for img in imgs])
            imgs = [D.imresize(img, (align_h, None)) for img in imgs]
            sum_w = sum([img.shape[1] for img in imgs])
            interval = (self.output_size[1] - sum_w) // (len(imgs) - 1)
            interval = max(interval, 0)

            imgs_add_interval = []
            img_interval = np.zeros((align_h, interval, 3))
            img_interval = img_interval + background_color

            for i, img in enumerate(imgs):
                imgs_add_interval.append(img)
                if i != len(imgs) - 1:
                    imgs_add_interval.append(img_interval)

            img = np.concatenate(imgs_add_interval, axis=1)

        elif direction == 'ttb':

            # For `self.text_ascept_ratio` is not 1.0
            if self.text_ascept_ratio != 1.0:
                imgs = [
                    D.imresize(
                        img,
                        (int(img.shape[0] * self.text_ascept_ratio),
                         img.shape[1])
                    ) for img in imgs
                ]

            align_w = max([img.shape[1] for img in imgs])

            pad_imgs = []
            for img in imgs:
                pad_r = (align_w - img.shape[1]) // 2
                pad_r = max(pad_r, 0)
                pad_l = align_w - pad_r - img.shape[1]
                pad_l = max(pad_l, 0)
                img = D.pad(img, (0, 0, pad_l, pad_r), background_color)
                pad_imgs.append(img)

            sum_h = sum([img.shape[0] for img in pad_imgs])
            interval = (self.output_size[1] - sum_h) // (len(pad_imgs) - 1)
            interval = max(interval, 0)

            imgs_add_interval = []
            img_interval = np.zeros((interval, align_w, 3))
            img_interval = img_interval + background_color

            for i, img in enumerate(pad_imgs):
                imgs_add_interval.append(img)
                if i != len(pad_imgs) - 1:
                    imgs_add_interval.append(img_interval)

            img = np.concatenate(imgs_add_interval, axis=0)

        return img

    def __call__(self, text: str) -> np.ndarray:

        if self.random_font:
            # Load a random font from the bank
            font = np.random.choice(self.font_bank)
            font_name = font.path.stem
        else:
            font = self.font
            font_name = Path(self.font_path).stem

        if self.random_text:
            candidates = self.font_chars_tables[font_name]

            # Randomize text length
            text_length = np.random.randint(
                self.min_random_text_length, self.max_random_text_length + 1)
            text = ''.join(np.random.choice(candidates, text_length))

        # Overwrite text color with random color
        text_color = np.random.randint(0, 255, 3) \
            if self.random_text_color else self.text_color

        # Overwrite background color with random color
        background_color = np.random.randint(0, 255, 3) \
            if self.random_background_color else self.background_color

        # Randomize text direction
        direction = np.random.choice(['ltr', 'ttb']) \
            if self.random_direction else self.direction

        # Randomize align mode
        align_mode = np.random.choice(list(AlignMode)) \
            if self.random_align_mode else self.align_mode

        # Align model setting of `SCATTER` is special case
        if align_mode == AlignMode.Scatter:
            img = self.gen_scatter_image(
                text, font, direction, text_color, background_color)
            infos = {
                'text': text,
                'direction': direction,
                'background_color': background_color,
                'text_color': text_color,
            }
        else:
            img, infos = text2image(
                text=text,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
            )

        if self.output_size is not None:
            img = self.regularize_image(
                img,
                direction=direction,
                background_color=infos['background_color']
            )

        if self.output_direction == OutputDirection.Vertical \
                and infos['direction'] == 'ltr':
            img = D.imrotate90(img, rotate_code=D.ROTATE.ROTATE_90)
        elif self.output_direction == OutputDirection.Horizontal \
                and infos['direction'] == 'ttb':
            img = D.imrotate90(img, rotate_code=D.ROTATE.ROTATE_270)

        infos.update({
            'font_name': font_name,
            'align_mode': align_mode,
        })
        pprint(infos)

        return img


if __name__ == '__main__':
    gen = TextGenerator(output_size=(64, 1024), random_font=False,
                        align_mode=AlignMode.Scatter, direction='ltr',
                        output_direction=OutputDirection.Remain)
    img = gen('測試輸出！ ABCD')
    D.imwrite(img)
