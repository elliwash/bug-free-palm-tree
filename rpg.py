#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import sys

# ========== ゲームデータ ==========

JOBS = {
    "スライム": {"hp": 30, "atk": 3, "special": "分裂", "emoji": "🟢"},
    "ゴブリン": {"hp": 25, "atk": 5, "special": "ガバガバ戦術", "emoji": "👺"},
    "スケルトン": {"hp": 20, "atk": 6, "special": "骨を外す", "emoji": "💀"},
    "ミミック": {"hp": 35, "atk": 4, "special": "宝箱のフリ", "emoji": "📦"},
}

EVENTS = [
    {
        "title": "森の中で迷子の勇者に出会った",
        "desc": "「お前、魔物じゃないか！」勇者が剣を構えた。",
        "choices": [
            ("土下座して仲良くなろうとする", "hero_friend", "なぜか感動した勇者と友達になった！ HP+5"),
            ("全力で逃げる", "run", "見事に逃げ切った。でも転んだ。HP-3"),
            ("戦う", "fight_hero", ""),
        ]
    },
    {
        "title": "魔王の城の求人広告を見つけた",
        "desc": "「幹部募集中。待遇良好。残業なし（嘘）」と書いてある。",
        "choices": [
            ("応募する", "apply_demon", "面接に合格！魔王軍に入隊。謎の装備をもらった。ATK+2"),
            ("無視して通り過ぎる", "ignore", "特に何も起きなかった。"),
            ("求人票を破る", "tear", "魔王がどこかで嚏をした気がした。"),
        ]
    },
    {
        "title": "村人に話しかけられた",
        "desc": "「魔物が出たぞ！逃げろ！」……自分のことだった。",
        "choices": [
            ("「私が魔物です」と正直に言う", "honest", "なぜか村人に受け入れられた。村の守護神になった。HP+8"),
            ("一緒に逃げる", "run_together", "村人と一緒にパニックになった。何も解決しなかった。"),
            ("魔物のフリをして脅かす", "scare", "村人が全員倒れた。罪悪感でHP-2"),
        ]
    },
    {
        "title": "不思議な泉を見つけた",
        "desc": "キラキラと光る泉。飲んでみる？",
        "choices": [
            ("飲む", "drink", f"{'回復した！HP+10' if random.random() > 0.3 else 'お腹を壊した。HP-5'}"),
            ("入浴する", "bath", "さっぱりした。気分UP。HP+3"),
            ("泉に話しかける", "talk_spring", "「……」泉は何も答えなかった。"),
        ]
    },
    {
        "title": "賢者の塔にたどり着いた",
        "desc": "「異世界転生者よ、汝の望みを言え」",
        "choices": [
            ("「故郷に帰りたい」", "go_home", "「無理です」と即答された。"),
            ("「最強になりたい」", "strongest", "「努力してください」と言われた。ATK+3"),
            ("「お昼ご飯が食べたい」", "lunch", "賢者が飯を奢ってくれた。HP満タン回復！"),
        ]
    },
]

ENDINGS = {
    "勇者の相棒エンド": "勇者と友達になり、魔王討伐の旅へ。まさかの主人公交代。",
    "魔王軍幹部エンド": "魔王軍に就職。意外と福利厚生が良かった。",
    "村の守護神エンド": "村人に崇められ、のどかな異世界ライフを満喫。",
    "賢者の弟子エンド": "賢者に気に入られ、修行の日々。強くなれそう。",
    "普通に生き残りエンド": "特に何も成し遂げなかったが、元気に生きている。",
}


# ========== ゲームエンジン ==========

def clear_screen():
    print("\n" + "="*40 + "\n")

def print_status(player):
    print(f"【{player['emoji']} {player['name']}】 HP: {player['hp']}/{player['max_hp']}  ATK: {player['atk']}")

