import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown('<meta name="robots" content="noindex">', unsafe_allow_html=True)

# サイドバー非表示CSS
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# ゲームが設定されていなければメインメニューに移動
if 'scores' not in st.session_state or st.session_state.scores.empty:
    st.warning("スコアデータがありません。メインメニューに戻ります。")
    st.switch_page("main.py")

st.title('🏆 最終結果')
st.balloons()

# --- スコア計算 ---
scores_df = st.session_state.scores
total_scores = scores_df.sum().sort_values(ascending=False)
winner_name = total_scores.idxmax()
winner_score = total_scores.max()

# --- 勝者と最終スコアの表示 ---
st.header(f'勝者は {winner_name} さんです！', divider='rainbow')
st.metric(label="最終スコア", value=f"{winner_score} 点")

st.divider()

color_sequence = px.colors.qualitative.Plotly
player_color_map = {player: color_sequence[i % len(color_sequence)] for i, player in enumerate(st.session_state.players)}


# --- 全プレイヤーの最終スコアをPlotlyで描画 ---
st.subheader('全プレイヤーの最終スコア')
total_scores_df = total_scores.reset_index()
total_scores_df.columns = ['Player', 'Score']

# Plotlyで棒グラフを作成
bar_fig = px.bar(
    total_scores_df,
    x='Player',
    y='Score',
    color='Player', 
    color_discrete_map=player_color_map, 
    labels={'Player': 'プレイヤー', 'Score': '合計点'}
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- 各月の得点詳細のグラフをPlotlyで描画 ---
st.subheader('各月の得点詳細')
tab1, tab2 = st.tabs(["折れ線グラフ",  "シンプル表"])
with tab1:
    st.write("各プレイヤーの累計得点の推移を表示します。")
    if not scores_df.empty:
        cumulative_scores_df = scores_df.astype(float).cumsum()

        line_df = cumulative_scores_df.reset_index().rename(columns={'index': '月'})
        line_df_long = line_df.melt(id_vars='月', var_name='Player', value_name='Cumulative Score')

        # 3. Plotlyで折れ線グラフを作成
        line_fig = px.line(
            line_df_long,
            x='月',
            y='Cumulative Score', 
            color='Player',
            color_discrete_map=player_color_map,
            labels={'Player': 'プレイヤー', 'Cumulative Score': '累計得点'} 
        )
        st.plotly_chart(line_fig, use_container_width=True)
    else:
        st.write("スコアデータがありません。")
with tab2:
    # シンプルな表: スクロールなしで全体表示
    if not scores_df.empty:
        table_df = scores_df.copy()
        new_index = ['初期値'] + [f'{i}月' for i in range(1, len(table_df))]
        table_df.index = new_index        
        total_scores_row = table_df.sum().to_dict()
        table_df.loc['合計点'] = total_scores_row
        st.table(table_df)
    else:
        st.write("スコアデータがありません。")

# --- 操作ボタン ---
if not scores_df.empty:
    csv_table_df = scores_df.copy()
    new_index_csv = ['初期値'] + [f'{i}月' for i in range(1, len(csv_table_df))]
    csv_table_df.index = new_index_csv

    total_scores_row = csv_table_df.sum().to_dict()
    csv_table_df.loc['合計点'] = total_scores_row
    csv_data = csv_table_df.to_csv(index_label='プレイヤー').encode('utf-8-sig')

    st.download_button(
        label="📜 結果をCSVでダウンロード",
        type="primary",
        data=csv_data,
        file_name='hanafuda_final_scores.csv',
        mime='text/csv',
        use_container_width=True
    )
else:
    st.info("ダウンロードできるスコアデータがありません。")

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('🔄 もう一度遊ぶ', use_container_width=True):
        # 既存のプレイヤー情報とゲーム設定を維持
        
        # scores DataFrameを初期値で再作成
        unique_player_names = st.session_state.players
        
        # ゲーム名が八八の場合は初期値を60、それ以外は0
        initial_score_value = 60 if st.session_state.game_rules["game_name"] == "八八" else 0
        
        initial_scores = {player: initial_score_value for player in unique_player_names}
        st.session_state.scores = pd.DataFrame([initial_scores])

        st.session_state.current_month = 1
        st.session_state.input_modes = {}
        st.session_state.navigate_to_results = False

        st.switch_page("pages/points.py")
with col2:
    # ---「ルール設定に戻る」ボタン---
    if st.button('⚙️ ルール設定に戻る', use_container_width=True):
        # ゲーム設定は維持し、スコアのみ初期化
        st.session_state.scores = pd.DataFrame()
        st.session_state.players = []
        st.session_state.current_month = 1
        st.session_state.input_modes = {}
        st.session_state.navigate_to_results = False
        del st.session_state['active_players']

        st.switch_page("pages/setting.py")
with col3:
    # --- 「新しいゲームを始める」ボタン ---
    if st.button('🎲 メインメニューに戻る', use_container_width=True):
        # 全てのセッション情報を初期化
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.switch_page("main.py")
