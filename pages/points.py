import streamlit as st
import pages.setting as setting
from ultralytics import YOLO
import hashlib
from functions import calculate_score_from_cards, calculate_points_from_detections, calculate_score_from_image, record_scores_callback, format_score
from YOLO_model.YOLO_fanctions import delete_detection_callback

st.markdown('<meta name="robots" content="noindex">', unsafe_allow_html=True)

@st.cache_resource
def load_yolo_model():
    """YOLOモデルをロードし、キャッシュする関数"""
    try:
        model = YOLO('YOLO_model/best.pt') 
        return model
    except Exception as e:
        st.error(f"モデルの読み込み中にエラーが発生しました: {e}")
        return None
    
if st.session_state.get("navigate_to_results", False):
    st.session_state.navigate_to_results = False
    st.switch_page("pages/result.py")

if 'run_id' not in st.session_state:
    st.session_state.run_id = 0
warning_message = None

# --- ゲーム設定チェック ---
if not st.session_state.get('players'):
    st.warning("ゲームが設定されていません。メインメニューに戻ります。")
    st.switch_page("main.py")

model = load_yolo_model()
current_month = st.session_state.current_month

scores_df = st.session_state.scores
total_scores = scores_df.sum()

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
st.divider()

# 現在の得点状況をダッシュボード風に表示
st.subheader('現在のスコア')

# 表示する列をプレイヤー数に合わせる
num_players = len(st.session_state.players)
if num_players >= 3:
    # プレイヤーが4人以上の場合、2行に分割する
    half_point = (num_players + 1) // 2 #切り上げで分割点を計算
    row1_cols = st.columns(half_point)
    row2_cols = st.columns(num_players - half_point)
    cols = row1_cols + row2_cols # 2つの行の列を結合
else:
    # 3人以下の場合は1行で表示
    cols = st.columns(num_players)
score_unit = st.session_state.game_rules.get("score_unit", "貫/点")
for i, player in enumerate(st.session_state.players):
    with cols[i]:
        total_score = total_scores.get(player, 0)
        
        # 前回の月から増えた点数（delta）を計算
        last_score = 0
        if not scores_df.empty:
            last_score = scores_df.iloc[-1].get(player, 0)

        st.metric(
            label=f"👤 {player}",
            value=format_score(total_score, score_unit),
            delta=format_score(last_score, score_unit, delta_mode=True) if last_score != 0 else ""
        )
st.divider()

with st.expander("プレイヤーを途中参加させる"):
    def add_player_callback():
        if len(st.session_state.players) >= 7:
            st.error("プレイヤーが上限の7人に達しているため、これ以上追加できません。")
            return 
        new_player_name = st.session_state.new_player_name_input
        new_player_score = st.session_state.new_player_initial_score_input
        if new_player_name:
            # 現在のプレイヤー名と新しい名前を結合して、重複チェック
            combined_names = st.session_state.players + [new_player_name]
            unique_names = setting.generate_unique_names(combined_names)            
            # 新しく追加されたプレイヤーのユニーク名を取得
            added_player_unique_name = unique_names[-1]
            # セッション情報を更新
            st.session_state.players.append(added_player_unique_name)
            st.session_state.scores[added_player_unique_name] = 0     
            st.session_state.scores.iloc[0, st.session_state.scores.columns.get_loc(added_player_unique_name)] = new_player_score     
            st.success(f"プレイヤー「{added_player_unique_name}」が参加しました！")
            st.session_state.new_player_name_input = ""
            if st.session_state.game_rules["game_name"] == "八八":
                st.session_state.new_player_initial_score_input = 60
            else: st.session_state.new_player_initial_score_input = 0 # 初期値に戻す            
        else:
            st.warning("プレイヤー名を入力してください。")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.session_state.game_rules["game_name"] == "八八":
            st.session_state.new_player_initial_score_input = 60
        else: st.session_state.new_player_initial_score_input = 0
        st.text_input("新しいプレイヤーの名前", key="new_player_name_input", placeholder="プレイヤー名")
    with col2: 
        score = st.number_input(f'初期得点{i+1}', key=f'new_player_initial_score_input', min_value=0, step=1, label_visibility="collapsed",value=st.session_state.new_player_initial_score_input)
    st.button("このプレイヤーを追加する", on_click=add_player_callback)

