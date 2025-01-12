from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from wordcanvas.font_utils import (CHARACTER_RANGES, extract_font_info,
                                   filter_characters_by_range,
                                   get_supported_characters,
                                   is_character_supported, load_ttfont,
                                   remove_control_characters)

FONT_ROOT = Path(__file__).parent.parent / "wordcanvas" / "fonts"


def test_load_ttfont():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    font = load_ttfont(font_path)
    assert isinstance(font, TTFont)


def test_load_ttfont_invalid_path():
    with pytest.raises(FileNotFoundError):
        load_ttfont("/invalid/path/to/font.ttf")


def test_filter_characters_by_range():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    result = filter_characters_by_range(font_path, CHARACTER_RANGES)
    assert "English" in result
    assert isinstance(result["English"], list)
    assert all(isinstance(char, str) for char in result["English"])


def test_filter_characters_by_range_no_filter():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    result = filter_characters_by_range(font_path, do_filter=False)
    assert "All Characters" in result
    assert isinstance(result["All Characters"], list)


def test_get_supported_characters():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    characters = get_supported_characters(font_path)
    assert isinstance(characters, list)
    assert all(isinstance(char, str) for char in characters)


def test_is_character_supported():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    font = load_ttfont(font_path)
    assert is_character_supported(font, "A") is True
    assert is_character_supported(font, "\u2603") in [
        True, False]  # Depends on font support


def test_remove_control_characters():
    text = "Hello\u202E World!\x07"
    sanitized = remove_control_characters(text)
    assert sanitized == "Hello World!"


def test_extract_font_info():
    font_path = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not font_path.is_file():
        pytest.skip("Font file not found.")

    info = extract_font_info(font_path)
    assert isinstance(info, dict)
    assert "fileName" in info
    assert "tables" in info
    assert "nameTable" in info
    assert "layoutMetrics" in info


def test_extract_font_info_invalid_path():
    with pytest.raises(FileNotFoundError):
        extract_font_info("/invalid/path/to/font.ttf")


if __name__ == "__main__":
    pytest.main()
