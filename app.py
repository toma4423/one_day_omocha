import streamlit as st
import streamlit.components.v1 as components

# ページの設定
st.set_page_config(
    page_title="🎁 今日のおもちゃ箱",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 背景デザイン（Streamlit 側の背景）
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 表示する HTML コンテンツ
TARGET_URL = "https://omocha-frontend-599665978822.asia-northeast1.run.app/"

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{transform: translateY(0);}}
            40% {{transform: translateY(-30px);}}
            60% {{transform: translateY(-15px);}}
        }}
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            text-align: center;
            background: transparent;
        }}
        .logo {{
            font-size: 100px;
            margin-bottom: 20px;
            animation: bounce 2s infinite;
        }}
        .title {{
            font-weight: 900;
            font-size: 3.5rem;
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .subtitle {{
            font-size: 1.2rem;
            color: #5e6d7e;
            margin-bottom: 40px;
            line-height: 1.6;
        }}
        .btn {{
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
            cursor: pointer;
        }}
        .btn:hover {{
            transform: scale(1.05);
            background-color: #ff3333;
            box-shadow: 0 15px 35px rgba(255,75,75,0.5);
        }}
        .note {{
            margin-top: 25px;
            color: #888;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="logo">🎁</div>
    <h1 class="title">今日のおもちゃ箱</h1>
    <p class="subtitle">新しい「今日のおもちゃ箱」へようこそ！<br>より快適に、もっと楽しく遊べるようになりました。</p>
    
    <a href="{TARGET_URL}" target="_blank" rel="noopener noreferrer" class="btn">
        🚀 おもちゃ箱を開いて遊ぶ 🚀
    </a>
    
    <p class="note">※ クリックすると新しいタブで開きます</p>
</body>
</html>
"""

# HTMLコンポーネントとして描画（iframeで分離されるため確実に描画されます）
components.html(html_content, height=600, scrolling=False)
