import numpy as np
import pytest
from wordcanvas import ExampleAug, Shear


@pytest.fixture
def sample_image():
    return np.ones((100, 100, 3), dtype=np.uint8) * 255


def test_shear_initialization():
    shear = Shear()
    assert shear.max_shear_left == 20
    assert shear.max_shear_right == 20
    assert shear.probability == 0.5

    custom_shear = Shear(max_shear_left=10, max_shear_right=15, p=0.7)
    assert custom_shear.max_shear_left == 10
    assert custom_shear.max_shear_right == 15
    assert custom_shear.probability == 0.7


def test_shear_effectiveness(sample_image):
    shear = Shear(max_shear_left=10, max_shear_right=10, p=1.0)
    sheared_image = shear(sample_image.copy())
    assert sheared_image.shape == sample_image.shape


def test_exampleaug_initialization():
    aug = ExampleAug(p=0.5)
    assert isinstance(aug.shear, Shear)
    assert aug.shear.probability == 0.5


def test_exampleaug_pipeline(sample_image):
    aug = ExampleAug(p=1.0)
    augmented_image = aug(sample_image.copy())
    assert augmented_image.shape == sample_image.shape


def test_shear_angle_boundaries(sample_image):
    max_angle = 15
    shear = Shear(max_shear_left=max_angle, max_shear_right=max_angle, p=1.0)
    for _ in range(10):
        img = shear(sample_image.copy())
