from enum import Enum
from typing import Union

import capybara as cb
import cv2
import numpy as np
import pandas as pd

from .code39table import load_39table
from .code128table import load_128table

DIR = cb.get_curdir(__file__)


class CodeType(cb.EnumCheckMixin, Enum):
    Code128_A = 0
    Code128_B = 1
    Code128_C = 2


class Code128Generator:

    def __init__(
        self,
        code_type: Union[CodeType, str, int] = CodeType.Code128_B,
        color: tuple = (0, 0, 0)
    ):
        """ Code128 barcode generator """
        table = load_128table()
        self.table = pd.DataFrame.from_dict(table)
        self.code_type = CodeType.obj_to_enum(code_type)
        self.color = color

    @property
    def start_type(self):
        return {
            CodeType.Code128_A: ('Start Code A', '_128A'),
            CodeType.Code128_B: ('Start Code B', '_128B'),
            CodeType.Code128_C: ('Start Code C', '_128C')
        }

    def _gen_code128(self, src: str):
        """ Generate Code128 barcode
        Args:
            src (str): input string

        Returns:
            output_code (str): barcode encoded in string
        """
        start, col = self.start_type[self.code_type]
        start_code, start_value = self.table.loc[
            self.table._128A == start,
            ['bar_pattern', 'Value']
        ].values.reshape(-1)
        end_code = self.table.loc[
            self.table._128A == 'Stop_pattern',
            'bar_pattern'
        ].values[0]

        code_ls, value_ls = [], []
        for char in src:
            code_ls.append(
                self.table.loc[self.table[col] == char, 'bar_pattern'].values[0])
            value_ls.append(
                self.table.loc[self.table[col] == char, 'Value'].values[0])

        info_code = ''
        for code in code_ls:
            info_code += code

        values = 0
        for idx, value in enumerate(value_ls):
            value = int(value)
            values += value * (idx+1)

        check_value = str((int(start_value) + values) % 103)
        check_code = self.table.loc[self.table.Value ==
                                    check_value, 'bar_pattern'].values[0]
        output_code = start_code + info_code + check_code + end_code

        return output_code

    def _gen_image(self, encode: str, width: int, height: int):

        def draw_line(img, x, thickness, rand_color):

            for _ in range(thickness):
                point_start = np.array([x, 0])
                point_end = np.array([x, height])
                cv2.line(img, point_start, point_end, rand_color, thickness=1)
                x += 1

        thickness = width // len(encode)
        img = np.ones((height, width, 3), dtype='uint8') * 255

        x = 0
        for Bool in encode:
            if Bool == '1':
                draw_line(img, x, thickness, self.color)
            x = x + thickness

        # Calibration
        # There is space error between self.width and barcode width within 0~144
        img = img[0:height, 0:len(encode)*thickness]
        img = cb.imresize(img, (height, width), interpolation=cb.INTER.NEAREST)

        return img

    def __call__(self, text: str, w: int, h: int):
        """Generate Code128 barcode image
        Args:
            text (str): input string
            w (int): barcode width
            h (int): barcode height

        Returns:
            img (np.ndarray): barcode image
        """
        encode = self._gen_code128(text)
        return self._gen_image(encode, w, h)


class Code39Generator:

    def __init__(
        self,
        width_rate: int = 2,
        color: tuple = (0, 0, 0)
    ):
        """ Code39 barcode generator
        Args:
            img_size: Image size you'd like to, but might be change by calibration.
            width_rate: Make barcode wide line thicker, value at least be 2.
        """

        if width_rate < 2:
            raise ValueError(
                f'width_rate should be at least 2, but got {width_rate}')

        table = load_39table()
        self.table = pd.DataFrame.from_dict(table)
        self.convert_dict = {'w': '0', 'W': '0' *
                             width_rate, 'b': '1', 'B': '1'*width_rate}
        self.color = color

    def _gen_code39(self, src: str):
        """ Generate Code39 barcode
        Args:
            src (str): input string

        Returns:
            output_code (str): barcode encoded in string
        """

        def tobar(string):
            bar_ls = [self.convert_dict[char] for char in string]
            bar_pattern = ''.join(bar_ls)
            return bar_pattern

        self.table['bar_pattern'] = self.table['pattern'].apply(
            lambda x: tobar(x))

        start_code = self.table.loc[self.table['character']
                                    == '*', 'bar_pattern'].values[0] + '0'
        end_code = start_code

        info_code = ''
        for char in src:
            info = self.table.loc[self.table['character']
                                  == char, 'bar_pattern'].values[0]
            info_code += (info + '0')

        output_code = start_code + info_code + end_code

        return output_code

    def _gen_image(self, encode: str, width: int, height: int):
        """ Draw barcode line makes code string to barcode image.
        Args:
            encode: encoded string
            color: barcode random color range
        """

        def draw_line(img, x, thickness, rand_color):

            for _ in range(thickness):
                point_start = np.array([x, 0])
                point_end = np.array([x, height])
                cv2.line(img, point_start, point_end, rand_color, thickness=1)
                x += 1

        thickness = width // len(encode)
        img = np.ones((height, width, 3), dtype='uint8') * 255

        x = 0
        for Bool in encode:
            if Bool == '1':
                draw_line(img, x, thickness, self.color)
            x = x + thickness

        # Calibration
        # There is space error between self.width and barcode width within 0~144
        img = img[0:height, 0:len(encode)*thickness]
        img = cb.imresize(img, (height, width), interpolation=cb.INTER.NEAREST)

        return img

    def __call__(self, text: str, w: int, h: int):
        """Generate Code128 barcode image
        Args:
            text (str): input string
            w (int): barcode width
            h (int): barcode height

        Returns:
            img (np.ndarray): barcode image
        """
        encode = self._gen_code39(text)
        return self._gen_image(encode, w, h)
