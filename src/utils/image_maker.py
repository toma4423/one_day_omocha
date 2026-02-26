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

    # 枠線の太さが0の場合は枠線を描画しない
    outline = hex_to_rgba(frame_color) if frame_width > 0 else None
    fill = hex_to_rgba(bg_color)

    # 枠（角丸矩形）を描画
    # パディングを設けて枠線が切れないようにする
    pad = frame_width // 2 if frame_width > 0 else 0
    draw.rounded_rectangle(
        [(pad, pad), (width - pad - 1, height - pad - 1)],
        radius=corner_radius,
        outline=outline,
        width=frame_width,
        fill=fill,
    )

    # フォントの読み込み
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except OSError:
        # フォントファイルが見つからない場合はデフォルトフォント
        font = ImageFont.load_default()  # type: ignore

    # テキストを描画 (中央揃え)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) / 2
    # y座標はアセンダ/ディセンダを考慮した補正
    y = (height - text_h) / 2 - bbox[1]

    draw.text((x, y), text, fill=hex_to_rgba(text_color), font=font)

    # 画像をバイト列に変換
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
