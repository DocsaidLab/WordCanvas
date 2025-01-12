from pathlib import Path

import numpy as np
import pytest
from PIL import ImageFont

from wordcanvas.text_image_renderer import (_clamp_color, load_truetype_font,
                                            text2image)

FONT_ROOT = Path(__file__).parent.parent / "wordcanvas" / "fonts"


@pytest.fixture
def sample_font_path(tmp_path) -> Path:
    """
    建立或複製一個測試用的 TTF 檔案到 tmp_path 以進行測試。
    假設有一個測試用字型檔案 'test_font.ttf' 放在 tests/fonts/ 目錄。
    若您無法提供實體字型，可視情況 Mock。
    """
    # 假設你在專案中有準備 "tests/fonts/test_font.ttf"
    # 這裡示範複製到 tmp_path 供測試：
    src = FONT_ROOT / "NotoSansTC-Regular.otf"
    if not src.is_file():
        pytest.skip(
            "No test_font.ttf found. Please provide a valid TTF for testing.")
    dest = tmp_path / "test_font.ttf"
    dest.write_bytes(src.read_bytes())
    return dest


# ----------------------------------------------
#           Tests for load_truetype_font
# ----------------------------------------------
class TestLoadTrueTypeFont:
    def test_load_truetype_font_with_pil_font(self):
        """
        測試直接傳入 PIL ImageFont.FreeTypeFont 實例。
        """
        # Arrange
        font = ImageFont.FreeTypeFont(
            FONT_ROOT / "NotoSansTC-Regular.otf", size=20)
        # Act
        loaded_font = load_truetype_font(font)
        # Assert
        assert isinstance(loaded_font, ImageFont.FreeTypeFont)
        assert loaded_font is font  # 與傳入同一個物件

    def test_load_truetype_font_with_string_path(self, sample_font_path):
        """
        測試以字串形式的檔案路徑載入字型。
        """
        loaded_font = load_truetype_font(str(sample_font_path), size=24)
        assert isinstance(loaded_font, ImageFont.FreeTypeFont)

    def test_load_truetype_font_with_path_object(self, sample_font_path):
        """
        測試以 Path 物件載入字型。
        """
        loaded_font = load_truetype_font(sample_font_path, size=30)
        assert isinstance(loaded_font, ImageFont.FreeTypeFont)

    def test_load_truetype_font_non_existing_file(self, tmp_path):
        """
        測試傳入不存在的字型路徑，預期拋出 IOError。
        """
        non_existent_path = tmp_path / "non_existent.ttf"
        with pytest.raises(IOError):
            _ = load_truetype_font(non_existent_path, size=20)

    def test_load_truetype_font_with_return_infos(self, sample_font_path):
        """
        測試 return_infos=True，可同時獲得字型與字型資訊。
        """
        font_obj, font_info = load_truetype_font(
            font_source=sample_font_path,
            size=18,
            return_infos=True
        )
        assert isinstance(font_obj, ImageFont.FreeTypeFont)
        assert isinstance(font_info, dict)
        assert "font_path" in font_info
        assert "font_size" in font_info
        assert "font_name" in font_info
        # 簡單檢查值
        assert font_info["font_path"] == str(sample_font_path)
        assert font_info["font_size"] == 18

    def test_load_truetype_font_invalid_source_type(self):
        """
        測試傳入不支援的類型，預期程式碼內若無保護，可能拋 IOError 或 TypeError。
        """
        with pytest.raises(Exception):  # 可視程式碼實作改成 IOError 或 TypeError
            _ = load_truetype_font(12345, size=20)  # int 類型應該不支援


# ----------------------------------------------
#           Tests for _clamp_color (Optional)
# ----------------------------------------------
class TestClampColor:
    @pytest.mark.parametrize(
        "input_color, expected",
        [
            ((-10, 128, 300), (0, 128, 255)),
            ((0, 0, 0), (0, 0, 0)),
            ((255, 256, 999), (255, 255, 255)),
            ([100, 50, -5], (100, 50, 0)),
        ]
    )
    def test_clamp_color_range(self, input_color, expected):
        """
        測試 _clamp_color 將 RGB 分量正確限制在 [0, 255]。
        """
        result = _clamp_color(input_color)
        assert result == expected


