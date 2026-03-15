import json
import time
from collections.abc import Callable
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
        html = f"<div style='text-align: center; background-color: #1a1c23; border-radius: 16px; padding: 20px; margin-bottom: 10px;'>{display_dice_html(temp_dice, size)}</div>"
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
        <h3 style='margin-top:0; color:#ff4b4b; font-size:18px;'>⚡ 開発者にエナドリを奢る (PayPay)</h3>
        <p style='margin-bottom:15px; font-size:14px; color:#555;'>
            PayPayで開発者にエナジードリンクを奢って、さらに開発を加速させましょう！
        </p>
        <a href='{paypay_url}' target='_blank' style='text-decoration:none;'>
            <div style='background-color:#ff4b4b; color:white; padding:10px 24px; border-radius:30px; font-weight:bold; font-size:16px; box-shadow: 0 4px 10px rgba(255,75,75,0.3); display:inline-block; transition: transform 0.2s;'>
                PayPayでエナドリを差し入れる 🚀
            </div>
        </a>
    </div>
    """
    if is_sidebar:
        target.write("---")

    target.markdown(html, unsafe_allow_html=True)


def render_storage_controls(
    storage: Any,
    storage_key: str,
    current_data: Any,
    on_load_callback: Callable[[Any], None],
    on_save_callback: Callable[[], None] | None = None,
    file_prefix: str = "config",
    is_pydantic: bool = False,
) -> None:
    """
    LocalStorage への保存、JSON出力、JSON読み込みを行う共通UIをレンダリングします。
    """
    st.write("---")
    with st.container(border=True):
        st.subheader("📁 データの管理")
        col_save, col_export, col_import = st.columns([1.5, 1, 1])

        with col_save:
            if st.button("💾 ブラウザに保存", use_container_width=True, type="primary"):
                try:
                    data_to_save = current_data.model_dump() if is_pydantic else current_data
                    storage.set_item(storage_key, data_to_save)
                    if on_save_callback:
                        on_save_callback()
                    st.success("ブラウザに保存しました！")
                    st.toast("設定を保存しました 💾")
                except Exception as e:
                    st.error(f"保存失敗: {e}")

        with col_export:
            try:
                data_to_export = current_data.model_dump() if is_pydantic else current_data
                json_str = json.dumps(data_to_export, indent=2, ensure_ascii=False)
                # ファイル名は現在時刻を付与
                from datetime import datetime

                filename = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.download_button("📥 JSON保存", json_str, filename, "application/json", use_container_width=True)
            except Exception as e:
                st.error(f"エクスポート失敗: {e}")

        with col_import:
            uploaded_file = st.file_uploader("📤 JSON読込", type="json", label_visibility="collapsed")
            if uploaded_file:
                if st.button("反映実行", use_container_width=True, key=f"import_btn_{storage_key}"):
                    try:
                        data = json.load(uploaded_file)
                        on_load_callback(data)
                        st.success("読み込みました！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"読込失敗: {e}")


def wait_for_storage_load(storage: Any, storage_key: str, initialized_key: str) -> Any:
    """
    LocalStorage からのデータ読み込みを待ちます。
    読み込みが完了していない場合は st.stop() で処理を中断します。
    """
    if initialized_key not in st.session_state:
        saved_data = storage.get_item(storage_key, is_json=True)
        if saved_data is not None:
            # 取得できた（nullでなければOK。空リストなどはデータありとみなす）
            st.session_state[initialized_key] = True
            return saved_data
        else:
            # まだロード中（コンポーネントが準備できていない）
            st.info("データを読み込み中...")
            # 読み込みに失敗し続ける場合の回避策として、強制的にデフォルトで開始するボタンを出す
            if st.button("読み込みをスキップして新規作成"):
                st.session_state[initialized_key] = True
                st.rerun()
            st.stop()
    return None
