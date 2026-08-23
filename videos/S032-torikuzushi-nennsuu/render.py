#!/usr/bin/env python3
"""S032: 1000万円を月5万ずつ取り崩すと、何歳で尽きるのか。

新デザイン1本目(自前キャラ・明るい背景・冥鳴ひまり)。
型は competitor-shorts-teardown-2026-08-23.md の分解にもとづく:
  0〜5% カバー / 5〜73% 本編 / 73〜76% 結論 / 76〜100% CTA
  1カット1.6〜1.8秒。表は出しっぱなしにして**赤枠を1行ずつ動かす**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

TITLE = "1000万円を毎月5万円ずつ使うと?"
BADGE = "※ 利回りは仮定。元本保証ではありません"
F.use_fp_theme(TITLE, speaker=14,
               badge=BADGE)      # 冥鳴ひまり

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

M0 = V.RESULT[0.00]; M3 = V.RESULT[0.03]; M5 = V.RESULT[0.05]
assert M0[0] == 200 and round(M0[2]) == 82

SCENES = {
    "ie": sf.person("01_base"),
    "ie__cover": sf.cover("老後のお金、どこまで使える?", "1000万円を毎月5万円ずつ", "何歳まで持つ?"),

    # ---- 答えを先に出す(競合の型: 冒頭で言い切る)
    "kotae": sf.hero("82歳", "65歳から 毎月5万円ずつ", name="04_surprised"),

    # ---- 中身は割り算1回。表は出しっぱなしで赤枠を1行ずつ動かす
    "keisan0": sf.table(["", ""], [("1000万 ÷ 5万", "200か月"), ("200か月", "16年と少し")],
                        highlight=0, title="割り算1回で出る"),
    "keisan1": sf.table(["", ""], [("1000万 ÷ 5万", "200か月"), ("200か月", "16年と少し")],
                        highlight=1, title="割り算1回で出る"),

    # ---- この動画の芯: 足りない13年
    "obi": sf.timeline(65, 82, 95, "お金がある", "", show_gap=False,
                       title="65歳から毎月5万円ずつ"),
    "obi2": sf.timeline(65, 82, 95, "お金がある", "13年 足りない",
                        title="95歳まで生きたら"),

    # ---- 逃げ道: 運用すれば延びる
    "nobiru": sf.person("02_point"),
    "hyo": sf.table(["利回り", "尽きる年齢"],
                    [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                    title="65歳から毎月5万円ずつ"),
    "hyo3": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=1, title="65歳から毎月5万円ずつ"),
    "hyo5": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=2, title="65歳から毎月5万円ずつ"),
    "hyo0": sf.table(["利回り", "尽きる年齢"],
                     [("0%", "82歳"), ("3%", "88歳"), ("5%", "101歳")],
                     highlight=0, title="65歳から毎月5万円ずつ"),
    "kari": sf.person("03_troubled"),

    # ---- 本当の答え
    "ue": sf.hero("2万7000円", "95歳まで使うなら 毎月", name=None),
    "hikaku": sf.bars([("つもり", 50000, "5万円"), ("実際", 27000, "2万7000円")],
                      highlight=1, title="毎月使える額"),

    # ---- 持ち帰る式
    "kime": sf.person("02_point"),
    "shiki": sf.formula("貯金 ÷ 年数 ÷ 12", "= 毎月使っていい額"),
    "cta1": sf.cta("", "01_base"),
    "cta2": sf.cta("", "02_point", show_button=True),
}

UNITS = [
    # ---- カバー
    Unit("ie", "貯金1000万円。毎月5万円で何歳まで?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.2, chara="none"),

    # ---- 答えを先に
    Unit("kotae", "毎月5万円ずつ使うと、【82歳】で尽きます。", anim=1.2,
         se="don", speed=1.0, intonation=1.2, chara="none"),

    # ---- 中身は割り算1回
    Unit("keisan0", "1000万円を5万円で割ると、【200か月】。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("keisan1", "200か月は、【16年】と少し。", anim=1.2,
         speed=1.05, chara="none"),

    # ---- 芯: 13年足りない
    Unit("obi", "【65歳】から使い始めて、その【16年】で足りますか?", anim=1.2,
         speed=1.05, chara="none"),
    Unit("obi2", "【95歳】まで生きたら、【13年】足りません。", anim=1.2,
         se="impact", se_at=0.2, speed=1.0, intonation=1.2, pad=0.3, chara="none"),

    # ---- 逃げ道: 運用すれば延びる
    Unit("nobiru", "足りない分は、運用で延ばせます。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("hyo", "運用の利回りとは、1年でふえる割合のこと。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("hyo3", "利回り【3%】なら、【88歳】まで。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("hyo5", "利回り【5%】なら、【101歳】まで。", anim=1.2,
         se="don", speed=1.05, chara="none"),

    # ---- 逃げ道はあてにできない
    Unit("kari", "ただし、【利回り】に保証はありません。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("kari", "【利回り】は仮定で、減る年もあります。", anim=0.0,
         speed=1.05, pad=0.35, chara="none"),
    Unit("hyo0", "いまは、【利回り】ゼロで考えます。", anim=1.2,
         speed=1.05, chara="none"),

    # ---- 本当の答え
    Unit("obi2", "ゼロのまま、【95歳】まで持たせるなら?", anim=1.2,
         speed=1.05, chara="none"),
    Unit("ue", "答えは、毎月【2万7000円】。", anim=1.2,
         se="don", speed=1.0, intonation=1.2, chara="none"),
    Unit("hikaku", "毎月【5万円】のつもりが、半分ちょっとです。", anim=1.2,
         se="impact", se_at=0.25, speed=1.0, pad=0.35, chara="none"),

    # ---- 持ち帰る式
    Unit("kime", "だから、金額から決めないでください。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("kime", "決めるのは【金額】ではなく、【年数】です。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("shiki", "あなたは、その【年数】を何年にしますか?", anim=1.2,
         speed=1.05, chara="none"),
    Unit("shiki", "貯金を、その【年数】と12で割ります。", anim=0.0,
         se="don", speed=1.05, chara="none"),

    # ---- CTA
    Unit("cta1", "【貯金】の数字を、毎回こうして確かめます。", anim=1.2,
         speed=1.05, chara="none"),
    Unit("cta2", "【1000万円】の続きは、チャンネル登録で。", anim=1.2,
         speed=1.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S032.mp4", speaker=14, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
