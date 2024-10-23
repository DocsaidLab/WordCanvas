from pathlib import Path
from typing import List, Union
from warnings import warn

from docsaidkit import dump_json, get_curdir, load_json
from fontTools.pens.recordingPen import RecordingPen
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
    as_strings: bool = True,
    check_glyph_empty: bool = True,
    verbose: bool = False,
    use_cache: bool = False
) -> List[Union[str, int]]:
    """
    Retrieve all characters supported by a font.

    Args:
        font: A path to the font file or a TTFont object.
        as_strings: Return characters as strings if True, or as their Unicode integer values if False.
        check_glyph_empty: Whether to check if the glyph is empty.
        verbose: If True, print detailed information.

    Returns:
        A list of supported characters or their Unicode values.
    """
    name = None
    if isinstance(font, (str, Path)):
        name = Path(font).stem

    if not isinstance(font, TTFont):
        if verbose:
            warn(f'Make sure to pass a `TTFont` object for better performance.')
        font = TTFont(font)

        if name is None:
            try:
                name = font['name'].names[0].string.decode('utf-8')
            except Exception:
                name = 'empty'

    if use_cache and (fp := DIR / 'cache' / f'{name}_cache.json').exists():
        return load_json(fp)

    chars = []
    cmap = font.getBestCmap()
    for codepoint in cmap.keys():
        glyph_name = cmap[codepoint]

        glyph_is_empty = False

        if 'CFF ' in font:
            # For CFF-based OpenType fonts
            cff = font['CFF '].cff
            top_dict = cff.topDictIndex[0]
            charstrings = top_dict.CharStrings

            if glyph_name in charstrings:
                glyph = charstrings[glyph_name]

                if check_glyph_empty:
                    # Use RecordingPen to check if the glyph has any drawing commands
                    pen = RecordingPen()
                    try:
                        glyph.draw(pen)
                        if len(pen.value) == 0:
                            glyph_is_empty = True
                            if verbose:
                                print(
                                    f'Character {chr(codepoint)} (ord= {codepoint}) has an empty glyph in CFF table.')
                    except Exception as e:
                        glyph_is_empty = True
                        if verbose:
                            print(
                                f'Error drawing glyph for character {chr(codepoint)}: {e}')
            else:
                glyph_is_empty = True
                if verbose:
                    print(
                        f'Glyph name {glyph_name} not found in CFF CharStrings.')

        elif 'glyf' in font:
            # For TrueType fonts
            glyph = font['glyf'][glyph_name]
            if check_glyph_empty:
                if (glyph.numberOfContours == 0 and not glyph.isComposite()):
                    glyph_is_empty = True
                    if verbose:
                        print(
                            f'Character {chr(codepoint)} (ord= {codepoint}) has an empty glyph in glyf table.')
        else:
            raise ValueError(
                'Unsupported font format: The font does not contain glyf or CFF tables.')

        if not glyph_is_empty:
            chars.append(chr(codepoint))

    # if and only if the space character is not in the list, add it
    if ' ' not in chars:
        chars.append(' ')

    chars = sorted(chars, key=ord)
    if not as_strings:
        chars = [ord(char) for char in chars]

    if use_cache:
        if not (fp := DIR / 'cache').is_dir():
            fp.mkdir(parents=True)
        dump_json(chars, DIR / 'cache' / f'{name}_cache.json')

    return chars


def is_character_supported(
    font: TTFont,
    character: str,
    verbose: bool = True
) -> bool:
    """
    Check if a character is supported by a font.

    Args:
        font: A TTFont object.
        character: A character to check.
        verbose: Whether to print warnings.

    Returns:
        A boolean indicating whether the character is supported.
    """
    cmap = font.getBestCmap()
    codepoint = ord(character)

    character_supported = codepoint in cmap
    if verbose and not character_supported:
        print(
            f"Character '{character}' ({ord(character):#x}) is not supported by the font.")
    return character_supported
