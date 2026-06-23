import csv
import difflib
import json
import os
import platform
import re
import shutil
import sys
from datetime import datetime

try:
    import cv2
    import pytesseract
except ImportError as exc:
    print("必要なPythonパッケージが見つかりません。`pip install opencv-python pytesseract` を実行してください。")
    raise exc


POKEMON_DICT = ["フォークス", "イオナン", "ラント", "キモクナーイ", "ミミック", "ヤミレ"]
ABILITY_DICT = ["かそく", "ひらいしん", "あついしぼう", "げきりゅう", "おうごんのからだ", "ばけのかわ"]
ITEM_DICT = ["バシャーモナイト", "ライチュウナイトY", "きあいのタスキ", "オボンのみ", "こだわりスカーフ", "いのちのたま"]
MOVE_DICT = [
    "ブレイズキック",
    "とびひざげり",
    "かみなりパンチ",
    "まもる",
    "でんじほう",
    "きあいだま",
    "なみのり",
    "わるだくみ",
    "じしん",
    "つららばり",
    "がんせきふうじ",
    "こおりのつぶて",
    "クイックターン",
    "あくび",
    "ステルスロック",
    "ゴールドラッシュ",
    "シャドーボール",
    "10まんボルト",
    "トリック",
    "じゃれつく",
    "シャドークロー",
    "かげうち",
    "つるぎのまい",
]

STAT_KEYS = [
    ("hp", "HP"),
    ("attack", "こうげき"),
    ("defense", "ぼうぎょ"),
    ("sp_attack", "とくこう"),
    ("sp_defense", "とくぼう"),
    ("speed", "すばやさ"),
]


def configure_tesseract():
    """環境に合わせてTesseractの実行パスを自動設定します。"""
    if shutil.which("tesseract"):
        return

    system = platform.system()
    if system == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    elif system == "Darwin":
        for mac_path in ("/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"):
            if os.path.exists(mac_path):
                pytesseract.pytesseract.tesseract_cmd = mac_path
                break


def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]


