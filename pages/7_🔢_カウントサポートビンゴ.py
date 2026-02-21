import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils.time import get_jst_now
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage

# ページの設定
st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

# スマホ対応用のカスタムCSS
st.markdown("""
    <style>
    .stButton > button {
        height: 60px !important;
        font-size: 24px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    .stNumberInput input {
        font-size: 20px !important;
        text-align: center !important;
        height: 50px !important;
    }
    .stTextInput input {
        font-size: 16px !important;
        text-align: center !important;
    }
    @media (max_width: 600px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔢 カウントサポートビンゴ")

# SafeStorage の初期化（ページ読み込みごとに確実にインスタンス化）
# コンポーネント自体の戻り値を SafeStorage でラップします
storage = SafeStorage(LocalStorage())

# 初期状態のロードを一度だけ行うためのフラグ
if 'just_reset' not in st.session_state:
    st.session_state.just_reset = False

# セッション状態の初期化
def init_cell_state(r, c):
    label_key = f"csb_label_{r}_{c}"
    count_key = f"csb_count_{r}_{c}"
    
    # リセット直後、または初めての場合のみデフォルト値を設定
    if st.session_state.just_reset or label_key not in st.session_state:
        # storage から取得（リセット直後でない場合のみ）
        saved_label = storage.get_item(label_key) if not st.session_state.just_reset else None
        st.session_state[label_key] = saved_label if saved_label is not None else f"項目 {r+1}-{c+1}"
    
    if st.session_state.just_reset or count_key not in st.session_state:
        # storage から取得（リセット直後でない場合のみ）
        saved_count = storage.get_item(count_key) if not st.session_state.just_reset else None
        try:
            st.session_state[count_key] = int(saved_count) if saved_count is not None else 0
        except (ValueError, TypeError, Exception):
            st.session_state[count_key] = 0
            
    return label_key, count_key

# サイドバーの設定項目
with st.sidebar:
    st.header("設定")
    rows = st.number_input("行数", min_value=1, max_value=15, value=5)
    cols_num = st.number_input("列数", min_value=1, max_value=15, value=5)
    
    st.write("---")
    st.subheader("💾 セーブ & ロード")
    
    # ダウンロードデータの準備
    save_data = []
    for r in range(rows):
        for c in range(cols_num):
            lk, ck = init_cell_state(r, c)
            save_data.append({"row": r, "col": c, "label": st.session_state[lk], "count": st.session_state[ck]})
    
    df_save = pd.DataFrame(save_data)
    csv_data = df_save.to_csv(index=False).encode('utf-8')
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="CSVをダウンロード",
        data=csv_data,
        file_name=f"bingo_save_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ロード機能
    uploaded_file = st.file_uploader("CSVをアップロード", type="csv")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                df_load = pd.read_csv(uploaded_file)
                for _, row_data in df_load.iterrows():
                    r, c = int(row_data['row']), int(row_data['col'])
                    lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
                    st.session_state[lk] = str(row_data['label'])
                    st.session_state[ck] = int(row_data['count'])
                    storage.set_item(lk, st.session_state[lk])
                    storage.set_item(ck, st.session_state[ck])
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("ロードに失敗しました")

    st.write("---")
    # リセットボタン（AttributeError を防ぐために SafeStorage インスタンスを確実に呼び出す）
    if st.button("全てをリセット", use_container_width=True):
        st.session_state.just_reset = True
        storage.clear_all_with_prefix("csb_")
        st.success("リセット完了")
        st.rerun()

    st.info("自動保存：ブラウザ（LocalStorage）")

# コールバック関数
def on_val_change(key):
    storage.set_item(key, st.session_state[key])

def on_plus(key):
    st.session_state[key] += 1
    on_val_change(key)

def on_minus(key):
    st.session_state[key] -= 1
    on_val_change(key)

# リセットフラグを戻す
if st.session_state.just_reset:
    st.session_state.just_reset = False

# メイングリッド表示
for r in range(rows):
    cols = st.columns(cols_num)
    for c in range(cols_num):
        label_key, count_key = init_cell_state(r, c)
        with cols[c]:
            st.text_input(f"L_{r}_{c}", key=label_key, label_visibility="collapsed", on_change=on_val_change, args=(label_key,))
            
            c_m, c_v, c_p = st.columns([1, 1.5, 1])
            with c_m:
                st.button("－", key=f"btn_m_{r}_{c}", use_container_width=True, on_click=on_minus, args=(count_key,))
            with c_v:
                st.number_input(f"N_{r}_{c}", key=count_key, label_visibility="collapsed", step=1, on_change=on_val_change, args=(count_key,))
            with c_p:
                st.button("＋", key=f"btn_p_{r}_{c}", use_container_width=True, on_click=on_plus, args=(count_key,))
