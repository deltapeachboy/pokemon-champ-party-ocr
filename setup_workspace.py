import os
import json

def setup():
    # 1. 必要なディレクトリの作成
    dirs = [
        "data/masters",
        "data/test_assets",
        "data/outputs",
        "assets/css",
        "assets/js"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")

    # 2. 共通設定ファイル config.json の定義
    config_data = {
        "image_normalization": {
            "target_width": 1920,
            "target_height": 1080,
            "aspect_ratio": "16:9"
        },
        "panel_coordinates": [
            {"slot": 1, "x": 184, "y": 262},
            {"slot": 2, "x": 986, "y": 262},
            {"slot": 3, "x": 184, "y": 482},
            {"slot": 4, "x": 986, "y": 482},
            {"slot": 5, "x": 184, "y": 704},
            {"slot": 6, "x": 986, "y": 704}
        ],
        "ocr_regions": {
            "front": {
                "pokemon":   {"dx": 78,  "dy": 10,  "w": 280, "h": 45},
                "ability":   {"dx": 95,  "dy": 62,  "w": 260, "h": 38},
                "item":      {"dx": 95,  "dy": 112, "w": 310, "h": 42},
                "moves": [
                    {"dx": 430, "dy": 8,   "w": 300, "h": 42},
                    {"dx": 430, "dy": 56,  "w": 300, "h": 42},
                    {"dx": 430, "dy": 103, "w": 300, "h": 42},
                    {"dx": 430, "dy": 150, "w": 300, "h": 42}
                ]
            },
            "back": {
                "hp":         {"stat": [200, 45, 85, 42], "ev": [320, 45, 48, 42]},
                "attack":     {"stat": [200, 90, 85, 42], "ev": [320, 90, 48, 42]},
                "defense":    {"stat": [200, 132, 85, 42], "ev": [320, 132, 48, 42]},
                "sp_attack":  {"stat": [560, 45, 75, 42], "ev": [680, 45, 45, 42]},
                "sp_defense": {"stat": [560, 90, 75, 42], "ev": [680, 90, 45, 42]},
                "speed":      {"stat": [560, 132, 75, 42], "ev": [680, 132, 45, 42]}
            }
        },
        "hsv_nature_detection": {
            "red_arrow":   {"h_min": 0, "h_max": 12,  "s_min": 80, "v_min": 120, "pixel_threshold": 15},
            "blue_arrow":  {"h_min": 75, "h_max": 120, "s_min": 35, "v_min": 120, "pixel_threshold": 40}
        }
    }
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
        print("Created config.json")

    # 3. マスターデータの作成
    masters = {
        "data/masters/pokemon.csv": (
            "dex_no,name_ja,name_en,type_1,type_2\n"
            "257,フォークス,Blaziken,fire,fighting\n"
            "26,イオナン,Raichu,electric,none\n"
            "473,ラント,Mamoswine,ice,ground\n"
            "260,キモクナーイ,Swampert,water,ground\n"
            "1000,ミミック,Gholdengo,steel,ghost\n"
            "778,ヤミレ,Mimikyu,ghost,fairy\n"
        ),
        "data/masters/ability.csv": (
            "id,name_ja,name_en\n"
            "1,かそく,Speed Boost\n"
            "2,ひらいしん,Lightning Rod\n"
            "3,あついしぼう,Thick Fat\n"
            "4,げきりゅう,Torrent\n"
            "5,おうごんのからだ,Good as Gold\n"
            "6,ばけのかわ,Disguise\n"
        ),
        "data/masters/item.csv": (
            "id,name_ja,name_en,is_megastone\n"
            "1,バシャーモナイト,Blazikenite,true\n"
            "2,ライチュウナイトY,Raichuite Y,true\n"
            "3,きあいのタスキ,Focus Sash,false\n"
            "4,オボンのみ,Sitrus Berry,false\n"
            "5,こだわりスカーフ,Choice Scarf,false\n"
            "6,いのちのたま,Life Orb,false\n"
        ),
        "data/masters/move.csv": (
            "id,name_ja,name_en,type,category\n"
            "1,ブレイズキック,Blaze Kick,fire,physical\n"
            "2,とびひざげり,High Jump Kick,fighting,physical\n"
            "3,かみなりパンチ,Thunder Punch,electric,physical\n"
            "4,まもる,Protect,normal,status\n"
            "5,でんじほう,Zap Cannon,electric,special\n"
            "6,きあいだま,Focus Blast,fighting,special\n"
            "7,なみのり,Surf,water,special\n"
            "8,わるだくみ,Nasty Plot,dark,status\n"
            "9,じしん,Earthquake,ground,physical\n"
            "10,つららばり,Icicle Spear,ice,physical\n"
            "11,がんせきふうじ,Rock Tomb,rock,physical\n"
            "12,こおりのつぶて,Ice Shard,ice,physical\n"
            "13,クイックターン,Flip Turn,water,physical\n"
            "14,あくび,Yawn,normal,status\n"
            "15,ステルスロック,Stealth Rock,rock,status\n"
            "16,ゴールドラッシュ,Make It Rain,steel,special\n"
            "17,シャドーボール,Shadow Ball,ghost,special\n"
            "18,10まんボルト,Thunderbolt,electric,special\n"
            "19,トリック,Trick,psychic,status\n"
            "20,じゃれつく,Play Rough,fairy,physical\n"
            "21,シャドークロー,Shadow Claw,ghost,physical\n"
            "22,かげうち,Shadow Sneak,ghost,physical\n"
            "23,つるぎのまい,Swords Dance,normal,status\n"
        )
    }

    for path, content in masters.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"Created master data: {path}")

    # 4. 検証用正解データ (ground_truth.json) の作成
    ground_truth = {
        "test_set_id": "sample_01",
        "front_image_path": "data/test_assets/sample_front.jpeg",
        "back_image_path": "data/test_assets/sample_back.jpeg",
        "team": [
            {
                "slot": 1, "pokemon": "フォークス", "ability": "かそく", "item": "バシャーモナイト",
                "moves": ["ブレイズキック", "とびひざげり", "かみなりパンチ", "まもる"],
                "nature": "+こうげき -とくこう",
                "stats": {"hp": 187, "attack": 189, "defense": 90, "sp_attack": 117, "sp_defense": 90, "speed": 102},
                "evs": {"hp": 32, "attack": 32, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 2}
            },
            {
                "slot": 2, "pokemon": "イオナン", "ability": "ひらいしん", "item": "ライチュウナイトY",
                "moves": ["でんじほう", "きあいだま", "なみのり", "わるだくみ"],
                "nature": "+すばやさ -こうげき",
                "stats": {"hp": 137, "attack": 99, "defense": 75, "sp_attack": 142, "sp_defense": 100, "speed": 178},
                "evs": {"hp": 2, "attack": 0, "defense": 0, "sp_attack": 32, "sp_defense": 0, "speed": 32}
            },
            {
                "slot": 3, "pokemon": "ラント", "ability": "あついしぼう", "item": "きあいのタスキ",
                "moves": ["じしん", "つららばり", "がんせきふうじ", "こおりのつぶて"],
                "nature": "+こうげき -とくこう",
                "stats": {"hp": 217, "attack": 200, "defense": 102, "sp_attack": 81, "sp_defense": 80, "speed": 100},
                "evs": {"hp": 32, "attack": 32, "defense": 2, "sp_attack": 0, "sp_defense": 0, "speed": 0}
            },
            {
                "slot": 4, "pokemon": "キモクナーイ", "ability": "げきりゅう", "item": "オボンのみ",
                "moves": ["じしん", "クイックターン", "あくび", "ステルスロック"],
                "nature": "+ぼうぎょ -とくこう",
                "stats": {"hp": 207, "attack": 130, "defense": 123, "sp_attack": 94, "sp_defense": 142, "speed": 80},
                "evs": {"hp": 32, "attack": 0, "defense": 2, "sp_attack": 0, "sp_defense": 32, "speed": 0}
            },
            {
                "slot": 5, "pokemon": "ミミック", "ability": "おうごんのからだ", "item": "こだわりスカーフ",
                "moves": ["ゴールドラッシュ", "シャドーボール", "10まんボルト", "トリック"],
                "nature": "+すばやさ -こうげき",
                "stats": {"hp": 164, "attack": 72, "defense": 115, "sp_attack": 185, "sp_defense": 111, "speed": 149},
                "evs": {"hp": 2, "attack": 0, "defense": 0, "sp_attack": 32, "sp_defense": 0, "speed": 32}
            },
            {
                "slot": 6, "pokemon": "ヤミレ", "ability": "ばけのかわ", "item": "いのちのたま",
                "moves": ["じゃれつく", "シャドークロー", "かげうち", "つるぎのまい"],
                "nature": "+こうげき -とくこう",
                "stats": {"hp": 162, "attack": 156, "defense": 100, "sp_attack": 63, "sp_defense": 125, "speed": 118},
                "evs": {"hp": 32, "attack": 32, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 2}
            }
        ]
    }
    with open("data/test_assets/ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)
        print("Created data/test_assets/ground_truth.json")

    print("\nWorkspace setup completed. Please put 'sample_front.jpeg' and 'sample_back.jpeg' into 'data/test_assets/' directory.")

if __name__ == "__main__":
    setup()