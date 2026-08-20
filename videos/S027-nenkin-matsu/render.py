#!/usr/bin/env python3
"""S027: 年金を1年待つと、何歳で得になるのか。

企画書は plan.md、数値は verify.py。
答え: 78歳で追いつく。それより長生きするなら、待つほど得。

この人の欲求(yokkyu-map A/B: 損したくない・選び間違えたくない):
  **もらい方で損をしたくない。いつから受け取るかを選び間違えたくない。**
S011(年金、何歳まで生きたら元が取れる? — ユーザー評価が高い)の直接の続き。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・月16万円と仮定した計算"

ZOU = 13_440
assert round(160_000 * 0.084) == ZOU

SCENES = {
    "toi": sc.card("この動画の問い", "何歳で得になる?", "※ 月16万円と仮定した例です",
                   BADGE, BRAND, main_size=92, head_fs=32),
    "toi__cover": sc.cover("年金、1年待つと何歳で得になる?", "78歳",
                           "それより長生きなら、待つほど得",
                           "2026年8月時点", BRAND),
    "shikumi": sc.card("遅らせた月ごとに", "0.7%ずつ増える", "※ もらい始めを後ろにできます",
                       BADGE, BRAND, main_size=86, head_fs=32),
    "zou": sc.bars2("月にもらえる額",
                    ("待たない場合", 16.0, "16万円"),
                    ("1年待つと", 17.344, "17万3440円"), BADGE, BRAND, ymax=20),
    "minoga": sc.bars2("待つあいだの年金",
                       ("待たない場合", 19.2, "192万円"),
                       ("待つ場合", 0.0, "ゼロ"), BADGE, BRAND, ymax=23),
    "oitsuku": sc.card("追いつくのは", "78歳", "※ 追いつくまで143ヶ月",
                       BADGE, BRAND, main_size=136, head_fs=32),
    "matome": sc.hayami("待つかどうかの判定",
                        [("78歳より長生き", "待つほど得"), ("78歳より前", "待った分だけ損"),
                         ("増える率", "1年で8.4%"), ("増えた額", "一生つづく")],
                        "※ 2026年8月時点。月16万円と仮定した例です",
                        BADGE, BRAND, col1="自分の見立て", col2="どちらが得か", focal=0),
    "shime": sc.chips("あなたなら何歳からがおすすめ?",
                      ["待たずにもらう", "少しだけ待つ", "数年待つ", "ぎりぎりまで待つ"],
                      BADGE, BRAND),
}

UNITS = [
    Unit("toi", "年金、1年待つと何歳で得になる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("shikumi", "年金は、もらう時期を遅らせられるのだ。", anim=1.4, speed=1.05),
    Unit("shikumi", "時期をひと月遅らせると、0.7%増える。", anim=0.0, speed=1.05),
    Unit("shikumi", "0.7%を1年ぶん足すと、8.4%になる。", anim=0.0, speed=1.05),
    Unit("zou", "たとえば月16万円の人で、見てみる。", anim=1.6, speed=1.05),
    Unit("zou", "その16万円が、1年待つと17万3440円。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("zou", "つまり月に、1万3440円ふえるのだ。", anim=0.0,
         face="happy", speed=1.05),
    Unit("minoga", "そのかわり、待つあいだは年金が入らない。", anim=1.6,
         face="troubled", speed=1.05),
    Unit("minoga", "入らない年金は、1年で192万円になる。", anim=0.0,
         se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("oitsuku", "192万円を、増えた1万3440円で取り返す。", anim=1.6, speed=1.05),
    Unit("oitsuku", "すると取り返すのに、143ヶ月かかるのだ。", anim=0.0, speed=1.05),
    Unit("oitsuku", "143ヶ月は、ほぼ12年なのだ。", anim=0.0, speed=1.05),
    Unit("oitsuku", "だから追いつくのは、78歳になるのだ。", anim=0.0,
         face="surprised", se="don", speed=1.05, intonation=1.25),
    Unit("matome", "78歳より長生きするなら、待つほど得。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("matome", "逆に78歳より前だと、待った分だけ損。", anim=0.0, speed=1.05),
    Unit("shime", "だから自分の見立てで、決めてほしいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S027.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
