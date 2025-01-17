import random
from enum import IntEnum
from pathlib import Path
from typing import List, Tuple, Union

import capybara as cb
import numpy as np
import regex
from prettytable import PrettyTable

from .font_utils import get_supported_characters
from .text_image_renderer import load_truetype_font, text2image

DIR = cb.get_curdir(__file__)


__all__ = [
    'AlignMode',
    'OutputDirection',
    'WordCanvas',
]


class AlignMode(cb.EnumCheckMixin, IntEnum):
    Left = 0
    Right = 1
    Center = 2
    Scatter = 3


class OutputDirection(cb.EnumCheckMixin, IntEnum):
    Remain = 0
    Horizontal = 1
    Vertical = 2


class WordCanvas:

    def __init__(
        self,
        font_path: Union[str, Path] = None,
        font_size: int = 64,
        direction: str = 'ltr',
        text_color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (0, 0, 0),
        text_aspect_ratio: float = 1.0,
        align_mode: str = AlignMode.Left,
        output_size: Tuple[int, int] = None,
        output_direction: str = OutputDirection.Remain,
        block_font_list: List[str] = [],
        stroke_width: int = 0,
        stroke_fill: Tuple[int, int, int] = (0, 0, 0),
        spacing: int = 4,
        return_infos: bool = False,
    ):

        for block_font in block_font_list:
            if block_font in Path(font_path).stem:
                raise ValueError(
                    f"\nFont: {cb.colorstr(Path(font_path).stem, 'RED')} is in the block list.\n"
                    f"\tIt means that the font has some problems and cannot be used.\n"
                )

        if stroke_width > 0:
            print(
                f"\n\tUsing `stroke_width` may cause an {cb.colorstr('OSError: array allocation size too large', 'red')} error with certain text.\n"
                f"\tThis is a known issue with the `Pillow` library (see https://github.com/python-pillow/Pillow/issues/7287) and cannot be resolved directly.\n"
            )

        if font_path is None:
            font_path = DIR / 'fonts' / 'NotoSansTC-Regular.otf'

        # Private settings
        self._font_size = font_size
        self._font_path = Path(font_path)
        self._font_tb = {}

        # Basic settings
        self.direction = direction
        self.text_color = text_color
        self.background_color = background_color
        self.text_aspect_ratio = text_aspect_ratio
        self.output_size = output_size
        self.align_mode = AlignMode.obj_to_enum(align_mode)
        self.output_direction = OutputDirection.obj_to_enum(output_direction)
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill
        self.spacing = spacing
        self.return_infos = return_infos

        self.font = load_truetype_font(font_path, size=font_size)

        _chars = get_supported_characters(font_path)
        self.chars_table = {char: i for i, char in enumerate(_chars)}

        self.font_chars_tables = {}
        self.font_chars_tables[Path(font_path).stem] = _chars

    @ property
    def font_size(self):
        return self._font_size

    @ property
    def font_path(self):
        return self._font_path

    def __repr__(self):
        return self.dashboard

    @ staticmethod
    def colorize(value):
        def select_color(value):
            return cb.COLORSTR.GREEN if value else cb.COLORSTR.RED
        return cb.colorstr(value, select_color(value))

    @ property
    def dashboard(self):

        table = PrettyTable()
        table.field_names = [
            "Property", "CurrentValue",  "SetMethod", "DType", "Description"
        ]
        table.align = "l"

        data = [
            ["font_path", self._font_path.stem,
                "reinit", "str", "Path of font file."],
            ["font_size", self._font_size, "reinit", "int", "Size of font."],
            ["direction", self.direction, "set",
                "str", "Text direction. (ltr | ttb)"],
            ["text_aspect_ratio", self.text_aspect_ratio, "set", "float",
                "Text aspect ratio. ex: set to 0.5 for half width."],
            ["text_color", self.text_color, "set",
                "Tuple[int, int, int]", "Color of text."],
            ["background_color", self.background_color, "set",
                "Tuple[int, int, int]", "Color of background."],
            ["output_size", self.output_size, "set",
                "Tuple[int, int]", "Fixed size of output image."],
            ["align_mode", self.align_mode.name, "set",
                "AlignMode", "Text alignment mode. (Left | Right | Center | Scatter)"],
            ["output_direction", self.output_direction.name, "set",
                "OutputDirection", "Output image direction. (Remain | Horizontal | Vertical)"],
        ]

        for row in data:
            table.add_row(row)

        # print(table)
        return table.get_string()

    def regularize_image(self, img, direction, align_mode, background_color) -> np.ndarray:
        h, w = self.output_size
        if direction == 'ltr':
            if self.text_aspect_ratio != 1.0:
                img = cb.imresize(
                    img,
                    (img.shape[0], int(img.shape[1] // self.text_aspect_ratio))
                )

            img = cb.imresize(img, (h, None))
            img_w = img.shape[1]
            if img_w >= w:
                img = cb.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if align_mode == AlignMode.Left:
                    pad_size = (0, 0, 0, w - img_w)
                elif align_mode == AlignMode.Right:
                    pad_size = (0, 0, w - img_w, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = (0, 0, (w - img_w) // 2, (w - img_w) // 2)
                img = cb.pad(img, pad_size, pad_value=background_color)
        elif direction == 'ttb':
            h, w = w, h

            if align_mode != AlignMode.Scatter and \
                    self.text_aspect_ratio != 1.0:
                img = cb.imresize(
                    img,
                    (img.shape[0], int(img.shape[1] // self.text_aspect_ratio))
                )

            img = cb.imresize(img, (None, w))
            img_h = img.shape[0]
            if img_h >= h:
                img = cb.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if align_mode == AlignMode.Left:
                    pad_size = (0, h - img_h, 0, 0)
                elif align_mode == AlignMode.Right:
                    pad_size = (h - img_h, 0, 0, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = ((h - img_h) // 2, (h - img_h) // 2, 0, 0)

                img = cb.pad(img, pad_size, pad_value=background_color)
        img = cb.imresize(img, (h, w))
        return img

    def gen_scatter_image(
        self, text, font, direction, text_color, background_color,
        stroke_width, stroke_fill, spacing, **kwargs
    ) -> np.ndarray:

        def split_text(text: str):
            """ Split text into a list of characters. """
            pattern = r"[a-zA-Z0-9\p{P}\p{S}]+|."
            matches = regex.findall(pattern, text)
            matches = [m for m in matches if not regex.match(r'\p{Z}', m)]
            if len(matches) == 1:
                matches = list(text)
            return matches

        if "\n" in text:
            raise ValueError(
                f"\nText:\n {cb.colorstr(text, 'RED')} \tcontains '\\n'.\n"
                f"It is not supported in the scatter mode.\n"
            )

        if 'return_infos' in kwargs:
            kwargs.pop('return_infos')

        _, infos = text2image(
            text=text,
            font=font,
            direction=direction,
            text_color=text_color,
            background_color=background_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
            spacing=spacing,
            return_infos=True,
            **kwargs
        )

        offset = infos['offset']
        width, height = infos['bbox(wh)']

        texts = split_text(text)

        if len(texts):
            imgs = [
                text2image(
                    text=t,
                    font=font,
                    direction=direction,
                    text_color=text_color,
                    background_color=background_color,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                    spacing=spacing,
                    height=height if direction == 'ltr' else None,
                    offset=offset if direction == 'ltr' else None,
                    return_infos=False,
                    **kwargs
                ) for t in texts
            ]
        else:
            img = np.zeros((height, width, 3)) + background_color
            imgs = [img.astype(np.uint8)]

        if direction == 'ltr':

            # For `self.text_aspect_ratio` is not 1.0
            if self.text_aspect_ratio != 1.0:
                imgs = [
                    cb.imresize(
                        img, (img.shape[0], int(
                            img.shape[1] // self.text_aspect_ratio))
                    ) for img in imgs
                ]

            # If there is only one image, return it directly
            if len(imgs) == 1:
                return imgs[0]

            align_h = max([img.shape[0] for img in imgs])
            imgs = [cb.imresize(img, (align_h, None)) for img in imgs]
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

            # For `self.text_aspect_ratio` is not 1.0
            if self.text_aspect_ratio != 1.0:
                imgs = [
                    cb.imresize(
                        img,
                        (max(int(img.shape[0] * self.text_aspect_ratio), 1),
                            img.shape[1])
                    ) for img in imgs
                ]

            # If there is only one image, return it directly
            if len(imgs) == 1:
                return imgs[0]

            align_w = max([img.shape[1] for img in imgs])

            pad_imgs = []
            for img in imgs:
                pad_r = (align_w - img.shape[1]) // 2
                pad_r = max(pad_r, 0)
                pad_l = align_w - pad_r - img.shape[1]
                pad_l = max(pad_l, 0)

                background_color = tuple(np.array(background_color).tolist())
                img = cb.pad(img, (0, 0, pad_l, pad_r), background_color)

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

        return img.astype(np.uint8)

    def __call__(self, text: str = None) -> np.ndarray:

        font = self.font
        font_name = Path(self._font_path).stem

        text_color = self.text_color
        background_color = self.background_color
        direction = self.direction
        align_mode = self.align_mode
        stroke_width = self.stroke_width
        stroke_fill = self.stroke_fill
        spacing = self.spacing

        if align_mode == AlignMode.Scatter and self.output_size is not None:
            img = self.gen_scatter_image(
                text=text,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                spacing=spacing,
                return_infos=True
            )

            infos = {
                'text': text,
                'direction': direction,
                'background_color': tuple(background_color.tolist()) if isinstance(background_color, np.ndarray) else background_color,
                'text_color': tuple(text_color.tolist()) if isinstance(text_color, np.ndarray) else text_color,
            }
        else:
            img, infos = text2image(
                text=text,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                spacing=spacing,
                align=align_mode.name.lower(),
                return_infos=True
            )

        if self.output_size is not None:
            img = self.regularize_image(
                img,
                direction=direction,
                align_mode=align_mode,
                background_color=infos['background_color']
            )

        if self.output_direction == OutputDirection.Vertical \
                and infos['direction'] == 'ltr':
            img = cb.imrotate90(img, rotate_code=cb.ROTATE.ROTATE_90)
        elif self.output_direction == OutputDirection.Horizontal \
                and infos['direction'] == 'ttb':
            img = cb.imrotate90(img, rotate_code=cb.ROTATE.ROTATE_270)

        infos.update({
            'font_name': font_name,
            'align_mode': align_mode,
            'output_direction': self.output_direction,
        })

        if self.return_infos:
            return img, infos

        return img


class RandomWordCanvas(WordCanvas):

    def __init__(
        self,
        font_bank: Union[str, Path] = None,
        font_size: int = 64,
        output_size: Tuple[int, int] = None,
        output_direction: str = OutputDirection.Remain,
        block_font_list: List[str] = [],
        random_font: bool = False,
        random_text: bool = False,
        random_align_mode: bool = False,
        random_text_color: bool = False,
        random_background_color: bool = False,
        random_direction: bool = False,
        random_font_weight: bool = False,
        random_spacing: bool = False,
        random_stroke_width: bool = False,
        random_stroke_fill: bool = False,
        random_lines: bool = False,
        min_random_text_length: int = 1,
        max_random_text_length: int = 9,
        min_random_stroke_width: int = 0,
        max_random_stroke_width: int = 5,
        min_random_spacing: int = 0,
        max_random_spacing: int = 5,
        min_random_lines: int = 1,
        max_random_lines: int = 2,
        return_infos: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)

        if random_stroke_width:
            print(
                f"\n\tUsing `random_stroke_width` may cause an {cb.colorstr('OSError: array allocation size too large', 'red')} error with certain text.\n"
                f"\tThis is a known issue with the `Pillow` library (see https://github.com/python-pillow/Pillow/issues/7287) and cannot be resolved directly.\n"
            )

        self._font_bank = DIR / 'fonts' \
            if font_bank is None else Path(font_bank)
        self._font_size = font_size

        self.output_size = output_size
        self.output_direction = OutputDirection.obj_to_enum(output_direction)
        self.return_infos = return_infos

        self.random_font = random_font
        self.random_text = random_text
        self.random_align_mode = random_align_mode
        self.random_direction = random_direction
        self.random_text_color = random_text_color
        self.random_background_color = random_background_color
        self.random_spacing = random_spacing
        self.random_stroke_width = random_stroke_width
        self.random_stroke_fill = random_stroke_fill
        self.random_lines = random_lines
        self.min_random_text_length = min_random_text_length
        self.max_random_text_length = max_random_text_length
        self.min_random_stroke_width = min_random_stroke_width
        self.max_random_stroke_width = max_random_stroke_width
        self.min_random_spacing = min_random_spacing
        self.max_random_spacing = max_random_spacing
        self.min_random_lines = min_random_lines
        self.max_random_lines = max_random_lines
        self.random_font_weight = random_font_weight

        # Using random fonts with bank
        self.font_table = {}
        if self.random_font:
            print('Loading all fonts from bank...')

            unique_chars = set()
            number_font_chars = {}
            font_bank_fs = []
            for font in cb.Tqdm(cb.get_files(self.font_bank, suffix=['.ttf', '.otf'])):

                is_block_font = False
                for block_font in block_font_list:
                    if block_font in font.stem:
                        print(
                            f"\rFont: {cb.colorstr(font.stem, 'RED')} is in the block list.\n"
                            f"\tIt means that the font has some problems and cannot be used.\n"
                        )
                        is_block_font = True
                        break

                if is_block_font:
                    continue

                if font.stem in self.font_table:
                    print(
                        f'Find duplicated font in FONT_BANK: {cb.colorstr(font.stem, "BLUE")}, Skip.')
                    continue

                font_chars = get_supported_characters(font)
                number_font_chars[font.stem] = len(font_chars)
                unique_chars.update(font_chars)
                font_bank_fs.append(font)

                self.font_chars_tables[font.stem] = font_chars
                self.font_table[font.stem] = load_truetype_font(
                    font, size=font_size)

            self.chars_table = {
                char: i for i, char in enumerate(sorted(unique_chars, key=ord))
            }

            if self.random_font_weight:
                sum_chars = sum(number_font_chars.values())
                self.weighted_font = {
                    font.stem: number_font_chars[font.stem] / sum_chars
                    for font in font_bank_fs
                }
        else:
            self.weighted_font = {Path(self._font_path).stem: 1.0}

    @ property
    def font_bank(self):
        return self._font_bank

    @ property
    def dashboard(self):

        table = PrettyTable()
        table.field_names = [
            "Property", "CurrentValue",  "SetMethod", "DType", "Description"
        ]
        table.align = "l"

        data = [
            ["font_path", self._font_path.stem,
                "reinit", "str", "Path of font file."],
            ["font_bank", self._font_bank, "reinit", "str", "Path of font bank."],
            ["font_size", self._font_size, "reinit", "int", "Size of font."],
            ["direction", self.direction, "set",
                "str", "Text direction. (ltr | ttb)"],
            ["text_color", self.text_color, "set",
                "Tuple[int, int, int]", "Color of text."],
            ["background_color", self.background_color, "set",
                "Tuple[int, int, int]", "Color of background."],
            ["output_size", self.output_size, "set",
                "Tuple[int, int]", "Fixed size of output image."],
            ["align_mode", self.align_mode.name, "set",
                "AlignMode", "Text alignment mode. (Left | Right | Center | Scatter)"],
            ["output_direction", self.output_direction.name, "set",
                "OutputDirection", "Output image direction. (Remain | Horizontal | Vertical)"],
            ["min_random_text_length", self.min_random_text_length, "set", "int",
                "Random minimum text length."],
            ["max_random_text_length", self.max_random_text_length, "set", "int",
                "Random maximum text length."],
            ["min_random_stroke_width", self.min_random_stroke_width, "set", "int",
                "Random minimum stroke width."],
            ["max_random_stroke_width", self.max_random_stroke_width, "set", "int",
                "Random maximum stroke width."],
            ["min_random_spacing", self.min_random_spacing, "set", "int",
                "Random minimum spacing."],
            ["max_random_spacing", self.max_random_spacing, "set", "int",
                "Random maximum spacing."],
            ["min_random_lines", self.min_random_lines, "set", "int",
                "Random minimum lines."],
            ["max_random_lines", self.max_random_lines, "set", "int",
                "Random maximum lines."],
            ["random_font", self.colorize(
                self.random_font), "set", "bool", "Randomize font."],
            ["random_text", self.colorize(
                self.random_text), "set", "bool", "Randomize text."],
            ["random_direction", self.colorize(
                self.random_direction), "set", "bool", "Randomize direction."],
            ["random_text_color", self.colorize(
                self.random_text_color), "set", "bool", "Randomize text color."],
            ["random_background_color", self.colorize(
                self.random_background_color), "set", "bool", "Randomize background color."],
            ["random_align_mode", self.colorize(
                self.random_align_mode), "set", "bool", "Randomize align mode."],
            ["random_font_weight", self.colorize(
                self.random_font_weight), "set", "bool", "Randomize font weight."],
            ["random_spacing", self.colorize(
                self.random_spacing), "set", "bool", "Randomize spacing."],
            ["random_stroke_width", self.colorize(
                self.random_stroke_width), "set", "bool", "Randomize stroke width."],
            ["random_stroke_fill", self.colorize(
                self.random_stroke_fill), "set", "bool", "Randomize stroke fill."],
            ["random_lines", self.colorize(
                self.random_lines), "set", "bool", "Randomize lines."],
        ]

        for row in data:
            table.add_row(row)

        # print(table)
        return table.get_string()

    def __call__(self, text: str = None) -> np.ndarray:

        if self.random_font:
            weighted_font = None
            if self.random_font_weight:
                weighted_font = list(self.weighted_font.values())
            candi_font = list(self.font_table.keys())
            font_idx = np.random.choice(len(candi_font), p=weighted_font)
            font = self.font_table[candi_font[font_idx]]
            font_name = Path(font.path).stem
        else:
            font = self.font
            font_name = Path(self._font_path).stem

        if self.random_text:
            candidates = self.font_chars_tables[font_name]
            text_length = np.random.randint(
                self.min_random_text_length, self.max_random_text_length + 1)
            text = ''.join(np.random.choice(candidates, text_length))

            if self.random_lines:
                lines = np.random.randint(
                    self.min_random_lines, self.max_random_lines + 1)
                num_change = lines - 1
                if num_change > 0 and len(text) > num_change:
                    for _ in range(num_change):
                        idx = np.random.randint(1, len(text))
                        text = text[:idx] + '\n' + text[idx:]

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
        align_mode = list(AlignMode)
        if "\n" in text:
            align_mode.remove(AlignMode.Scatter)

        align_mode = random.choice(align_mode) \
            if self.random_align_mode else self.align_mode

        # Randomize stroke width
        min_stroke_width = self.min_random_stroke_width
        max_stroke_width = self.max_random_stroke_width
        stroke_width = np.random.randint(min_stroke_width, max_stroke_width) \
            if self.random_stroke_width else self.stroke_width

        # Randomize stroke fill
        stroke_fill = np.random.randint(0, 255, 3) \
            if self.random_stroke_fill else self.stroke_fill

        # Randomize spacing
        min_spacing = self.min_random_spacing
        max_spacing = self.max_random_spacing
        spacing = np.random.randint(min_spacing, max_spacing) \
            if self.random_spacing else self.spacing

        if align_mode == AlignMode.Scatter and self.output_size is not None:
            img = self.gen_scatter_image(
                text=text,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                spacing=spacing,
            )

            infos = {
                'text': text,
                'direction': direction,
                'background_color': tuple(background_color.tolist()) if isinstance(background_color, np.ndarray) else background_color,
                'text_color': tuple(text_color.tolist()) if isinstance(text_color, np.ndarray) else text_color,
            }
        else:
            img, infos = text2image(
                text=text,
                font=font,
                direction=direction,
                text_color=text_color,
                background_color=background_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                spacing=spacing,
                return_infos=True,
                align=align_mode.name.lower()
            )

        if self.output_size is not None:
            img = self.regularize_image(
                img,
                direction=direction,
                align_mode=align_mode,
                background_color=infos['background_color']
            )

        if self.output_direction == OutputDirection.Vertical \
                and infos['direction'] == 'ltr':
            img = cb.imrotate90(img, rotate_code=cb.ROTATE.ROTATE_90)
        elif self.output_direction == OutputDirection.Horizontal \
                and infos['direction'] == 'ttb':
            img = cb.imrotate90(img, rotate_code=cb.ROTATE.ROTATE_270)

        infos.update({
            'font_name': font_name,
            'align_mode': align_mode,
            'output_direction': self.output_direction,
        })

        if self.return_infos:
            return img, infos

        return img


# if __name__ == '__main__':

#     from pprint import pprint

    # gen = WordCanvas(output_size=(64, 512), random_font=False,
    #                  align_mode=AlignMode.Scatter, direction='ltr',
    #                  text_aspect_ratio=1, random_text=True,
    #                  random_text_color=True, random_background_color=True,
    #                  random_align_mode=True, use_random_font_weight=True,
    #                  output_direction=OutputDirection.Remain)
    # gen = WordCanvas(
    #     background_color=(0, 0, 255),
    #     text_color=(255, 0, 0),
    #     output_size=(64, 1024),
    #     align_mode=AlignMode.Left,
    #     direction='ltr',
    #     stroke_width=5,
    #     stroke_fill=(0, 255, 0),
    #     return_infos=True,
    # )
    # for _ in cb.Tqdm(range(100000)):
    #     img, infos = gen('測試輸出')
    # img, infos = text2image(
    #     '測試輸出', font=DIR / 'fonts' / '/home/shayne/workspace/WordCanvas/wordcanvas/fonts/TW-Kai-98_1.ttf', size=60)
    # gen = RandomWordCanvas(
    #     random_font=True,
    #     random_text=False,
    #     random_background_color=True,
    #     random_text_color=True,
    #     return_infos=True,
    #     random_align_mode=True,
    #     output_size=(64, 512),
    #     random_spacing=False,
    #     random_stroke_width=False,
    #     random_stroke_fill=False,
    # )
    # breakpoint()
    # for _ in cb.Tqdm(range(100000)):
    #     img, infos = gen()
    # img, infos = gen('測試輸出\nＡＢＣ123')
    # pprint(infos)
    # cb.imwrite(img)
