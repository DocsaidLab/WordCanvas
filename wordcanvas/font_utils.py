import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Union

from capybara import get_curdir
from fontTools.ttLib import TTFont

DIR = get_curdir(__file__)

__all__ = [
    'load_ttfont',
    'remove_control_characters',
    'extract_font_info',
    'get_supported_characters',
    'filter_characters_by_range',
    'is_character_supported',
    'CHARACTER_RANGES',
    'TTFont',
]


CHARACTER_RANGES = {

    # 基礎字符集
    "English": [(0x0020, 0x007E)],                     # 英文與基礎 ASCII
    "Latin Extended-A": [(0x0100, 0x017F)],            # 擴展拉丁字符 A
    "Latin Extended-B": [(0x0180, 0x024F)],            # 擴展拉丁字符 B
    "Latin Extended Additional": [(0x1E00, 0x1EFF)],   # 進一步擴展拉丁字符

    # 中日韓字符集
    "CJK Unified Ideographs": [(0x4E00, 0x9FFF)],      # 基本漢字
    "CJK Extension A": [(0x3400, 0x4DBF)],             # 擴展 A
    "CJK Extension B-F": [(0x20000, 0x2FFFF)],         # 擴展 B-F
    "Hiragana": [(0x3040, 0x309F)],                    # 平假名
    "Katakana": [(0x30A0, 0x30FF)],                    # 片假名
    "Katakana Phonetic Extensions": [(0x31F0, 0x31FF)],  # 片假名擴展
    "Hangul Syllables": [(0xAC00, 0xD7AF)],            # 韓文音節
    "Hangul Jamo": [(0x1100, 0x11FF)],                 # 韓文 Jamo
    "CJK Symbols and Punctuation": [(0x3000, 0x303F)],  # CJK 標點

    # 西里爾字符集
    "Cyrillic": [(0x0400, 0x04FF)],                    # 基本西里爾字符
    "Cyrillic Supplement": [(0x0500, 0x052F)],         # 西里爾字符補充
    "Cyrillic Extended-A": [(0x2DE0, 0x2DFF)],         # 擴展 A
    "Cyrillic Extended-B": [(0xA640, 0xA69F)],         # 擴展 B

    # 希臘字符集
    "Greek and Coptic": [(0x0370, 0x03FF)],            # 希臘字符和科普特字符

    # 阿拉伯字符集
    "Arabic": [(0x0600, 0x06FF)],                      # 基本阿拉伯字符
    "Arabic Supplement": [(0x0750, 0x077F)],           # 阿拉伯字符補充
    "Arabic Extended-A": [(0x08A0, 0x08FF)],           # 擴展 A

    # 印度次大陸字符集
    "Devanagari": [(0x0900, 0x097F)],                  # 天城文
    "Bengali": [(0x0980, 0x09FF)],                     # 孟加拉文
    "Gurmukhi": [(0x0A00, 0x0A7F)],                    # 古木基文
    "Gujarati": [(0x0A80, 0x0AFF)],                    # 古吉拉特文
    "Oriya": [(0x0B00, 0x0B7F)],                       # 奧里亞文
    "Tamil": [(0x0B80, 0x0BFF)],                       # 泰米爾文
    "Telugu": [(0x0C00, 0x0C7F)],                      # 泰盧固文
    "Kannada": [(0x0C80, 0x0CFF)],                     # 卡納達文
    "Malayalam": [(0x0D00, 0x0D7F)],                   # 馬拉雅拉姆文
    "Sinhala": [(0x0D80, 0x0DFF)],                     # 僧伽羅文

    # 東南亞字符集
    "Thai": [(0x0E00, 0x0E7F)],                        # 泰文
    "Lao": [(0x0E80, 0x0EFF)],                         # 寮文
    "Myanmar": [(0x1000, 0x109F)],                     # 緬甸文
    "Khmer": [(0x1780, 0x17FF)],                       # 高棉文

    # 非洲字符集
    "Ethiopic": [(0x1200, 0x137F)],                    # 埃塞俄比亞文

    # 地中海字符集
    "Hebrew": [(0x0590, 0x05FF)],                      # 希伯來文

    # 雜項符號與表情符號
    "Emoji and Symbols": [(0x1F300, 0x1F5FF), (0x1F600, 0x1F64F)],  # 表情符號
    "Mathematical Symbols": [(0x2200, 0x22FF)],         # 數學符號
    "Currency Symbols": [(0x20A0, 0x20CF)],             # 貨幣符號

    # 標點和特殊字符
    "General Punctuation": [(0x2000, 0x206F)],          # 常規標點
    "Supplemental Punctuation": [(0x2E00, 0x2E7F)],     # 補充標點
    "Fullwidth and Halfwidth": [(0xFF00, 0xFFEF)]       # 全形和半形字符
}


