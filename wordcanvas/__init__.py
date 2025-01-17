from .barcode import Code39Generator, Code128Generator, CodeType
from .custom_aug import ExampleAug, Shear
from .font_utils import (CHARACTER_RANGES, extract_font_info,
                         filter_characters_by_range, get_supported_characters,
                         is_character_supported, load_ttfont,
                         remove_control_characters)
from .mrz_generator import MRZGenerator
from .text_image_renderer import load_truetype_font, text2image
from .word_canvas import (AlignMode, OutputDirection, RandomWordCanvas,
                          WordCanvas)

__version__ = '2.1.0'
