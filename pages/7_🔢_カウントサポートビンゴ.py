import streamlit as st
import pandas as pd

st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

st.title("🔢 カウントサポートビンゴ")

# セッション状態の初期化
def init_cell_state(r, c):
    """
    セルの初期状態をセットアップします。
    """
    label_key = f"csb_label_{r}_{c}"
    count_key = f"csb_count_{r}_{c}"
    if label_key not in st.session_state:
        st.session_state[label_key] = f"項目 {r+1}-{c+1}"
    if count_key not in st.session_state:
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
        st.download_button(
            label="現在の状態を保存 (CSV)",
            data=csv_data,
            file_name="bingo_save.csv",
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
                    st.session_state[f"csb_label_{r}_{c}"] = row_data['label']
                    st.session_state[f"csb_count_{r}_{c}"] = row_data['count']
                st.success("復元しました！")
                st.rerun()
        except Exception as e:
            st.error(f"エラー: ファイル形式が正しくありません。")

    st.write("---")
    if st.button("全てをリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("csb_"):
                del st.session_state[key]
        st.rerun()
    
    st.write("---")
    st.info("ビンゴのようにマス目を作り、各マスのカウントを記録できます。")

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

def decrement_counter(key):
    st.session_state[key] -= 1

# ビンゴグリッドの表示
for r in range(rows):
    cols = st.columns(cols_num)
    for c in range(cols_num):
        label_key, count_key = init_cell_state(r, c)
        
        with cols[c]:
            # ラベル入力
            st.session_state[label_key] = st.text_input(
                f"L_{r}_{c}", 
                value=st.session_state[label_key], 
                key=f"input_{r}_{c}",
                label_visibility="collapsed"
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
                    step=1
                )
            with col_p:
                st.button(
                    "＋", 
                    key=f"plus_{r}_{c}", 
                    use_container_width=True,
                    on_click=increment_counter,
                    args=(count_key,)
                )