def load_ttfont(font_path: Union[str, Path], **kwargs) -> TTFont:
    """Loads a TrueType or OpenType font using fontTools' TTFont.

    This function loads a font from a file or directly returns the
    provided `TTFont` object if it is already loaded.

    Args:
        font_path (Union[str, Path]):
            The path to the font file. It can be:
            - A string representing the file path.
            - A `Path` object pointing to the font file.
            - An already loaded `TTFont` object, which will be returned as is.
        **kwargs: Additional keyword arguments passed to the `TTFont` constructor.

    Returns:
        TTFont: The loaded `TTFont` object representing the font.

    Raises:
        FileNotFoundError: If the specified font file does not exist.
        TTLibError: If the font cannot be loaded due to invalid format or corruption.
    """
    if isinstance(font_path, Path):
        font_path = str(font_path)  # Convert Path to string

    if isinstance(font_path, TTFont):
        return font_path  # If already a TTFont object, return as is

    return TTFont(font_path, **kwargs)  # Load the font from file


def is_in_ranges(char: str, rangeqs: List[tuple]) -> bool:
    """Checks if a character's Unicode code point falls within any specified ranges.

    This function determines whether the Unicode code point of a given character
    is within one or more specified ranges.

    Args:
        char (str):
            A single character to check.
        ranges (List[tuple]):
            A list of tuples, where each tuple represents a range in the form
            `(start, end)`. Both `start` and `end` are integers representing
            Unicode code points, and the range is inclusive.

    Returns:
        bool:
            `True` if the character's Unicode code point is within any of the
            specified ranges, `False` otherwise.

    Raises:
        TypeError: If `char` is not a single character.
    """
    char_code = ord(char)
    return any(start <= char_code <= end for start, end in rangeqs)


def filter_characters_by_range(
    font_path: Union[str, Path],
    ranges: Dict[str, List[tuple]] = CHARACTER_RANGES,
    do_filter: bool = True
) -> Dict[str, List[str]]:
    """Filters the characters in a font based on specified Unicode ranges.

    This function extracts the characters supported by a font and optionally
    filters them into categories based on predefined Unicode ranges.

    Args:
        font_path (Union[str, Path]):
            The file path to the font. It can be a string or a `Path` object.
        ranges (Dict[str, List[tuple]], optional):
            A dictionary where keys represent category names and values are
            lists of tuples defining inclusive Unicode ranges for that category.
            Defaults to `CHARACTER_RANGES`.
        do_filter (bool, optional):
            If `True`, filters characters into categories based on `ranges`.
            If `False`, returns all supported characters in the font without filtering.
            Defaults to `True`.

    Returns:
        Dict[str, List[str]]:
            A dictionary containing:
            - If `do_filter` is `True`: Keys are category names, and values
              are lists of characters falling within the specified ranges.
            - If `do_filter` is `False`: A single key `"All Characters"`
              mapping to a list of all supported characters in the font.

    Raises:
        FileNotFoundError: If the specified font file does not exist.
        TTLibError: If the font cannot be loaded due to invalid format or corruption.
    """
    font = load_ttfont(font_path)
    cmap = font.getBestCmap()
    supported_chars = {chr(char_code) for char_code in cmap.keys()}

    if not do_filter:
        return {"All Characters": list(supported_chars)}

    result = {}
    for category, category_ranges in ranges.items():
        result[category] = [
            char for char in supported_chars if is_in_ranges(char, category_ranges)
        ]

    return result


def remove_control_characters(text: str, normalize: bool = True) -> str:
    """Removes control characters and optional Unicode normalization from a string.

    This function removes control characters, invisible formatting characters,
    and directional formatting characters from the input text. Optionally,
    it normalizes the text to NFC or NFKC form for consistent representation.

    Args:
        text (str): The input string from which control characters will be removed.
        normalize (bool, optional):
            If `True`, normalizes the sanitized text to Unicode NFKC form.
            Defaults to `True`.

    Returns:
        str: The sanitized string with control characters removed.

    Notes:
        - Removes the following character ranges:
          - Basic control characters: `[\x00-\x1F\x7F-\x9F]`.
          - Unicode formatting characters: `[\u200B-\u200F\u2028-\u202F\u2060-\u206F]`.
          - Directional formatting characters: `[\u202A-\u202E]`.
        - Normalization uses `unicodedata.normalize` with `NFKC` form,
          which applies compatibility decomposition followed by canonical
          composition for consistent representation.
    """
    # Remove basic control characters (C0 and C1 control codes)
    sanitized = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

    # Remove specific Unicode control and invisible formatting characters
    sanitized = re.sub(
        r'[\u200B-\u200F\u2028-\u202F\u2060-\u206F]', '', sanitized)

    # Remove directional formatting characters (e.g., left-to-right override)
    sanitized = re.sub(r'[\u202A-\u202E]', '', sanitized)

    # Optionally normalize the text to NFC or NFKC form
    if normalize:
        sanitized = unicodedata.normalize('NFKC', sanitized)

    return sanitized


