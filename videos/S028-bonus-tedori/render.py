#!/usr/bin/env python3
"""S028: ボーナス50万円、手取りはいくらか。

企画書は plan.md、数値は verify.py。
答え: 39万1709円。10万8291円が引かれて消える。ただし住民税はここからは引かれない。

この人の欲求(yokkyu-map A: 取られたくない):
  **ボーナスの額面で予定を立てて、あとでがっかりしたくない。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402
import shortlib as _sl  # noqa: E402

_sl.set_accent("tax")  # カテゴリ色(docs/research/sakubun-gensoku.md とは別の画面施策)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度・東京の会社員で計算"

TEDORI = 391_709
assert 500_000 - TEDORI == 108_291

SCENES = {
    "toi": sc.card("この動画の問い", "手取りはいくら?", "※ 東京の会社員の例です",
                   BADGE, BRAND, main_size=92, head_fs=32),
    "toi__cover": sc.cover("ボーナス50万、手取りはいくら?", "??万円",
                           "答えの額を見て、使い道を決めてほしい",
                           "2026年度", BRAND),
    "gaku": sc.card("この例のボーナス", "50万円", "※ 金額はすべて仮定の例です",
                    BADGE, BRAND, main_size=132, head_fs=32),
    "shaho": sc.bars2("まず引かれるもの",
                      ("社会保険料", 7.345, "7万3450円"),
                      ("残り", 42.655, "42万6550円"), BADGE, BRAND, ymax=50),
    "zei": sc.card("残りにかかる所得税", "3万4841円", "※ この例では8.168%で計算",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "kekka": sc.card("手元に来る額", "39万1709円", "※ 額面と手取りは別ものです",
                     BADGE, BRAND, main_size=100, head_fs=32,
                     ask="使い道は手取りで決めた?"),
    "matome": sc.hayami("50万円の行き先",
                        [("社会保険料", "7万3450円"), ("所得税", "3万4841円"),
                         ("住民税", "0円(給料の側)"), ("手元に来る", "39万1709円")],
                        "※ 2026年度・東京。率は前月の給料で変わります",
                        BADGE, BRAND, col1="どこへ行くか", col2="いくら", focal=3),
    "shime": sc.chips("ボーナスの使い道、おすすめは?",
                      ["先に貯める", "投資にまわす", "借金を返す", "ぱっと使う"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "ボーナス50万、手取りはいくら?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("gaku", "たとえばボーナスが、50万円出たとする。", anim=1.4, speed=1.05),
    Unit("gaku", "その50万円は、まるごとは来ないのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("shaho", "まず引かれるのが、社会保険料なのだ。", anim=1.6, speed=1.05),
    Unit("shaho", "社会保険料とは、健康保険や年金のこと。", anim=0.0, speed=1.05),
    Unit("shaho", "社会保険料の率は、いま14.69%なのだ。", anim=0.0, speed=1.05),
    Unit("shaho", "すると7万3450円が、引かれるのだ。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("shaho", "だから残りは、42万6550円になるのだ。", anim=0.0, speed=1.05),
    Unit("zei", "その42万6550円に、所得税がかかる。", anim=1.6, speed=1.05),
    Unit("zei", "所得税の率は、前の月の給料で決まるのだ。", anim=0.0, speed=1.05),
    Unit("zei", "たとえばその率を、8.168%とするのだ。", anim=0.0, speed=1.05),
    Unit("zei", "すると所得税は、3万4841円になるのだ。", anim=0.0, speed=1.05),
    Unit("kekka", "だから手取りは、39万1709円なのだ。", anim=1.6,
         face="surprised", se="don", speed=1.05, intonation=1.25),
    Unit("kekka", "そして残りの10万8291円は、消えたのだ。", anim=0.0, speed=1.05),
    Unit("matome", "ちなみに住民税は、ここでは0円なのだ。", anim=1.6, speed=1.05),
    Unit("matome", "住民税は毎月の給料から、引かれているのだ。", anim=0.0, speed=1.05),
    Unit("shime", "ボーナスの予定は、手取りの39万円で立てる。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S028.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
