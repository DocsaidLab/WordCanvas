**[English](./README.md)** | [中文](./README_tw.md)

# WordCanvas

<p align="left">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache%202-dfd.svg"></a>
    <a href="https://github.com/DocsaidLab/WordCanvas/releases"><img src="https://img.shields.io/github/v/release/DocsaidLab/WordCanvas?color=ffa"></a>
    <a href=""><img src="https://img.shields.io/badge/python-3.8+-aff.svg"></a>
</p>

## Introduction

<div align="center">
    <img src="./docs/title.jpg" width="800">
</div>

The core functionality of this project is the "Text Image Generation Tool".

We addressed issues such as insufficient data volume, class imbalance, and lack of diversity by generating a large variety of synthetic Chinese text images. To achieve this, we referred to several existing text synthesis tools, which provided us with significant insights and inspired us to create a new text image generator from scratch.

## Documentation

For information on how to install and use this package, please refer to the [**WordCanvas Documents**](https://docsaid.org/en/docs/wordcanvas/intro). You can get all detailed information about this project from the documents.

## Installation

Currently, there is no package available on PyPI, and there are no plans to provide one in the near future. To use this project, you must clone it directly from Github and then install the required dependencies.

- Note: Before installation, please ensure you have installed `DocsaidKit`. If you have not installed `DocsaidKit`, please refer to the [**DocsaidKit Installation Guide**](https://docsaid.org/en/docs/docsaidkit/installation).

### Installation Steps

1. **Clone the project:**

   ```bash
   git clone https://github.com/DocsaidLab/WordCanvas.git
   ```

2. **Enter the project directory:**

   ```bash
   cd WordCanvas
   ```

3. **Install dependencies:**

   ```bash
   pip install wheel
   ```

4. **Build the package:**

   ```bash
   python setup.py bdist_wheel
   ```

5. **Install the package:**

   ```bash
   pip install dist/wordcanvas-*-py3-none-any.whl
   ```

Following these steps, you should be able to successfully install `WordCanvas`.

Once installed, you are ready to use the project.

### Test the Installation

You can test whether the installation was successful with the following command:

```bash
python -c "import wordcanvas; print(wordcanvas.__version__)"
# >>> 0.4.2
```

If you see a version number similar to `0.4.2`, it indicates the installation was successful.

## QuickStart

Getting started is often the hardest part, so let's keep it simple.

### Starting with a String

Start with a basic declaration to begin using the tool.

```python
from wordcanvas import WordCanvas

gen = WordCanvas()
```

Using default settings, you can directly call the function to generate a text image.

```python
text = "你好！Hello, World!"
img, infos = gen(text)
print(img.shape)
# >>> (67, 579, 3)
```

![sample1](./docs/sample1.jpg)

### Specifying a Specific Font

You can specify your preferred font using the `font` parameter.

```python
gen = WordCanvas(
    font_path="/path/to/your/font/OcrB-Regular.ttf"
)

text = 'Hello, World!'
img, infos = gen(text)
```

![sample14](./docs/sample14.jpg)

When the font does not support the input text, tofu characters will appear.

```python
text = 'Hello, 中文!'
img, infos = gen(text)
```

![sample15](./docs/sample15.jpg)

### Setting Image Size

Use the `output_size` parameter to adjust the image size.

```python
gen = WordCanvas(output_size=(64, 1024)) # Height 64, Width 1024
img, infos = gen(text)
print(img.shape)
# >>> (64, 1024, 3)
```

![sample4](./docs/sample4.jpg)

When the set size is smaller than the text image size, the text image will automatically be scaled down.

That is, the text will be squeezed together, forming a thin rectangle, like this:

```python
text = '你好' * 10
gen = WordCanvas(output_size=(64, 512))  # Height 64, Width 512
img, infos = gen(text)
```

![sample8](./docs/sample8.jpg)

### Adjusting Background Color

Use the `background_color` parameter to adjust the background color.

```python
gen = WordCanvas(background_color=(255, 0, 0)) # Red background
img, infos = gen(text)
```

![sample2](./docs/sample2.jpg)

### Adjusting Text Color

Use the `text_color` parameter to adjust the text color.

```python
gen = WordCanvas(text_color=(0, 255, 0)) # Green text
img, infos = gen(text)
```

![sample3](./docs/sample3.jpg)

### Adjusting Text Alignment

:::warning
Remember the image size we mentioned earlier? In default settings, **setting text alignment is meaningless**. You must allow extra space in the text image to see the effect of alignment.
:::

Use the `align_mode` parameter to adjust the text alignment mode.

```python
from wordcanvas import AlignMode, WordCanvas

gen = WordCanvas(
    output_size=(64, 1024),
    align_mode=AlignMode.Center
)

text = '你好！ Hello, World!'
img, infos = gen(text)
```

- **Center alignment: `AlignMode.Center`**

  ![sample5](./docs/sample5.jpg)

- **Right alignment: `AlignMode.Right`**

  ![sample6](./docs/sample6.jpg)

- **Left alignment: `AlignMode.Left`**

  ![sample7](./docs/sample4.jpg)

- **Scatter alignment: `AlignMode.Scatter`**

  ![sample8](./docs/sample7.jpg)

### Adjusting Text Direction

Use the `direction` parameter to adjust the text direction.

- **Outputting horizontal text**

  ```python
  text = '你好！'
  gen = WordCanvas(direction='ltr') # Left to right horizontal text
  img, infos = gen(text)
  ```

  ![sample9](./docs/sample9.jpg)

- **Outputting vertical text**

  ```python
  text = '你好！'
  gen = WordCanvas(direction='ttb') # Top to bottom vertical text
  img, infos = gen(text)
  ```

  ![sample10](./docs/sample10.jpg)

- **Outputting vertical text with scatter alignment**

  ```python
  text = '你好！'
  gen = WordCanvas(
      direction='ttb',
      align_mode=AlignMode.Scatter,
      output_size=(64, 512)
  )
  img, infos = gen(text)
  ```

  ![sample11](./docs/sample11.jpg)

### Adjusting Output Direction

Use the `output_direction` parameter to adjust the output direction.

- **Vertical text, horizontal output**

  ```python
  from wordcanvas import OutputDirection, WordCanvas

  gen = WordCanvas(
      direction='ttb',
      output_direction=OutputDirection.Horizontal
  )

  text = '你好！'
  img, infos = gen(text)
  ```

  ![sample12](./docs/sample12.jpg)

- **Horizontal text, vertical output**

  ```python
  from wordcanvas import OutputDirection, WordCanvas

  gen = WordCanvas(
      direction='ltr',
      output_direction=OutputDirection.Vertical
  )

  text = '你好！'
  img, infos = gen(text)
  ```

  ![sample13](./docs/sample13.jpg)

### Flattening Text

In scenarios where the text is particularly flat, you can use the `text_aspect_ratio` parameter.

```python
gen = WordCanvas(
    text_aspect_ratio=0.25, # Text height / text width = 1/4
    output_size=(32, 1024),
)  # Flattened text

text = "Flattened test"
img, infos = gen(text)
```

![sample16](./docs/sample16.jpg)

### Dashboard

That's a brief overview of the basic functionality.

Finally, let's take a look at the dashboard feature.

```python
gen = WordCanvas()
print(gen)
```

You can also skip `print` and just output directly, as we've implemented the `__repr__` method. The output will display a simple dashboard.

![dashboard](./docs/dashboard.jpg)

You can see:

- The first column is Property, which lists all the settings.
- The second column is Current Value, which shows the value of the parameters "at this moment."
- The third column is SetMethod, which describes the method to set the parameter. Parameters marked `set` can be directly modified; those marked `reinit` require reinitialization of the `WordCanvas` object.
- The fourth column is DType, which is the data type of the parameter.
- The fifth column is Description, which describes the parameter.

Most parameters can be directly set, meaning when you need to change output characteristics, you don't need to rebuild a `WordCanvas` object, just set them directly. Parameters that require `reinit` typically involve font initialization, like `text_size`. So, be aware, not all parameters can be directly set.

```python
gen.output_size = (64, 1024)
gen.text_color = (0, 255, 0)
gen.align_mode = AlignMode.Center
gen.direction = 'ltr'
gen.output_direction = OutputDirection.Horizontal
```

After setting, simply call to get the new text image.

If you've set a parameter that requires `reinit`, you'll encounter an error:

- **AttributeError: can't set attribute**

  ```python
  gen.text_size = 128
  # >>> AttributeError: can't set attribute
  ```

## Summary

While many features weren't mentioned, this covers the basic functionalities.

That concludes the basic usage of this project; if you need more advanced features, please refer to the [**WordCanvas Documents**](https://docsaid.org/en/docs/wordcanvas/intro).

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
