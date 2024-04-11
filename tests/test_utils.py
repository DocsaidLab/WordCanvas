from pathlib import Path

import pytest
from docsaidkit import get_curdir
from fontTools.ttLib import TTFont
from PIL import ImageFont
from textgenerator.utils import *
from textgenerator.utils import (get_supported_characters,
                                 is_character_supported, load_truetype_font,
                                 load_ttfont)

DIR = get_curdir(__file__)

# Path to the test font
TEST_FONT_PATH = DIR.parent / "textgenerator" / "fonts" / "OcrB-Regular.ttf"


@pytest.fixture
def ttfont():
    """Fixture to load a TTFont object for use in tests."""
    return load_ttfont(TEST_FONT_PATH)


@pytest.fixture
def truetype_font():
    """Fixture to load a PIL ImageFont object for use in tests."""
    return load_truetype_font(TEST_FONT_PATH)


def test_load_truetype_font(truetype_font):
    assert isinstance(
        truetype_font, ImageFont.FreeTypeFont), "Should return a PIL FreeTypeFont object"


def test_load_ttfont(ttfont):
    assert isinstance(ttfont, TTFont), "Should return a TTFont object"


def test_get_supported_characters(ttfont):

    # A character known to be supported by the test font
    KNOWN_CHARACTER = 'A'  # Adjust this based on your test font

    # A character known not to be supported by the test font
    UNKNOWN_CHARACTER = '試'  # A non-character in Unicode, unlikely to be supported

    for status in [True, False]:

        if not status:
            KNOWN_CHARACTER = ord(KNOWN_CHARACTER)
            UNKNOWN_CHARACTER = ord(UNKNOWN_CHARACTER)

        supported_chars = get_supported_characters(ttfont, as_strings=status)
        assert isinstance(supported_chars, list), \
            "Should return a list"
        assert KNOWN_CHARACTER in supported_chars, \
            f"Known character '{KNOWN_CHARACTER}' should be supported by the font"
        assert UNKNOWN_CHARACTER not in supported_chars, \
            f"Unknown character '{UNKNOWN_CHARACTER}' should not be supported by the font"
        assert len(supported_chars) == 208, \
            "Should return a non-empty list"

        if status:
            assert all(isinstance(char, str) for char in supported_chars), \
                "All characters should be strings"
        else:
            assert all(isinstance(char, int) for char in supported_chars), \
                "All characters should be integers"


def test_is_character_supported(ttfont):

    # A character known to be supported by the test font
    KNOWN_CHARACTER = 'A'  # Adjust this based on your test font

    # A character known not to be supported by the test font
    UNKNOWN_CHARACTER = '試'  # A non-character in Unicode, unlikely to be supported

    assert is_character_supported(
        ttfont, KNOWN_CHARACTER), f"Font should support character '{KNOWN_CHARACTER}'"
    assert not is_character_supported(
        ttfont, UNKNOWN_CHARACTER), f"Font should not support character '{UNKNOWN_CHARACTER}'"
