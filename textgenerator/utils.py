from pathlib import Path
from typing import List, Union
from warnings import warn

from docsaidkit import get_curdir
from fontTools.ttLib import TTFont
from PIL import ImageFont

DIR = get_curdir(__file__)


__all__ = [
    'load_truetype_font', 'load_ttfont', 'get_supported_characters',
    'is_character_supported'
]


def load_truetype_font(
    font_path: str,
    **kwargs
) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path, **kwargs)


def load_ttfont(
    font_path: str,
    **kwargs
) -> TTFont:
    return TTFont(font_path, **kwargs)


def get_supported_characters(
    font: Union[str, Path, TTFont],
    as_strings: bool = True
) -> List[Union[str, int]]:
    """
    Retrieve all characters supported by a font.

    Args:
        font: A path to the font file or a TTFont object.
        as_strings: Return characters as strings if True, or as their Unicode integer values if False.

    Returns:
        A list of supported characters or their Unicode values.
    """
    if not isinstance(font, TTFont):
        warn(f'Make sure to pass a `TTFont` object for better performance.')
        font = TTFont(font)

    chars = set()
    for cmap in font['cmap'].tables:
        for k in cmap.cmap.keys():
            character = chr(k)
            if character.isprintable():
                if as_strings:
                    chars.add(character)
                else:
                    chars.add(k)
    chars = sorted(chars, key=ord) if as_strings else sorted(chars)

    return chars


def is_character_supported(font: TTFont, character: str, verbose: bool = False) -> bool:
    """
    Check if the specified character is supported by the font.

    Args:
        font: A TTFont object.
        character: The character to check.
        verbose: If True, print detailed information about unsupported characters.

    Returns:
        True if the character is supported, False otherwise.
    """
    character_supported = any(
        ord(character) in table.cmap for table in font['cmap'].tables
    )

    if verbose and not character_supported:
        print(
            f"Character '{character}' ({ord(character):#x}) is not supported by the font.", flush=True)

    return character_supported