# ----------------------------------------------
#           Tests for text2image
# ----------------------------------------------
class TestText2Image:
    def test_text2image_basic(self, sample_font_path):
        """
        測試基礎文字轉成影像，確保輸出是 np.ndarray，且包含基礎資訊。
        """
        # Act
        img_arr, info = text2image(
            text="Hello World",
            font=str(sample_font_path),
            size=32,
            return_infos=True
        )
        # Assert
        assert isinstance(img_arr, np.ndarray)
        assert img_arr.shape[2] == 3  # 預設 RGB 三通道
        assert isinstance(info, dict)
        assert info["text"] == "Hello World"
        assert info["font_path"] == str(sample_font_path)
        assert "bbox(xyxy)" in info
        assert "bbox(wh)" in info

    @pytest.mark.parametrize("direction", ["ltr", "rtl", "ttb"])
    def test_text2image_valid_directions(self, direction, sample_font_path):
        """
        測試不同 valid direction 設定，可順利產生影像。
        """
        img_arr, info = text2image(
            text="Test",
            font=sample_font_path,
            direction=direction,
            return_infos=True
        )
        assert isinstance(img_arr, np.ndarray)
        assert info["direction"] == direction

    def test_text2image_invalid_direction(self, sample_font_path):
        """
        測試傳入無效的 direction，應拋出 ValueError。
        """
        with pytest.raises(ValueError, match="Invalid direction"):
            text2image(
                text="Test",
                font=sample_font_path,
                direction="invalid_dir"
            )

    def test_text2image_with_existing_font_object(self, sample_font_path):
        """
        測試傳入 (font_obj, font_meta) tuple，而非字串或 Path。
        """
        font_obj, font_info = load_truetype_font(
            sample_font_path, size=20, return_infos=True
        )
        # 這裡 font 直接傳 (font_obj, font_info)
        img_arr, info = text2image(
            text="Sample Text",
            font=(font_obj, font_info),
            return_infos=True
        )
        assert isinstance(img_arr, np.ndarray)
        assert info["font_path"] == font_info["font_path"]

    def test_text2image_force_width_height(self, sample_font_path):
        """
        測試自訂 width, height，最終輸出影像大小應符合這些參數。
        """
        target_width, target_height = 300, 100
        img_arr, info = text2image(
            text="Forced size",
            font=sample_font_path,
            size=32,
            width=target_width,
            height=target_height,
            return_infos=True
        )
        assert img_arr.shape[1] == target_width
        assert img_arr.shape[0] == target_height

    def test_text2image_with_offset(self, sample_font_path):
        """
        測試手動設定 offset，檢查回傳資訊的 offset 是否一致。
        """
        offset = (10, 20)
        _, info = text2image(
            text="Offset Test",
            font=sample_font_path,
            size=20,
            offset=offset,
            return_infos=True
        )
        assert info["offset"] == offset

    def test_text2image_with_stroke(self, sample_font_path):
        """
        測試文字加上描邊 (stroke_width, stroke_fill)。
        """
        img_arr, info = text2image(
            text="Stroke Text",
            font=sample_font_path,
            size=32,
            stroke_width=2,
            stroke_fill=(255, 0, 0),  # 紅色描邊
            return_infos=True
        )
        # 簡單驗證
        assert info["stroke_width"] == 2
        assert info["stroke_fill"] == (255, 0, 0)
        # shape 仍應該是 RGB
        assert img_arr.shape[2] == 3

    def test_text2image_error_during_text_rendering(self, mocker, sample_font_path):
        """
        模擬 PIL 在 textbbox 時出現錯誤，預期 text2image 會拋出 ValueError。
        """
        # mock PIL 的 textbbox 讓它直接拋錯
        mock_draw = mocker.patch(
            "PIL.ImageDraw.ImageDraw.textbbox", side_effect=Exception("Mock error"))
        with pytest.raises(ValueError, match="Error rendering text: 'Test'"):
            text2image(
                text="Test",
                font=sample_font_path,
                return_infos=True
            )
        mock_draw.assert_called_once()


@pytest.mark.parametrize(
    "text_color, bg_color",
    [
        ((255, 0, 0), (255, 255, 255)),
        ((0, 255, 100), (10, 10, 10)),
        ((-10, 999, 1000), (-5, -5, -5)),  # 測試超出範圍會被 clamp
    ]
)
def test_text2image_color_clamping(text_color, bg_color, sample_font_path):
    """
    測試 text_color, background_color 超出 0~255 範圍時是否被正確 clamp。
    """
    img_arr, info = text2image(
        text="Color clamp",
        font=sample_font_path,
        text_color=text_color,
        background_color=bg_color,
        return_infos=True
    )
    # 只要執行成功表示 _clamp_color 有生效，不拋錯即可
    # 也可檢查 info 內的 text_color, background_color 是否已被 clamp
    for c in info["text_color"]:
        assert 0 <= c <= 255
    for c in info["background_color"]:
        assert 0 <= c <= 255
    assert isinstance(img_arr, np.ndarray)
