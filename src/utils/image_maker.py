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
    # 背景全体は完全に透過
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
    total_text: str,
    text_color: str = "#FFFFFF",
    frame_color: str = "#FF5722",
    bg_color: str = "#000000CC",
    frame_width: int = 8,
    corner_radius: int = 30,
    width: int = 600,
) -> bytes:
    """
    Palmuの7日間のスケジュールとポイントを描画したカレンダー画像を生成します。
    """
    # 行の高さなどを設定
    title_height = 80
    row_height = 50
    footer_height = 80
    padding_top = 30
    padding_bottom = 30

    # 画像全体の高さを計算
    height = padding_top + title_height + (len(schedule_data) * row_height) + footer_height + padding_bottom

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
        footer_font = ImageFont.truetype(str(FONT_PATH), 36)
    except OSError:
        title_font = ImageFont.load_default()  # type: ignore
        row_font = ImageFont.load_default()  # type: ignore
        footer_font = ImageFont.load_default()  # type: ignore

    text_rgba = hex_to_rgba(text_color)

    # 1. タイトルの描画
    bbox = draw.textbbox((0, 0), title, font=title_font)
    t_w = bbox[2] - bbox[0]
    t_h = bbox[3] - bbox[1]
    t_x = (width - t_w) / 2
    t_y = padding_top + (title_height - t_h) / 2 - bbox[1]
    draw.text((t_x, t_y), title, fill=text_rgba, font=title_font)

    # 2. 区切り線 (タイトルの下)
    line_y = padding_top + title_height
    draw.line([(width * 0.1, line_y), (width * 0.9, line_y)], fill=text_rgba, width=2)

    # 3. スケジュール行の描画
    current_y = line_y + 10
    for date_str, point_str in schedule_data:
        # 日付 (左側)
        d_bbox = draw.textbbox((0, 0), date_str, font=row_font)
        d_y = current_y + (row_height - (d_bbox[3] - d_bbox[1])) / 2 - d_bbox[1]
        draw.text((width * 0.15, d_y), date_str, fill=text_rgba, font=row_font)

        # ポイント (右側)
        p_bbox = draw.textbbox((0, 0), point_str, font=row_font)
        p_w = p_bbox[2] - p_bbox[0]
        p_y = current_y + (row_height - (p_bbox[3] - p_bbox[1])) / 2 - p_bbox[1]
        draw.text((width * 0.85 - p_w, p_y), point_str, fill=text_rgba, font=row_font)

        current_y += row_height

    # 4. 区切り線 (フッターの上)
    line2_y = current_y + 10
    draw.line([(width * 0.1, line2_y), (width * 0.9, line2_y)], fill=text_rgba, width=2)

    # 5. フッター (合計) の描画
    f_bbox = draw.textbbox((0, 0), total_text, font=footer_font)
    f_w = f_bbox[2] - f_bbox[0]
    f_h = f_bbox[3] - f_bbox[1]
    f_x = (width - f_w) / 2
    f_y = line2_y + (footer_height - f_h) / 2 - f_bbox[1]
    draw.text((f_x, f_y), total_text, fill=text_rgba, font=footer_font)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