def extract_font_info(
    font_path: Union[str, Path],
    normalize: bool = True
) -> dict:
    """Extracts detailed metadata and metrics from a font file.

    This function parses a font file to extract metadata, including name tables,
    character mappings, layout metrics, and more. It provides a comprehensive
    dictionary summarizing the font's properties.

    Args:
        font_path (Union[str, Path]):
            The path to the font file. It can be a string or a `Path` object.
            Alternatively, an already loaded `TTFont` object can be passed.
        normalize (bool, optional):
            If `True`, normalizes all extracted text data using Unicode NFKC
            normalization and removes control characters. Defaults to `True`.

    Returns:
        dict: A dictionary containing detailed font information with the following keys:
            - `fileName`: The name or path of the font file.
            - `tables`: A list of available font tables.
            - `nameTable`: A dictionary of raw name table entries.
            - `nameTableReadable`: A dictionary of readable name table fields (e.g., `fontFamily`, `fullName`).
            - `cmapTable`: A dictionary of character-to-glyph mappings grouped by platform and encoding.
            - `cmapTableIndex`: A list of keys identifying the `cmapTable` groups.
            - `headTable`: Metadata from the `head` table (e.g., units per EM, bounding box).
            - `hheaTable`: Horizontal metrics from the `hhea` table (e.g., ascent, descent, line gap).
            - `OS2Table`: Metrics from the `OS/2` table (e.g., weight class, width class, embedding type).
            - `postTable`: PostScript-related metrics (e.g., italic angle, fixed pitch).
            - `layoutMetrics`: A consolidated dictionary of layout metrics.
            - `summary`: A summary of key font properties (e.g., `fontFamily`, version, weight class).

    Raises:
        FileNotFoundError: If the font file does not exist.
        TTLibError: If the font file is invalid or cannot be loaded.

    Notes:
        - The `CHARACTER_RANGES` constant can be used to filter characters based
          on Unicode ranges, if necessary.
        - Text normalization and control character removal ensure compatibility
          with different text processing systems.
    """
    font_info = {}

    if isinstance(font_path, (str, Path)):
        font_path = str(font_path)

    if isinstance(font_path, TTFont):
        font = font_path
        font_info['fileName'] = "Unknown"
    else:
        font = TTFont(font_path)
        font_info['fileName'] = font_path

    # File name and available tables
    font_info['tables'] = list(font.keys())

    # Parse name table
    name_table = {}
    for record in font['name'].names:
        try:
            raw_string = record.string.decode('utf-16-be').strip()
            clean_string = remove_control_characters(raw_string, normalize)
            name_table[record.nameID] = clean_string
        except UnicodeDecodeError:
            name_table[record.nameID] = remove_control_characters(
                record.string.decode(errors='ignore'), normalize)
    font_info['nameTable'] = name_table

    # Readable name table for common nameIDs
    name_table_readable = {
        'copyright': name_table.get(0, ''),
        'fontFamily': name_table.get(1, ''),
        'fontSubfamily': name_table.get(2, ''),
        'uniqueID': name_table.get(3, ''),
        'fullName': name_table.get(4, ''),
        'version': name_table.get(5, ''),
        'postScriptName': name_table.get(6, ''),
    }
    font_info['nameTableReadable'] = {
        k: remove_control_characters(v, normalize)
        for k, v in name_table_readable.items()
    }

    # Parse cmap table
    cmap_table = {}
    cmap_table_index = []

    for cmap in font['cmap'].tables:
        platform_name = {
            0: 'Unicode',
            1: 'Macintosh',
            3: 'Windows'
        }.get(cmap.platformID, f"Platform {cmap.platformID}")

        encoding_name = {
            (0, 0): 'Unicode 1.0',
            (0, 3): 'Unicode 2.0+',
            (0, 4): 'Unicode 2.0+ with BMP',
            (1, 0): 'Mac Roman',
            (3, 1): 'Windows Unicode BMP',
            (3, 10): 'Windows Unicode Full'
        }.get((cmap.platformID, cmap.platEncID), f"Encoding {cmap.platEncID}")

        cmap_entries = {}
        for codepoint, glyph_name in cmap.cmap.items():
            char = chr(codepoint)
            cmap_entries[remove_control_characters(char, normalize)] = \
                remove_control_characters(glyph_name, normalize)

        key = f"{platform_name}, {encoding_name}"
        cmap_table[key] = cmap_entries
        cmap_table_index.append(key)

    font_info['cmapTable'] = cmap_table
    font_info['cmapTableIndex'] = cmap_table_index

    # Parse head table
    head = font['head']
    head_table = {
        'unitsPerEm': head.unitsPerEm,
        'xMin': head.xMin,
        'yMin': head.yMin,
        'xMax': head.xMax,
        'yMax': head.yMax,
    }
    font_info['headTable'] = head_table

    # Parse hhea table
    hhea = font['hhea']
    hhea_table = {
        'ascent': hhea.ascent,
        'descent': hhea.descent,
        'lineGap': hhea.lineGap,
    }
    font_info['hheaTable'] = hhea_table

    # Parse OS/2 table
    os2 = font['OS/2']
    os2_table = {
        'usWeightClass': os2.usWeightClass,
        'usWidthClass': os2.usWidthClass,
        'fsType': os2.fsType,
    }
    font_info['OS2Table'] = os2_table

    # Parse post table
    post = font['post']
    post_table = {
        'isFixedPitch': post.isFixedPitch,
        'italicAngle': post.italicAngle,
    }
    font_info['postTable'] = post_table

    # Combine layout-related metrics
    font_info['layoutMetrics'] = {
        'unitsPerEm': head_table['unitsPerEm'],
        'boundingBox': {
            'xMin': head_table['xMin'],
            'yMin': head_table['yMin'],
            'xMax': head_table['xMax'],
            'yMax': head_table['yMax']
        },
        'ascent': hhea_table['ascent'],
        'descent': hhea_table['descent'],
        'lineGap': hhea_table['lineGap']
    }

    # Font summary
    font_info['summary'] = {
        'fontFamily': name_table_readable['fontFamily'],
        'fontSubfamily': name_table_readable['fontSubfamily'],
        'version': name_table_readable['version'],
        'weightClass': os2.usWeightClass,
        'isItalic': post_table['italicAngle'] != 0
    }

    return font_info


