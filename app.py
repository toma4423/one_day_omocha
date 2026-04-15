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
    /* メインコンテナの背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* サイドバーを完全に非表示 */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* ポータル全体のレイアウト */
    .portal-main {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 15vh;
        text-align: center;
    }
    
    .logo-anim {
        font-size: 100px;
        margin-bottom: 20px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-30px);}
        60% {transform: translateY(-15px);}
    }
    
    .main-title {
        font-weight: 900;
        font-size: 3.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-family: 'sans-serif';
    }
    
    .sub-title {
        font-size: 1.3rem;
        color: #5e6d7e;
        margin-bottom: 3rem;
        line-height: 1.6;
    }

    /* カスタムリンクボタン */
    .portal-link {
        display: inline-block;
        background-color: #ff4b4b;
        color: white !important;
        padding: 1.2rem 3.5rem;
        border-radius: 50px;
        font-size: 26px;
        font-weight: bold;
        text-decoration: none !important;
        box-shadow: 0 10px 25px rgba(255,75,75,0.4);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        /* クリックを確実に通すための設定 */
        position: relative;
        z-index: 1000;
        pointer-events: auto;
    }
    
    .portal-link:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 35px rgba(255,75,75,0.5);
        background-color: #ff3333;
    }
    
    .portal-link:active {
        transform: translateY(0) scale(0.98);
    }
    </style>
    
    <div class="portal-main">
        <div class="logo-anim">🎁</div>
        <h1 class="main-title">今日のおもちゃ箱</h1>
        <p class="sub-title">新しい「今日のおもちゃ箱」へようこそ！<br>より快適に、もっと楽しく遊べるようになりました。</p>
        
        <!-- target="_blank" で新しいタブを開くことを明示。rel="noopener noreferrer" はセキュリティ上のベストプラクティス -->
        <a href="https://omocha-frontend-599665978822.asia-northeast1.run.app/" target="_blank" rel="noopener noreferrer" class="portal-link">
            🚀 おもちゃ箱を開いて遊ぶ 🚀
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
