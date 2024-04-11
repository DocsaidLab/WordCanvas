from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def text2image(
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int] = (255, 255, 255),
    background_color: Tuple[int, int, int] = (0, 0, 0),
    direction: str = 'ltr',
    **kwargs
) -> np.ndarray:
    """
    Generate an image from the input text using the specified font.

    Args:
        text (str): The text to be rendered.
        font (ImageFont.FreeTypeFont): The font to be used for rendering the text.
        text_color (Tuple[int, int, int], optional):
            The color of the text in RGB format.
            Default is (255, 255, 255).
        background_color (Tuple[int, int, int], optional):
            The color of the background in RGB format.
            Default is (0, 0, 0).
        direction (str, optional):
            The direction of the text. Can be 'ltr' (left-to-right) or 'rtl' (right-to-left).
            Default is 'ltr'.
        **kwargs: Additional keyword arguments.

    Returns:
        np.ndarray: A NumPy array representing the generated image.
    """

    left, top, right, bottom = font.getbbox(text, direction=direction)
    _, offset = font.getmask2(text, direction=direction)
    text_width = right - left
    text_height = bottom - top

    img = Image.new(
        mode='RGB',
        size=(text_width, text_height),
        color=tuple(background_color)
    )

    d = ImageDraw.Draw(img)

    d.text(
        xy=(-offset[0], -offset[1]),
        text=text,
        font=font,
        direction=direction,
        fill=tuple(text_color),
        **kwargs
    )

    infos = {
        'text': text,
        'bbox': (left, top, right, bottom),
        'wh': (text_width, text_height),
        'offset': offset,
        'direction': direction,
        'background_color': tuple(background_color),
        'text_color': tuple(text_color),
    }

    return np.array(img), infos
