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
def render_donation_box(paypay_url: str, is_sidebar: bool = False):
    """
    開発を応援するための募金箱をレンダリングします。
    is_sidebar=True の場合はサイドバーに、False の場合はメインエリアに表示します。
    """
    target = st.sidebar if is_sidebar else st
    
    if is_sidebar:
        target.write("---")
        target.subheader("☕ 開発を応援する")
    
    target.markdown(f"""
        <div style='background-color:#FFF3E0; padding:20px; border-radius:15px; border:2px solid #FFB74D; text-align:center; margin: 20px 0;'>
            <h3 style='margin-top:0; color:#E65100;'>☕ 開発を応援する</h3>
            <p style='margin-bottom:15px; font-size:16px; color:#5D4037;'>
                このアプリが役に立ったら、コーヒー一杯分のご支援をいただけると嬉しいです！<br>
                新しいおもちゃの開発やサーバー維持の励みになります。
            </p>
            <a href='{paypay_url}' target='_blank' style='text-decoration:none;'>
                <div style='background-color:#ff0033; color:white; padding:12px 30px; border-radius:30px; font-weight:bold; font-size:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); display:inline-block;'>
                    PayPayで送金する 💸
                </div>
            </a>
            <p style='margin-top:10px; font-size:12px; color:#A1887F;'>※送金は任意です。いつもありがとうございます！</p>
        </div>
    """, unsafe_allow_html=True)
