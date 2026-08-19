#!/usr/bin/env python3
"""S022: 2026年4月から引かれ始めたお金は、年にいくらか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  2026年4月から新しく引かれ始めた「子ども・子育て支援金」は年にいくらか。
答え:
  標準報酬月額36万円の人で、月414円・年6118円。
  しかも明細に新しい行は増えず、健康保険料に混ざって引かれる。

この人の欲求(yokkyu-map A: 取られたくない):
  **知らないうちに引かれるのが嫌だ。何がいつから増えたのかを知りたい。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度・標準報酬月額36万円で計算"

TSUKI, NEN = 414, 6_118
assert TSUKI * 12 + 1_150 == NEN

SCENES = {
    "toi": sc.card("この動画の問い", "年いくら?", "※ 標準報酬月額36万円の例です",
                   BADGE, BRAND, main_size=118, head_fs=32),
    "toi__cover": sc.cover("給料から4月に増えた分、年いくら?", "6,118円",
                           "明細に新しい行は、増えない",
                           "2026年度", BRAND),
    "nani": sc.card("4月に増えたもの", "子育て支援金",
                    "※ 2028年度まで段階的に上がる予定", BADGE, BRAND,
                    main_size=88, head_fs=32),
    "ritsu": sc.bars2("率の分かれ方",
                      ("制度ぜんたい", 2.3, "0.23%"),
                      ("自分が払う分", 1.15, "0.115%"), BADGE, BRAND, ymax=2.8),
    "gaku": sc.card("毎月引かれる額", "414円", "※ 標準報酬月額36万円のとき",
                    BADGE, BRAND, main_size=132, head_fs=32,
                    ask="あなたの明細は上がった?"),
    "nenkan": sc.bars2("1年ぶんに直すと",
                       ("1年ぶん", 4.968, "4968円"),
                       ("賞与ぶん", 1.15, "1150円"), BADGE, BRAND, ymax=6),
    "matome": sc.hayami("明細で確かめる4つ",
                        [("始まった月", "2026年4月"), ("引かれる場所", "健康保険料の行"),
                         ("毎月", "414円"), ("賞与からも", "引かれる")],
                        "※ 2026年度。標準報酬月額と賞与の額で変わります",
                        BADGE, BRAND, col1="どこを見るか", col2="何が分かるか", focal=1),
    "shime": sc.chips("明細で他に増えたものは?",
                      ["健康保険", "厚生年金", "雇用保険", "気づかなかった"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "給料から4月に増えた分、年いくら?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("nani", "2026年4月から、ある名前が増えたのだ。", anim=1.4, speed=1.05),
    Unit("nani", "その名前が、子育て支援金なのだ。", anim=0.0, speed=1.05),
    Unit("nani", "子育て支援金は、医療保険に上乗せされる。", anim=0.0, speed=1.05),
    Unit("ritsu", "上乗せの率は、0.23%と決まっている。", anim=1.6, speed=1.05),
    Unit("ritsu", "ただし会社と半分ずつなので、自分は0.115%。", anim=0.0,
         speed=1.05),
    Unit("gaku", "たとえば給料が、36万円だとする。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("gaku", "すると毎月414円が、引かれるのだ。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("nenkan", "414円を1年ぶんに、直してみるのだ。", anim=1.6, speed=1.05),
    Unit("nenkan", "すると4968円になるのだ。", anim=0.0, speed=1.05),
    Unit("nenkan", "さらに賞与からも、1150円が引かれる。", anim=0.0,
         speed=1.05),
    Unit("nenkan", "だから合わせて、6118円になるのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("matome", "でも明細に、新しい行は増えないのだ。", anim=1.6,
         face="troubled", se="don", speed=1.05, intonation=1.2),
    Unit("matome", "その行の健康保険料に、混ざっているのだ。", anim=0.0, speed=1.05),
    Unit("matome", "だから気づかないまま、払っている人が多い。", anim=0.0, speed=1.05),
    Unit("matome", "しかも率は、これから上がる予定なのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから4月の明細と、3月ぶんを見くらべてほしい。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S022.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
