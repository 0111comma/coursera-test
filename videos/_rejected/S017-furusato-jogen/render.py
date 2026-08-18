#!/usr/bin/env python3
"""S017: ふるさと納税、上限を超えたらいくら損するのか。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  上限を超えて1万円出すと、上限の内で出すのと何が変わるのか。
答え:
  上限の内なら手出しはほぼ増えず、返礼品3000円ぶんが残る。
  上限の外だと1万円がまるまる手出しになり、7000円のマイナス。差は1万円。

この人の欲求(yokkyu-map A: 取られたくない / C: 無駄にしたくない):
  **上限ギリギリまでやりたい。でも超えて自腹になるのは嫌だ。**

作り直しの経緯(ループ71のユーザー指摘):
  前の版は「10月から地場産品の基準が厳しくなる」という**制度の解説**だった。
  ユーザー:「制度を紹介するとか、変わったルールを解説するのは別に俺らじゃなくていい。
            なぜかというと、それは自治体とか税務署がやってることだし」
  そのとおりで、基準の改正は視聴者の財布の話になっていなかった。
  「年末でいいと思っている人」に向けていたが、**それは欲求ではない**。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

KIFU, HENREI = 10_000, 3_000
assert KIFU - HENREI == 7_000

SCENES = {
    "toi": sc.card("この動画の問い", "いくら損する?", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, main_size=104, head_fs=32),
    "toi__cover": sc.cover("ふるさと納税、上限を超えたらどうなる?", "7,000円",
                           "同じ1万円が、得にも損にもなる",
                           "2026年8月時点", BRAND),
    "jogen": sc.card("上限とは", "税金が減る限度", "※ 年収と家族構成で変わります",
                     BADGE, BRAND, main_size=94, head_fs=32),
    "uchi": sc.bars2("上限の内なら",
                     ("税金から引かれる", 10.0, "1万円"),
                     ("じぶんの手出し", 0.0, "ゼロ"), BADGE, BRAND, ymax=12),
    "soto": sc.bars2("上限の外なら",
                     ("税金から引かれる", 0.0, "ゼロ"),
                     ("じぶんの手出し", 10.0, "1万円"), BADGE, BRAND, ymax=12,
                     ),
    "son": sc.card("超えた1万円の差し引き", "7000円の損", "※ 返礼品のぶんを引いた額",
                   BADGE, BRAND, main_size=108, head_fs=32,
                   ask="あなたは上限を計算した?"),
    "matome": sc.hayami("寄付する前に見る4つ",
                        [("上限の内", "手出しは増えない"), ("上限の外", "まるまる手出し"),
                         ("返礼品", "寄付の一部だけ"), ("内と外の差", "1万円")],
                        "※ 2026年8月時点。金額はすべて仮定の例です",
                        BADGE, BRAND, col1="どこで寄付するか", col2="どうなるか", focal=1),
    "shime": sc.chips("あなたの上限は?",
                      ["計算した", "だいたい知ってる", "知らない", "まだやってない"],
                      BADGE, BRAND),
}

UNITS = [
    # 1ユニット目は、欲求を問いの形にして言う(ループ71)
    Unit("toi", "ふるさと納税、上限を超えたらどうなる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("jogen", "その上限とは、税金が減る限度のこと。", anim=1.4, speed=1.05),
    Unit("jogen", "その限度までなら、自己負担は2000円だけ。", anim=0.0, speed=1.05),
    Unit("uchi", "まず上限の内で、1万円ふやしたとする。", anim=1.6, speed=1.05),
    Unit("uchi", "その1万円は、税金からそのまま引かれる。", anim=0.0, speed=1.05),
    Unit("uchi", "だから手出しは、ほぼゼロなのだ。", anim=0.0, speed=1.05),
    Unit("uchi", "しかもその返礼品が、3000円ぶん残る。", anim=0.0,
         face="happy", speed=1.05),
    Unit("soto", "では上限を超えて、出したらどうなるか。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("soto", "その1万円は、税金から引かれずゼロ。", anim=0.0,
         face="surprised", se="impact", se_at=0.30, speed=1.05, intonation=1.25),
    Unit("soto", "だからその1万円が、手出しになるのだ。", anim=0.0, speed=1.05),
    Unit("son", "その返礼品は同じ、3000円ぶんなのだ。", anim=1.6, speed=1.05),
    Unit("son", "つまり差し引き、7000円のマイナス。", anim=0.0,
         se="don", speed=1.05, intonation=1.2),
    Unit("son", "だから同じ1万円で、1万円ちがうのだ。", anim=0.0, speed=1.05),
    Unit("matome", "その上限は、いま2026年の年収で変わる。", anim=1.6, speed=1.05),
    Unit("matome", "しかも家族の人数でも、動くのだ。", anim=0.0, speed=1.05),
    Unit("matome", "でもその年収は、年末まで決まらないのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("matome", "だから上限も、いまは確かな数字ではない。", anim=0.0, speed=1.05),
    Unit("shime", "だから上限は、少し手前で止めてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
