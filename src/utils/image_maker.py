import os
import urllib.request
import ssl
from io import BytesIO
from pathlib import Path
from typing import Any, Dict

from PIL import Image, ImageDraw, ImageFont

# 実行環境に合わせてベースディレクトリを特定
BASE_DIR = Path(__file__).parent.parent.parent
FONT_DIR = BASE_DIR / "src" / "assets"
CACHE_DIR = Path("/tmp/one_day_omocha_fonts") if not FONT_DIR.exists() or not os.access(FONT_DIR, os.W_OK) else FONT_DIR

# メモリ上のキャッシュ
_font_cache: Dict[str, Any] = {}

# フォントの配布元URL定義 (GitHub Raw または Google Fonts 直接)
FONT_URLS = {
    "NotoSansJP-Bold.otf": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansJP-Bold.otf",
    "NotoSerifJP-Bold.otf": "https://github.com/googlefonts/noto-cjk/raw/main/Serif/OTF/Japanese/NotoSerifJP-Bold.otf",
    "Mplus1-Bold.ttf": "https://github.com/googlefonts/mplus-fonts/raw/main/fonts/ttf/Mplus1-Bold.ttf",
    "HachiMaruPop-Regular.ttf": "https://github.com/googlefonts/hachimarupop/raw/main/fonts/ttf/HachiMaruPop-Regular.ttf",
    "YuseiMagic-Regular.ttf": "https://github.com/googlefonts/yuseimagic/raw/main/fonts/ttf/YuseiMagic-Regular.ttf",
    "DotGothic16-Regular.ttf": "https://github.com/googlefonts/dotgothic16/raw/main/fonts/ttf/DotGothic16-Regular.ttf",
    "DelaGothicOne-Regular.ttf": "https://github.com/googlefonts/delagothicone/raw/main/fonts/ttf/DelaGothicOne-Regular.ttf",
    "KaiseiTokumin-Bold.ttf": "https://github.com/googlefonts/kaiseitokumin/raw/main/fonts/ttf/KaiseiTokumin-Bold.ttf",
    "Stick-Regular.ttf": "https://github.com/googlefonts/stick/raw/main/fonts/ttf/Stick-Regular.ttf",
}


def download_font(filename: str) -> bool:
    """指定されたフォントファイルをダウンロードします。"""
    url = FONT_URLS.get(filename)
    if not url:
        return False
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        target_path = CACHE_DIR / filename
        
        # User-Agent を設定してブロックを回避
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        req = urllib.request.Request(url, headers=headers)
        
        # SSL証明書のエラーを無視する設定（環境によって必要）
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=context) as response:
            data = response.read()
            if len(data) < 1000:  # ファイルが小さすぎる場合は失敗とみなす
                return False
            with open(target_path, "wb") as out_file:
                out_file.write(data)
        return True
    except Exception:
        return False


def get_available_fonts() -> dict[str, str]:
    """
    利用可能なフォントの表示名とファイル名の辞書を返します。
    """
    presets = {
        "NotoSansJP-Bold.otf": "ゴシック (標準)",
        "NotoSerifJP-Bold.otf": "明朝 (標準)",
        "Mplus1-Bold.ttf": "モダンゴシック",
        "HachiMaruPop-Regular.ttf": "ポップ (手書き風)",
        "YuseiMagic-Regular.ttf": "手書き (マジック風)",
        "DotGothic16-Regular.ttf": "レトロ (ドット風)",
        "DelaGothicOne-Regular.ttf": "力強い (インパクト)",
        "KaiseiTokumin-Bold.ttf": "和風 (懐風明朝)",
        "Stick-Regular.ttf": "デザイン (スティック)",
    }

    fonts = {}
    # プリセットは存在に関わらずすべて選択肢に出す
    for filename, display_name in presets.items():
        fonts[display_name] = filename

    # プリセットにない既存ファイルも追加 (FONT_DIR と CACHE_DIR の両方をスキャン)
    for d in [FONT_DIR, CACHE_DIR]:
        if d.exists():
            for ext in [".otf", ".ttf", ".ttc"]:
                for f in d.glob(f"*{ext}"):
                    if f.name not in presets:
                        fonts[f.stem] = f.name

    return fonts


