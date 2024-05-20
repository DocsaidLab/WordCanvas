[English](./README.md) | **[中文](./README_tw.md)**

# WordCanvas

<p align="left">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache%202-dfd.svg"></a>
    <a href="https://github.com/DocsaidLab/WordCanvas/releases"><img src="https://img.shields.io/github/v/release/DocsaidLab/WordCanvas?color=ffa"></a>
    <a href=""><img src="https://img.shields.io/badge/python-3.8+-aff.svg"></a>
</p>

## 介紹

<div align="center">
    <img src="./docs/title.jpg" width="800">
</div>

本專案的核心功能為「**文字圖像生成工具**」，取名為 **WordCanvas**，即「文字畫布」的意思。

我們透過合成資料的方式，生成大量多樣性的中文文字圖像，以應對資料量不足、類別不平衡、缺乏多樣性等問題。對此我們參考了一些現有的文字合成工具，他們的設計方式帶給了我們很多啟發，讓我們決定從頭打造一個新的文字圖像生成器。

## 技術文件

套件安裝和使用的方式，請參閱 [**WordCanvas Documents**](https://docsaid.org/docs/wordcanvas/intro/)。

在那裡你可以找到所有有關本專案的詳細資訊。

## 安裝

目前沒有提供 Pypi 上的安裝包，短時間內也沒有相關規劃。

若要使用本專案，你必須直接從 Github 上 clone 本專案，然後安裝相依套件。

- 注意：安裝前請確認你已經安裝了 `DocsaidKit`。如果你還沒有安裝 `DocsaidKit`，請參考 [**DocsaidKit 安裝指南**](https://docsaid.org/en/docs/docsaidkit/installation)。

### 安裝步驟

1. **Clone 本專案：**

   ```bash
   git clone https://github.com/DocsaidLab/WordCanvas.git
   ```

2. **進入專案目錄：**

   ```bash
   cd WordCanvas
   ```

3. **安裝相依套件：**

   ```bash
   pip install wheel
   ```

4. **建立打包文件：**

   ```bash
   python setup.py bdist_wheel
   ```

5. **安裝打包文件：**

   ```bash
   pip install dist/wordcanvas-*-py3-none-any.whl
   ```

遵循這些步驟，你應該能夠順利完成 `WordCanvas` 的安裝。

安裝完成後即可以使用本專案。

### 測試安裝

你可以使用以下指令來測試安裝是否成功：

```bash
python -c "import wordcanvas; print(wordcanvas.__version__)"
# >>> 0.4.2
```

如果你看到類似 `0.4.2` 的版本號，則表示安裝成功。

## 快速開始

萬事起頭難，所以我們需要一個簡單的開始。

### 從一個字串開始

先給定一個基本宣告，然後就可以開始使用了。

```python
from wordcanvas import WordCanvas

gen = WordCanvas()
```

全部使用預設功能，直接調用函數即可生成文字圖像。

```python
text = "你好！Hello, World!"
img, infos = gen(text)
print(img.shape)
# >>> (67, 579, 3)
```

![sample1](./docs/sample1.jpg)

### 指定特定字型

使用 `font` 參數可以指定自己喜歡的字型。

```python
gen = WordCanvas(
    font_path="/path/to/your/font/OcrB-Regular.ttf"
)

text = 'Hello, World!'
img, infos = gen(text)
```

![sample14](./docs/sample14.jpg)

當字型不支援輸入文字時，會出現豆腐字。

```python
text = 'Hello, 中文!'
img, infos = gen(text)
```

![sample15](./docs/sample15.jpg)

### 設定影像尺寸

使用 `output_size` 參數可以調整影像尺寸。

```python
gen = WordCanvas(output_size=(64, 1024)) # 高度 64，寬度 1024
img, infos = gen(text)
print(img.shape)
# >>> (64, 1024, 3)
```

![sample4](./docs/sample4.jpg)

當設定的尺寸小於文字圖像的尺寸時，會自動縮放文字圖像。

也就是說，文字會擠在一起，變成瘦瘦地長方形，例如：

```python
text = '你好' * 10
gen = WordCanvas(output_size=(64, 512))  # 高度 64，寬度 512
img, infos = gen(text)
```

![sample8](./docs/sample8.jpg)

### 調整背景顏色

使用 `background_color` 參數可以調整背景顏色。

```python
gen = WordCanvas(background_color=(255, 0, 0)) # 藍色背景
img, infos = gen(text)
```

![sample2](./docs/sample2.jpg)

### 調整文字顏色

使用 `text_color` 參數可以調整文字顏色。

```python
gen = WordCanvas(text_color=(0, 255, 0)) # 綠色文字
img, infos = gen(text)
```

![sample3](./docs/sample3.jpg)

### 調整文字對齊

使用 `align_mode` 參數可以調整文字對齊模式。

```python
from wordcanvas import AlignMode, WordCanvas

gen = WordCanvas(
    output_size=(64, 1024),
    align_mode=AlignMode.Center
)

text = '你好！ Hello, World!'
img, infos = gen(text)
```

- **中間對齊：`AlignMode.Center`**

  ![sample5](./docs/sample5.jpg)

- **靠右對齊：`AlignMode.Right`**

  ![sample6](./docs/sample6.jpg)

- **靠左對齊：`AlignMode.Left`**

  ![sample7](./docs/sample4.jpg)

- **分散對齊：`AlignMode.Scatter`**

  ![sample8](./docs/sample7.jpg)

### 調整文字方向

使用 `direction` 參數可以調整文字方向。

- **輸出橫向文字**

  ```python
  text = '你好！'
  gen = WordCanvas(direction='ltr') # 從右到左的橫向文字
  img, infos = gen(text)
  ```

  ![sample9](./docs/sample9.jpg)

- **輸出直向文字**

  ```python
  text = '你好！'
  gen = WordCanvas(direction='ttb') # 從上到下的直向文字
  img, infos = gen(text)
  ```

  ![sample10](./docs/sample10.jpg)

- **輸出直向文字且分散對齊**

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

### 調整輸出方向

使用 `output_direction` 參數可以調整輸出方向。

- **直向文字，水平輸出**

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

- **橫向文字，垂直輸出**

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

### 壓扁文字

有些場景的文字會特別扁，這時候可以使用 `text_aspect_ratio` 參數。

```python
gen = WordCanvas(
    text_aspect_ratio=0.25, # 文字高度 / 文字寬度 = 1/4
    output_size=(32, 1024),
)  # 壓扁文字

text="壓扁測試"
img, infos = gen(text)
```

![sample16](./docs/sample16.jpg)

### 儀表板

基礎功能大致上就是這樣。

最後我們介紹一下儀表板的功能。

```python
gen = WordCanvas()
print(gen)
```

你也可以不需要 `print`，直接輸出就好，因為我們有實作 `__repr__` 方法。

輸出後可以看到一個簡單的儀表板。

![dashboard](./docs/dashboard.jpg)

你可以看到：

- 第一個 column 是 Property，是所有的設定參數。
- 第二個 column 是 Current Value，是參數「此時此刻」的值。
- 第三個 column 是 SetMethod，是參數的設定方法。寫著 `set` 的參數，可以直接指定修改；寫著 `reinit` 的參數，則是需要重新初始化 `WordCanvas` 物件。
- 第四個 column 是 DType，是參數的資料型態。
- 第五個 column 是 Description，是參數的描述。

沒錯，參數大部分可以直接設定，這表示當你需要修改輸出特性時，不需要重新建立一個 `WordCanvas` 物件，只需要直接設定即可。會需要使用 `reinit` 的參數，通常是涉及到字型格式的初始化，例如文字高度 `text_size` 之類的。所以請注意，不是所有的參數都可以直接設定。

```python
gen.output_size = (64, 1024)
gen.text_color = (0, 255, 0)
gen.align_mode = AlignMode.Center
gen.direction = 'ltr'
gen.output_direction = OutputDirection.Horizontal
```

設定完之後，直接調用，就可以得到新的文字圖像。

如果你設定了 `reinit` 相關的參數，那你會收到錯誤：

- **AttributeError: can't set attribute**

  ```python
  gen.text_size = 128
  # >>> AttributeError: can't set attribute
  ```

## 小結

還有許多功能沒有提到，但是基本功能已經介紹完畢。

以上就是本專案的基本使用方法，更多詳細資訊和使用方法，請直接查閱 [**WordCanvas Documents**](https://docsaid.org/docs/wordcanvas/intro/)。

## 引用

如果你認為我們的工作對你有幫助，請引用以下內容：

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
