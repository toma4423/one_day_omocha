from io import BytesIO
from typing import Literal

from PIL import Image, ImageOps
from pydantic import BaseModel, Field


class ImageProcessParams(BaseModel):
    """画像処理のパラメータを管理するモデル"""

    aspect_ratio_x: float = Field(default=1.0, gt=0)
    aspect_ratio_y: float = Field(default=1.0, gt=0)
    scale: float = Field(default=1.0, gt=0)
    offset_x: float = 0.5  # 0.0 to 1.0 (center position)
    offset_y: float = 0.5  # 0.0 to 1.0 (center position)
    target_width: int | None = Field(default=None, gt=0)
    target_height: int | None = Field(default=None, gt=0)
    output_format: Literal["PNG", "JPEG"] = "PNG"


def load_image_with_orientation(image_bytes: bytes) -> Image.Image:
    """
    画像を読み込み、EXIF情報に基づいて回転を補正します。
    """
    img_raw = Image.open(BytesIO(image_bytes))
    # EXIF情報に基づいて回転を補正 (iPhone/Android 対策)
    img_fixed = ImageOps.exif_transpose(img_raw)
    return img_fixed.convert("RGBA")


def process_image(img: Image.Image, params: ImageProcessParams) -> bytes:
    """
    指定されたパラメータに従って画像を加工します。
    """
    img_w, img_h = img.size
    target_ratio = params.aspect_ratio_x / params.aspect_ratio_y

    # 現在の画像のアスペクト比
    current_ratio = img_w / img_h

    crop_w: float
    crop_h: float

    if current_ratio > target_ratio:
        # 画像の方が横長い -> 高さを基準に幅を決定
        crop_h = float(img_h)
        crop_w = float(img_h * target_ratio)
    else:
        # 画像の方が縦長い -> 幅を基準に高さを決定
        crop_w = float(img_w)
        crop_h = float(img_w / target_ratio)

    # スケーリング (zoom)
    # scale=1.0 で最大範囲、scale > 1.0 で拡大 (クロップ範囲を小さくする)
    crop_w /= params.scale
    crop_h /= params.scale

    # クロップ範囲の計算 (offset_x/y は中心点の位置 0.0~1.0)
    # 中心点の座標
    center_x = img_w * params.offset_x
    center_y = img_h * params.offset_y

    left = center_x - crop_w / 2
    top = center_y - crop_h / 2
    right = center_x + crop_w / 2
    bottom = center_y + crop_h / 2

    # 画像の範囲外に出ないように調整（余裕があれば）
    # 今回はシンプルに切り抜く
    cropped_img = img.crop((int(left), int(top), int(right), int(bottom)))

    # リサイズ
    if params.target_width and params.target_height:
        final_img = cropped_img.resize((params.target_width, params.target_height), Image.Resampling.LANCZOS)
    elif params.target_width:
        h = int(params.target_width / target_ratio)
        final_img = cropped_img.resize((params.target_width, h), Image.Resampling.LANCZOS)
    elif params.target_height:
        w = int(params.target_height * target_ratio)
        final_img = cropped_img.resize((w, params.target_height), Image.Resampling.LANCZOS)
    else:
        final_img = cropped_img

    # 出力
    buf = BytesIO()
    if params.output_format == "JPEG":
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
    else:
        final_img.save(buf, format="PNG")

    return buf.getvalue()
