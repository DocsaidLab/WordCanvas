import numpy as np
import pytest

from wordcanvas import MRZGenerator


def test_mrz_generator_initialization():
    gen = MRZGenerator(
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
        spacing=32
    )
    assert gen.spacing == 32
    assert gen.background_color == (255, 255, 255)


def test_gen_random_mrz():
    gen = MRZGenerator()
    mrz = gen.gen_random_mrz(10)
    assert len(mrz) == 10
    assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<' for c in mrz)


def test_mrz_l_property():
    gen = MRZGenerator()
    assert gen.mrz_l == {'TD1': 30, 'TD2': 36, 'TD3': 44}


def test_mrz_call_random():
    gen = MRZGenerator()
    result = gen()
    assert result['typ'] in ['TD1', 'TD2', 'TD3']
    assert 'text' in result
    assert 'points' in result
    assert 'image' in result
    assert isinstance(result['image'], np.ndarray)


def test_mrz_call_with_text():
    gen = MRZGenerator()
    mrz_text = ["ABCDEFGHIJKLMNOPQRSTUVWXY01234500000",
                "ZYXWVUTSRQPONMLKJIHGFEDCBA0987650000"]
    result = gen(mrz_type='TD2', mrz_text=mrz_text)
    assert result['typ'] == 'TD2'
    assert result['text'] == '\n'.join(mrz_text)
    assert len(result['points']) == 72  # 每行 36 個字符，2 行
    assert isinstance(result['image'], np.ndarray)


def test_mrz_call_invalid_text():
    gen = MRZGenerator()

    with pytest.raises(ValueError, match="mrz_text must contain exactly 3 lines with 30 characters each"):
        gen(mrz_type='TD1', mrz_text="INVALID")

    with pytest.raises(ValueError, match="mrz_text must be a list of 3 strings with 30 characters each"):
        gen(mrz_type='TD1', mrz_text=["SHORT", "TOO", "FEW"])

    with pytest.raises(ValueError, match="mrz_text must contain exactly 2 lines with 36 characters each"):
        gen(mrz_type='TD2', mrz_text="WRONGFORMAT")

    with pytest.raises(ValueError, match="mrz_text must be either a string or a list of strings"):
        gen(mrz_type='TD3', mrz_text=123)


def test_mrz_call_coordinates():
    gen = MRZGenerator()
    result = gen(mrz_type='TD1')
    points = result['points']
    image = result['image']

    assert len(points) == 90  # TD1 有 3 行，每行 30 字符
    assert all(isinstance(point, tuple) and len(
        point) == 2 for point in points)
    assert all(0 <= x < image.shape[1] and 0 <=
               y < image.shape[0] for x, y in points)
