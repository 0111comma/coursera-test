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
import shortlib as _sl  # noqa: E402

_sl.set_accent("pension")  # カテゴリ色(docs/research/sakubun-gensoku.md とは別の画面施策)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・月16万円と仮定した計算"

ZOU = 13_440
assert round(160_000 * 0.084) == ZOU

SCENES = {
    "toi": sc.card("この動画の問い", "何歳で得になる?", "※ 月16万円と仮定した例です",
                   BADGE, BRAND, main_size=92, head_fs=32),
    "toi__cover": sc.cover("年金、1年待つと何歳で得になる?", "??歳",
                           "答えの歳より長く生きるなら、待つほど得",
                           "2026年8月時点", BRAND),
    "shikumi": sc.bars2("増える割合",
                        ("ひと月遅らせる", 0.7, "0.7%"),
                        ("1年遅らせる", 8.4, "8.4%"), BADGE, BRAND, ymax=10),
    "zou": sc.bars2("月にもらえる額",
                    ("待たない場合", 16.0, "16万円"),
                    ("1年待つと", 17.344, "+1万3440円"), BADGE, BRAND, ymax=20),
    "minoga": sc.bars2("待つあいだの年金",
                       ("待たない場合", 19.2, "192万円"),
                       ("待つ場合", 0.0, "ゼロ"), BADGE, BRAND, ymax=23),
    "oitsuku": sc.card("もらい損ねは重い", "143ヶ月", "※ ほぼ12年です",
                       BADGE, BRAND, main_size=110, head_fs=32,
                       ask="あなたは何歳だと思う?"),
    "kotae": sc.card("追いつくのは", "78歳", "※ 1年待って始めた場合",
                     BADGE, BRAND, main_size=140, head_fs=32),
    "shime": sc.chips("あなたなら何歳からがおすすめ?",
                      ["待たずにもらう", "少しだけ待つ", "数年待つ", "ぎりぎりまで待つ"],
                      BADGE, BRAND),
}

UNITS = [
    # 維持率の新しい型(ループ71 / hold-rate-2026-08.md):
    #   カバーは「??歳」で答えをマスク / 答えの78歳は87%地点まで出さない /
    #   途中に「あなたは何歳だと思う?」の参加を挟む / 締めは冒頭の問いに戻す
    Unit("toi", "年金、1年待つと何歳で得になる?", anim=1.0, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("toi", "年金は待つほど増えると、聞いたはず。", anim=1.4, speed=1.05),
    Unit("toi", "でも何歳で得かは、誰も計算しない。", anim=0.0, speed=1.05),
    Unit("shikumi", "計算すると、ひと月遅らせるごとに0.7%。", anim=1.4, speed=1.05),
    Unit("shikumi", "0.7%を1年つづけると、8.4%になる。", anim=0.0, speed=1.05),
    Unit("zou", "月16万円の人で、8.4%を見てみる。", anim=1.6,
         speed=1.05, intonation=1.2),
    Unit("zou", "すると月に、1万3440円ふえるのだ。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("zou", "ふえた1万3440円は、一生つづく。", anim=0.0,
         face="happy", speed=1.05),
    Unit("zou", "一生つづくなら、待つほど得に見える。", anim=0.0, speed=1.05),
    Unit("minoga", "でも待った1年、年金は1円も入らない。", anim=1.6,
         face="troubled", se="impact", se_at=0.30, speed=1.05, intonation=1.2),
    Unit("minoga", "入らない年金は、192万円にもなる。", anim=0.0, speed=1.05),
    Unit("oitsuku", "192万円を、1万3440円で取り返すのだ。", anim=1.6, speed=1.05),
    Unit("oitsuku", "1万3440円ずつでは、143ヶ月かかる。", anim=0.0, speed=1.05),
    Unit("oitsuku", "143ヶ月はほぼ12年、では何歳なのか。", anim=0.0,
         face="troubled", speed=1.05, intonation=1.2),
    Unit("kotae", "答えは、78歳なのだ。", anim=1.6,
         face="surprised", se="don", speed=1.05, intonation=1.3),
    Unit("kotae", "78歳より長く生きるなら、待つほど得なのだ。", anim=0.0, speed=1.05),
    Unit("shime", "何歳まで生きるかの見立てで、決まるのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.1, intonation=1.2),
]

if __name__ == "__main__":
    require_voicevox()
    r = render_video(UNITS, SCENES, OUTDIR, "S027.mp4")
    print(f"total: {r['total_sec']:.1f}s / mp4: {r['mp4']}")