def choose_job():
    print("="*40)
    print("  異世界転生RPG 〜俺、魔物なんだけど〜")
    print("="*40)
    print("\n前世の記憶もなく、気づいたら異世界に転生していた。")
    print("しかも……人間じゃない何かとして。\n")
    print("あなたが転生したのは？\n")

    jobs = list(JOBS.items())
    for i, (name, data) in enumerate(jobs, 1):
        print(f"  {i}. {data['emoji']} {name}  (HP:{data['hp']} ATK:{data['atk']} 特技:{data['special']})")

    print()
    while True:
        try:
            choice = int(input("選択 (1-4): "))
            if 1 <= choice <= len(jobs):
                name, data = jobs[choice - 1]
                return {
                    "name": name,
                    "hp": data["hp"],
                    "max_hp": data["hp"],
                    "atk": data["atk"],
                    "special": data["special"],
                    "emoji": data["emoji"],
                    "flags": [],
                }
        except ValueError:
            pass
        print("1〜4の数字を入力してください")

def do_choice(player, event, choice_idx):
    _, flag, effect = event["choices"][choice_idx]

    if flag == "hero_friend":
        player["hp"] = min(player["max_hp"], player["hp"] + 5)
        player["flags"].append("勇者の相棒")
    elif flag == "run":
        player["hp"] = max(1, player["hp"] - 3)
    elif flag == "fight_hero":
        dmg = random.randint(3, 8)
        player["hp"] = max(1, player["hp"] - dmg)
        effect = f"戦ったが手加減された。HP-{dmg}"
    elif flag == "apply_demon":
        player["atk"] += 2
        player["flags"].append("魔王軍幹部")
    elif flag == "honest":
        player["hp"] = min(player["max_hp"], player["hp"] + 8)
        player["flags"].append("村の守護神")
    elif flag == "scare":
        player["hp"] = max(1, player["hp"] - 2)
    elif flag == "drink":
        if random.random() > 0.3:
            player["hp"] = min(player["max_hp"], player["hp"] + 10)
            effect = "回復した！HP+10"
        else:
            player["hp"] = max(1, player["hp"] - 5)
            effect = "お腹を壊した。HP-5"
    elif flag == "bath":
        player["hp"] = min(player["max_hp"], player["hp"] + 3)
    elif flag == "strongest":
        player["atk"] += 3
        player["flags"].append("賢者の弟子")
    elif flag == "lunch":
        player["hp"] = player["max_hp"]
        player["flags"].append("賢者の弟子")

    return effect

def get_ending(player):
    flags = player["flags"]
    if "勇者の相棒" in flags:
        return "勇者の相棒エンド", ENDINGS["勇者の相棒エンド"]
    elif "魔王軍幹部" in flags and "村の守護神" not in flags:
        return "魔王軍幹部エンド", ENDINGS["魔王軍幹部エンド"]
    elif "村の守護神" in flags:
        return "村の守護神エンド", ENDINGS["村の守護神エンド"]
    elif "賢者の弟子" in flags:
        return "賢者の弟子エンド", ENDINGS["賢者の弟子エンド"]
    else:
        return "普通に生き残りエンド", ENDINGS["普通に生き残りエンド"]


def main():
    player = choose_job()
    clear_screen()
    print(f"{player['emoji']} {player['name']}として、異世界の旅が始まる……\n")

    selected_events = random.sample(EVENTS, min(3, len(EVENTS)))

    for i, event in enumerate(selected_events, 1):
        print(f"--- イベント {i}/{len(selected_events)} ---")
        print(f"\n【{event['title']}】")
        print(f"{event['desc']}\n")
        print_status(player)
        print()

        for j, (choice_text, _, _) in enumerate(event["choices"], 1):
            print(f"  {j}. {choice_text}")

        print()
        while True:
            try:
                choice = int(input("選択: ")) - 1
                if 0 <= choice < len(event["choices"]):
                    break
            except ValueError:
                pass
            print("正しい番号を入力してください")

        effect = do_choice(player, event, choice)
        if effect:
            print(f"\n→ {effect}")

        if player["hp"] <= 0:
            print("\n力尽きた……でも異世界では死んでも復活するらしい。HP1で復活！")
            player["hp"] = 1

        input("\n[Enterで続ける]")
        clear_screen()

    # エンディング
    ending_title, ending_desc = get_ending(player)
    print("="*40)
    print("        ＊ ENDING ＊")
    print("="*40)
    print(f"\n【{ending_title}】\n")
    print(ending_desc)
    print()
    print_status(player)
    print("\n異世界での新しい生活が始まった。")
    print("（完）\n")


if __name__ == "__main__":
    main()
