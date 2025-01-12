from pathlib import Path

import numpy as np
import pytest

from wordcanvas import AlignMode, OutputDirection, RandomWordCanvas, WordCanvas

FONT_ROOT = Path(__file__).parent.parent / "wordcanvas" / "fonts"


def test_word_canvas_initialization():

    wc = WordCanvas(
        font_path=FONT_ROOT / "NotoSansTC-Regular.otf",
        font_size=48,
        direction="ltr",
        text_color=(255, 255, 255),
        background_color=(0, 0, 0),
        text_aspect_ratio=1.0,
        align_mode=AlignMode.Left,
        output_size=(300, 300),
        output_direction=OutputDirection.Remain,
        stroke_width=1,
        stroke_fill=(255, 0, 0),
        spacing=4,
        return_infos=True
    )
    assert wc.font_size == 48
    assert wc.direction == "ltr"
    assert wc.text_color == (255, 255, 255)
    assert wc.background_color == (0, 0, 0)
    assert wc.align_mode == AlignMode.Left
    assert wc.output_direction == OutputDirection.Remain


def test_font_block_list():
    with pytest.raises(ValueError, match="is in the block list"):
        WordCanvas(
            font_path=FONT_ROOT / "NotoSansTC-Regular.otf",
            block_font_list=["NotoSansTC-Regular"]
        )


def test_dashboard():
    wc = WordCanvas(
        font_path=FONT_ROOT / "NotoSansTC-Regular.otf",
        font_size=32,
        direction="ltr",
        align_mode=AlignMode.Center
    )
    dashboard = wc.dashboard
    assert "font_path" in dashboard
    assert "font_size" in dashboard
    assert "direction" in dashboard
    assert "align_mode" in dashboard


def test_regularize_image():
    wc = WordCanvas(output_size=(300, 300))
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    regularized_img = wc.regularize_image(
        img, direction="ltr", align_mode=AlignMode.Center, background_color=(0, 0, 0))
    assert regularized_img.shape == (300, 300, 3)


def test_gen_scatter_image():
    wc = WordCanvas(
        output_size=(300, 300),
        align_mode=AlignMode.Scatter,
    )
    scatter_image = wc(text="Hello")
    assert scatter_image.shape == (300, 300, 3)
    assert scatter_image.dtype == np.uint8


def test_call_method():
    wc = WordCanvas(
        font_path=FONT_ROOT / "NotoSansTC-Regular.otf",
        output_size=(300, 300),
        return_infos=True
    )
    text = "Hello, World!"
    img, infos = wc(text)
    assert isinstance(img, np.ndarray)
    assert "font_name" in infos
    assert infos["text"] == text


def test_output_direction():
    for direction in [OutputDirection.Remain, OutputDirection.Horizontal, OutputDirection.Vertical]:
        wc = WordCanvas(
            font_path=FONT_ROOT / "NotoSansTC-Regular.otf",
            output_size=(300, 300),
            output_direction=direction
        )
        img = np.ones((100, 300, 3), dtype=np.uint8)
        rotated_img = wc.regularize_image(
            img, direction="ltr", align_mode=AlignMode.Center, background_color=(0, 0, 0))
        assert rotated_img.shape == (300, 300, 3)


def test_font_size_extremes():
    wc = WordCanvas(font_path=FONT_ROOT /
                    "NotoSansTC-Regular.otf", font_size=1)
    assert wc.font_size == 1
    wc = WordCanvas(font_path=FONT_ROOT /
                    "NotoSansTC-Regular.otf", font_size=500)
    assert wc.font_size == 500


def test_output_size_extremes():
    wc = WordCanvas(output_size=(1, 1))
    img = np.ones((10, 10, 3), dtype=np.uint8)
    regularized_img = wc.regularize_image(
        img, "ltr", AlignMode.Center, (0, 0, 0))
    assert regularized_img.shape == (1, 1, 3)
    wc = WordCanvas(output_size=(10000, 10000))
    regularized_img = wc.regularize_image(
        img, "ltr", AlignMode.Center, (0, 0, 0))
    assert regularized_img.shape == (10000, 10000, 3)


def test_non_english_text():
    wc = WordCanvas(output_size=(300, 300))
    text = "你好，世界！"
    img = wc(text)
    assert img.shape == (300, 300, 3)


def test_multiline_text_handling():
    wc = WordCanvas(output_size=(300, 300), align_mode=AlignMode.Center)
    text = "Hello\nWorld"
    with pytest.raises(ValueError, match=r"contains '\\n'"):
        wc.gen_scatter_image(text=text, font=wc.font, direction="ltr",
                             text_color=(255, 255, 255), background_color=(0, 0, 0),
                             stroke_width=1, stroke_fill=(0, 0, 0), spacing=4)


def test_large_text_performance():
    wc = WordCanvas(output_size=(1000, 1000))
    text = "Hello " * 1000  # 非常長的文本
    img = wc(text)
    assert img.shape == (1000, 1000, 3)


def test_random_word_canvas_initialization():
    rwc = RandomWordCanvas(
        font_bank=FONT_ROOT,
        font_size=64,
        output_size=(300, 300),
        random_font=True,
        random_text=True,
        random_align_mode=True,
        random_text_color=True,
        random_background_color=True,
        random_direction=True,
        random_spacing=True,
        random_stroke_width=True,
        random_stroke_fill=True,
        min_random_text_length=1,
        max_random_text_length=9,
        min_random_stroke_width=0,
        max_random_stroke_width=5,
        min_random_spacing=0,
        max_random_spacing=5
    )
    assert rwc.random_font is True
    assert rwc.random_text is True
    assert rwc.random_align_mode is True
    assert rwc.min_random_text_length == 1
    assert rwc.max_random_text_length == 9


def test_random_text_generation():
    rwc = RandomWordCanvas(
        font_bank=FONT_ROOT,
        font_size=64,
        random_text=True,
        min_random_text_length=5,
        max_random_text_length=10,
        return_infos=True
    )
    img, infos = rwc()
    assert isinstance(img, np.ndarray)
    assert 5 <= len(infos["text"]) <= 10


def test_random_font_selection():
    rwc = RandomWordCanvas(
        font_bank=FONT_ROOT,
        font_size=64,
        random_font=True,
        return_infos=True
    )
    img, infos = rwc("Test")
    assert "font_name" in infos
    assert infos["font_name"] is not None


def test_random_color_generation():
    rwc = RandomWordCanvas(
        font_bank=FONT_ROOT,
        font_size=64,
        random_text_color=True,
        random_background_color=True,
        return_infos=True
    )
    img, infos = rwc("Test")
    assert isinstance(infos["text_color"], tuple)
    assert isinstance(infos["background_color"], tuple)


def test_random_spacing_and_stroke():
    rwc = RandomWordCanvas(
        font_bank=FONT_ROOT,
        font_size=64,
        random_spacing=True,
        random_stroke_width=True,
        min_random_spacing=1,
        max_random_spacing=10,
        min_random_stroke_width=1,
        max_random_stroke_width=5,
        return_infos=True
    )
    img, infos = rwc("Test")
    assert infos["spacing"] >= 1 and infos["spacing"] <= 10
    assert infos["stroke_width"] >= 1 and infos["stroke_width"] <= 5
