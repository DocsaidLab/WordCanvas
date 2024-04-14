import numpy as np
import pytest
from wordcanvas import AlignMode, OutputDirection, WordCanvas


class TestWordCanvas:

    @pytest.fixture
    def generator(self):
        return WordCanvas(output_size=(64, 512), text_aspect_ratio=1.0, random_font=False, enable_all_random=False)

    def test_init_with_custom_parameters(self, generator):
        assert generator.output_size == (64, 512)
        assert generator.text_aspect_ratio == 1.0
        assert generator.random_font is False
        assert generator.enable_all_random is False

    @pytest.mark.parametrize("align_mode", [AlignMode.Left, AlignMode.Right, AlignMode.Center, AlignMode.Scatter])
    def test_align_modes(self, generator, align_mode):
        generator.align_mode = align_mode
        _, infos = generator("test")
        assert infos['align_mode'] == align_mode

    @pytest.mark.parametrize("output_direction", [OutputDirection.Default, OutputDirection.Horizontal, OutputDirection.Vertical])
    def test_output_directions(self, generator, output_direction):
        generator.output_direction = output_direction
        img, infos = generator("test")
        assert infos['output_direction'] == output_direction

    def test_random_text_generation(self, generator):
        np.random.seed(42)
        generator.random_text = True
        generator.min_random_text_length = 5
        generator.max_random_text_length = 5
        _, infos = generator("test")
        generated_text = infos['text']
        assert len(generated_text) == 5

    def test_error_handling(self):
        with pytest.raises(OSError):
            WordCanvas(font_path="invalid/path/to/font.ttf")

    def test_dashboard(self, generator):
        text = generator.dashboard
        expected_properties = [
            "font_path", "font_bank", "random_font", "random_text",
            "text_size", "direction", "text_aspect_ratio", "text_color",
            "background_color", "output_size", "align_mode", "output_direction",
            "min_random_text_length", "max_random_text_length",
            "random_direction", "random_text_color", "random_background_color",
            "random_align_mode", "enable_all_random"
        ]
        for prop in expected_properties:
            assert prop in text


class TestWordCanvasExtended:

    @pytest.fixture
    def generator(self):
        return WordCanvas(enable_all_random=False, random_text=False, random_font=False)

    @pytest.mark.parametrize("text_color,background_color", [((255, 0, 0), (0, 0, 0)), ((0, 255, 0), (255, 255, 255))])
    def test_colors(self, generator, text_color, background_color):
        generator.text_color = text_color
        generator.background_color = background_color
        img, infos = generator("test")
        # 檢查圖像的顏色分布是否符合預期，這可能需要進行圖像分析來確定文本和背景顏色

    def test_random_color_generation(self, generator):
        np.random.seed(42)
        generator.random_text_color = True
        generator.random_background_color = True
        _, infos = generator("test")
        # 驗證隨機生成的顏色是否在預期範圍內

    def test_direction_effect(self, generator):
        generator.output_size = (64, 512)
        generator.direction = 'ttb'
        img, _ = generator('test')
        # 驗證輸出方向為ttb時，圖像的高應大於寬

        assert img.shape[0] > img.shape[1]

    @pytest.mark.parametrize("min_length,max_length", [(5, 5), (1, 10)])
    def test_text_length_limits(self, generator, min_length, max_length):
        generator.random_text = True
        generator.min_random_text_length = min_length
        generator.max_random_text_length = max_length
        _, infos = generator("test")
        text_length = len(infos['text'])
        assert min_length <= text_length <= max_length

    def test_invalid_font_path_handling(self):
        with pytest.raises(Exception) as e_info:
            WordCanvas(font_path="nonexistent/font/path.ttf")

    def test_invalid_text_size_handling(self):
        with pytest.raises(ValueError) as e_info:
            WordCanvas(text_size=-1)

    @pytest.mark.parametrize("align_mode", [AlignMode.Left, AlignMode.Center, AlignMode.Right])
    def test_align_mode_application(self, generator, align_mode):
        generator.align_mode = align_mode
        generator.output_size = (100, 100)
        img, infos = generator('test')


class TestWordCanvasRandomFont:

    @pytest.fixture
    def generator(self):
        return WordCanvas(random_font=True, random_text=True)

    def test_random_font_generation(self, generator):
        img, infos = generator("test")

    def test_properties(self, generator):
        assert generator.text_size is 64
        assert generator.font_path == generator.DEFAULT_FONT_PATH


class TestWordCanvasDirection:

    @pytest.fixture
    def generator(self):
        return WordCanvas(direction='ttb', output_size=(64, 512))

    def test_ttb_direction(self, generator):
        generator.align_mode = AlignMode.Center
        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Center

        generator.align_mode = AlignMode.Left
        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Left

        generator.align_mode = AlignMode.Right
        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Right

    def test_scatter_image(self, generator):
        generator.align_mode = AlignMode.Scatter

        generator.direction = 'ltr'
        generator.text_aspect_ratio = 1.0

        img, infos = generator("t")
        assert infos['text'] == 't'
        assert infos['align_mode'] == AlignMode.Scatter

        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Scatter

        generator.text_aspect_ratio = 0.5
        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Scatter

        generator.direction = 'ttb'
        generator.text_aspect_ratio = 1.0

        img, infos = generator("t")
        assert infos['text'] == 't'
        assert infos['align_mode'] == AlignMode.Scatter

        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Scatter

        generator.text_aspect_ratio = 0.5
        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Scatter

        generator.direction = 'ttb'
        generator.output_direction = OutputDirection.Horizontal
        generator.text_aspect_ratio = 1.0

        img, infos = generator("測試")
        assert infos['text'] == '測試'
        assert infos['align_mode'] == AlignMode.Scatter