st.title(f'✍️ {current_month}月の得点入力')
# ジャンプ先の目印（アンカー）を設置
st.markdown("<a id='top_anchor'></a>", unsafe_allow_html=True)
if 'monthly_scores' not in st.session_state:
    st.session_state.monthly_scores = {}

st.divider()
st.subheader('今月の設定')

# プレイヤーが4人以上の場合に「出る・降りる」選択を表示
game_rules = st.session_state.game_rules
num_players = len(st.session_state.players)
active_players_options = st.session_state.players
orita_players = [p for p in st.session_state.players if p not in st.session_state.get('active_players', [])]

if num_players >= 4:
    st.multiselect(
        "今月勝負するプレイヤー（出る人）を選択",
        options=st.session_state.players,
        default=st.session_state.players,
        key='active_players'
    )
    if len(st.session_state.active_players) < 2:
        st.warning("最低でも2人は勝負に参加する必要があります。")
    if game_rules.get("enable_orichin") or game_rules.get("enable_oikomi") or game_rules.get("enable_mizuten"):
        with st.expander("下り賃・追い込み賃・みずてんの設定"):
            # みずてん
            if game_rules.get("enable_mizuten"):
                st.selectbox("みずてんのプレイヤー", options=['なし'] + st.session_state.active_players, key='mizuten_player')
                st.divider()

            # 下り賃・追い込み賃
            if orita_players:
                st.write("**下りたプレイヤーの設定**")
                cols = st.columns(len(orita_players))
                for i, player in enumerate(orita_players):
                    with cols[i]:
                        st.write(f"**{player}**")
                        if game_rules.get("enable_orichin"):
                            st.number_input("下り賃", min_value=0, step=1, key=f'orichin_{player}')
                        if game_rules.get("enable_oikomi"):
                            st.number_input("追い込み賃", min_value=0, step=1, key=f'oikomichin_{player}')
            else:
                st.info("下りたプレイヤーがいないため、下り賃・追い込み賃の入力欄はありません。")
elif num_players < 4 and 'active_players' not in st.session_state:
    st.session_state.active_players = st.session_state.players

if game_rules.get("zetsuba_oba", True):
    ba_options = ("小場 (x1)", "大場 (x2)", "絶場 (x4)")
    st.radio("場の状況", options=ba_options, key='ba_status', horizontal=True)

# 倍率設定UI
st.number_input("追加の倍率", min_value=1, step=1, key='custom_multiplier')
ba_choice = st.session_state.get('ba_status', '小場 (x1)')
ba_multiplier = 1
if "大場" in ba_choice: ba_multiplier = 2
if "絶場" in ba_choice: ba_multiplier = 4

custom_multiplier = st.session_state.get('custom_multiplier', 1)
multiplier = ba_multiplier * custom_multiplier

st.divider()
st.subheader('今回の得点を入力')
# ---手役の処理 ---
with st.expander("手役が成立した場合"):
    # 勝負しているプレイヤー全員分の入力欄を作成
    display_players = st.session_state.get('active_players', st.session_state.players)
    active_teyaku = [name for name, data in st.session_state.game_rules['teyaku'].items() if data['active']]
    
    # プレイヤーの人数に応じて列を分割
    num_display_players = len(display_players)
    if num_display_players > 0:
        cols = st.columns(num_display_players)
        for i, player in enumerate(display_players):
            with cols[i]:
                selected_teyaku = st.multiselect(
                    f"**{player}**さんの手役",
                    options=active_teyaku,
                    key=f'teyaku_selection_{player}' 
                )
                tobikomi_yaku = {"三本", "立三本"}
                nukeyaku_yaku = {"赤", "短一", "十一", "空素"}

                # setを使って選択された役と条件役の共通部分があるかチェック
                if not tobikomi_yaku.isdisjoint(selected_teyaku):
                    st.checkbox("飛び込み (+12点)", key=f"tobikomi_{player}")
                
                if not nukeyaku_yaku.isdisjoint(selected_teyaku):
                    st.checkbox("抜け役 (+12点)", key=f"nukeyaku_{player}")

