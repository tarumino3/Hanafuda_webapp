import streamlit as st
import pandas as pd
import collections
from PIL import Image
from rules import TYPE_ABBREVIATION_MAP, ITSUMONO_HACHIHACHI_RULES, DEFAULT_HACHIHACHI_RULES, DEFAULT_KOIKOI_RULES

def create_yaku_editor(yaku_type_jp, yaku_type_en):
    """出来役と手役の編集UIを生成する共通関数"""
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    c1.write("**役の名前**")
    c2.write("**点数**")
    c3.write("**有効/無効**")
    c4.write("**法度適用**")
    
    for name, data in list(st.session_state.game_rules[yaku_type_en].items()):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            st.write(name)
        with c2:
            input_col, display_col = st.columns([1, 2])

            with input_col:
                st.number_input(
                    "点数", 
                    value=data['score'], 
                    key=f'score_{yaku_type_en}_{name}', 
                    on_change=update_yaku_score, 
                    args=(yaku_type_en, name), 
                    label_visibility="collapsed"
                )        
            # score_unitが「貫/点」の場合のみ、換算値を表示
            score = data['score']
            if st.session_state.game_rules.get("score_unit") == "貫/点" and score > 0:
                kan, ten = divmod(score, 12)
                with display_col:
                    st.markdown(f"<div style='padding-top: 8px;'>({kan}貫{ten}点)</div>", unsafe_allow_html=True)
        with c3:
            st.toggle(
                "有効", 
                value=data['active'], 
                key=f'toggle_{yaku_type_en}_{name}', 
                on_change=toggle_yaku_active, 
                args=(yaku_type_en, name), 
                label_visibility="collapsed"
            )
        if yaku_type_en == 'dekiyaku':
            with c4:
                st.toggle(
                    "法度", 
                    value=data.get('hatto_applicable', False), 
                    key=f'hatto_{yaku_type_en}_{name}', 
                    on_change=toggle_yaku_hatto, 
                    args=(yaku_type_en, name), 
                    label_visibility="collapsed"
                )

    st.write("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.text_input("新しい役の名前", key=f'new_{yaku_type_en}_name')
    with c2:
        st.number_input("点数", min_value=0, key=f'new_{yaku_type_en}_score', label_visibility="collapsed")
    with c3:
        st.button("追加", key=f'add_{yaku_type_en}', on_click=add_yaku, args=(yaku_type_en,))

def generate_unique_names(names):
    counts = collections.Counter(names)
    duplicates = {name for name, count in counts.items() if count > 1}
    new_names, suffix_counters = [], collections.defaultdict(int)
    for name in names:
        if name in duplicates:
            suffix_counters[name] += 1
            new_names.append(f"{name}_{suffix_counters[name]}")
        else:
            new_names.append(name)
    return new_names

def load_preset(game_type):
    if game_type == '八八':
        st.session_state.game_rules = DEFAULT_HACHIHACHI_RULES.copy()
    elif game_type == 'こいこい':
        st.session_state.game_rules = DEFAULT_KOIKOI_RULES.copy()
    elif game_type == 'いつもの八八':
        st.session_state.game_rules = ITSUMONO_HACHIHACHI_RULES.copy()

def toggle_yaku_active(yaku_type, yaku_name):
    """役の有効/無効を切り替えるコールバック"""
    current_status = st.session_state.game_rules[yaku_type][yaku_name]['active']
    st.session_state.game_rules[yaku_type][yaku_name]['active'] = not current_status

def update_yaku_score(yaku_type, yaku_name):
    """役の点数を更新するコールバック"""
    key = f'score_{yaku_type}_{yaku_name}'
    if key in st.session_state:
        st.session_state.game_rules[yaku_type][yaku_name]['score'] = st.session_state[key]

def add_yaku(yaku_type):
    """新しい役を追加するコールバック"""
    new_name = st.session_state[f'new_{yaku_type}_name']
    new_score = st.session_state[f'new_{yaku_type}_score']
    if new_name and new_name not in st.session_state.game_rules[yaku_type]:
        st.session_state.game_rules[yaku_type][new_name] = {"score": new_score, "active": True}
        st.session_state[f'new_{yaku_type}_name'] = ""
        st.session_state[f'new_{yaku_type}_score'] = 0

def toggle_yaku_hatto(yaku_type, yaku_name):
    """役の法度適用を切り替えるコールバック"""
    if yaku_name in st.session_state.game_rules[yaku_type]:
        current_status = st.session_state.game_rules[yaku_type][yaku_name].get('hatto_applicable', False)
        st.session_state.game_rules[yaku_type][yaku_name]['hatto_applicable'] = not current_status
    else:
        st.warning(f"Warning: 役'{yaku_name}'が見つかりませんでした。")

def format_score(score, unit, delta_mode=False):
    """指定された単位に合わせてスコアをフォーマットする"""
    score = int(round(score))
    if unit == "貫/点":
        kan = score // 12
        ten = score % 12
        display_val = f"{score} 点\n({kan}貫{ten}点)"
        delta_val = f"{score} 点"
        return display_val if not delta_mode else delta_val
    else: 
        return f"{score} 文"

def calculate_score_from_cards(brights, animals, ribbons, chaff):
    """取り札の枚数から点数を計算する関数"""
    card_scores = st.session_state.game_rules['card_scores']
    score = (
        brights * card_scores.get('光', 0) +
        animals * card_scores.get('タネ', 0) +
        ribbons * card_scores.get('短冊', 0) +
        chaff * card_scores.get('カス', 0)
    )
    return int(score)

def calculate_points_from_detections(detected_card_names, game_rules):
    """認識されたカード名のリストから、取り札の合計点を計算する関数"""
    counts = {"光": 0, "タネ": 0, "短冊": 0, "カス": 0}
    for card_name in detected_card_names:
        try:
            type_abbr = card_name.split('-')[1]
            card_type = TYPE_ABBREVIATION_MAP.get(type_abbr, "カス") # 不明なものはカスとして扱う
            counts[card_type] += 1
        except IndexError:
            continue
    
    return calculate_score_from_cards(
        counts["光"], counts["タネ"], counts["短冊"], counts["カス"]
    )
def calculate_score_from_image(uploaded_file, yolo_model):
    """画像からYOLOで認識し、カード名、信頼度、合計点を返す関数"""
    if yolo_model is None:
        return 0, []
    try:
        image = Image.open(uploaded_file).convert("RGB")
        results = yolo_model(image)
        
        boxes = results[0].boxes
        detected_indices = boxes.cls.tolist()
        confidences = boxes.conf.tolist()
        class_names = yolo_model.names
        
        confidence_threshold = 0.5 
        
        # 認識結果を構築する際に、信頼度がしきい値以上のものだけをリストに含める
        detections = [
            {"name": class_names[int(i)], "conf": conf}
            for i, conf in zip(detected_indices, confidences)
            if conf >= confidence_threshold
        ]

        return detections
    except Exception as e:
        st.error(f"画像処理中にエラーが発生しました: {e}")
        return []

def record_scores_callback():
    # --- Step 1: 準備 ---
    st.session_state.form_error = None
    st.session_state.score_sum_warning = None
    active_players = st.session_state.get('active_players', st.session_state.players)
    orita_players = [p for p in st.session_state.players if p not in active_players]
    game_rules = st.session_state.game_rules

    if len(st.session_state.players) >= 4 and len(active_players) < 2:
        st.session_state.form_error = "参加者が2人未満です。出る人を2人以上選択してください。"
        return

    # --- Step 2: その月の参加者間のスコア変動を記録する辞書を初期化 ---
    monthly_score_change = {player: 0 for player in active_players}
    outcome_type = st.session_state.get('outcome_type', '役なし（取り札勝負）')

    # --- Step 3: 主得点を計算 ---
    # A) 役なし（取り札勝負）の場合
    if outcome_type == "役なし（取り札勝負）":
        base_scores = {}
        for player in active_players:
            mode = st.session_state.input_modes.get(player, "取り札入力")
            if mode == "得点入力":
                base_scores[player] = st.session_state.get(f'manual_score_{player}', 0)
            elif mode == "取り札入力":
                b = st.session_state.get(f'brights_{player}', 0); a = st.session_state.get(f'animals_{player}', 0)
                r = st.session_state.get(f'ribbons_{player}', 0); c = st.session_state.get(f'chaff_{player}', 0)
                base_scores[player] = calculate_score_from_cards(b, a, r, c)
            elif mode == "写真で自動入力":
                # session_stateに保存された認識結果からスコアを計算
                detections = st.session_state.get(f'detections_{player}', [])
                detected_names = [d['name'] for d in detections]
                base_scores[player] = calculate_points_from_detections(detected_names, game_rules)
        
        if len(active_players) == 2:
            # 【2人プレイの場合】 点差を直接やり取り
            p1, p2 = active_players
            score1 = base_scores.get(p1, 0)
            score2 = base_scores.get(p2, 0)
            difference = abs(score1 - score2)
            
            if score1 > score2:
                monthly_score_change[p1] = difference
                monthly_score_change[p2] = -difference
            elif score2 > score1:
                monthly_score_change[p1] = -difference
                monthly_score_change[p2] = difference
            # 同点の場合は変動なし (初期値0のまま)

        elif len(active_players) > 2:
            avg = sum(base_scores.values()) / len(active_players)
            float_s = {p: base_scores.get(p, 0) - avg for p in active_players}
            rounded_s = {p: int(round(s)) for p, s in float_s.items()}
            err = sum(rounded_s.values())
            if err != 0 and base_scores:
                winner = max(base_scores, key=base_scores.get); rounded_s[winner] -= err
            monthly_score_change = rounded_s

    # B) 役で勝負が決まる場合
    else:
        yaku_type_en, state_prefix = "", ""
        if outcome_type == "出来役あり": yaku_type_en, state_prefix = "dekiyaku", "dekiyaku"
        else: yaku_type_en, state_prefix = "special_yaku", "special_yaku"

        winner = st.session_state.get(f'{state_prefix}_winner', 'なし')
        if winner != 'なし' and winner in active_players:
            selected_yaku = st.session_state.get(f'{state_prefix}_selection', [])
            total_yaku_score = 0
            for yaku in selected_yaku:
                yaku_data = game_rules[yaku_type_en][yaku]
                base_score = yaku_data['score']
                if yaku_data.get('is_variable', False):
                    extra_items = st.session_state.get(f'{state_prefix}_extra_{yaku}', 0)
                    base_score += extra_items * yaku_data.get('per_item_score', 1)
                total_yaku_score += base_score

            losers = [p for p in active_players if p != winner]
            hatto_players = st.session_state.get('hatto_players', [])
            is_hatto_round = any(game_rules['dekiyaku'][yaku].get('hatto_applicable', False) for yaku in selected_yaku)

            winner_gain = 0
            if outcome_type == "出来役あり":
                hatto_players = st.session_state.get('hatto_players', [])
                is_hatto_round = any(game_rules['dekiyaku'][yaku].get('hatto_applicable', False) for yaku in selected_yaku)
                
                if is_hatto_round and hatto_players:
                    # 法度が発生した場合の特別な精算
                    winner_gain = 0
                    for loser in losers:
                        if loser in hatto_players:
                            payment = total_yaku_score * 2 
                            monthly_score_change[loser] = -payment
                            winner_gain += payment
                        else:
                            monthly_score_change[loser] = 0
                    monthly_score_change[winner] = winner_gain
                else:
                    # 法度がない通常の役での勝利
                    if losers:
                        monthly_score_change[winner] = total_yaku_score * len(losers)
                        for loser in losers:
                            monthly_score_change[loser] = -total_yaku_score
            else: # 特殊役の場合は法度を考慮しない
                if losers:
                    monthly_score_change[winner] = total_yaku_score * len(losers)
                    for loser in losers:
                        monthly_score_change[loser] = -total_yaku_score

    if outcome_type != "特殊役あり":
        teyaku_totals = {}
        for p in active_players:
            selected_teyaku = st.session_state.get(f'teyaku_selection_{p}', [])
            base_teyaku_score = sum(game_rules['teyaku'][y]['score'] for y in selected_teyaku)
            
            # チェックボックスがONならボーナス点を加算
            if st.session_state.get(f'tobikomi_{p}', False):
                base_teyaku_score += 12
            if st.session_state.get(f'nukeyaku_{p}', False):
                base_teyaku_score += 12
            
            teyaku_totals[p] = base_teyaku_score
        if any(teyaku_totals.values()):
            for p1 in active_players:
                for p2 in active_players:
                    if p1 != p2: monthly_score_change[p1] += teyaku_totals[p1] - teyaku_totals[p2]

    orita_players = [p for p in st.session_state.players if p not in active_players]

    scores_to_record = {player: 0 for player in st.session_state.players}
    for player in st.session_state.players:
        scores_to_record[player] = monthly_score_change.get(player, 0)

    if game_rules.get("enable_orichin", False) and orita_players and monthly_score_change:
        winner_for_orichin = max(monthly_score_change, key=monthly_score_change.get)
        for player in orita_players:
            orichin = st.session_state.get(f'orichin_{player}', 0)
            if orichin > 0:
                scores_to_record[player] -= orichin
                scores_to_record[winner_for_orichin] += orichin
    
    if game_rules.get("enable_oikomi", False) and orita_players and active_players:
        for player in orita_players:
            oikomichin = st.session_state.get(f'oikomichin_{player}', 0)
            if oikomichin > 0:
                scores_to_record[player] += oikomichin * len(active_players)
                for active_player in active_players:
                    scores_to_record[active_player] -= oikomichin

    if game_rules.get("enable_mizuten", False):
        mizuten_player = st.session_state.get('mizuten_player', 'なし')
        if mizuten_player != 'なし':
            scores_to_record[mizuten_player] += 12 * (len(st.session_state.players) - 1)
            for player in st.session_state.players:
                if player != mizuten_player:
                    scores_to_record[player] -= 12

    # Step 4: 場の状況に応じて点数を倍化
    ba_multiplier = 1
    if game_rules.get("zetsuba_oba", True):
        ba_choice = st.session_state.get('ba_status', '小場 (x1)')
        if "大場" in ba_choice: ba_multiplier = 2
        if "絶場" in ba_choice: ba_multiplier = 4
    
    # 次に追加の倍率を取得
    custom_multiplier = st.session_state.get('custom_multiplier', 1)

    # 最終的な倍率を計算
    final_multiplier = ba_multiplier * custom_multiplier
    
    if final_multiplier > 1:
        for player in active_players:
            scores_to_record[player] *= final_multiplier
  
    final_scores_to_record = {player: int(round(score)) for player, score in scores_to_record.items()}
    new_row = pd.DataFrame([final_scores_to_record], index=[f'{st.session_state.current_month}月'])
    st.session_state.scores = pd.concat([st.session_state.scores, new_row])
    st.session_state.current_month += 1
    
    game_rules = st.session_state.game_rules 
    for player in st.session_state.players:
        # 点数入力・取り札入力
        st.session_state[f'manual_score_{player}'] = 0
        st.session_state[f'brights_{player}'] = 0
        st.session_state[f'animals_{player}'] = 0
        st.session_state[f'ribbons_{player}'] = 0
        st.session_state[f'chaff_{player}'] = 0
        # 役選択
        st.session_state[f'yaku_dekiyaku_{player}'] = []
        st.session_state[f'teyaku_selection_{player}'] = []
        st.session_state[f'tobikomi_{player}'] = False
        st.session_state[f'nukeyaku_{player}'] = False
        # 下り賃・追い込み賃
        st.session_state[f'orichin_{player}'] = 0
        st.session_state[f'oikomichin_{player}'] = 0
        # 写真モード関連
        st.session_state[f'uploader_{player}'] = None
        st.session_state[f'cam_input_{player}'] = None
        st.session_state[f'detections_{player}'] = []
        st.session_state[f'last_photo_hash_{player}'] = None

    # 月ごとの設定をリセット
    st.session_state.active_players = st.session_state.players
    st.session_state.ba_status = "小場 (x1)"
    st.session_state.custom_multiplier = 1
    st.session_state.input_modes = {}
    if game_rules.get('game_name') == 'こいこい':
        st.session_state.outcome_type = '出来役あり'
    else:
        st.session_state.outcome_type = '役なし（取り札勝負）'
    st.session_state.dekiyaku_winner = 'なし'; st.session_state.dekiyaku_selection = []
    st.session_state.special_yaku_winner = 'なし'; st.session_state.special_yaku_selection = []
    st.session_state.hatto_players = []; st.session_state.mizuten_player = 'なし'
    # 可変点数役の入力欄をリセット
    for yaku_type_en in ['dekiyaku', 'special_yaku']:
        if yaku_type_en in game_rules:
            for yaku, data in game_rules[yaku_type_en].items():
                if data.get('is_variable', False): 
                    st.session_state[f'{yaku_type_en}_extra_{yaku}'] = 0
    if st.session_state.current_month > 12:
        st.session_state.navigate_to_results = True
    else:
        month_recorded = st.session_state.current_month - 1
        st.session_state.run_id += 1  # run_idをインクリメントして、次の入力に備える
        st.session_state.success_message = f"{month_recorded}月のスコアを記録しました。 [今月の設定に戻る](#top_anchor)"