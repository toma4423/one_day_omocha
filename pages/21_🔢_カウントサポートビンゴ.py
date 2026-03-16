import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.count_support import BingoBoard
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

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
    
    /* 入力欄の基本スタイル */
    .stTextInput input { height: 24px !important; font-size: 11px !important; padding: 0 4px !important; margin-bottom: 2px !important; }
    .stNumberInput input { height: 32px !important; font-size: 20px !important; font-weight: 900 !important; padding: 0 !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label { display: none !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    hr { margin: 0.5rem 0 !important; }

    /* モバイル向けの調整 */
    @media (max-width: 768px) {
        /* カラムを無理に縦に並べず、横並びを維持しつつフォントを小さくする */
        [data-testid="column"] {
            min-width: 0 !important;
            flex: 1 1 0% !important;
            padding: 0 1px !important;
        }
        .stTextInput input { font-size: 9px !important; height: 20px !important; }
        .stNumberInput input { font-size: 16px !important; height: 28px !important; }
        
        /* 画面からはみ出さないようにパディングを極限まで削る */
        div[data-testid="stElementContainer"] div.st-emotion-cache-16idsys, 
        div[data-testid="stElementContainer"] div.st-emotion-cache-1r6slb0 { padding: 2px !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>🔢 カウントサポートビンゴ</h1>", unsafe_allow_html=True)

storage = SafeStorage(LocalStorage())
DATA_KEY = "csb_data_v5"

# --- 初期化とデータ復元 ---
if "csb_board" not in st.session_state:
    saved = wait_for_storage_load(storage, DATA_KEY, "_csb_initialized")
    # wait_for_storage_load が st.stop() しなかった場合 (データが見つかったか、スキップされた場合)
    if saved:
        try:
            st.session_state.csb_board = BingoBoard(**saved)
        except Exception:
            st.session_state.csb_board = BingoBoard()
    else:
        # ロードスキップ等の場合
        st.session_state.csb_board = BingoBoard()

    if "csb_reset_id" not in st.session_state:
        st.session_state.csb_reset_id = 0
    st.rerun()

board: BingoBoard = st.session_state.csb_board
reset_id = st.session_state.csb_reset_id


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

                # keyに reset_id を含めることで強制リセットを可能にする
                new_label = st.text_input(
                    f"L{r}{c}",
                    value=cell.label,
                    key=f"lk_{r}_{c}_{reset_id}",
                    label_visibility="collapsed",
                    placeholder="項目名",
                )
                if new_label != cell.label:
                    cell.label = new_label

                new_count = st.number_input(
                    f"N{r}{c}",
                    value=cell.count,
                    key=f"ck_{r}_{c}_{reset_id}",
                    label_visibility="collapsed",
                    step=1,
                )
                if new_count != cell.count:
                    cell.count = new_count
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


# データの管理
def on_load(data):
    st.session_state.csb_board = BingoBoard(**data)
    st.session_state.csb_reset_id += 1


render_storage_controls(
    storage=storage,
    storage_key=DATA_KEY,
    current_data=board,
    on_load_callback=on_load,
    file_prefix="bingo",
    is_pydantic=True,
)

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    # 行数・列数の変更時も reset_id を上げてウィジェットを再描画させる
    new_rows = st.number_input("行数", 1, 15, value=board.rows)
    new_cols = st.number_input("列数", 1, 15, value=board.cols)
    if new_rows != board.rows or new_cols != board.cols:
        board.rows = new_rows
        board.cols = new_cols
        st.session_state.csb_reset_id += 1
        st.rerun()

    st.write("---")
    st.subheader("🚨 リセット")

    if st.button("🔢 カウントのみリセット", use_container_width=True):
        board.reset_counts_only()
        st.session_state.csb_reset_id += 1
        st.rerun()

    if st.button("🚨 全てリセット", use_container_width=True, type="primary"):
        st.session_state.csb_board = BingoBoard()
        st.session_state.csb_reset_id += 1
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