outcome_options = ("役なし（取り札勝負）", "出来役あり", "特殊役あり")
st.radio("今月の勝負の決まり方を選択", options=outcome_options, key='outcome_type', horizontal=True)
outcome_type = st.session_state.outcome_type

active_players_list = st.session_state.get('active_players', st.session_state.players)
base_scores = {}
base_score = 0

if outcome_type == "役なし（取り札勝負）":
    for player in active_players_list:
        st.subheader(f'"{player}" さんの入力欄')
        mode_options = ("取り札入力", "得点入力", "写真で自動入力")
        mode = st.selectbox("入力モード", options=mode_options, key=f'mode_select_{player}')
        st.session_state.input_modes[player] = mode
        if mode == "得点入力":
            st.number_input("獲得点数", step=1,min_value=0, key=f'manual_score_{player}', label_visibility="collapsed")
            base_scores[player] = st.session_state[f'manual_score_{player}']
        elif mode == "取り札入力":
            c1, c2, c3, c4 = st.columns(4)
            with c1: brights = st.number_input("光札", min_value=0, key=f'brights_{player}')
            with c2: animals = st.number_input("タネ", min_value=0, key=f'animals_{player}')
            with c3: ribbons = st.number_input("短冊", min_value=0, key=f'ribbons_{player}')
            with c4: chaff = st.number_input("カス", min_value=0, key=f'chaff_{player}')
            
            # 倍率を反映した計算結果を表示
            base_score = calculate_score_from_cards(brights, animals, ribbons, chaff)
            final_score = base_score * multiplier
            st.info(f"計算結果: {base_score}点 × {multiplier}倍 = **{final_score}点**")
            base_scores[player] = base_score

        elif mode == "写真で自動入力":
            detections_key = f'detections_{player}'
            last_photo_hash_key = f'last_photo_hash_{player}'
            tab1, tab2 = st.tabs(["ファイルからアップロード", "カメラで撮影"])
            with tab1:
                uploaded_file = st.file_uploader("写真をアップロード", key=f'uploader_{player}_{st.session_state.run_id}', type=['jpg', 'jpeg', 'png'])
            with tab2:
                camera_file = st.camera_input("カメラで撮影", key=f'cam_input_{player}_{st.session_state.run_id}')
            
            image_buffer = uploaded_file or camera_file

            is_new_photo = False
            if image_buffer:
                # アップロードされたファイルの中身を読み取り、ハッシュ値を計算
                file_bytes = image_buffer.getvalue()
                current_photo_hash = hashlib.md5(file_bytes).hexdigest()
                # 保存されている前回のハッシュ値と比較
                if st.session_state.get(last_photo_hash_key) != current_photo_hash:
                    is_new_photo = True
            
            # 新しい画像の場合のみ、YOLOの認識処理を実行
            if is_new_photo:
                with st.spinner('画像を認識中...'):
                    st.session_state[detections_key] = calculate_score_from_image(image_buffer, model)
                    # 処理済みの画像のハッシュ値を保存
                    st.session_state[last_photo_hash_key] = current_photo_hash

            # 写真がクリアされた場合、関連する状態をリセット
            if not image_buffer and st.session_state.get(detections_key):
                st.session_state[detections_key] = []
                st.session_state[last_photo_hash_key] = None
                st.rerun()

            # 認識結果をエキスパンダーの中に表示
            if st.session_state.get(detections_key):
                with st.expander("認識されたカード一覧（クリックで表示/非表示）"):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write("**札の名前**")
                    c2.write("**信頼度**")
                    sorted_detections = sorted(st.session_state[detections_key], key=lambda x: x['conf'], reverse=True)
                    
                    if not sorted_detections:
                        st.write("カードがありません。")

                    for i, detection in enumerate(sorted_detections):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1: st.text(detection['name'])
                        with col2: st.progress(detection['conf'], text=f"{detection['conf']:.0%}")
                        with col3: st.button("削除", key=f"del_{player}_{i}", on_click=delete_detection_callback, args=(detections_key, i))
                    st.divider()

                # リアルタイムでスコアを再計算して表示
                current_detected_names = [d['name'] for d in st.session_state[detections_key]]
                base_score = calculate_points_from_detections(current_detected_names, game_rules)
                final_score = base_score * multiplier
                st.success(f"認識結果: {base_score}点 × {multiplier}倍 = **{final_score}点**")
            
            # 写真がクリアされた場合、関連する状態をリセット
            if not image_buffer and st.session_state.get(detections_key):
                st.session_state[detections_key] = []
                st.session_state[last_photo_hash_key] = None
                st.rerun()

            base_scores[player] = base_score

    if game_rules.get('game_name') == '八八':
        total_base_score = sum(base_scores.values())
        if total_base_score != 264 and total_base_score != 0:
            warning_message = f"警告: 参加プレイヤーの合計点が264点になりません (現在: {total_base_score}点)"

