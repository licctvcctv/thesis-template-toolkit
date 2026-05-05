from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "images"
DATA_DIR = Path("/Users/a136/vs/45425/郑州论文新要求/白日梦/work/data/processed_data")

CATEGORIES = [
    ("angry", "愤怒"),
    ("disgust", "厌恶"),
    ("fear", "恐惧"),
    ("happy", "高兴"),
    ("neutral", "中性"),
    ("sad", "悲伤"),
    ("surprise", "惊讶"),
]

COLORS = {
    "angry": "#d95f5f",
    "disgust": "#7aa66a",
    "fear": "#7b6fb1",
    "happy": "#e3a844",
    "neutral": "#6f8fb7",
    "sad": "#5f79b5",
    "surprise": "#d58562",
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size, index=1 if bold and candidate.endswith(".ttc") else 0)
    return ImageFont.load_default()


FONT_TITLE = font(24, True)
FONT_LABEL = font(18, True)
FONT_SMALL = font(14)
FONT_TINY = font(12)


def list_images(category):
    paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
        paths.extend((DATA_DIR / category).glob(ext))
    return sorted(paths)


def fit_square(path, size):
    im = Image.open(path).convert("RGB")
    im = ImageOps.exif_transpose(im)
    im.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), "#f7f9fc")
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas


def rounded_rect(draw, xy, fill, outline=None, width=1, radius=12):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_dataset_samples():
    random.seed(42)
    cell = 132
    gap = 14
    label_w = 138
    top = 36
    left = 28
    rows = len(CATEGORIES)
    cols = 6
    width = left * 2 + label_w + cols * cell + (cols - 1) * gap
    height = top * 2 + rows * cell + (rows - 1) * gap
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    for r, (cat, zh) in enumerate(CATEGORIES):
        y = top + r * (cell + gap)
        color = COLORS[cat]
        rounded_rect(draw, (left, y, left + label_w - 14, y + cell), "#f4f7fb", color, 2, 12)
        draw.text((left + 16, y + 32), zh, font=FONT_LABEL, fill="#172033")
        draw.text((left + 16, y + 64), cat, font=FONT_SMALL, fill="#526070")
        samples = list_images(cat)
        chosen = random.sample(samples, min(cols, len(samples)))
        for c, path in enumerate(chosen):
            x = left + label_w + c * (cell + gap)
            thumb = fit_square(path, cell - 10)
            rounded_rect(draw, (x, y, x + cell, y + cell), "#ffffff", "#d7dee8", 1, 10)
            canvas.paste(thumb, (x + 5, y + 5))
    canvas.save(IMG_DIR / "fig3-1-dataset-samples-rich.png", quality=95)


def letterbox(im, size=180, fill="#edf2f7"):
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), fill)
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas


def center_crop(im, size):
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return im.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)


def draw_resize_compare():
    random.seed(12)
    sample_paths = [
        random.choice(list_images("happy")),
        random.choice(list_images("sad")),
        random.choice(list_images("surprise")),
        random.choice(list_images("neutral")),
    ]
    row_h = 220
    col_w = 230
    left = 36
    top = 60
    width = left * 2 + col_w * 4
    height = top + row_h * len(sample_paths) + 40
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    headers = ["原始样本", "比例缩放", "填充到640输入", "中心裁剪对比"]
    for i, h in enumerate(headers):
        draw.text((left + i * col_w + 38, 20), h, font=FONT_LABEL, fill="#182334")
    for r, path in enumerate(sample_paths):
        y = top + r * row_h
        base = Image.open(path).convert("RGB")
        versions = [
            fit_square(path, 180),
            letterbox(base.copy(), 180),
            ImageOps.contain(base.copy(), (180, 180), Image.LANCZOS),
            center_crop(base.copy(), 180),
        ]
        for c, im in enumerate(versions):
            x = left + c * col_w
            rounded_rect(draw, (x, y, x + 194, y + 194), "#ffffff", "#d7dee8", 1, 10)
            if c == 2:
                tmp = Image.new("RGB", (180, 180), "#edf2f7")
                im.thumbnail((154, 154), Image.LANCZOS)
                tmp.paste(im, ((180 - im.width) // 2, (180 - im.height) // 2))
                im = tmp
            canvas.paste(im, (x + 7, y + 7))
            if c == 2:
                draw.rectangle((x + 27, y + 27, x + 167, y + 167), outline="#2f6fb0", width=2)
                draw.text((x + 58, y + 170), "640×640", font=FONT_TINY, fill="#2f6fb0")
        draw.text((left, y + 198), f"{path.parent.name} 样本尺寸处理对比", font=FONT_SMALL, fill="#526070")
    canvas.save(IMG_DIR / "fig3-4-resize-compare-rich.png", quality=95)


def adjust_brightness(im, factor):
    return ImageEnhance.Brightness(im).enhance(factor)


def color_jitter(im):
    im = ImageEnhance.Color(im).enhance(1.35)
    return ImageEnhance.Contrast(im).enhance(1.12)


def shift_image(im, dx=14, dy=-10):
    shifted = Image.new("RGB", im.size, "#edf2f7")
    shifted.paste(im, (dx, dy))
    return shifted


def mosaic(paths, size=150):
    canvas = Image.new("RGB", (size, size), "white")
    half = size // 2
    for i, path in enumerate(paths[:4]):
        im = fit_square(path, half)
        canvas.paste(im, ((i % 2) * half, (i // 2) * half))
    return canvas


def draw_augmentation_compare():
    random.seed(21)
    base_paths = [
        random.choice(list_images("angry")),
        random.choice(list_images("happy")),
        random.choice(list_images("fear")),
        random.choice(list_images("surprise")),
    ]
    labels = ["原图", "水平翻转", "亮度扰动", "轻微旋转", "平移缩放", "颜色扰动", "Mosaic"]
    thumb = 136
    gap = 12
    left = 34
    top = 70
    label_h = 32
    row_h = thumb + label_h + 20
    width = left * 2 + len(labels) * thumb + (len(labels) - 1) * gap
    height = top + len(base_paths) * row_h + 34
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    for i, text in enumerate(labels):
        draw.text((left + i * (thumb + gap) + 34, 24), text, font=FONT_SMALL, fill="#172033")

    for r, path in enumerate(base_paths):
        y = top + r * row_h
        base = fit_square(path, thumb)
        variants = [
            base,
            ImageOps.mirror(base),
            adjust_brightness(base, 1.28),
            base.rotate(7, resample=Image.BICUBIC, fillcolor="#edf2f7"),
            shift_image(base.resize((122, 122), Image.LANCZOS), 8, 8).resize((thumb, thumb), Image.LANCZOS),
            color_jitter(base),
            mosaic([
                path,
                random.choice(list_images("sad")),
                random.choice(list_images("neutral")),
                random.choice(list_images("disgust")),
            ], thumb),
        ]
        for c, im in enumerate(variants):
            x = left + c * (thumb + gap)
            rounded_rect(draw, (x - 3, y - 3, x + thumb + 3, y + thumb + 3), "#ffffff", "#d7dee8", 1, 10)
            canvas.paste(im, (x, y))
        draw.text((left, y + thumb + 8), f"{path.parent.name} 样本增强对比", font=FONT_SMALL, fill="#526070")
    canvas.save(IMG_DIR / "fig3-6-augmentation-compare-rich.png", quality=95)


if __name__ == "__main__":
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    draw_dataset_samples()
    draw_resize_compare()
    draw_augmentation_compare()
    print("generated rich chapter 3 figures")
