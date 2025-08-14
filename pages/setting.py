import streamlit as st
import pandas as pd
from functions import create_yaku_editor, generate_unique_names, load_preset
from rules import DEFAULT_KOIKOI_RULES

st.markdown('<meta name="robots" content="noindex">', unsafe_allow_html=True)

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# --- UI描画 ---
st.title('⚙️ ゲーム設定')

if 'game_rules' not in st.session_state:
    st.session_state.game_rules = DEFAULT_KOIKOI_RULES.copy()

# --- プリセット選択 ---
st.subheader('プリセット')
preset_type = st.radio("基本となるルールを選択", ('こいこい','八八','いつもの八八'), horizontal=True)
st.button("プリセットを読み込む", on_click=load_preset, args=(preset_type,))
st.info("プリセットを読み込むと、下の詳細設定が上書きされます。")
st.divider()

# --- カスタムルール設定 ---
st.subheader('詳細設定')
with st.expander("ルールの編集", expanded=True):

    tab_basic, tab_cards, tab_dekiyaku, tab_teyaku, tab_special = st.tabs([
        "基本ルール", "札の点数", "出来役の設定", "手役の設定", "特殊役の設定"
    ])

    with tab_basic:
        st.session_state.game_rules["score_unit"] = st.radio(
            "点数表示の単位", 
            ("貫/点", "文"),
            index=("貫/点", "文").index(st.session_state.game_rules.get("score_unit", "貫/点")),
            horizontal=True
        )        
        st.session_state.game_rules["zetsuba_oba"] = st.toggle(
            "絶場・大場を有効にする", 
            value=st.session_state.game_rules["zetsuba_oba"]
        )
        st.session_state.game_rules["enable_orichin"] = st.toggle("下り賃を有効にする", value=st.session_state.game_rules.get("enable_orichin", True))
        st.session_state.game_rules["enable_oikomi"] = st.toggle("追い込み賃を有効にする", value=st.session_state.game_rules.get("enable_oikomi", True))
        st.session_state.game_rules["enable_mizuten"] = st.toggle("みずてんを有効にする", value=st.session_state.game_rules.get("enable_mizuten", True))
    with tab_cards:
        scores = st.session_state.game_rules["card_scores"]
        st.write("各種別の札の基本点を設定します。")
        c1, c2, c3, c4 = st.columns(4)
        with c1: scores["光"] = st.number_input("光札", value=scores["光"])
        with c2: scores["タネ"] = st.number_input("タネ", value=scores["タネ"])
        with c3: scores["短冊"] = st.number_input("短冊", value=scores["短冊"])
        with c4: scores["カス"] = st.number_input("カス", value=scores["カス"])
    with tab_dekiyaku:
        create_yaku_editor("出来役", "dekiyaku")
    with tab_teyaku:
        create_yaku_editor("手役", "teyaku")
    with tab_special:
        create_yaku_editor("特殊な役", "special_yaku")

st.divider()

# --- プレイヤー情報入力とゲーム開始 ---
st.subheader("プレイヤー設定")
num_players = st.number_input('プレイヤーの人数', min_value=2, max_value=7, step=1)
player_names = []
initial_scores = {}

name_col, score_col = st.columns([2, 1])
with name_col:
    st.write("プレイヤー名")
with score_col:
    st.write("初期得点")

for i in range(num_players):
    name_col, score_col = st.columns([2, 1])
    with name_col:
        name = st.text_input(f'プレイヤー{i+1}の名前', key=f'p{i}', label_visibility="collapsed")
        player_names.append(name)
    with score_col:
        if st.session_state.game_rules["game_name"] == "八八":
            score = st.number_input(f'初期得点{i+1}', key=f'initial_score_{i}', min_value=0, step=1, label_visibility="collapsed",value=60)
        else: score = st.number_input(f'初期得点{i+1}', key=f'initial_score_{i}', min_value=0, step=1, label_visibility="collapsed")
        initial_scores[name] = score

if st.button('この内容でゲームを開始する', type="primary", use_container_width=True):
    if all(player_names):
        unique_player_names = generate_unique_names(player_names)
        if player_names != unique_player_names:
            st.info(f"名前が重複していたため自動調整しました: {', '.join(unique_player_names)}")
        
        st.session_state.players = unique_player_names
        
        # 入力された初期スコアを元にDataFrameを初期化
        final_initial_scores = {unique_name: initial_scores.get(original_name, 0) for original_name, unique_name in zip(player_names, unique_player_names)}
        st.session_state.scores = pd.DataFrame([final_initial_scores])

        st.session_state.current_month = 1
        st.session_state.input_modes = {}
        st.success("設定が完了しました！")
        st.switch_page("pages/points.py")
    else:
        st.error('全てのプレイヤーの名前を入力してください。')