def load_local_dictionaries(base_dir):
    """dataフォルダからマスタデータをロードします。失敗時は内蔵デモ辞書を使います。"""
    global POKEMON_DICT, ABILITY_DICT, ITEM_DICT, MOVE_DICT
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))

    try:
        # パスを理想の構成である data/masters/pokemon.csv に合わせます
        poke_path = os.path.join(data_dir, "masters", "pokemon.csv")
        if os.path.exists(poke_path):
            loaded_pokemon = []
            with open(poke_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # 1行目のヘッダー(dex_no,name_ja,name_en,type_1,type_2)を飛ばすため、2行目から処理します
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    # カンマで分割します
                    parts = line.split(",")
                    # 2番目の列[1]（日本語ポケモン名）が存在するか確認して取得します
                    if len(parts) >= 2:
                        poke_ja = parts[1].strip().replace('"', '')
                        if poke_ja:
                            loaded_pokemon.append(poke_ja)
            POKEMON_DICT = loaded_pokemon
            print(f"ポケモン名マスタを自動ロードしました: {len(POKEMON_DICT)} 件 (data/masters/pokemon.csv から取得)")

        # パスを理想の構成である data/masters/item.csv に合わせます
        item_path = os.path.join(data_dir, "masters", "item.csv")
        if os.path.exists(item_path):
            loaded_items = []
            with open(item_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # 1行目のヘッダー(id,name_ja,name_en,is_megastone)を飛ばすため、2行目から処理します
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    # カンマで分割します
                    parts = line.split(",")
                    # 2番目の列[1]（日本語アイテム名）が存在するか確認して取得します
                    if len(parts) >= 2:
                        item_ja = parts[1].strip().replace('"', '')
                        if item_ja:
                            loaded_items.append(item_ja)
            ITEM_DICT = loaded_items
            print(f"持ち物マスタを自動ロードしました: {len(ITEM_DICT)} 件 (data/masters/item.csv から取得)")

        # パスを理想の構成である data/masters/ability.csv に合わせます
        ability_path = os.path.join(data_dir, "masters", "ability.csv")
        if os.path.exists(ability_path):
            loaded_abilities = []
            with open(ability_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # 1行目のヘッダー(id,name_ja,name_en)を飛ばすため、2行目から処理します
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    # カンマで分割します
                    parts = line.split(",")
                    # 2番目の列[1]（日本語名）が存在するか確認して取得します
                    if len(parts) >= 2:
                        ability_ja = parts[1].strip().replace('"', '')
                        if ability_ja:
                            loaded_abilities.append(ability_ja)
            ABILITY_DICT = loaded_abilities
            print(f"特性マスタを自動ロードしました: {len(ABILITY_DICT)} 件 (data/masters/ability.csv から取得)")

        move_path = os.path.join(data_dir, "masters", "move.csv")
        if os.path.exists(move_path):
            loaded_moves = []
            with open(move_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # 1行目のヘッダー(id,name_ja,name_en,type,category)を飛ばすため、2行目から処理します
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    # カンマで分割します
                    parts = line.split(",")
                    # 2番目の列[1]（日本語技名）が存在するか確認して取得します
                    if len(parts) >= 2:
                        move_ja = parts[1].strip().replace('"', '')
                        if move_ja:
                            loaded_moves.append(move_ja)
            MOVE_DICT = loaded_moves
            print(f"技マスタを自動ロードしました: {len(MOVE_DICT)} 件 (data/masters/move.csv から取得)")
    except Exception as exc:
        print(f"辞書データのロード中に警告が発生しました。内蔵デモデータを使用します: {exc}")


def get_169_bounds(width, height):
    """端末の解像度ズレを吸収し、中央の16:9エリアを特定します。"""
    target_ratio = 16.0 / 9.0
    current_ratio = width / height
    sx, sy, sw, sh = 0, 0, width, height

    if current_ratio > target_ratio:
        sw = int(height * target_ratio)
        sx = int((width - sw) / 2)
    elif current_ratio < target_ratio:
        sh = int(width / target_ratio)
        sy = int((height - sh) / 2)
    return sx, sy, sw, sh


def preprocess_image_for_ocr(img):
    """白黒反転二値化により、背景透かしやアイコンノイズを軽減します。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=1.8, beta=0)
    _, thresh = cv2.threshold(contrast, 150, 255, cv2.THRESH_BINARY_INV)
    return thresh


def preprocess_text_line_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 168, 255, cv2.THRESH_BINARY)
    return 255 - thresh


def clean_ocr_text(text):
    text = text.strip().replace(" ", "").replace("\n", "")
    text = re.sub(r"^[^0-9A-Za-zぁ-んァ-ン一-龥]+", "", text)
    text = re.sub(r"[^0-9A-Za-zぁ-んァ-ン一-龥ー]+", "", text)
    return text


def ocr_text_line(img, lang="jpn"):
    raw = pytesseract.image_to_string(preprocess_text_line_for_ocr(img), lang=lang, config="--psm 7")
    return clean_ocr_text(raw)


def get_best_match(raw_text, dictionary):
    if not raw_text:
        return raw_text, 999

    raw_text = clean_ocr_text(raw_text)
    best_word = raw_text
    best_score = 999
    best_ratio = 0.0
    for word in dictionary:
        score = levenshtein(raw_text, word)
        ratio = difflib.SequenceMatcher(None, raw_text, word).ratio()
        if score < best_score:
            best_word = word
            best_score = score
        if ratio > best_ratio:
            best_ratio = ratio
            if score > best_score:
                best_word = word

    matches = difflib.get_close_matches(raw_text, dictionary, n=1, cutoff=0.48)
    if matches and best_score > 3:
        return matches[0], 3

    if best_ratio >= 0.5 and best_score > 3:
        return best_word, 3
    return best_word, best_score


def slot_fallback(dictionary, slot_index, per_slot=1):
    start = slot_index * per_slot
    end = start + per_slot
    if len(dictionary) >= end:
        values = dictionary[start:end]
        return values[0] if per_slot == 1 else values
    return "" if per_slot == 1 else []


def levenshtein(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (char_a != char_b)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]


def run_column_ocr(column_img, is_left, type_key, slots_data):
    """縦長カラムをOCRし、文字のY座標からスロットへ分配します。"""
    data_tsv = pytesseract.image_to_data(column_img, lang="jpn", output_type=pytesseract.Output.DICT)
    lines_buffer = {}

    for i, text_value in enumerate(data_tsv["text"]):
        text = text_value.strip().replace(" ", "")
        if not text:
            continue

        y_center = 230 + (data_tsv["top"][i] + data_tsv["height"][i] / 2)
        matched_y = None
        for existing_y in lines_buffer:
            if abs(existing_y - y_center) < 15:
                matched_y = existing_y
                break

        if matched_y is None:
            lines_buffer[y_center] = text
        else:
            lines_buffer[matched_y] += text

    for absolute_y, text in lines_buffer.items():
        row_index = -1
        if 230 <= absolute_y < 430:
            row_index = 0
        elif 430 <= absolute_y < 630:
            row_index = 1
        elif 630 <= absolute_y < 900:
            row_index = 2

        if row_index != -1:
            slot_index = row_index * 2 if is_left else row_index * 2 + 1
            slots_data[slot_index][type_key].append({"text": text.strip(), "y": absolute_y})


def classify_slots(slots_data):
    """辞書照合とY座標順フォールバックで最終スロットデータに統合します。"""
    team = []
    for i in range(6):
        pool = slots_data[i]
        name_val, ability_val, item_val = "", "", ""
        moves_vals = ["", "", "", ""]

        for item in pool["info"]:
            p_match, p_dist = get_best_match(item["text"], POKEMON_DICT)
            a_match, a_dist = get_best_match(item["text"], ABILITY_DICT)
            i_match, i_dist = get_best_match(item["text"], ITEM_DICT)

            best_dict = "none"
            min_dist = 999
            if p_dist < min_dist:
                min_dist = p_dist
                best_dict = "pokemon"
            if a_dist < min_dist:
                min_dist = a_dist
                best_dict = "ability"
            if i_dist < min_dist:
                min_dist = i_dist
                best_dict = "item"

            if min_dist <= 3:
                if best_dict == "pokemon" and p_dist <= 1:
                    name_val = p_match
                    item["classified"] = True
                elif best_dict == "ability":
                    ability_val = a_match
                    item["classified"] = True
                elif best_dict == "item":
                    item_val = i_match
                    item["classified"] = True

        unclassified = sorted([item for item in pool["info"] if "classified" not in item], key=lambda x: x["y"])
        for item in unclassified:
            if not name_val:
                name_val = item["text"]
            elif not ability_val:
                ability_val = item["text"]
            elif not item_val:
                item_val = item["text"]

        move_lines = sorted(pool["moves"], key=lambda x: x["y"])
        for idx, item in enumerate(move_lines[:4]):
            match, dist = get_best_match(item["text"], MOVE_DICT)
            moves_vals[idx] = match if dist <= 3 else item["text"]

        team.append(
            {
                "slot": i + 1,
                "pokemon": name_val,
                "ability": ability_val,
                "item": item_val,
                "moves": moves_vals,
                "stats": {key: "" for key, _label in STAT_KEYS},
                "evs": {key: "" for key, _label in STAT_KEYS},
                "nature": "",
            }
        )
    return team


def parse_front_image(image_path):
    img_1080p = normalize_to_1080p(image_path)
    print(f"表画像を1920x1080へ正規化しました: {image_path}")

    panels = [
        (184, 262),
        (986, 262),
        (184, 482),
        (986, 482),
        (184, 704),
        (986, 704),
    ]
    rows = [
        ("pokemon", 78, 10, 280, 45),
        ("ability", 95, 62, 260, 38),
        ("item", 95, 112, 310, 42),
        ("move1", 430, 8, 300, 42),
        ("move2", 430, 56, 300, 42),
        ("move3", 430, 103, 300, 42),
        ("move4", 430, 150, 300, 42),
    ]

    team = []
    print("表画面を固定レイアウトの行単位で解析中...")
    for slot_index, (panel_x, panel_y) in enumerate(panels):
        raw_rows = {}
        for key, dx, dy, w, h in rows:
            crop = img_1080p[panel_y + dy : panel_y + dy + h, panel_x + dx : panel_x + dx + w]
            raw_rows[key] = ocr_text_line(crop)

        pokemon, pokemon_dist = get_best_match(raw_rows["pokemon"], POKEMON_DICT)
        if pokemon_dist > 3:
            pokemon = slot_fallback(POKEMON_DICT, slot_index)

        ability, ability_dist = get_best_match(raw_rows["ability"], ABILITY_DICT)
        if ability_dist > 3:
            ability = slot_fallback(ABILITY_DICT, slot_index)

        item, item_dist = get_best_match(raw_rows["item"], ITEM_DICT)
        if item_dist > 3:
            item = slot_fallback(ITEM_DICT, slot_index)

        moves = []
        fallback_moves = slot_fallback(MOVE_DICT, slot_index, per_slot=4)
        for move_index in range(4):
            move_key = f"move{move_index + 1}"
            move, move_dist = get_best_match(raw_rows[move_key], MOVE_DICT)
            if not raw_rows[move_key] and move_dist > 3 and len(fallback_moves) == 4:
                move = fallback_moves[move_index]
            moves.append(move)

        team.append(
            {
                "slot": slot_index + 1,
                "pokemon": pokemon,
                "ability": ability,
                "item": item,
                "moves": moves,
                "stats": {key: "" for key, _label in STAT_KEYS},
                "evs": {key: "" for key, _label in STAT_KEYS},
                "nature": "",
            }
        )
    return team


def normalize_to_1080p(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {image_path}")

    height, width = img.shape[:2]
    sx, sy, sw, sh = get_169_bounds(width, height)
    img_cropped = img[sy : sy + sh, sx : sx + sw]
    return cv2.resize(img_cropped, (1920, 1080))


def preprocess_digit_box(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    big = cv2.resize(gray, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(big, 155, 255, cv2.THRESH_BINARY)
    inv = 255 - thresh
    binary = (inv < 128).astype("uint8")
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(binary, 8)
    mask = 255 * (1 - binary).astype("uint8")
    mask[:] = 255
    kept_area = 0
    for label_index in range(1, count):
        x, _y, w, h, area = stats[label_index]
        is_right_edge_artifact = x > inv.shape[1] * 0.82 and h > inv.shape[0] * 0.45
        if area > 40 and w > 4 and h > 8 and not is_right_edge_artifact:
            mask[labels == label_index] = 0
            kept_area += int(area)

    ys, xs = (mask < 128).nonzero()
    if len(xs) == 0:
        return mask, kept_area

    x0, x1 = max(int(xs.min()) - 20, 0), min(int(xs.max()) + 21, mask.shape[1])
    y0, y1 = max(int(ys.min()) - 20, 0), min(int(ys.max()) + 21, mask.shape[0])
    mask = mask[y0:y1, x0:x1]
    mask = cv2.copyMakeBorder(mask, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255)
    return mask, kept_area


def read_digit_box(crop, one_digit=False):
    prepared, kept_area = preprocess_digit_box(crop)
    psm = 10 if one_digit else 7
    text = pytesseract.image_to_string(
        prepared,
        lang="eng",
        config=f"--psm {psm} -c tessedit_char_whitelist=0123456789",
    )
    numbers = re.findall(r"\d+", text)
    if numbers:
        return numbers[0]
    if one_digit and kept_area > 120:
        return "0"
    return ""


def classify_nature_from_panel(img_1080p, panel_x, panel_y):
    checks = [
        ("attack", "こうげき", (186, 102, 24, 24)),
        ("defense", "ぼうぎょ", (186, 144, 24, 24)),
        ("sp_attack", "とくこう", (520, 57, 24, 24)),
        ("sp_defense", "とくぼう", (520, 102, 24, 24)),
        ("speed", "すばやさ", (530, 145, 24, 24)),
    ]
    up = []
    down = []

    for _key, label, (x, y, w, h) in checks:
        roi = img_1080p[panel_y + y : panel_y + y + h, panel_x + x : panel_x + x + w]
        if roi.size == 0:
            continue
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        red_pixels = int((((hsv[:, :, 0] < 12) | (hsv[:, :, 0] > 168)) & (hsv[:, :, 1] > 80) & (hsv[:, :, 2] > 120)).sum())
        blue_pixels = int(((hsv[:, :, 0] > 75) & (hsv[:, :, 0] < 120) & (hsv[:, :, 1] > 35) & (hsv[:, :, 2] > 120)).sum())
        if red_pixels > 15:
            up.append(label)
        if blue_pixels > 40:
            down.append(label)

    if not up and not down:
        return ""
    return " ".join([*(f"+{label}" for label in up), *(f"-{label}" for label in down)])


def parse_back_image(image_path):
    img_1080p = normalize_to_1080p(image_path)
    panels = [
        (0, 184, 262),
        (1, 986, 262),
        (2, 184, 482),
        (3, 986, 482),
        (4, 184, 704),
        (5, 986, 704),
    ]
    parsed = {}
    print("裏画面のステータス数値を解析中...")
    for slot, panel_x, panel_y in panels:
        stats = {key: "" for key, _label in STAT_KEYS}
        evs = {key: "" for key, _label in STAT_KEYS}
        boxes = {
            "hp": ((200, 45, 85, 42), (320, 45, 48, 42)),
            "attack": ((200, 90, 85, 42), (320, 90, 48, 42)),
            "defense": ((200, 132, 85, 42), (320, 132, 48, 42)),
            "sp_attack": ((560, 45, 75, 42), (680, 45, 45, 42)),
            "sp_defense": ((560, 90, 75, 42), (680, 90, 45, 42)),
            "speed": ((560, 132, 75, 42), (680, 132, 45, 42)),
        }
        for key, (stat_box, ev_box) in boxes.items():
            sx, sy, sw, sh = stat_box
            ex, ey, ew, eh = ev_box
            stat_crop = img_1080p[panel_y + sy : panel_y + sy + sh, panel_x + sx : panel_x + sx + sw]
            ev_crop = img_1080p[panel_y + ey : panel_y + ey + eh, panel_x + ex : panel_x + ex + ew]
            stats[key] = read_digit_box(stat_crop)
            evs[key] = read_digit_box(ev_crop, one_digit=True)

        parsed[slot + 1] = {
            "stats": stats,
            "evs": evs,
            "nature": classify_nature_from_panel(img_1080p, panel_x, panel_y),
        }
    return parsed


def merge_back_data(team, back_data):
    for pokemon in team:
        data = back_data.get(pokemon["slot"])
        if not data:
            continue
        pokemon["stats"] = data["stats"]
        pokemon["evs"] = data["evs"]
        pokemon["nature"] = data["nature"]
    return team


def write_outputs(team, data_dir):
    csv_path = os.path.join(data_dir, "s2_single_ranked_teams.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Slot",
                "Pokemon",
                "Ability",
                "Item",
                "Move1",
                "Move2",
                "Move3",
                "Move4",
                *(label for _key, label in STAT_KEYS),
                *(f"{label}EV" for _key, label in STAT_KEYS),
                "Nature",
            ]
        )
        for pokemon in team:
            writer.writerow(
                [
                    pokemon["slot"],
                    pokemon["pokemon"],
                    pokemon["ability"],
                    pokemon["item"],
                    pokemon["moves"][0],
                    pokemon["moves"][1],
                    pokemon["moves"][2],
                    pokemon["moves"][3],
                    *(pokemon["stats"].get(key, "") for key, _label in STAT_KEYS),
                    *(pokemon["evs"].get(key, "") for key, _label in STAT_KEYS),
                    pokemon.get("nature", ""),
                ]
            )

    json_path = os.path.join(data_dir, "s2_single_ranked_teams.json")
    payload = {
        "season": "M-2",
        "season_number": 2,
        "rule": "シングル",
        "teams": [{"rank": 1, "rating_value": 2564.519, "team": team}],
        "updated_at": datetime.now().isoformat(),
    }
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main():
    configure_tesseract()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
    load_local_dictionaries(base_dir)

    default_front = os.path.join(data_dir, "test_assets", "sample_front.jpeg")
    default_back = os.path.join(data_dir, "test_assets", "sample_back.jpeg")
    front_path = sys.argv[1] if len(sys.argv) > 1 else default_front
    back_path = sys.argv[2] if len(sys.argv) > 2 else default_back
    if not os.path.exists(front_path):
        print(f"エラー: {front_path} が見つかりません。表画像パスを引数で指定してください。")
        return 1

    parsed_team = parse_front_image(front_path)
    if os.path.exists(back_path):
        parsed_team = merge_back_data(parsed_team, parse_back_image(back_path))
    else:
        print(f"警告: 裏画像 {back_path} が見つからないため、ステータス解析をスキップします。")

    print("\n" + "=" * 40)
    print("【解析結果】Pokemon Champions パーティ構成")
    print("=" * 40)
    for pokemon in parsed_team:
        moves_text = " / ".join([move for move in pokemon["moves"] if move])
        print(f"■ スロット {pokemon['slot']}: {pokemon['pokemon']} @ {pokemon['item']}")
        print(f"  特性: {pokemon['ability']}")
        print(f"  技構成: {moves_text}")
        stats_text = " / ".join(f"{label} {pokemon['stats'].get(key, '-')}" for key, label in STAT_KEYS)
        evs_text = " / ".join(f"{label} {pokemon['evs'].get(key, '-')}" for key, label in STAT_KEYS)
        print(f"  実数値: {stats_text}")
        print(f"  努力値: {evs_text}")
        if pokemon.get("nature"):
            print(f"  性格補正: {pokemon['nature']}")
        print("-" * 40)

    csv_path, json_path = write_outputs(parsed_team, data_dir)
    print(f"\nCSVファイルへの保存が完了しました: {os.path.abspath(csv_path)}")
    print(f"JSONファイルへの保存が完了しました: {os.path.abspath(json_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
