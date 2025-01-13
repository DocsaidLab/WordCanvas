**[English](./README.md)** | [中文](./README_tw.md)

# WordCanvas

<p align="left">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache%202-dfd.svg"></a>
    <a href=""><img src="https://img.shields.io/badge/python-3.10+-aff.svg"></a>
    <a href="https://github.com/DocsaidLab/WordCanvas/releases"><img src="https://img.shields.io/github/v/release/DocsaidLab/WordCanvas?color=ffa"></a>
    <a href="https://pypi.org/project/wordcanvas_docsaid/"><img src="https://img.shields.io/pypi/v/wordcanvas_docsaid.svg"></a>
    <a href="https://pypi.org/project/wordcanvas_docsaid/"><img src="https://img.shields.io/pypi/dm/wordcanvas_docsaid?color=9cf"></a>
</p>

## Introduction

<div align="center">
    <img src="https://github.com/DocsaidLab/WordCanvas/blob/main/docs/title.jpg?raw=true" width="800">
</div>

The core functionality of this project is a "**Text-to-Image Generation Tool**", named **WordCanvas**, meaning "text canvas."

We generate a large variety of Chinese text images through data synthesis, addressing issues such as insufficient data, class imbalance, and lack of diversity. In doing so, we have referenced existing text synthesis tools, whose design ideas inspired us to build a completely new text image generator from scratch.

## Technical Documentation

