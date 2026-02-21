import streamlit as st

def render_styled_number(label: str, value: float | int, bg_color: str = "#E3F2FD", border_color: str = "#2196F3", text_color: str = "#0D47A1", font_size: int = 48):
    """
    スタイル付きの大きな数字をレンダリングします。
    """
    st.markdown(f"""
        <div style='background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px; border:2px solid {border_color};'>
            <span style='font-size:20px; color:{text_color};'>{label}:</span>
            <span style='font-size:{font_size}px; font-weight:bold; color:{text_color}; margin-left:20px;'>{value}</span>
        </div>
    """, unsafe_allow_html=True)

def render_result_box(title: str, value: float | int, bg_color: str = "#2196F3", border_color: str = "#0D47A1", text_color: str = "white", font_size: int = 48):
    """
    結果表示用のボックスをレンダリングします。
    """
    st.markdown(f"### {title}")
    st.markdown(f"""
        <div style='background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center; font-size:{font_size}px; font-weight:bold; color:{text_color}; border:2px solid {border_color};'>
            {value}
        </div>
    """, unsafe_allow_html=True)

def apply_global_styles():
    """
    アプリケーション全体に適用する共通スタイルを定義します。
    """
def render_donation_box(paypay_url: str):
    """
    サイドバーに募金箱をレンダリングします。
    """
    st.sidebar.write("---")
    st.sidebar.subheader("☕ 開発を応援する")
    st.sidebar.markdown(f"""
        <div style='background-color:#FFF3E0; padding:15px; border-radius:10px; border:1px solid #FFB74D; text-align:center;'>
            <p style='margin-bottom:10px; font-size:14px; color:#E65100;'>
                もしこのアプリが役に立ったら、<br>コーヒー一杯分のご支援を<br>いただけると嬉しいです！
            </p>
            <a href='{paypay_url}' target='_blank' style='text-decoration:none;'>
                <div style='background-color:#ff0033; color:white; padding:10px; border-radius:25px; font-weight:bold; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    PayPayで送金する 💸
                </div>
            </a>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption("※送金は任意です。")
