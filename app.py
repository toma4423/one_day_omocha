import streamlit as st

# ページの設定
st.set_page_config(
    page_title="🎁 今日のおもちゃ箱",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# スタイルの定義
st.markdown(
    """
    <style>
    /* メインコンテナの背景とレイアウト */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .portal-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        text-align: center;
    }
    
    .logo {
        font-size: 80px;
        margin-bottom: 20px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-30px);}
        60% {transform: translateY(-15px);}
    }
    
    .title {
        font-weight: 900;
        font-size: 3rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #5e6d7e;
        margin-bottom: 3rem;
    }
    
    .redirect-button {
        display: inline-block;
        background-color: #ff4b4b;
        color: white !important;
        padding: 1.2rem 3rem;
        border-radius: 50px;
        font-size: 24px;
        font-weight: bold;
        text-decoration: none;
        box-shadow: 0 10px 20px rgba(255,75,75,0.3);
        transition: all 0.3s ease;
        border: none;
    }
    
    .redirect-button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 30px rgba(255,75,75,0.4);
        background-color: #ff3333;
    }

    /* サイドバーを非表示にする（Streamlitのデフォルトメニューは残るが、ナビゲーションは空） */
    section[data-testid="stSidebar"] {
        display: none;
    }
    </style>
    
    <div class="portal-container">
        <div class="logo">🎁</div>
        <div class="title">今日のおもちゃ箱</div>
        <p class="subtitle">新しい「今日のおもちゃ箱」へようこそ！<br>より快適に、もっと楽しく遊べるようになりました。</p>
        
        <a href="https://omocha-frontend-599665978822.asia-northeast1.run.app/" target="_self" class="redirect-button">
            🚀 おもちゃ箱を開いて遊ぶ 🚀
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# 自動リダイレクトの補助（必要であれば）
st.markdown(
    """
    <script>
    // ユーザーがクリックしなくても自動的にリダイレクトさせたい場合は以下を有効にできます
    // window.location.href = "https://omocha-frontend-599665978822.asia-northeast1.run.app/";
    </script>
    """,
    unsafe_allow_html=True,
)
