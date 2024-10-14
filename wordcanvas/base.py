import random
from enum import IntEnum
from pathlib import Path
from typing import List, Tuple, Union

import docsaidkit as D
import numpy as np
import regex
from prettytable import PrettyTable

from .text2image import text2image
from .utils import get_supported_characters, load_truetype_font

DIR = D.get_curdir(__file__)


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


class WordCanvas:

    # Using `font_bank` to setting for your own font bank.
    DEFAULT_FONT_BANK = DIR / 'fonts'

    # Using `font_path` to setting for your own font.
    DEFAULT_FONT_PATH = DIR / 'fonts' / 'NotoSansTC-Regular.otf'

    def __init__(
        self,
        font_path: Union[str, Path] = DEFAULT_FONT_PATH,
        text_size: int = 64,
        direction: str = 'ltr',
        text_color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (0, 0, 0),
        text_aspect_ratio: float = 1.0,
        align_mode: str = AlignMode.Default,
        output_size: Tuple[int, int] = None,
        output_direction: str = OutputDirection.Default,
        block_font_list: List[str] = [],
        *,
        enable_all_random: bool = False,
        font_bank: Union[str, Path] = DEFAULT_FONT_BANK,
        random_font: bool = False,
        use_random_font_weight: bool = False,
        random_text: bool = False,
        min_random_text_length: int = 1,
        max_random_text_length: int = 7,
        random_direction: bool = False,
        random_text_color: bool = False,
        random_align_mode: bool = False,
        random_background_color: bool = False,
    ):

        for block_font in block_font_list:
            if block_font in Path(font_path).stem:
                raise ValueError(
                    f"\nFont: {D.colorstr(Path(font_path).stem, 'RED')} is in the block list.\n"
                    f"\tIt means that the font has some problems and cannot be used.\n"
                )

        # Private settings
        self._text_size = text_size
        self._font_path = font_path
        self._font_bank = font_bank
        self._font_tb = {}
        self._random_font = random_font

        # Basic settings
        self.direction = direction
        self.text_color = text_color
        self.background_color = background_color
        self.text_aspect_ratio = text_aspect_ratio
        self.output_size = output_size
        self.align_mode = AlignMode.obj_to_enum(align_mode)
        self.output_direction = OutputDirection.obj_to_enum(output_direction)
        self.min_random_text_length = min_random_text_length
        self.max_random_text_length = max_random_text_length

        # Random settings
        self.random_text = random_text  # Not affected by `enable_all_random`
        self.enable_all_random = enable_all_random
        self.random_align_mode = random_align_mode or enable_all_random
        self.random_direction = random_direction or enable_all_random
        self.random_text_color = random_text_color or enable_all_random
        self.random_background_color = random_background_color or enable_all_random

        # Only if `random_font` is True and `random_text` is True
        # and `use_random_font_weight` is True, the font weight will be used.
        if random_font and random_text:
            self._use_random_font_weight = use_random_font_weight
        else:
            self._use_random_font_weight = False

        self.font_chars_tables = {}
        if random_font:
            # Using random fonts with bank
            print('Loading all fonts from bank...')

            unique_chars = set()
            number_font_chars = {}
            font_bank_fs = []
            for font in D.Tqdm(D.get_files(font_bank, suffix=['.ttf', '.otf'])):

                for block_font in block_font_list:
                    if block_font in font.stem:
                        print(
                            f"\rFont: {D.colorstr(font.stem, 'RED')} is in the block list.\n"
                            f"\tIt means that the font has some problems and cannot be used.\n"
                        )
                        continue

                if font.stem in self._font_tb:
                    print(
                        f'Find duplicated font in FONT_BANK: {D.colorstr(font.stem, "BLUE")}, Skip.')
                    continue

                try:
                    _chars = get_supported_characters(font, use_cache=True)

                    # checking font characters
                    # 不支援範圍：異體選擇字元補充區（Variation Selectors Supplement）
                    # U+E0100 ～ U+E01EF
                    checking_chars = list(map(ord, _chars))
                    checking_chars = np.array(checking_chars)
                    if (checking_chars > int("0xE0100", 16)).any():
                        print(
                            f'\n\nFont: {D.colorstr(font.stem, "GREEN")} is not supported.\n'
                            f"Some characters are in the Variation Selectors Supplement. Skip.\n\n"
                        )
                        continue

                    number_font_chars[font.stem] = len(_chars)
                    unique_chars.update(_chars)
                    font_bank_fs.append(font)

                    self.font_chars_tables[font.stem] = _chars
                    self._font_tb[font.stem] = load_truetype_font(
                        font, size=text_size)

                except:
                    print(
                        f'Error loading font: {D.colorstr(font.stem, "RED")}, Skip.')
                    continue

            self.chars_table = {
                char: i for i, char in enumerate(sorted(unique_chars, key=ord))
            }

            if self.use_random_font_weight:
                sum_chars = sum(number_font_chars.values())
                self.weighted_font = {
                    font.stem: number_font_chars[font.stem] / sum_chars
                    for font in font_bank_fs
                }

        else:
            # Using single font
            self.font = load_truetype_font(font_path, size=text_size)
            _chars = get_supported_characters(font_path)
            self.chars_table = {char: i for i, char in enumerate(_chars)}
            self.font_chars_tables[Path(font_path).stem] = _chars

    @ property
    def text_size(self):
        return self._text_size

    @ property
    def font_path(self):
        return self._font_path

    @ property
    def font_bank(self):
        return self._font_bank

    @ property
    def random_font(self):
        return self._random_font

    @ property
    def use_random_font_weight(self):
        return self._use_random_font_weight

    def __repr__(self):
        return self.dashboard

    @ staticmethod
    def colorize(value):
        def select_color(value):
            return D.COLORSTR.GREEN if value else D.COLORSTR.RED
        return D.colorstr(value, select_color(value))

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
            ["font_bank", self.font_bank, "reinit", "str",
                "Path of Font bank. Only activated when setting `random_font` to True."],
            ["random_font", self.colorize(
                self.random_font), "reinit", "bool", "Randomize font. Overwrite `font_path`."],
            ["random_text", self.colorize(
                self.random_text), "reinit", "bool", "Randomize text. Overwrite input text."],
            ["use_random_font_weight", self.colorize(
                self.use_random_font_weight), "reinit", "bool", "Use random font weight. Only activated when the `random_font` setting is set to True."],
            ["text_size", self._text_size, "reinit", "int", "Size of font."],
            ["direction", self.direction, "set",
                "str", "Text direction. (ltr | ttb)"],
            ["text_aspect_ratio", self.text_aspect_ratio, "set", "float",
                "Text aspect ratio. ex: set to 0.5 for half width."],
            ["text_color", self.text_color, "set",
                "Tuple[int, int, int]", "Color of text."],
            ["background_color", self.background_color, "set",
                "Tuple[int, int, int]", "Color of background."],
            ["output_size", self.output_size, "set",
                "Tuple[int, int]", "Fixed size of output image. If None, the output size will be determined by the input text and font size."],
            ["align_mode", self.align_mode, "set",
                "AlignMode", "Text alignment mode. (Left | Right | Center | Scatter)"],
            ["output_direction", self.output_direction, "set",
                "OutputDirection", "Output image direction. (Remain | Horizontal | Vertical)"],
            ["min_random_text_length", self.min_random_text_length, "set", "int",
                "Random minimum text length. Only activated when the `random_text` setting is set to True."],
            ["max_random_text_length", self.max_random_text_length, "set", "int",
                "Random maximum text length. Only activated when the `random_text` setting is set to True."],
            ["random_direction", self.colorize(
                self.random_direction), "set", "bool", "Randomize direction. Overwrite `direction`."],
            ["random_text_color", self.colorize(
                self.random_text_color), "set", "bool", "Randomize text color. Overwrite `text_color`."],
            ["random_background_color", self.colorize(
                self.random_background_color), "set", "bool", "Randomize background color. Overwrite `background_color`."],
            ["random_align_mode", self.colorize(
                self.random_align_mode), "set", "bool", "Randomize align mode. Overwrite `align_mode`."],
            ["enable_all_random", self.colorize(
                self.enable_all_random), "set", "bool", "Enable all random. Overwrite all random settings."],
        ]

        for row in data:
            table.add_row(row)

        # print(table)
        return table.get_string()

    def regularize_image(self, img, direction, align_mode, background_color) -> np.ndarray:
        h, w = self.output_size
        if direction == 'ltr':
            if self.text_aspect_ratio != 1.0:
                img = D.imresize(
                    img,
                    (img.shape[0], int(img.shape[1] // self.text_aspect_ratio))
                )

            img = D.imresize(img, (h, None))
            img_w = img.shape[1]
            if img_w >= w:
                img = D.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if align_mode == AlignMode.Left:
                    pad_size = (0, 0, 0, w - img_w)
                elif align_mode == AlignMode.Right:
                    pad_size = (0, 0, w - img_w, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = (0, 0, (w - img_w) // 2, (w - img_w) // 2)
                img = D.pad(img, pad_size, fill_value=background_color)
        elif direction == 'ttb':
            h, w = w, h

            if align_mode != AlignMode.Scatter and \
                    self.text_aspect_ratio != 1.0:
                img = D.imresize(
                    img,
                    (img.shape[0], int(img.shape[1] // self.text_aspect_ratio))
                )

            img = D.imresize(img, (None, w))
            img_h = img.shape[0]
            if img_h >= h:
                img = D.imresize(img, (h, w))
            else:
                # Align mode will affect the padding position
                if align_mode == AlignMode.Left:
                    pad_size = (0, h - img_h, 0, 0)
                elif align_mode == AlignMode.Right:
                    pad_size = (h - img_h, 0, 0, 0)
                else:
                    # Accepted align mode: Center, Scatter
                    pad_size = ((h - img_h) // 2, (h - img_h) // 2, 0, 0)
                img = D.pad(img, pad_size, fill_value=background_color)
        img = D.imresize(img, (h, w))
        return img

    def gen_scatter_image(self, text, font, direction, text_color, background_color) -> np.ndarray:

        def split_text(text: str):
            """ Split text into a list of characters. """
            pattern = r"[a-zA-Z0-9\p{P}\p{S}]+|."
            matches = regex.findall(pattern, text)
            matches = [m for m in matches if not regex.match(r'\p{Z}', m)]
            if len(matches) == 1:
                matches = list(text)

            # 防止圖像太小，導致所有字元黏在一起
            matches_with_space = []
            for i, m in enumerate(matches):
                matches_with_space.append(m)
                if i != len(matches) - 1:
                    matches_with_space.append(' ')

            return matches_with_space

        try:
            left, top, right, bottom = font.getbbox(text, direction=direction)
            width = max(right - left, 1)
            height = max(bottom - top, 1)
            _, offset = font.getmask2(text, direction=direction)
        except Exception as e:
            raise ValueError(
                f"Something went wrong while rendering the text: {text}. Error: {e}.\n"
                f"Auto-Logging the font information: \n\n\t{font.getname()}\n\n"
                f"DO NOT USE THIS FONT FOR RENDERING TEXTS.\n\n"
            )

        texts = split_text(text)

        if len(texts):
            imgs = [
                text2image(
                    text=t,
                    font=font,
                    direction=direction,
                    text_color=text_color,
                    background_color=background_color,
                    height=height if direction == 'ltr' else None,
                    width=width if direction == 'ttb' else None,
                    offset=offset,
                )[0] for t in texts
            ]
        else:
            img = np.zeros((height, width, 3)) + background_color
            imgs = [img.astype(np.uint8)]

        if direction == 'ltr':

            # For `self.text_aspect_ratio` is not 1.0
            if self.text_aspect_ratio != 1.0:
                imgs = [
                    D.imresize(
                        img, (img.shape[0], int(
                            img.shape[1] // self.text_aspect_ratio))
                    ) for img in imgs
                ]

            # If there is only one image, return it directly
            if len(imgs) == 1:
                return imgs[0]

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

            # For `self.text_aspect_ratio` is not 1.0
            if self.text_aspect_ratio != 1.0:
                imgs = [
                    D.imresize(
                        img,
                        (int(img.shape[0] * self.text_aspect_ratio),
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

        return img.astype(np.uint8)

    def __call__(self, text: str = None) -> np.ndarray:

        if text is None and not self.random_text:
            raise ValueError(
                "Please provide a text or set `random_text` to True.")

        if self.random_font:
            # Load a random font from the bank
            weighted_font = None
            if self.use_random_font_weight:
                weighted_font = list(self.weighted_font.values())
            candi_font = list(self._font_tb.keys())
            font_idx = np.random.choice(len(candi_font), p=weighted_font)
            font = self._font_tb[candi_font[font_idx]]
            font_name = font.path.stem
        else:
            font = self.font
            font_name = Path(self._font_path).stem

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
        align_mode = random.choice(list(AlignMode)) \
            if self.random_align_mode else self.align_mode

        # Align model setting of `SCATTER` is special case
        if align_mode == AlignMode.Scatter and self.output_size is not None:
            img = self.gen_scatter_image(
                text, font, direction, text_color, background_color)
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
            img = D.imrotate90(img, rotate_code=D.ROTATE.ROTATE_90)
        elif self.output_direction == OutputDirection.Horizontal \
                and infos['direction'] == 'ttb':
            img = D.imrotate90(img, rotate_code=D.ROTATE.ROTATE_270)

        infos.update({
            'font_name': font_name,
            'align_mode': align_mode,
            'output_direction': self.output_direction,
        })

        return img, infos


# if __name__ == '__main__':

#     from pprint import pprint

#     gen = WordCanvas(output_size=(64, 512), random_font=True,
#                      align_mode=AlignMode.Scatter, direction='ltr',
#                      text_aspect_ratio=1, random_text=True,
#                      random_text_color=True, random_background_color=True,
#                      random_align_mode=True, use_random_font_weight=True,
#                      output_direction=OutputDirection.Remain)
#     breakpoint()
#     for _ in D.Tqdm(range(100000)):
#         img, infos = gen('測試輸出')

#     img, infos = gen('測試輸出')
#     pprint(infos)
#     D.imwrite(img)
