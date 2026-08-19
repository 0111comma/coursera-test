#!/usr/bin/env python3
"""S021: 1000万円を20年で貯めるには、毎月いくら必要か。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  1000万円という目標に、預金だけで届くには月いくら要るのか。
答え:
  預金だけなら月4万円。年5%と仮定して増やすなら月2万4300円。差は月1万5700円。

この人の欲求(yokkyu-map B: 大きな選択を間違えたくない):
  **1000万円は貯めたい。でも毎月いくら出せばいいのかが分からない。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年5%は仮定・2026年8月時点"

YOKIN, UNYO = 40_000, 24_300
assert YOKIN - UNYO == 15_700

SCENES = {
    "toi": sc.card("この動画の問い", "月いくら?", "※ 20年で貯める場合の例です",
                   BADGE, BRAND, main_size=118, head_fs=32),
    "toi__cover": sc.cover("貯金1000万円、月いくらで届く?", "月4万円",
                           "年5%で増やすなら、月2万4300円",
                           "年5%は仮定", BRAND),
    "mokuhyo": sc.card("この動画の目標", "20年で1000万円", "※ 金額はすべて仮定の例です",
                       BADGE, BRAND, main_size=82, head_fs=32),
    "yokin": sc.card("銀行に置くだけなら", "月4万円", "※ 増えないぶん、減りもしません",
                     BADGE, BRAND, main_size=124, head_fs=32),
    "unyo": sc.bars2("毎月いくら出すか",
                     ("預金だけ", 4.0, "4万円"),
                     ("年5%で増やす", 2.43, "2万4300円"), BADGE, BRAND, ymax=5),
    "sa": sc.card("毎月の差", "1万5700円", "※ 20年ぶんで377万円",
                  BADGE, BRAND, main_size=118, head_fs=32,
                  ask="あなたは月いくら貯めてる?"),
    "matome": sc.hayami("20年で出すお金",
                        [("預金だけ", "961万円"), ("年5%で増やす", "584万円"),
                         ("その差", "377万円"), ("受け取る額", "どちらも1000万円")],
                        "※ 年5%は仮定。増える保証はありません",
                        BADGE, BRAND, col1="どうやって貯めるか", col2="出すお金", focal=2),
    "shime": sc.chips("1000万円、何のために?",
                      ["老後のため", "家のため", "教育のため", "まだ決めてない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "貯金1000万円、月いくらで届く?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("mokuhyo", "たとえば20年で、貯めるとするのだ。", anim=1.4, speed=1.05),
    Unit("yokin", "まず銀行の預金だけで、貯めるとする。", anim=1.6, speed=1.05),
    Unit("yokin", "その預金の金利は、いま年0.4%とする。", anim=0.0, speed=1.05),
    Unit("yokin", "すると毎月4万円を、出すことになるのだ。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("unyo", "では年5%で増えたら、どうなるか。", anim=1.6, speed=1.05),
    Unit("unyo", "すると毎月2万4300円で、足りるのだ。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("sa", "だから毎月の差は、1万5700円になるのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.2),
    Unit("sa", "その差を20年ぶんに直すと、377万円。", anim=0.0, speed=1.05),
    Unit("matome", "つまり預金だけなら、961万円を出す。", anim=1.6, speed=1.05),
    Unit("matome", "増やしながらなら、584万円で足りるのだ。", anim=0.0, speed=1.05),
    Unit("matome", "受け取る額は、どちらも1000万円で同じ。", anim=0.0, speed=1.05),
    Unit("matome", "ただし年5%で増えると、決まってはいない。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "預金なら減らないかわりに、月4万円が要る。", anim=0.0, speed=1.05),
    Unit("shime", "だから毎月出せる額から、決めてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S021.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
