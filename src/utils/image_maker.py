from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path("src/assets/NotoSansJP-Bold.otf")


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

    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except OSError:
        font = ImageFont.load_default()  # type: ignore

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
    schedule_data: list[tuple[str, str]],
    text_color: str = "#FFFFFF",
    frame_color: str = "#FF5722",
    bg_color: str = "#000000CC",
    frame_width: int = 8,
    corner_radius: int = 30,
    width: int = 600,
) -> bytes:
    """
    Palmuのスケジュールを描画したリスト形式の画像を生成します。
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

    try:
        title_font = ImageFont.truetype(str(FONT_PATH), 40)
        row_font = ImageFont.truetype(str(FONT_PATH), 30)
    except OSError:
        title_font = ImageFont.load_default()  # type: ignore
        row_font = ImageFont.load_default()  # type: ignore

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
    for date_str, point_str in schedule_data:
        d_bbox = draw.textbbox((0, 0), date_str, font=row_font)
        d_y = current_y + (row_height - (d_bbox[3] - d_bbox[1])) / 2 - d_bbox[1]
        draw.text((width * 0.15, d_y), date_str, fill=text_rgba, font=row_font)

        p_bbox = draw.textbbox((0, 0), point_str, font=row_font)
        p_w = p_bbox[2] - p_bbox[0]
        p_y = current_y + (row_height - (p_bbox[3] - p_bbox[1])) / 2 - p_bbox[1]
        draw.text((width * 0.85 - p_w, p_y), point_str, fill=text_rgba, font=row_font)
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
) -> bytes:
    """
    Palmuの月間スケジュールを7列のグリッド形式（カレンダー風）で描画した画像を生成します。
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
    fill = hex_to_rgba(bg_color)
    text_rgba = hex_to_rgba(text_color)

    # 背景と外枠
    draw.rounded_rectangle(
        [(10, 10), (width - 11, height - 11)],
        radius=30,
        outline=outline,
        width=8,
        fill=fill,
    )

    try:
        title_font = ImageFont.truetype(str(FONT_PATH), 50)
        date_font = ImageFont.truetype(str(FONT_PATH), 24)
        point_font = ImageFont.truetype(str(FONT_PATH), 28)
    except OSError:
        title_font = ImageFont.load_default()  # type: ignore
        date_font = ImageFont.load_default()  # type: ignore
        point_font = ImageFont.load_default()  # type: ignore

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

        # セルの枠
        draw.rectangle([(x, y), (x + cell_size, y + cell_size)], outline=outline, width=2)

        # 日付 (左上)
        date_text = item.get("date", "")
        draw.text((x + 8, y + 8), date_text, fill=text_rgba, font=date_font)

        # 曜日 (日付の横)
        day_text = item.get("day", "")
        draw.text(
            (x + 40, y + 10),
            f"({day_text})",
            fill=text_rgba,
            font=ImageFont.truetype(str(FONT_PATH), 18) if isinstance(date_font, ImageFont.FreeTypeFont) else date_font,
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
