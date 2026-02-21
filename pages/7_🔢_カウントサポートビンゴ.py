import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

st.title("🔢 カウントサポートビンゴ")

# LocalStorage の初期化
storage = LocalStorage()

# セッション状態の初期化
def init_cell_state(r, c):
    """
    セルの初期状態をセットアップし、LocalStorage からの復元を試みます。
    """
    label_key = f"csb_label_{r}_{c}"
    count_key = f"csb_count_{r}_{c}"
    
    # セッション状態にない場合、LocalStorage からの取得を試みる
    if label_key not in st.session_state:
        saved_label = storage.getItem(label_key)
        st.session_state[label_key] = saved_label if saved_label is not None else f"項目 {r+1}-{c+1}"
    
    if count_key not in st.session_state:
        saved_count = storage.getItem(count_key)
        st.session_state[count_key] = int(saved_count) if saved_count is not None else 0
        
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
        
        # 保存時の日時を取得してファイル名を作成
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
                    st.session_state[l_k] = row_data['label']
                    st.session_state[c_k] = row_data['count']
                    # LocalStorage も更新
                    storage.setItem(l_k, row_data['label'])
                    storage.setItem(c_k, row_data['count'])
                st.success("復元しました！")
                st.rerun()
        except Exception as e:
            st.error(f"エラー: ファイル形式が正しくありません。")

    st.write("---")
    if st.button("全てをリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("csb_"):
                del st.session_state[key]
                storage.deleteItem(key) # LocalStorage も削除
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
    storage.setItem(key, st.session_state[key]) # LocalStorage を更新

def decrement_counter(key):
    st.session_state[key] -= 1
    storage.setItem(key, st.session_state[key]) # LocalStorage を更新

def on_label_change(key):
    storage.setItem(key, st.session_state[key]) # LocalStorage を更新

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
                on_change=on_label_change,
                args=(label_key,)
            )

            # スタイル取得
            bg_color, text_color = get_cell_style(st.session_state[count_key])

            # カウンター操作（横並び）
            col_m, col_v, col_p = st.columns([1, 1.5, 1])
            with col_m:
                st.button(
                    "－", 
                    key=f"minus_{r}_{c}", 
                    use_container_width=True,
                    on_click=decrement_counter,
                    args=(count_key,)
                )
            with col_v:
                # key に直接 count_key を指定し、コールバックで操作することで同期させる
                st.number_input(
                    f"N_{r}_{c}",
                    key=count_key,
                    label_visibility="collapsed",
                    step=1,
                    on_change=on_label_change,
                    args=(count_key,)
                )
            with col_p:
                st.button(
                    "＋", 
                    key=f"plus_{r}_{c}", 
                    use_container_width=True,
                    on_click=increment_counter,
                    args=(count_key,)
                )
