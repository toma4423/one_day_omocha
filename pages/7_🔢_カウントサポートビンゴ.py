import streamlit as st

st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

st.title("🔢 カウントサポートビンゴ")

# サイドバーで設定
with st.sidebar:
    st.header("設定")
    rows = st.number_input("行数", min_value=1, max_value=10, value=5)
    cols_num = st.number_input("列数", min_value=1, max_value=10, value=5)
    
    if st.button("全てをリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("csb_"):
                del st.session_state[key]
        st.rerun()
    
    st.write("---")
    st.info("ビンゴのようにマス目を作り、各マスのカウントを記録できます。")

# セッション状態の初期化
def init_state(r, c):
    label_key = f"csb_label_{r}_{c}"
    count_key = f"csb_count_{r}_{c}"
    if label_key not in st.session_state:
        st.session_state[label_key] = f"項目 {r+1}-{c+1}"
    if count_key not in st.session_state:
        st.session_state[count_key] = 0

# 全体のカウント計算
total_count = 0
for r in range(rows):
    for c in range(cols_num):
        init_state(r, c)
        total_count += st.session_state[f"csb_count_{r}_{c}"]

# 合計表示
st.markdown(f"### 合計: {total_count}")

# ビンゴグリッドの表示
for r in range(rows):
    cols = st.columns(cols_num)
    for c in range(cols_num):
        with cols[c]:
            label_key = f"csb_label_{r}_{c}"
            count_key = f"csb_count_{r}_{c}"
            
            # セルのスタイル（背景色や枠線）
            bg_color = "#f0f2f6"
            text_color = "#1f77b4"
            if st.session_state[count_key] > 0:
                bg_color = "#e1f5fe"
                text_color = "#0288d1"
            elif st.session_state[count_key] < 0:
                bg_color = "#ffebee"
                text_color = "#d32f2f"
            
            # ラベル入力
            st.session_state[label_key] = st.text_input(
                f"L_{r}_{c}", 
                value=st.session_state[label_key], 
                key=f"input_{r}_{c}",
                label_visibility="collapsed"
            )

            # カウンター操作（横並び）
            # 背景色などのスタイル計算
            bg_color = "#f0f2f6"
            text_color = "#1f77b4"
            if st.session_state[count_key] > 0:
                bg_color = "#e1f5fe"
                text_color = "#0288d1"
            elif st.session_state[count_key] < 0:
                bg_color = "#ffebee"
                text_color = "#d32f2f"

            # ボタンと数字を横に並べる
            col_m, col_v, col_p = st.columns([1, 1.5, 1])
            with col_m:
                if st.button("－", key=f"minus_{r}_{c}", use_container_width=True):
                    st.session_state[count_key] -= 1
                    st.rerun()
            with col_v:
                st.markdown(f"""
                    <div style='background-color:{bg_color}; padding:5px; border-radius:5px; border:1px solid #ddd; text-align:center;'>
                        <div style='font-size:20px; font-weight:bold; color:{text_color};'>{st.session_state[count_key]}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_p:
                if st.button("＋", key=f"plus_{r}_{c}", use_container_width=True):
                    st.session_state[count_key] += 1
                    st.rerun()
