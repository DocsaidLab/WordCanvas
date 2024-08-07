from .barcode import Code39Generator, Code128Generator, CodeType
from .base import AlignMode, OutputDirection, WordCanvas
from .imgaug import ExampleAug, Shear
from .mrz import MRZGenerator
from .text2image import text2image
from .utils import *

__version__ = '0.5.1'
