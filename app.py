import streamlit as st

# ページの設定
st.set_page_config(
    page_title="🎁 今日のおもちゃ箱",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 外部からのCSS干渉を防ぐための最小限のスタイル
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    /* アニメーション定義のみ残す */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-30px);}
        60% {transform: translateY(-15px);}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 全てのデザインをインラインスタイルで記述し、確実にボタンに見えるようにします
TARGET_URL = "https://omocha-frontend-599665978822.asia-northeast1.run.app/"

portal_html = f"""
<div style="
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 10vh;
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
">
    <div style="font-size: 100px; margin-bottom: 20px; animation: bounce 2s infinite;">🎁</div>
    
    <h1 style="
        font-weight: 900;
        font-size: 3.5rem;
        color: #2c3e50;
        margin: 0 0 10px 0;
    ">今日のおもちゃ箱</h1>
    
    <p style="
        font-size: 1.2rem;
        color: #5e6d7e;
        margin-bottom: 40px;
        line-height: 1.6;
    ">新しい「今日のおもちゃ箱」へようこそ！<br>より快適に、もっと楽しく遊べるようになりました。</p>
    
    <a href="{TARGET_URL}" target="_blank" rel="noopener noreferrer" style="
        display: inline-block;
        background-color: #ff4b4b;
        color: white !important;
        padding: 20px 60px;
        border-radius: 50px;
        font-size: 28px;
        font-weight: bold;
        text-decoration: none !important;
        box-shadow: 0 10px 30px rgba(255,75,75,0.4);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer !important;
    " onmouseover="this.style.transform='scale(1.05)'; this.style.backgroundColor='#ff3333';" 
       onmouseout="this.style.transform='scale(1)'; this.style.backgroundColor='#ff4b4b';">
        🚀 おもちゃ箱を開いて遊ぶ 🚀
    </a>
    
    <p style="margin-top: 20px; color: #888; font-size: 0.9rem;">
        ※ クリックすると新しいタブで開きます
    </p>
</div>
"""

st.markdown(portal_html, unsafe_allow_html=True)