elif outcome_type == "出来役あり":
    st.selectbox("勝者", options=['なし'] + active_players_list, key='dekiyaku_winner')
    active_dekiyaku = [name for name, data in st.session_state.game_rules['dekiyaku'].items() if data['active']]
    selected_yaku = st.multiselect("成立した出来役", options=active_dekiyaku, key='dekiyaku_selection')
    if selected_yaku: 
        game_rules = st.session_state.game_rules
        st.markdown("###### 追加点の入力")
        for yaku in selected_yaku:
            # 役のデータに 'is_variable': True が設定されているかチェック
            if game_rules['dekiyaku'][yaku].get('is_variable', False):
                yaku_data = game_rules['dekiyaku'][yaku]
                st.number_input(
                    label=f"「{yaku}」の追加{yaku_data.get('item_unit', '枚')}", 
                    min_value=0, 
                    step=1, 
                    key=f"dekiyaku_extra_{yaku}" # ユニークなキー
                )    
    # 選択された役の中に法度適用役があるかチェック
    is_hatto_round = any(st.session_state.game_rules['dekiyaku'][yaku].get('hatto_applicable', False) for yaku in selected_yaku)
    if is_hatto_round:
        winner = st.session_state.get('dekiyaku_winner', 'なし')
        losers = [p for p in active_players_list if p != winner]
        st.multiselect("法度(ハット)を犯したプレイヤーを選択", options=losers, key='hatto_players')


elif outcome_type == "特殊役あり":
    st.selectbox("勝者", options=['なし'] + active_players_list, key='special_yaku_winner')
    active_special_yaku = [name for name, data in st.session_state.game_rules['special_yaku'].items() if data['active']]
    st.multiselect("成立した特殊な役", options=active_special_yaku, key='special_yaku_selection')
    st.info("※特殊役が成立した場合、手役の点数は無効になります。")

active_players_list = st.session_state.get('active_players', st.session_state.get('players', []))
is_button_disabled = len(active_players_list) < 2

# --- 記録ボタンにコールバック関数を指定 ---
st.button(f'{st.session_state.current_month}月の得点を記録する', type="primary", use_container_width=True, on_click=record_scores_callback,disabled=is_button_disabled)
if st.session_state.get("success_message"):
    st.success(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None # 一度表示したら消す
if len(active_players_list) < 2:
    st.session_state.form_error = "参加者が2人未満です。出る人を2人以上選択してください。"
# ボタンの直下で、session_stateにエラーメッセージがあれば表示する
if st.session_state.get("form_error"):
    st.error(st.session_state.form_error)
    # 一度表示したらメッセージをクリア
    st.session_state.form_error = None
if warning_message:
    st.warning(warning_message)

# --- ページ下部のナビゲーション ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button('メインメニューに戻る', use_container_width=True):
        st.switch_page("main.py")
with c2:
    if st.button('ゲームを終了してリザルトへ', type="secondary", use_container_width=True):
        st.switch_page("pages/result.py")