def get_font(font_name: str, size: int) -> Any:
    """指定されたフォント名とサイズで ImageFont を返します。"""
    cache_key = f"{font_name}_{size}"
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    available_fonts = get_available_fonts()
    font_file = available_fonts.get(font_name, "NotoSansJP-Bold.otf")
    
    # 複数のパス候補を試す
    paths = [FONT_DIR / font_file, CACHE_DIR / font_file]
    font_path = None
    for p in paths:
        if p.exists():
            font_path = p
            break
            
    # ファイルがない場合はダウンロードを試みる
    if font_path is None:
        if download_font(font_file):
            font_path = CACHE_DIR / font_file

    try:
        if font_path and font_path.exists():
            f = ImageFont.truetype(str(font_path), size)
            _font_cache[cache_key] = f
            return f
    except OSError:
        pass

    # フォールバック: 標準フォント
    fallback_key = f"NotoSansJP-Bold.otf_{size}"
    if fallback_key in _font_cache:
        return _font_cache[fallback_key]
        
    fallback_paths = [FONT_DIR / "NotoSansJP-Bold.otf", CACHE_DIR / "NotoSansJP-Bold.otf"]
    for p in fallback_paths:
        if p.exists():
            try:
                f = ImageFont.truetype(str(p), size)
                _font_cache[fallback_key] = f
                return f
            except OSError:
                continue

    # 最終手段
    f = ImageFont.load_default()
    return f


def hex_to_rgba(hex_str: str) -> tuple[int, int, int, int]:
    """16進数のカラーコードをRGBAタプルに変換します。"""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 6:
        r, g, b = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
        return r, g, b, 255
    elif len(hex_str) == 8:
        r, g, b, a = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4, 6))
        return r, g, b, a
    return 0, 0, 0, 0


