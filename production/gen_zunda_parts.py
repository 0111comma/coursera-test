#!/usr/bin/env python3
"""坂本アヒル氏「ずんだもん立ち絵素材2.3」から動画用の状態別合成PNGを生成する。

出力: production/assets/zunda/parts/{expr}_{mouth}_{eyes}.png(uniform crop=状態間で位置が揺れない)
状態設計(deep-loops ㉙): 表情5種 × 口3種(閉/半/開) × 目(開/閉=まばたき。専用目の表情はまばたきなし)
腕ポーズ・枝豆・顔色・眉・記号(汗)も表情に連動させる。
"""
from pathlib import Path

from psd_tools import PSDImage

PSD_PATH = Path(__file__).resolve().parent / "assets" / "zunda" / "ずんだもん立ち絵素材2.3.psd"
OUT_DIR = Path(__file__).resolve().parent / "assets" / "zunda" / "parts"
CROP = (170, 95, 970, 1010)  # 全状態共通(バストアップ+尻尾まで収まる)

# 表情ごとのパーツ選択。(グループ名, レイヤー名)のリスト
EXPRESSIONS = {
    "normal": {
        "arms": [("!右腕", "*基本"), ("!左腕", "*基本")],
        "eyes_open": [("!目", "*目セット"), ("*目セット", "*普通白目"), ("!黒目", "*カメラ目線")],
        "eyes_closed": [("!目", "*UU")],
        "brow": [("!眉", "*普通眉")],
        "cheek": [("!顔色", "*ほっぺ")],
        "edamame": [("!枝豆", "*枝豆通常")],
        "extras": [],
    },
    "surprised": {
        "arms": [("!右腕", "*口元"), ("!左腕", "*基本")],
        "eyes_open": [("!目", "*目セット"), ("*目セット", "*見開き白目"), ("!黒目", "*カメラ目線")],
        "eyes_closed": None,  # 驚きはまばたきなし
        "brow": [("!眉", "*上がり眉")],
        "cheek": [("!顔色", "*ほっぺ")],
        "edamame": [("!枝豆", "*枝豆通常")],
        "extras": ["汗1"],
    },
    "troubled": {
        "arms": [("!右腕", "*基本"), ("!左腕", "*考える")],
        "eyes_open": [("!目", "*目セット"), ("*目セット", "*普通白目"), ("!黒目", "*目逸らし")],
        "eyes_closed": None,
        "brow": [("!眉", "*困り眉1")],
        "cheek": [("!顔色", "*ほっぺ")],
        "edamame": [("!枝豆", "*枝豆萎え")],  # 困りは枝豆も萎える
        "extras": ["汗2"],
    },
    "happy": {
        "arms": [("!右腕", "*基本"), ("!左腕", "*腰")],
        "eyes_open": [("!目", "*にっこり2")],
        "eyes_closed": None,
        "brow": [("!眉", "*普通眉")],
        "cheek": [("!顔色", "*ほっぺ赤め")],
        "edamame": [("!枝豆", "*枝豆通常")],
        "extras": [],
    },
    "smug": {
        "arms": [("!右腕", "*指差し"), ("!左腕", "*腰")],
        "eyes_open": [("!目", "*ジト目")],
        "eyes_closed": None,
        "brow": [("!眉", "*普通眉")],
        "cheek": [("!顔色", "*ほっぺ2")],
        "edamame": [("!枝豆", "*枝豆通常")],
        "extras": [],
    },
}
MOUTHS = {0: {"normal": "*むふ", "troubled": "*むー"},   # 閉じ(困りはへの字)
          1: {"normal": "*ほあ"},                        # 半開き
          2: {"normal": "*ほあー"}}                      # 開き


def build_layer_index(psd):
    """(親グループ名, レイヤー名) → レイヤーオブジェクト"""
    idx = {}
    def walk(layers, parent_name):
        for l in layers:
            idx[(parent_name, l.name)] = l
            if l.is_group():
                walk(l, l.name)
    walk(psd, "")
    return idx


def main():
    psd = PSDImage.open(PSD_PATH)
    idx = build_layer_index(psd)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 常時表示するベース(いつもの服・尻尾)。服装2系は不使用
    def base_selection():
        sel = set()
        sel.add(("", "尻尾的なアレ"))
        sel.add(("", "*服装1"))
        sel.add(("*服装1", "*いつもの服"))
        return sel

    def resolve(sel):
        """選択セット(親,名前)からレイヤー実体の集合(グループ含む)を得る"""
        layers = set()
        for key in sel:
            l = idx[key]
            layers.add(id(l))
        return layers

    count = 0
    for expr, spec in EXPRESSIONS.items():
        eye_variants = {"open": spec["eyes_open"]}
        if spec["eyes_closed"]:
            eye_variants["closed"] = spec["eyes_closed"]
        for mouth_id, mouth_map in MOUTHS.items():
            mouth_layer = mouth_map.get(expr, mouth_map["normal"])
            for eye_name, eye_sel in eye_variants.items():
                sel = base_selection()
                # 腕(服装1配下)
                for g, l in spec["arms"]:
                    sel.add(("*服装1", g))
                    sel.add((g, l))
                for part in (eye_sel, spec["brow"], spec["cheek"], spec["edamame"]):
                    for g, l in part:
                        # グループ自身も可視に
                        sel.add((g, l))
                        if g:
                            # 親グループのキーを探す(トップレベル or ネスト)
                            for (pg, name) in list(idx.keys()):
                                if name == g:
                                    sel.add((pg, g))
                sel.add(("!口", mouth_layer))
                sel.add(("", "!口"))
                for ex in spec["extras"]:
                    sel.add(("記号など", ex))
                    sel.add(("", "記号など"))
                wanted = resolve(sel)
                img = psd.composite(
                    layer_filter=lambda l: id(l) in wanted)
                img = img.crop(CROP)
                out = OUT_DIR / f"{expr}_{mouth_id}_{eye_name}.png"
                img.save(out)
                count += 1
                print(f"{out.name} ✓")
    print(f"{count} states generated")


if __name__ == "__main__":
    main()
