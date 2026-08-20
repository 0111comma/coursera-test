#!/usr/bin/env python3
"""S021: 「老後2000万円」は、月いくらで届くのか。

企画書は plan.md、数値は verify.py。
答え: 預金だけなら月5万2300円。年5%と仮定するなら月2万4000円。

この人の欲求(yokkyu-map D: 先の不安を減らしたい):
  **「老後2000万円」と聞いて不安なだけで、何もできていない。
    毎月の数字に直して、不安を手元の判断に変えたい。**
yokkyu-map D の note のとおり「数字を出すと不安はむしろ下がる」方向で作る。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年5%は仮定・2026年8月時点"

YOKIN, UNYO = 52_300, 24_000
assert YOKIN - UNYO == 28_300

SCENES = {
    "toi": sc.card("この動画の問い", "月いくらで届く?", "※ 30年かけて貯める場合の例です",
                   BADGE, BRAND, main_size=90, head_fs=32),
    "toi__cover": sc.cover("老後の2000万円、月いくらで届く?", "5万2300円",
                           "年5%と仮定するなら、月2万4000円",
                           "年5%は仮定", BRAND),
    "fuan": sc.card("よく聞く数字", "老後に2000万円", "※ 足りない額は人によって違います",
                    BADGE, BRAND, main_size=86, head_fs=32),
    "yokin": sc.bars2("増える力のちがい",
                       ("預金の金利", 0.4, "年0.4%"),
                       ("仮定する利回り", 5.0, "年5%"), BADGE, BRAND, ymax=6),
    "unyo": sc.bars2("毎月いくら出すか",
                     ("預金だけ", 5.23, "5万2300円"),
                     ("年5%と仮定", 2.4, "2万4000円"), BADGE, BRAND, ymax=6.2),
    "sa": sc.card("毎月の差", "2万8300円", "※ 30年ぶんでは1018万円",
                  BADGE, BRAND, main_size=112, head_fs=32,
                  ask="あなたは月いくらなら出せる?"),
    "matome": sc.hayami("30年で出すお金",
                        [("預金だけ", "月5万2300円"), ("年5%と仮定", "月2万4000円"),
                         ("30年で出す差", "1018万円"), ("受け取り", "どちらも2000万円")],
                        "※ 年5%は仮定。増える保証はありません",
                        BADGE, BRAND, col1="どうやって届かせるか", col2="出すお金", focal=2),
    "shime": sc.chips("老後資金の目標、どう決めるのがおすすめ?",
                      ["生活費から逆算", "年金しだいで決める", "多いほど安心", "目標はいらない"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "老後の2000万円、月いくらで届く?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("fuan", "老後に2000万円いる、という話をよく聞く。", anim=1.4, speed=1.05),
    Unit("fuan", "2000万円を、不安なまま置いていないか。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("fuan", "毎月の数字に直すと、不安は判断に変わる。", anim=0.0, speed=1.05),
    Unit("yokin", "たとえば定年までの30年で、貯めるとする。", anim=1.6, speed=1.05),
    Unit("yokin", "まず預金の金利だけで、届かせてみるのだ。", anim=0.0, speed=1.05),
    Unit("yokin", "金利はいま、年0.4%の水準なのだ。", anim=0.0, speed=1.05),
    Unit("unyo", "この場合は毎月5万2300円、要るのだ。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("unyo", "では積立が年5%で、増えたと仮定する。", anim=0.0, speed=1.05),
    Unit("unyo", "仮定どおりなら毎月2万4000円で、足りる。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("sa", "毎月の差は、2万8300円になるのだ。", anim=1.6,
         se="don", speed=1.05, intonation=1.2),
    Unit("matome", "ちなみに30年で出すお金も、大きくちがう。", anim=1.6, speed=1.05),
    Unit("matome", "30年ぶんの差は、1018万円にもなる。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("matome", "ただし年5%で増えると、決まってはいない。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "預金は増えないかわり、減りもしないのだ。", anim=0.0, speed=1.05),
    Unit("shime", "だから毎月出せる額から、決めてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S021.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