def create_badge_image(
    text: str,
    text_color: str = "#FFFFFF",
    frame_color: str = "#FF5722",
    bg_color: str = "#00000000",
    frame_width: int = 8,
    corner_radius: int = 30,
    width: int = 400,
    height: int = 150,
    font_size: int = 60,
    font_name: str = "ゴシック",
) -> bytes:
    """
    指定されたパラメータで透過背景のバッジ画像を生成します。
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    outline = hex_to_rgba(frame_color) if frame_width > 0 else None
    fill = hex_to_rgba(bg_color)

    pad = frame_width // 2 if frame_width > 0 else 0
    draw.rounded_rectangle(
        [(pad, pad), (width - pad - 1, height - pad - 1)],
        radius=corner_radius,
        outline=outline,
        width=frame_width,
        fill=fill,
    )

    font = get_font(font_name, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) / 2
    y = (height - text_h) / 2 - bbox[1]

    draw.text((x, y), text, fill=hex_to_rgba(text_color), font=font)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_palmu_schedule_image(
    title: str,
    schedule_data: list[tuple[str, str, str]],
    text_color: str = "#FFFFFF",
    frame_color: str = "#FF5722",
    bg_color: str = "#000000CC",
    frame_width: int = 8,
    corner_radius: int = 30,
    width: int = 600,
    font_name: str = "ゴシック",
) -> bytes:
    """
    Palmuのスケジュールを描画したリスト形式の画像を生成します。
    schedule_data: [(日付, 予定テキスト, ポイント), ...]
    """
    title_height = 80
    row_height = 50
    padding_top = 30
    padding_bottom = 30

    height = padding_top + title_height + (len(schedule_data) * row_height) + padding_bottom

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    outline = hex_to_rgba(frame_color) if frame_width > 0 else None
    fill = hex_to_rgba(bg_color)

    pad = frame_width // 2 if frame_width > 0 else 0
    draw.rounded_rectangle(
        [(pad, pad), (width - pad - 1, height - pad - 1)],
        radius=corner_radius,
        outline=outline,
        width=frame_width,
        fill=fill,
    )

    title_font = get_font(font_name, 40)
    row_font = get_font(font_name, 30)
    plan_font = get_font(font_name, 24)

    text_rgba = hex_to_rgba(text_color)

    bbox = draw.textbbox((0, 0), title, font=title_font)
    t_w = bbox[2] - bbox[0]
    t_h = bbox[3] - bbox[1]
    t_x = (width - t_w) / 2
    t_y = padding_top + (title_height - t_h) / 2 - bbox[1]
    draw.text((t_x, t_y), title, fill=text_rgba, font=title_font)

    line_y = padding_top + title_height
    draw.line([(width * 0.1, line_y), (width * 0.9, line_y)], fill=text_rgba, width=2)

    current_y = line_y + 10
    for date_str, plan_text, point_str in schedule_data:
        # 日付 (左側)
        d_bbox = draw.textbbox((0, 0), date_str, font=row_font)
        d_y = current_y + (row_height - (d_bbox[3] - d_bbox[1])) / 2 - d_bbox[1]
        draw.text((width * 0.1, d_y), date_str, fill=text_rgba, font=row_font)

        # ポイント (右側)
        p_bbox = draw.textbbox((0, 0), point_str, font=row_font)
        p_w = p_bbox[2] - p_bbox[0]
        p_y = current_y + (row_height - (p_bbox[3] - p_bbox[1])) / 2 - p_bbox[1]
        draw.text((width * 0.9 - p_w, p_y), point_str, fill=text_rgba, font=row_font)

        # 予定テキスト (中央)
        if plan_text:
            pl_bbox = draw.textbbox((0, 0), plan_text, font=plan_font)
            pl_w = pl_bbox[2] - pl_bbox[0]
            pl_h = pl_bbox[3] - pl_bbox[1]

            # 日付の右端とポイントの左端の間で中央揃え
            center_x_start = width * 0.1 + (d_bbox[2] - d_bbox[0]) + 20
            center_x_end = width * 0.9 - p_w - 20

            if center_x_end > center_x_start:
                pl_x = center_x_start + (center_x_end - center_x_start - pl_w) / 2
                pl_y = current_y + (row_height - pl_h) / 2 - pl_bbox[1]
                draw.text((pl_x, pl_y), plan_text, fill=text_rgba, font=plan_font)

        current_y += row_height

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_palmu_calendar_grid_image(
    title: str,
    calendar_data: list[dict[str, str]],
    text_color: str = "#FFFFFF",
    frame_color: str = "#FF5722",
    bg_color: str = "#000000CC",
    width: int = 1000,
    cell_bg_colors: list[str] | None = None,
    font_name: str = "ゴシック",
) -> bytes:
    """
    Palmuの月間スケジュールを7列のグリッド形式（カレンダー風）で描画し た画像を生成します。
    """
    cols = 7
    rows = (len(calendar_data) + cols - 1) // cols

    # 1セルのサイズ
    cell_size = (width - 100) // cols
    title_height = 100
    padding = 50

    height = title_height + (rows * cell_size) + (padding * 2)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    outline = hex_to_rgba(frame_color)
    default_fill = hex_to_rgba(bg_color)
    text_rgba = hex_to_rgba(text_color)

    # 背景と外枠
    draw.rounded_rectangle(
        [(10, 10), (width - 11, height - 11)],
        radius=30,
        outline=outline,
        width=8,
        fill=default_fill,
    )

    title_font = get_font(font_name, 50)
    date_font = get_font(font_name, 24)
    point_font = get_font(font_name, 28)

    # タイトル
    bbox = draw.textbbox((0, 0), title, font=title_font)
    t_w = bbox[2] - bbox[0]
    t_y = padding + (title_height - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text(((width - t_w) / 2, t_y), title, fill=text_rgba, font=title_font)

    # グリッド描画
    start_y = padding + title_height
    start_x = (width - (cell_size * cols)) / 2

    for idx, item in enumerate(calendar_data):
        r = idx // cols
        c = idx % cols

        x = start_x + (c * cell_size)
        y = start_y + (r * cell_size)

        # セルの背景色（個別指定があればそれを使う）
        current_fill = default_fill
        if cell_bg_colors and idx < len(cell_bg_colors) and cell_bg_colors[idx]:
            current_fill = hex_to_rgba(cell_bg_colors[idx])

        if current_fill != default_fill:
            draw.rectangle([(x, y), (x + cell_size, y + cell_size)], fill=current_fill)

        # セルの枠
        draw.rectangle([(x, y), (x + cell_size, y + cell_size)], outline=outline, width=2)

        # 日付 (左上)
        date_text = item.get("date", "")
        if date_text:
            draw.text((x + 8, y + 8), date_text, fill=text_rgba, font=date_font)

            # 曜日 (日付の横)
            day_text = item.get("day", "")
            draw.text(
                (x + 40, y + 10),
                f"({day_text})",
                fill=text_rgba,
                font=get_font(font_name, 18)
                if isinstance(date_font, ImageFont.FreeTypeFont)
                else date_font,
            )

            # ポイント (中央)
            point_text = item.get("point", "")
            p_bbox = draw.textbbox((0, 0), point_text, font=point_font)
            p_w = p_bbox[2] - p_bbox[0]
            p_h = p_bbox[3] - p_bbox[1]

            # 中央に配置
            draw.text(
                (x + (cell_size - p_w) / 2, y + (cell_size - p_h) / 2 + 5 - p_bbox[1]),
                point_text,
                fill=text_rgba,
                font=point_font,
            )

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def composite_images(
    bg_bytes: bytes,
    fg_bytes: bytes,
    offset_x: int,
    offset_y: int,
    scale: float = 1.0,
    anchor: str = "左上",
) -> bytes:
    """
    背景画像の上に前景画像を合成します。
    anchor: "左上", "中央", "右上", "左下", "右下"
    """
    bg = Image.open(BytesIO(bg_bytes)).convert("RGBA")
    fg = Image.open(BytesIO(fg_bytes)).convert("RGBA")

    if scale != 1.0:
        new_w = int(fg.width * scale)
        new_h = int(fg.height * scale)
        if new_w > 0 and new_h > 0:
            fg = fg.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 基準点（アンカー）に基づく座標計算
    bg_w, bg_h = bg.size
    fg_w, fg_h = fg.size

    x, y = offset_x, offset_y

    if anchor == "中央":
        x = (bg_w - fg_w) // 2 + offset_x
        y = (bg_h - fg_h) // 2 + offset_y
    elif anchor == "右上":
        x = (bg_w - fg_w) - offset_x
        y = offset_y
    elif anchor == "左下":
        x = offset_x
        y = (bg_h - fg_h) - offset_y
    elif anchor == "右下":
        x = (bg_w - fg_w) - offset_x
        y = (bg_h - fg_h) - offset_y
    elif anchor == "中央左":
        x = offset_x
        y = (bg_h - fg_h) // 2 + offset_y
    elif anchor == "中央右":
        x = (bg_w - fg_w) - offset_x
        y = (bg_h - fg_h) // 2 + offset_y
    elif anchor == "中央上":
        x = (bg_w - fg_w) // 2 + offset_x
        y = offset_y
    elif anchor == "中央下":
        x = (bg_w - fg_w) // 2 + offset_x
        y = (bg_h - fg_h) - offset_y

    # 合成用のキャンバス（背景と同じサイズ）
    canvas = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    canvas.paste(fg, (x, y), fg)

    # アルファブレンドで合成
    result = Image.alpha_composite(bg, canvas)

    buf = BytesIO()
    result.save(buf, format="PNG")
    return buf.getvalue()
