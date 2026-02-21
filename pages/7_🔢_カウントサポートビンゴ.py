import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage

st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

st.title("🔢 カウントサポートビンゴ")

# SafeStorage の初期化
if 'safe_storage' not in st.session_state:
    st.session_state.safe_storage = SafeStorage(LocalStorage())

storage = st.session_state.safe_storage

# セッション状態の初期化
def init_cell_state(r, c):
    """
    セルの初期状態をセットアップし、LocalStorage からの復元を試みます。
    """
    label_key = f"csb_label_{r}_{c}"
    count_key = f"csb_count_{r}_{c}"
    
    # セッション状態にない場合、LocalStorage からの取得を試みる
    if label_key not in st.session_state:
        saved_label = storage.get_item(label_key)
        st.session_state[label_key] = saved_label if saved_label is not None else f"項目 {r+1}-{c+1}"
    
    if count_key not in st.session_state:
        saved_count = storage.get_item(count_key)
        try:
            st.session_state[count_key] = int(saved_count) if saved_count is not None else 0
        except (ValueError, TypeError):
            st.session_state[count_key] = 0
            
    return label_key, count_key

# サイドバーで設定
with st.sidebar:
    st.header("設定")
    rows = st.number_input("行数", min_value=1, max_value=10, value=5)
    cols_num = st.number_input("列数", min_value=1, max_value=10, value=5)
    
    st.write("---")
    st.subheader("💾 セーブ & ロード")
    
    # セーブ（CSVダウンロード）
    save_data = []
    for r in range(rows):
        for c in range(cols_num):
            l_key, c_key = init_cell_state(r, c)
            save_data.append({
                "row": r,
                "col": c,
                "label": st.session_state[l_key],
                "count": st.session_state[c_key]
            })
    
    if save_data:
        df_save = pd.DataFrame(save_data)
        csv_data = df_save.to_csv(index=False).encode('utf-8')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        default_filename = f"bingo_save_{timestamp}.csv"
        
        st.download_button(
            label="現在の状態を保存 (CSV)",
            data=csv_data,
            file_name=default_filename,
            mime="text/csv",
            use_container_width=True
        )

    # ロード（CSVアップロード）
    uploaded_file = st.file_uploader("保存したCSVを読み込む", type="csv")
    if uploaded_file is not None:
        try:
            df_load = pd.read_csv(uploaded_file)
            if st.button("データを復元する", use_container_width=True):
                for _, row_data in df_load.iterrows():
                    r, c = int(row_data['row']), int(row_data['col'])
                    l_k, c_k = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
                    st.session_state[l_k] = str(row_data['label'])
                    st.session_state[c_k] = int(row_data['count'])
                    # LocalStorage も更新
                    storage.set_item(l_k, st.session_state[l_k])
                    storage.set_item(c_k, st.session_state[c_k])
                st.success("復元しました！")
                st.rerun()
        except Exception as e:
            st.error(f"ロード中にエラーが発生しました。")

    st.write("---")
    if st.button("全てをリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("csb_"):
                del st.session_state[key]
                storage.delete_item(key) # LocalStorage も安全に削除
        st.success("リセットしました")
        st.rerun()
    
    st.write("---")
    st.info("ブラウザの LocalStorage に自動保存されます。リロードしてもデータは保持されます。")

def get_cell_style(count):
    """
    カウント値に応じた背景色とテキスト色を返します。
    """
    if count > 0:
        return "#e1f5fe", "#0288d1"
    if count < 0:
        return "#ffebee", "#d32f2f"
    return "#f0f2f6", "#1f77b4"

# コールバック関数の定義
def increment_counter(key):
    st.session_state[key] += 1
    storage.set_item(key, st.session_state[key])

def decrement_counter(key):
    st.session_state[key] -= 1
    storage.set_item(key, st.session_state[key])

def on_input_change(key):
    """直接入力やラベル変更時の同期"""
    storage.set_item(key, st.session_state[key])

# ビンゴグリッドの表示
for r in range(rows):
    cols = st.columns(cols_num)
    for c in range(cols_num):
        label_key, count_key = init_cell_state(r, c)
        
        with cols[c]:
            # ラベル入力
            st.text_input(
                f"L_{r}_{c}", 
                key=label_key,
                label_visibility="collapsed",
                on_change=on_input_change,
                args=(label_key,)
            )

            # スタイル取得
            bg_color, text_color = get_cell_style(st.session_state[count_key])

            # カウンター操作
            col_m, col_v, col_p = st.columns([1, 1.5, 1])
            with col_m:
                st.button(
                    "－", key=f"minus_{r}_{c}", use_container_width=True,
                    on_click=decrement_counter, args=(count_key,)
                )
            with col_v:
                st.number_input(
                    f"N_{r}_{c}", key=count_key, label_visibility="collapsed",
                    step=1, on_change=on_input_change, args=(count_key,)
                )
            with col_p:
                st.button(
                    "＋", key=f"plus_{r}_{c}", use_container_width=True,
                    on_click=increment_counter, args=(count_key,)
                )
