#!/usr/bin/env python3
"""S018: 昇給1万円で、手取りはいくら増えるのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  月給が1万円上がったとき、手取りはいくら増えるのか。
答え:
  約6800円。3200円は社会保険料と税で消える。

この人の欲求(yokkyu-map A: 取られたくない):
  **上がったぶんを、知らないうちに持っていかれるのが嫌だ。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度・東京の会社員で計算"

AGARI, TEDORI = 10_000, 6_807
assert AGARI - TEDORI == 3_193

SCENES = {
    "toi": sc.card("この動画の問い", "いくら増える?", "※ 東京の会社員の例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("昇給1万円、手取りはいくら増える?", "6,807円",
                           "3,193円は、引かれて消える",
                           "2026年度", BRAND),
    "agaru": sc.card("月給が上がった額", "1万円", "※ 金額はすべて仮定の例です",
                     BADGE, BRAND, main_size=132, head_fs=32),
    "shaho": sc.bars2("まず引かれるもの",
                      ("社会保険料", 1.469, "1469円"),
                      ("残り", 8.531, "8531円"), BADGE, BRAND, ymax=10),
    "zei": sc.bars2("残りにかかる税",
                    ("所得税", 0.871, "871円"),
                    ("住民税", 0.853, "853円"), BADGE, BRAND, ymax=1.1),
    "kekka": sc.card("手元に増える額", "6807円", "※ 1万円のうち3193円が消えます",
                     BADGE, BRAND, main_size=126, head_fs=32,
                     ask="あなたの昇給、手取りで見た?"),
    "matome": sc.hayami("1万円の行き先",
                        [("社会保険料", "1469円"), ("所得税", "871円"),
                         ("住民税", "853円"), ("手元に残る", "6807円")],
                        "※ 2026年度・東京。年収や自治体で変わります",
                        BADGE, BRAND, col1="どこへ行くか", col2="いくら", focal=3),
    "shime": sc.chips("手取りを増やす決め手は?",
                      ["資格の手当", "残業を減らした", "転職した", "まだ無い"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "昇給1万円、手取りはいくら増える?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("agaru", "たとえば給料が、1万円上がったとする。", anim=1.4, speed=1.05),
    Unit("agaru", "1万円まるごと、手元に来ると思うか。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("shaho", "まず引かれるのが、社会保険料なのだ。", anim=1.6, speed=1.05),
    Unit("shaho", "社会保険料とは、健康保険と年金などのこと。", anim=0.0, speed=1.05),
    Unit("shaho", "社会保険料は1469円で、先に引かれる。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("shaho", "その残りが、8531円になるのだ。", anim=0.0, speed=1.05),
    Unit("zei", "そして8531円に、税がかかるのだ。", anim=1.6, speed=1.05),
    Unit("zei", "まず所得税として、871円が引かれる。", anim=0.0, speed=1.05),
    Unit("zei", "そして住民税として、853円が引かれる。", anim=0.0, speed=1.05),
    Unit("kekka", "だから手元に増えるのは、6807円。", anim=1.6,
         face="surprised", se="don", speed=1.05, intonation=1.25),
    Unit("kekka", "そして残りの3193円は、消えるのだ。", anim=0.0, speed=1.05),
    Unit("kekka", "その3193円は、およそ3割にあたるのだ。", anim=0.0, speed=1.05),
    Unit("kekka", "だから2倍上がっても、3割は消えるのだ。",
         anim=0.0, speed=1.05),
    Unit("matome", "しかもいま2026年は、年収が高いほど引かれる。", anim=1.6,
         speed=1.05),
    Unit("matome", "つまり上がった額だけでは、手取りは分からない。", anim=0.0, speed=1.05),
    Unit("shime", "だから昇給は、手取りで見てほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S018.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
