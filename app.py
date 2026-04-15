import streamlit as st

# ページの設定
st.set_page_config(
    page_title="🎁 今日のおもちゃ箱",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# スタイルの定義
# Streamlit標準のボタンをカスタマイズして巨大で目立つポータルボタンにします
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
        padding-top: 10vh;
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
    }
    
    .sub-title {
        font-size: 1.3rem;
        color: #5e6d7e;
        margin-bottom: 3rem;
        line-height: 1.6;
    }

    /* Streamlitボタンのカスタマイズ */
    div.stLinkButton > a {
        background-color: #ff4b4b !important;
        color: white !important;
        padding: 1.5rem 4rem !important;
        border-radius: 50px !important;
        font-size: 28px !important;
        font-weight: bold !important;
        text-decoration: none !important;
        box-shadow: 0 10px 25px rgba(255,75,75,0.4) !important;
        transition: all 0.3s ease !important;
        border: none !important;
        display: inline-block !important;
    }
    
    div.stLinkButton > a:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 15px 35px rgba(255,75,75,0.5) !important;
        background-color: #ff3333 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# コンテンツの配置
st.markdown('<div class="portal-main">', unsafe_allow_html=True)
st.markdown('<div class="logo-anim">🎁</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">今日のおもちゃ箱</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">新しい「今日のおもちゃ箱」へようこそ！<br>より快適に、もっと楽しく遊べるようになりました。</p>',
    unsafe_allow_html=True,
)

# リンクボタン（Streamlit標準の st.link_button を使用してクリックを確実にする）
# target="_top" を明示的に指定して、ページ全体を遷移させます
st.link_button(
    "🚀 おもちゃ箱を開いて遊ぶ 🚀",
    "https://omocha-frontend-599665978822.asia-northeast1.run.app/",
    use_container_width=False,
    type="primary",
)

st.markdown("</div>", unsafe_allow_html=True)

# ページ全体のクリックイベントを拾って遷移させるJS（最終手段としてのバックアップ）
st.components.v1.html(
    """
    <script>
    // ページ上の全てのリンクを target="_top" に強制する
    window.onload = function() {
        var links = parent.document.getElementsByTagName('a');
        for (var i = 0; i < links.length; i++) {
            if (links[i].href.includes('asia-northeast1.run.app')) {
                links[i].target = '_top';
            }
        }
    };
    </script>
    """,
    height=0,
)
