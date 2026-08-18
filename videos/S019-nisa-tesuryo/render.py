#!/usr/bin/env python3
"""S019: 積立の手数料0.9%の差が、20年でいくらになるのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  手数料が年0.1%の商品と年1.0%の商品で、20年後にいくら違うのか。
答え:
  約119万円。1年目の差はたった1522円なので、途中では気づかない。

この人の欲求(yokkyu-map A: 取られたくない):
  **知らないうちに引かれるのが嫌だ。手数料で取られたくない。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年5%は仮定・2026年8月時点"

YASUI, TAKAI = 1219, 1100
assert YASUI - TAKAI == 119

SCENES = {
    "toi": sc.card("この動画の問い", "いくら取られる?", "※ 毎月3万円・年5%と仮定した例です",
                   BADGE, BRAND, main_size=94, head_fs=32),
    "toi__cover": sc.cover("積立の手数料、20年でいくら取られる?", "119万円",
                           "1年目の差は、たった1522円",
                           "年5%は仮定", BRAND),
    "tesu": sc.card("積立にかかるもの", "毎年の手数料", "※ 買うときの値段とは別です",
                    BADGE, BRAND, main_size=104, head_fs=32),
    "hikaku": sc.bars2("20年後の合計",
                       ("手数料0.1%", 12.19, "1219万円"),
                       ("手数料1.0%", 11.00, "1100万円"), BADGE, BRAND, ymax=15),
    "sa": sc.card("差し引き", "119万円", "※ 積み立てた元本は同じです",
                  BADGE, BRAND, main_size=132, head_fs=32,
                  ask="あなたの商品の手数料は何%?"),
    "ichinen": sc.bars2("1年目だけで見ると",
                        ("手数料0.1%", 3.70, "ほぼ同じ"),
                        ("手数料1.0%", 3.69, "1522円下"), BADGE, BRAND, ymax=4.6),
    "matome": sc.hayami("商品を選ぶ前に見る4つ",
                        [("手数料の差", "0.9%"), ("1年目の差", "1522円"),
                         ("20年後の差", "119万円"), ("出したお金", "どちらも同じ")],
                        "※ 毎月3万円・年5%と仮定。特定の商品を指すものではありません",
                        BADGE, BRAND, col1="どこを見るか", col2="いくら", focal=2),
    "shime": sc.chips("あなたの手数料は?",
                      ["1%より下", "1%より上", "調べたことがある", "見たことがない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "積立の手数料、20年でいくら取られる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("tesu", "積立の商品には、毎年の手数料がかかるのだ。", anim=1.4, speed=1.05),
    Unit("tesu", "手数料は残高から、自動で引かれていく。", anim=0.0, speed=1.05),
    Unit("hikaku", "たとえば毎月3万円を、積み立てるとする。", anim=1.6, speed=1.05),
    Unit("hikaku", "その積立を20年つづけ、年5%で増えたとする。", anim=0.0, speed=1.05),
    Unit("hikaku", "まず手数料が、年0.1%だとする。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("hikaku", "すると20年後は、1219万円になる。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("hikaku", "では手数料が、年1.0%だとどうか。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("hikaku", "すると20年後は、1100万円にしかならない。", anim=0.0, speed=1.05),
    Unit("sa", "だから差は、119万円になるのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("sa", "出したお金は、どちらも720万円なのだ。", anim=0.0, speed=1.05),
    Unit("ichinen", "では1年目だけなら、いくら違うのか。", anim=1.6, speed=1.05),
    Unit("ichinen", "1年目の差は、たった1522円なのだ。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("ichinen", "1522円は小さすぎて、途中で気づかない。", anim=0.0, speed=1.05),
    Unit("matome", "つまり手数料の差は、0.9%しかない。", anim=1.6, speed=1.05),
    Unit("matome", "でも20年たつと、119万円まで育つのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だからいま持っている商品の、手数料を見てほしい。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S019.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
