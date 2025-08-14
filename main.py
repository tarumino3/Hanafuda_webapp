import streamlit as st
import pandas as pd

st.markdown('<meta name="robots" content="noindex">', unsafe_allow_html=True)

# --- ページ設定とCSSでのサイドバー非表示 ---
st.set_page_config(page_title="花札 得点計算", page_icon="🎴",initial_sidebar_state="collapsed")

# サイドバーのナビゲーションを非表示にするCSS
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# --- セッション管理の初期化 ---
if 'players' not in st.session_state:
    st.session_state.players = []
if 'scores' not in st.session_state:
    st.session_state.scores = pd.DataFrame()
if 'game_type' not in st.session_state:
    st.session_state.game_type = ""
if 'current_month' not in st.session_state:
    st.session_state.current_month = 1
if 'input_modes' not in st.session_state:
    st.session_state.input_modes = {}

# --- メインコンテンツ ---
st.title('🎴 花札 得点計算アプリ')

# ゲームが進行中かどうかで表示を切り替える
if not st.session_state.players:
    st.info('新しいゲームを開始します。')
    if st.button('新しいゲームを始める', type="primary"):
        st.switch_page("pages/setting.py")
else:
    st.success('進行中のゲームがあります。')
    st.write('**プレイヤー:**', '、'.join(st.session_state.players))
    st.write('**現在の得点:**')
    st.dataframe(st.session_state.scores)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('ゲームを続ける', type="primary"):
            st.switch_page("pages/points.py")
    with col2:
        if st.button('ゲームをリセットする'):
            st.session_state.players = []
            st.session_state.scores = pd.DataFrame()
            st.rerun()