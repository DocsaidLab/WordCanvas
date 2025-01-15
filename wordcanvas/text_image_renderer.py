import math
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

__all__ = ["load_truetype_font", "text2image"]


def load_truetype_font(
    font_source: Union[str, Path, ImageFont.FreeTypeFont],
    size: Optional[int] = None,
    return_infos: bool = False,
    **kwargs
) -> Union[ImageFont.FreeTypeFont, Tuple[ImageFont.FreeTypeFont, dict]]:
    """Loads a TrueType font and optionally returns font metadata.

    This function loads a TrueType font from a file path, a Path object,
    or an already loaded `ImageFont.FreeTypeFont` object. It can also
    return metadata about the font, such as its path, size, and name.

    Args:
        font_source (Union[str, Path, ImageFont.FreeTypeFont]):
            The font source, which can be:
            - A string representing the file path to the font.
            - A `Path` object pointing to the font file.
            - An instance of `ImageFont.FreeTypeFont` (already loaded font).
        size (Optional[int], optional):
            The desired size of the font if loading from a file.
            Defaults to `None`.
        return_infos (bool, optional):
            Whether to return font metadata along with the loaded font.
            Defaults to `False`.
        **kwargs:
            Additional keyword arguments to pass to `ImageFont.truetype`.

    Returns:
        Union[ImageFont.FreeTypeFont, Tuple[ImageFont.FreeTypeFont, dict]]:
            If `return_infos` is `False`, returns the loaded
            `ImageFont.FreeTypeFont` object.
            If `return_infos` is `True`, returns a tuple containing:
            - `ImageFont.FreeTypeFont`: The loaded font object.
            - `dict`: Metadata about the font with the keys:
                - `font_path`: The file path or source of the font.
                - `font_size`: The size of the font.
                - `font_name`: The name of the font.

    Raises:
        IOError: If the font file cannot be loaded.

    Example:
        ```python
        font, info = load_truetype_font("arial.ttf", size=24, return_infos=True)
        print(info)
        ```
    """
    if isinstance(font_source, ImageFont.FreeTypeFont):
        loaded_font = font_source
        font_path = getattr(loaded_font, "path", None)
        font_size = getattr(loaded_font, "size", None)
    else:
        if isinstance(font_source, Path):
            font_source = str(font_source)
        loaded_font = ImageFont.truetype(font_source, size=size, **kwargs)
        font_path = font_source
        font_size = size

    font_name_tuple = loaded_font.getname() \
        if hasattr(loaded_font, "getname") else None
    font_name = font_name_tuple[0] if font_name_tuple else "unknown_font"

    font_info = {
        "font_path": font_path,
        "font_size": font_size,
        "font_name": font_name,
    }

    if return_infos:
        return loaded_font, font_info

    return loaded_font


def _clamp_color(
    color: Union[Tuple[int, int, int], List[int]]
) -> Tuple[int, int, int]:
    """Clamps RGB color values to the valid range [0, 255].

    This function ensures that each component of an RGB color is within
    the valid range of 0 to 255. Any value less than 0 is set to 0,
    and any value greater than 255 is set to 255.

    Args:
        color (Union[Tuple[int, int, int], List[int]]):
            The input RGB color, represented as a tuple or list of three
            integer values.

    Returns:
        Tuple[int, int, int]:
            The clamped RGB color, represented as a tuple of three integer
            values, each in the range [0, 255].

    Example:
        ```python
        clamped_color = _clamp_color((-10, 128, 300))
        print(clamped_color)  # Output: (0, 128, 255)
        ```
    """
    return tuple(min(255, max(0, int(c))) for c in color)