For installation and usage instructions, please refer to [**WordCanvas Documents**](https://docsaid.org/en/docs/wordcanvas).

There you will find detailed information about the project.

## Installation

### Install via PyPI

1. Install `wordcanvas-docsaid`:

   ```bash
   pip install wordcanvas-docsaid
   ```

2. Verify installation:

   ```bash
   python -c "import wordcanvas; print(wordcanvas.__version__)"
   ```

3. If you see the version number, the installation is successful.

### Install from GitHub

1. Clone the project from GitHub:

   ```bash
   git clone https://github.com/DocsaidLab/WordCanvas.git
   ```

2. Install the wheel package:

   ```bash
   pip install wheel setuptools
   ```

3. Build the whl file:

   ```bash
   cd WordCanvas
   python setup.py bdist_wheel
   ```

4. Install the whl file:

   ```bash
   pip install dist/wordcanvas_docsaid-*-py3-none-any.whl
   ```

## Quick Start

The hardest part is getting started, so we need a simple beginning.

### Start with a String

Simply provide a basic declaration and you're ready to go.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(return_infos=True)
```

Using all default settings, you can directly call the function to generate a text image.

```python
text = "你好！Hello, World!"
img, infos = gen(text)

print(img.shape)
# >>> (67, 579, 3)

print(infos)
# {'text': '你好！Hello, World!',
#  'bbox(xyxy)': (0, 21, 579, 88),
#  'bbox(wh)': (579, 67),
#  'offset': (0, -21),
#  'direction': 'ltr',
#  'background_color': (0, 0, 0),
#  'text_color': (255, 255, 255),
#  'spacing': 4,
#  'align': 'left',
#  'stroke_width': 0,
#  'stroke_fill': (0, 0, 0),
#  'font_path': 'fonts/NotoSansTC-Regular.otf',
#  'font_size_actual': 64,
#  'font_name': 'NotoSansTC-Regular',
#  'align_mode': <AlignMode.Left: 0>,
#  'output_direction': <OutputDirection.Remain: 0>}
```

![sample1](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample1.jpg?raw=true)

> [!TIP]
> In default mode, the output image size depends on:
>
> 1. **Font size**: The default is 64. As the font size increases, the image size will also increase.
> 2. **Text length**: The longer the text, the wider the image will be, with the exact length determined by `pillow`.
> 3. The output information `infos` contains all drawing parameters, including text, background color, text color, etc.
> 4. To output only the image, set `return_infos=False`, which is the default setting.

### Specify a Specific Font

You can specify your preferred font using the `font` parameter.

```python
from wordcanvas import WordCanvas

# Do not specify return_infos, default is False, which will not return infos
gen = WordCanvas(
    font_path="/path/to/your/font/OcrB-Regular.ttf"
)

text = 'Hello, World!'
img = gen(text)
```

![sample14](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample14.jpg?raw=true)

If the font does not support the input text, tofu characters will appear.

```python
text = 'Hello, 中文!'
img = gen(text)
```

![sample15](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample15.jpg?raw=true)

> [!TIP]
>
> **How to Check if the Font Supports Characters:**
>
> I currently don’t have this requirement, so I’ve left a basic method. This is a simple check that only checks one character at a time, so you need to iterate through all the characters. If you have other requirements, feel free to expand on this.
>
> ```python title="check_font.py"
> from wordcanvas import is_character_supported, load_ttfont
>
> target_text = 'Hello, 中文!'
>
> font = load_ttfont("/path/to/your/font/OcrB-Regular.ttf")
>
> for c in target_text:
>     status = is_character_supported(font, c)
>
> # >>> Character '中' (0x4e2d) is not supported by the font.
> # >>> Character '文' (0x6587) is not supported by the font.
> ```

### Set Image Size

You can adjust the image size using the `output_size` parameter.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(output_size=(64, 1024)) # Height 64, Width 1024
img = gen(text)
print(img.shape)
# >>> (64, 1024, 3)
```

![sample4](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample4.jpg?raw=true)

When the specified size is smaller than the text image size, the text image will be automatically scaled.

In other words, the text will be squeezed together, becoming a narrow rectangle, for example:

```python
from wordcanvas import WordCanvas

text = '你好' * 10
gen = WordCanvas(output_size=(64, 512))  # Height 64, Width 512
img = gen(text)
```

![sample8](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample8.jpg?raw=true)

### Adjust Background Color

You can adjust the background color using the `background_color` parameter.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(background_color=(255, 0, 0)) # Red background
img = gen(text)
```

![sample2](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample2.jpg?raw=true)

### Adjust Text Color

You can adjust the text color using the `text_color` parameter.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(text_color=(0, 255, 0)) # Green text
img = gen(text)
```

![sample3](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample3.jpg?raw=true)

### Adjust Text Alignment

> [!WARNING]
> Do you remember the image size mentioned earlier?
>
> By default, **setting text alignment does not have any effect**. When drawing the image, there must be extra space in the text image to see the alignment effect.

You can adjust the text alignment using the `align_mode` parameter.

```python
from wordcanvas import AlignMode, WordCanvas

gen = WordCanvas(
    output_size=(64, 1024),
    align_mode=AlignMode.Center
)

text = '你好！ Hello, World!'
img = gen(text)
```

- **Center alignment: `AlignMode.Center`**

  ![sample5](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample5.jpg?raw=true)

- **Right alignment: `AlignMode.Right`**

  ![sample6](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample6.jpg?raw=true)

- **Left alignment: `AlignMode.Left`**

  ![sample4](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample4.jpg?raw=true)

- **Scatter alignment: `AlignMode.Scatter`**

  ![sample7](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample7.jpg?raw=true)

> [!TIP]
>
> In scatter alignment mode, not every character will be spread out, but words will be spread as a unit. In Chinese, the unit of a word is a character; in English, the unit of a word is a space.
>
> For example, the input text "你好！ Hello, World!" will be split into:
>
> - ["你", "好", "！", "Hello,", "World!"]
>
> Spaces are ignored, and scatter alignment is applied.
>
> Additionally, when the input text can only be split into a single word, scatter alignment for Chinese words is equivalent to center alignment, and English words will be split into individual characters for scatter alignment.
>
> The logic we use for this is:
>
> ```python
> def split_text(text: str):
>     """ Split text into a list of characters. """
>     pattern = r"[a-zA-Z0-9\p{P}\p{S}]+|."
>     matches = regex.findall(pattern, text)
>     matches = [m for m in matches if not regex.match(r'\p{Z}', m)]
>     if len(matches) == 1:
>         matches = list(text)
>     return matches
> ```

> [!WARNING]
> This is a very simple implementation and may not meet all requirements. If you have a more complete solution for string splitting, feel free to provide it.

### Adjust Text Direction

You can adjust the text direction using the `direction` parameter.

- **Output horizontal text**

  ```python
  from wordcanvas import AlignMode, WordCanvas

  text = '你好！'
  gen = WordCanvas(direction='ltr') # Left to right horizontal text
  img = gen(text)
  ```

  ![sample9](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample9.jpg?raw=true)

- **Output vertical text**

  ```python
  from wordcanvas import AlignMode, WordCanvas

  text = '你好！'
  gen = WordCanvas(direction='ttb') # Top to bottom vertical text
  img = gen(text)
  ```

  ![sample10](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample10.jpg?raw=true)

- **Output vertical text with scatter alignment**

  ```python
  from wordcanvas import AlignMode, WordCanvas

  text = '你好！'
  gen = WordCanvas(
      direction='ttb',
      align_mode=AlignMode.Scatter,
      output_size=(64, 512)
  )
  img = gen(text)
  ```

  ![sample11](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample11.jpg?raw=true)

### Adjust Output Direction

You can adjust the output direction using the `output_direction` parameter.

> [!TIP]
>
> **When to use this parameter**: When you choose "Output vertical text" but still want to view the text image horizontally, you can use this parameter.

- **Vertical text, horizontal output**

  ```python
  from wordcanvas import OutputDirection, WordCanvas

  gen = WordCanvas(
      direction='ttb',
      output_direction=OutputDirection.Horizontal
  )

  text = '你好！'
  img = gen(text)
  ```

  ![sample12](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample12.jpg?raw=true)

- **Horizontal text, vertical output**

  ```python
  from wordcanvas import OutputDirection, WordCanvas

  gen = WordCanvas(
      direction='ltr',
      output_direction=OutputDirection.Vertical
  )

  text = '你好！'
  img = gen(text)
  ```

  ![sample13](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample13.jpg?raw=true)

### Squeeze Text

In some scenarios, the text might need to be specially squeezed. You can use the `text_aspect_ratio` parameter to adjust this.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(
    text_aspect_ratio=0.25, # Text height / text width = 1/4
    output_size=(32, 1024),
)  # Squeezed text

text="壓扁測試"
img = gen(text)
```

![sample16](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample16.jpg?raw=true)

> [!IMPORTANT]
> It is important to note that if the squeezed text size exceeds the `output_size`, the image will go through an automatic scaling process. Therefore, you might end up squeezing the text, but it will be scaled back to its original size, and nothing will appear to have happened.

### Text Stroke

You can adjust the width of the text stroke using the `stroke_width` parameter.

```python
from wordcanvas import WordCanvas

gen = WordCanvas(
    font_size=64,
    text_color=(0, 0, 255), # Red text
    background_color=(255, 0, 0), # Blue background
    stroke_width=2, # Stroke width
    stroke_fill=(0, 255, 0), # Green stroke
)

text="文字外框測試"
img = gen(text)
```

![sample29](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample29.jpg?raw=true)

> [!WARNING]
> Using `stroke_width` may result in an OSError: array allocation size too large error with certain text.
>
> ```python
> Using `stroke_width` may cause an OSError: array allocation size too large error with certain text.
> This is a known issue with the `Pillow` library (see https://github.com/python-pillow/Pillow/issues/7287) and cannot be resolved directly.
> ```
>
> We found in testing that using `stroke_width` in `Pillow` may intermittently result in an `OSError`. This is a known issue with `Pillow`, and we have linked the relevant issue in the warning. You can click the link to view it.

### Multi-line Text

You can use the `\n` newline character to create multi-line text.

```python
from wordcanvas import WordCanvas

gen = WordCanvas()

text = '你好！\nHello, World!'
img = gen(text)
```

![sample30](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample30.jpg?raw=true)

In the case of multi-line text, you can combine it with most of the features mentioned above, for example:

```python
from wordcanvas import WordCanvas, AlignMode

gen = WordCanvas(
  text_color=(0, 0, 255), # Red text
  output_size=(128, 512), # Height 128, Width 512
  background_color=(0, 0, 0), # Black background
  align_mode=AlignMode.Center, # Center alignment
  stroke_width=2, # Stroke width
  stroke_fill=(0, 255, 0), # Green stroke
)

text = '你好！\nHello, World!'
img = gen(text)
```

![sample31](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/sample31.jpg?raw=true)

> [!WARNING]
>
> The following situations do not support multi-line text:
>
> 1. **`align_mode` does not support `AlignMode.Scatter`**
>
>    ```python
>    gen = WordCanvas(align_mode=AlignMode.Scatter)
>    ```
>
> 2. **`direction` does not support `ttb`**
>
>    ```python
>     gen = WordCanvas(direction='ttb')
>    ```
>
> If you need these features, please avoid using multi-line text.

### Dashboard

The basic functionality is more or less as described.

Finally, let's introduce the dashboard feature.

```python
from wordcanvas import WordCanvas

gen = WordCanvas()
print(gen)
```

You can also directly output without using `print`, as we have implemented the `__repr__` method.

Once output, you will see a simple dashboard.

![dashboard](https://github.com/DocsaidLab/WordCanvas/blob/main/docs/dashboard.jpg?raw=true)

Here you can see:

- The first column is **Property**, which lists all the setting parameters.
- The second column is **Current Value**, showing the current value of the parameter.
- The third column is **SetMethod**, which shows how the parameter is set.
  - Parameters set with `set` can be directly modified;
  - Parameters set with `reinit` require reinitialization of the `WordCanvas` object.
- The fourth column is **DType**, which shows the data type of the parameter.
- The fifth column is **Description**, which describes the parameter. (This column is not shown in the image above to save space.)

Most parameters can be directly set, meaning that when you need to modify output characteristics, you don't need to create a new object. Just modify the settings directly. Parameters that require `reinit` usually involve the initialization of font formats, such as text height (`font_size`) and others.

```python
gen.output_size = (64, 1024)
gen.text_color = (0, 255, 0)
gen.align_mode = AlignMode.Center
gen.direction = 'ltr'
gen.output_direction = OutputDirection.Horizontal
```

After setting, you can directly call the function to get the new text image. Additionally, if you modify parameters related to `reinit`, you will receive the corresponding error:

- **AttributeError: can't set attribute**

  ```python
  gen.font_size = 128
  # >>> AttributeError: can't set attribute
  ```

> [!CAUTION]
>
> Of course, you can still forcefully modify the parameters, but as a fellow Python user, I can't stop you:
>
> ```python
> gen._font_size = 128
> ```
>
> However, this will cause errors when generating the image later!
>
> Don't insist; just reinitialize the object.

## Summary

Many features haven't been mentioned, but the basic functionality has been covered.

This concludes the basic usage of the project. For more detailed information and usage methods, please refer directly to [**WordCanvas Advanced Usage**](https://docsaid.org/en/docs/wordcanvas/advance/).

## Citation

If you find our work helpful, please cite the following:

```bibtex
@misc{yuan2024wordcanvas,
  author = {Ze Yuan},
  title = {WordCanvas},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/DocsaidLab/WordCanvas}}
}
```
