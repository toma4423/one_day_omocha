import time
from typing import Any

import streamlit as st

from src.utils.dice import DICE_EMOJI, roll_dice


def render_page_header() -> None:
    """
    全ページ共通のグローバル CSS を読み込み、デザインを統一します。
    """
    try:
        with open("src/assets/global_style.css", encoding="utf-8") as f:
            global_css = f.read()
        st.markdown(f"<style>{global_css}</style>", unsafe_allow_html=True)
    except Exception:
        pass


def display_dice_html(dice: list[int], size: int = 100) -> str:
    """
    サイコロの絵文字を含むHTMLを生成します。
    """
    return "".join(
        [f"<span style='font-size: {size}px; margin: 0 10px;'>{DICE_EMOJI.get(d, '?')}</span>" for d in dice]
    )


def render_dice_animation(placeholder: Any, size: int = 100, iterations: int = 10) -> None:
    """
    サイコロが振られるアニメーションを表示します。
    """
    for _ in range(iterations):
        temp_dice = roll_dice(3)
        html = f"<div style='text-align: center;'>{display_dice_html(temp_dice, size)}</div>"
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.05)


def render_grid_board(total_items: int, cols_per_row: int, renderer_func: Any) -> None:
    """
    グリッド状の盤面をレンダリングします。
    """
    for i in range(0, total_items, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < total_items:
                with col:
                    renderer_func(idx)


def render_styled_number(
    label: str,
    value: float | int,
    bg_color: str = "#E3F2FD",
    border_color: str = "#2196F3",
    text_color: str = "#0D47A1",
    font_size: int = 48,
) -> None:
    """
    スタイル付きの大きな数字をレンダリングします。
    """
    st.markdown(
        f"""
        <div style='background-color:{bg_color}; padding:20px; border-radius:16px; text-align:center; margin-bottom:20px; border:1px solid {border_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>
            <span style='font-size:18px; font-weight:700; color:{text_color}; opacity: 0.8;'>{label}</span>
            <div style='font-size:{font_size}px; font-weight:900; color:{text_color}; line-height:1.2;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_box(
    title: str,
    value: float | int,
    bg_color: str = "#2196F3",
    border_color: str = "#0D47A1",
    text_color: str = "white",
    font_size: int = 48,
) -> None:
    """
    結果表示用のボックスをレンダリングします。
    """
    st.markdown(f"### {title}")
    st.markdown(
        f"""
        <div style='background-color:{bg_color}; padding:20px; border-radius:16px; text-align:center; font-size:{font_size}px; font-weight:900; color:{text_color}; box-shadow: 0 8px 24px rgba(0,0,0,0.12);'>
            {value}
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_global_styles() -> None:
    """
    (Deprecated) 代わりに render_page_header() を使用してください。
    """
    render_page_header()


def render_donation_box(paypay_url: str, is_sidebar: bool = False) -> None:
    """
    開発を応援するための募金箱をレンダリングします。
    """
    target = st.sidebar if is_sidebar else st

    html = f"""
    <div style='background-color:#fff3f3; padding:20px; border-radius:16px; border:1px dashed #ff4b4b; text-align:center; margin: 20px 0;'>
        <h3 style='margin-top:0; color:#ff4b4b; font-size:18px;'>🎁 開発を応援する</h3>
        <p style='margin-bottom:15px; font-size:14px; color:#555;'>
            このアプリが役に立ったら、開発を支援していただけると嬉しいです！
        </p>
        <a href='{paypay_url}' target='_blank' style='text-decoration:none;'>
            <div style='background-color:#ff4b4b; color:white; padding:10px 24px; border-radius:30px; font-weight:bold; font-size:16px; box-shadow: 0 4px 10px rgba(255,75,75,0.3); display:inline-block; transition: transform 0.2s;'>
                PayPayで送る 💸
            </div>
        </a>
    </div>
    """
    if is_sidebar:
        target.write("---")

    target.markdown(html, unsafe_allow_html=True)