def text2image(
    text: str,
    font: Union[str, Path, ImageFont.FreeTypeFont],
    size: int = 32,
    text_color: Tuple[int, int, int] = (255, 255, 255),
    background_color: Tuple[int, int, int] = (0, 0, 0),
    direction: str = 'ltr',
    offset: Optional[Tuple[int, int]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    spacing: int = 4,
    align: str = 'left',
    stroke_width: int = 0,
    stroke_fill: Optional[Tuple[int, int, int]] = (0, 0, 0),
    return_infos: bool = False,
    **kwargs
) -> Tuple[np.ndarray, dict]:
    """Renders text as an image and returns the result as a NumPy array.

    This function creates an image with the specified text using a TrueType
    font. It supports customization of text color, background color,
    alignment, direction, and stroke. Metadata about the rendering is
    also returned.

    Args:
        text (str): The text to render.
        font (Union[str, Path, ImageFont.FreeTypeFont]):
            The font source. It can be:
            - A string representing the file path to the font.
            - A `Path` object pointing to the font file.
            - An instance of `ImageFont.FreeTypeFont` (already loaded font).
        size (int, optional): The desired font size. Defaults to `32`.
        text_color (Tuple[int, int, int], optional):
            The RGB color of the text. Defaults to `(255, 255, 255)`.
        background_color (Tuple[int, int, int], optional):
            The RGB background color of the image. Defaults to `(0, 0, 0)`.
        direction (str, optional):
            The direction of the text. Must be `'ltr'`, `'rtl'`, or `'ttb'`.
            Defaults to `'ltr'`.
        offset (Optional[Tuple[int, int]], optional):
            The offset of the text in the image. If `None`, it is calculated
            automatically. Defaults to `None`.
        width (Optional[int], optional):
            The width of the image. If `None`, it is calculated automatically.
            Defaults to `None`.
        height (Optional[int], optional):
            The height of the image. If `None`, it is calculated automatically.
            Defaults to `None`.
        spacing (int, optional):
            The spacing between lines of text. Defaults to `4`.
        align (str, optional):
            The alignment of the text. Must be `'left'`, `'center'`, or
            `'right'`. Defaults to `'left'`.
        stroke_width (int, optional):
            The width of the text stroke. Defaults to `0`.
        stroke_fill (Optional[Tuple[int, int, int]], optional):
            The RGB color of the text stroke. Defaults to `(0, 0, 0)`.
        return_infos (bool, optional):
            Whether to return metadata about the rendered text. Defaults to `False`.
        **kwargs: Additional arguments to customize text rendering.

    Returns:
        Tuple[np.ndarray, dict]:
            A tuple containing:
            - `np.ndarray`: The rendered image as a NumPy array.
            - `dict`: Metadata about the rendered image, including:
                - `text`: The rendered text.
                - `bbox(xyxy)`: The bounding box of the text `(left, top, right, bottom)`.
                - `bbox(wh)`: The width and height of the bounding box.
                - `offset`: The text offset in the image.
                - `direction`: The text direction.
                - `background_color`: The background color.
                - `text_color`: The text color.
                - `spacing`: The line spacing.
                - `align`: The text alignment.
                - `stroke_width`: The stroke width.
                - `stroke_fill`: The stroke color.
                - `font_path`: The font file path.
                - `font_size_actual`: The actual font size.
                - `font_name`: The name of the font.

    Raises:
        ValueError: If `direction` is invalid or the font cannot be loaded.

    Example:
        ```python
        img, info = text2image(
            text="Hello, world!",
            font="arial.ttf",
            size=48,
            text_color=(255, 0, 0),
            background_color=(0, 0, 0)
        )
        print(info)
        ```
    """

    if direction not in ('ltr', 'rtl', 'ttb'):
        raise ValueError(
            f"Invalid direction '{direction}'. Must be 'ltr', 'rtl', or 'ttb'.")

    if isinstance(font, tuple) and isinstance(font[0], ImageFont.FreeTypeFont):
        loaded_font, font_meta = font
    elif isinstance(font, (str, Path, ImageFont.FreeTypeFont)):
        loaded_font, font_meta = load_truetype_font(
            font, size=size, return_infos=True)
    else:
        raise ValueError(
            "Invalid font source. Must be a file path, a Path object, or an ImageFont.FreeTypeFont object."
        )

    tmp_img = Image.new("RGB", (1, 1), color=(0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp_img)
    try:
        left, top, right, bottom = tmp_draw.textbbox(
            (0, 0),
            text,
            font=loaded_font,
            spacing=spacing,
            align=align,
            direction=direction,
            stroke_width=stroke_width,
            **kwargs
        )
        _offset = (-left, -top)
    except Exception as e:
        raise ValueError(
            f"Error rendering text: '{text}'. Reason: {e}\n"
            f"Font info: {loaded_font.getname()}\n"
            f"Do NOT use this font for rendering.\n"
        )

    text_width = max(int(math.ceil(right - left)), 1)
    text_height = max(int(math.ceil(bottom - top)), 1)

    if width is not None:
        text_width = max(int(math.ceil(width)), 1)
    else:
        text_width = max(int(math.ceil(right - left)), 1)

    if height is not None:
        text_height = max(int(math.ceil(height)), 1)
    else:
        max(int(math.ceil(bottom - top)), 1)

    offset = offset if offset is not None else _offset
    text_color = _clamp_color(text_color)
    background_color = _clamp_color(background_color)
    stroke_fill = _clamp_color(stroke_fill)

    img = Image.new(
        "RGB",
        (text_width, text_height),
        color=background_color
    )

    drawer = ImageDraw.Draw(img)
    drawer.text(
        xy=offset,
        text=text,
        font=loaded_font,
        fill=text_color,
        spacing=spacing,
        align=align,
        direction=direction,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
        **kwargs
    )

    img_arr = np.array(img)

    if return_infos:
        infos = {
            "text": text,
            "bbox(xyxy)": (left, top, right, bottom),
            "bbox(wh)": (text_width, text_height),
            "offset": offset,
            "direction": direction,
            "background_color": background_color,
            "text_color": text_color,
            "spacing": spacing,
            "align": align,
            "stroke_width": stroke_width,
            "stroke_fill": stroke_fill,
            "font_path": font_meta.get("font_path"),
            "font_size_actual": font_meta.get("font_size"),
            "font_name": font_meta.get("font_name"),
        }

        return img_arr, infos

    return img_arr


# if __name__ == "__main__":
#     from pprint import pprint

#     import capybara as cb

#     img, infos = text2image(
#         '測試輸出1234ABC',
#         font='/home/shayne/workspace/WordCanvas/wordcanvas/fonts/TW-Sung-98_1.ttf',
#         direction='ltr',
#         size=60,
#         background_color=(0, 0, 255),
#         text_color=(255, 0, 0),
#         align='center',
#         stroke_width=1,
#         spacing=10,
#         stroke_fill=(0, 255, 0),
#         return_infos=True
#     )
#     pprint(infos)
#     cb.imwrite(img)