def get_supported_characters(
    font_path: Union[str, Path],
    ranges: Dict[str, List[tuple]] = CHARACTER_RANGES,
    do_filter: bool = True
) -> List[str]:
    """Retrieves all characters supported by a font, sorted by Unicode code points.

    This function extracts all characters supported by the specified font,
    optionally filtered by predefined ranges, and returns them sorted in
    ascending order based on their Unicode code points.

    Args:
        font_path (Union[str, Path]):
            The file path to the font. It can be a string or a `Path` object.
        ranges (Dict[str, List[tuple]], optional):
            A dictionary where keys represent category names and values are
            lists of tuples defining inclusive Unicode ranges for that category.
            Defaults to `CHARACTER_RANGES`.
        do_filter (bool, optional):
            If `True`, filters characters into categories based on `ranges`.
            If `False`, returns all supported characters in the font without filtering.
            Defaults to `True`.

    Returns:
        List[str]:
            A sorted list of characters supported by the font.

    Raises:
        FileNotFoundError: If the font file does not exist.
        TTLibError: If the font file is invalid or cannot be loaded.
    """
    chars_dict = []

    # Extract supported characters from the font using specified ranges
    for chars in filter_characters_by_range(font_path, ranges, do_filter).values():
        chars_dict.extend(chars)

    chars_dict = ''.join(chars_dict)
    chars_dict = remove_control_characters(chars_dict, normalize=True)
    chars_dict = list(set(chars_dict))
    chars_dict = sorted(chars_dict, key=lambda x: ord(x))

    return chars_dict


def is_character_supported(
    font: TTFont,
    character: str,
    verbose: bool = True
) -> bool:
    """Checks if a specific character is supported by a given font.

    This function determines whether a character is supported by the font's
    character-to-glyph mapping table (cmap). Optionally, it can print a message
    when the character is not supported.

    Args:
        font (TTFont):
            An instance of `TTFont` representing the font to check.
        character (str):
            The character to check for support. Must be a single character.
        verbose (bool, optional):
            If `True`, prints a message when the character is not supported.
            Defaults to `True`.

    Returns:
        bool:
            `True` if the character is supported by the font, `False` otherwise.

    Raises:
        TypeError: If `character` is not a single character string.

    Example:
        ```python
        # Load a font
        font = TTFont("example.ttf")

        # Check if a character is supported
        is_supported = is_character_supported(font, "A")
        print(is_supported)  # Output: True or False
        ```

    Notes:
        - The function uses the font's best available `cmap` table for character
          lookup.
        - If `verbose` is `True`, it prints an informative message when the
          character is unsupported.
    """
    cmap = font.getBestCmap()
    codepoint = ord(character)

    character_supported = codepoint in cmap

    if verbose and not character_supported:
        print(
            f"Character '{character}' ({ord(character):#x}) is not supported by the font.")

    return character_supported
