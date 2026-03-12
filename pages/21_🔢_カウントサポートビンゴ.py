import json

import streamlit as st
from pydantic import BaseModel
from streamlit_local_storage import LocalStorage

from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now


# モデル定義
class BingoCell(BaseModel):
    label: str
    count: int = 0


class BingoBoard(BaseModel):
    rows: int = 5
    cols: int = 5
    cells: dict[str, BingoCell] = {}  # key: "r_c"

    def get_cell(self, r: int, c: int) -> BingoCell:
        key = f"{r}_{c}"
        if key not in self.cells:
            self.cells[key] = BingoCell(label=f"項目 {r + 1}-{c + 1}")
        return self.cells[key]


# ページの設定
st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 外部CSSの読み込み
try:
    with open("src/assets/counter/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# ビンゴ専用「超コンパクト」CSS
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    h1 { margin-top: -30px !important; margin-bottom: 0px !important; font-size: 1.8rem !important; }
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] { padding: 0px !important; gap: 2px !important; }
    div[data-testid="stElementContainer"] div.st-emotion-cache-16idsys, 
    div[data-testid="stElementContainer"] div.st-emotion-cache-1r6slb0 { padding: 4px !important; margin: 0px !important; }
    .stTextInput input { height: 24px !important; font-size: 11px !important; padding: 0 4px !important; margin-bottom: 2px !important; }
    .stNumberInput input { height: 32px !important; font-size: 20px !important; font-weight: 900 !important; padding: 0 !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label { display: none !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    hr { margin: 0.5rem 0 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>🔢 カウントサポートビンゴ</h1>", unsafe_allow_html=True)

storage = SafeStorage(LocalStorage())
DATA_KEY = "csb_data_v3"

# --- 初期化とデータ復元 ---
if "csb_board" not in st.session_state:
    saved = storage.get_item(DATA_KEY, is_json=True)
    if saved:
        st.session_state.csb_board = BingoBoard(**saved)
    else:
        st.session_state.csb_board = BingoBoard()

board: BingoBoard = st.session_state.csb_board


def save_to_storage():
    storage.set_item(DATA_KEY, board.model_dump())


# --- メイングリッド描画 ---
bingo_matrix = []

for r in range(board.rows):
    cols_ui = st.columns(board.cols)
    row_status = []
    for c in range(board.cols):
        cell = board.get_cell(r, c)
        is_active = cell.count > 0
        row_status.append(is_active)

        with cols_ui[c]:
            cell_class = "bingo-cell-active" if is_active else ""
            with st.container(border=True):
                st.markdown(f"<div id='cell-{r}-{c}' class='{cell_class}'>", unsafe_allow_html=True)

                new_label = st.text_input(
                    f"L{r}{c}", value=cell.label, key=f"lk_{r}_{c}", label_visibility="collapsed", placeholder="項目名"
                )
                if new_label != cell.label:
                    cell.label = new_label
                    save_to_storage()

                new_count = st.number_input(
                    f"N{r}{c}", value=cell.count, key=f"ck_{r}_{c}", label_visibility="collapsed", step=1
                )
                if new_count != cell.count:
                    cell.count = new_count
                    save_to_storage()
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
    bingo_matrix.append(row_status)

# --- ビンゴ判定 ---
bingo_indices = []
for r in range(board.rows):
    if all(bingo_matrix[r]):
        bingo_indices.extend([[r, c] for c in range(board.cols)])
for c in range(board.cols):
    if all(bingo_matrix[r][c] for r in range(board.rows)):
        bingo_indices.extend([[r, c] for r in range(board.rows)])
if board.rows == board.cols:
    if all(bingo_matrix[i][i] for i in range(board.rows)):
        bingo_indices.extend([[i, i] for i in range(board.rows)])
    if all(bingo_matrix[i][board.cols - 1 - i] for i in range(board.rows)):
        bingo_indices.extend([[i, board.cols - 1 - i] for i in range(board.rows)])

if bingo_indices:
    unique_indices = []
    for pair in bingo_indices:
        if pair not in unique_indices:
            unique_indices.append(pair)
    js_highlight = "".join(
        [
            f"document.getElementById('cell-{r}-{c}').parentElement.parentElement.parentElement.classList.add('bingo-line-complete');"
            for r, c in unique_indices
        ]
    )
    st.components.v1.html(f"<script>{js_highlight}</script>", height=0)
    st.balloons()

# --- データの保存と読み込み ---
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 保存",
            data=board.model_dump_json(indent=2),
            file_name=f"bingo_{get_jst_now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 復元", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映", use_container_width=True, type="primary"):
            try:
                d = json.load(uploaded_file)
                st.session_state.csb_board = BingoBoard(**d)
                save_to_storage()
                st.rerun()
            except Exception:
                st.error("失敗")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    new_rows = st.number_input("行数", 1, 15, value=board.rows)
    new_cols = st.number_input("列数", 1, 15, value=board.cols)
    if new_rows != board.rows or new_cols != board.cols:
        board.rows = new_rows
        board.cols = new_cols
        save_to_storage()
        st.rerun()

    st.write("---")
    st.subheader("🚨 リセット")

    if st.button("🔢 カウントのみリセット", use_container_width=True):
        for cell in board.cells.values():
            cell.count = 0
        save_to_storage()
        st.rerun()

    if st.button("🚨 全てリセット", use_container_width=True, type="primary"):
        st.session_state.csb_board = BingoBoard()
        save_to_storage()
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
