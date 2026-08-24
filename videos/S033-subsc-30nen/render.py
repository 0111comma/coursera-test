#!/usr/bin/env python3
"""S033: Netflix・Spotify・Amazonプライム。3つで30年いくらか。

P-M(35歳・男性・会社員)の1本目。
**カットは1本ずつ変える。**S032は40.1秒で11カット(3.65秒/カット)で、
競合の1.6〜1.8秒に対して2倍遅かった。check_tempo が落とすようにしてある。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

TITLE = "サブスク3つ、30年でいくら?"
BADGE = "※ 料金は2026年8月時点。運用は年5%と仮定した場合の計算です"
F.use_fp_theme(TITLE, speaker=108, badge=BADGE)      # 東北きりたん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

# 台本に出す値は verify.py と一致していること
assert V.MONTHLY == 3_162 and V.MONTHS == 360
assert V.PRINCIPAL == 1_138_320
assert round(V.DAILY) == 105
assert round(V.FV5 / 10_000) == 263
assert round(V.ONE_FV5 / 10_000) == 90 and round(V.ONE_PRINCIPAL / 10_000) == 39

SCENES = {
    "namae": sf.person("01_base", height=0.44, top=0.855),
    "namae__cover": sf.cover("Netflix、Spotify", "Amazonプライム", "3つで月いくら?"),
    "hyo": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=3, title="30代がよく持つ3つ"),
    "hyo2": sf.hero("3162円", "3つ合わせて", name="02_point"),
    "waru": sf.formula("3162円 ÷ 30日", "= 1日あたり"),
    "kan": sf.person_bubble("01_base", "缶コーヒー1本"),
    "nagai": sf.person("01_base", height=0.62),
    "kikan": sf.hero("360か月", "35歳から65歳までの30年", name="02_point"),
    "shiki1": sf.formula("3162円 × 360か月", "= 30年で出ていく額"),
    "deru": sf.hero("114万円", "30年で出ていく額", name="03_troubled"),
    "oboe": sf.person("03_troubled"),
    "hondai": sf.person("02_point"),
    "tameru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                       ("年5%と仮定", 2_631_602, "263万円")],
                      highlight=0, title="同じ3162円を積んだら"),
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, title="同じ3162円を積んだら"),
    "fue": sf.hero("263万円", "30年後", name="04_surprised"),
    "gyaku": sf.person("04_surprised"),
    "zenbu": sf.person_bubble("01_base", "3つとも?"),
    "tomeru": sf.person_bubble("02_point", "使ってない1つ"),
    "hitotsu": sf.hero("1080円", "使っていない1つ", name="02_point"),
    "hitotsu2": sf.bars([("出したお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, title="1つ止めたら"),
    "shiki2": sf.formula("月額 × 360か月", "= 30年で出ていく額"),
    "toi2": sf.person_bubble("02_point", "月いくら?"),
    "cta2": sf.cta("", "02_point", show_comment=True),
}

UNITS = [
    # 冒頭は**問い**。「サブスク」は30代の日常語(strategy.md §6.2で名指しを解禁)
    Unit("namae", "サブスク3つで、月いくら?", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    Unit("hyo", "1590円と1080円と492円。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo2", "合計で【3162円】。", anim=1.0, se="don", speed=1.0,
         intonation=1.2, chara="none"),
    Unit("waru", "3162円は1日【105円】。", anim=1.0, speed=1.05, chara="none"),
    Unit("kan", "105円は缶コーヒー1本ぶん。", anim=1.0, speed=1.1, chara="none"),
    Unit("nagai", "缶コーヒーを35歳から65歳まで。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("kikan", "65歳までは【360か月】。", anim=1.0, speed=1.05, chara="none"),
    Unit("shiki1", "3162円×360か月。", anim=1.0, speed=1.05, chara="none"),
    # 式と答えを割る(溜めて出す)。ここは1カットぶん止める
    Unit("deru", "【114万円】です。", anim=1.0, se="impact", se_at=0.1,
         speed=0.95, intonation=1.35, pad=0.35, chara="none"),
    Unit("oboe", "あなたはこの114万円、覚えがありますか?", anim=1.0, speed=1.05,
         pad=0.3, chara="none"),

    Unit("hondai", "この114万円を積んだら?", anim=1.0, speed=1.1, chara="none"),
    Unit("tameru", "貯めるだけなら【114万円】。", anim=1.0, speed=1.05, chara="none"),
    Unit("fueru", "出ていく114万円と同じ。", anim=1.0, speed=1.05, chara="none"),
    Unit("fue", "114万円が、年5%と仮定すると【263万円】。", anim=1.0, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("gyaku", "263万円。同じお金が逆側に。", anim=1.0, se="impact", se_at=0.2,
         speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    Unit("zenbu", "263万円のために、3つとも止める?", anim=1.0, speed=1.1,
         chara="none"),
    Unit("tomeru", "いりません。3つのうち【1つ】でいい。", anim=1.0,
         speed=1.05, chara="none"),
    Unit("hitotsu", "その1つが【1080円】なら。", anim=1.0, speed=1.05, chara="none"),
    Unit("hitotsu2", "30年で【約90万円】。", anim=1.0, se="don", speed=1.0,
         intonation=1.25, pad=0.3, chara="none"),
    Unit("shiki2", "30年ぶんは月額×360。", anim=1.0, speed=1.05, chara="none"),
    Unit("toi2", "あなたの月額を、コメントで教えてください。", anim=1.0,
         speed=1.05, chara="none"),
    # 冒頭の問いをそのまま繰り返して終わる(ループの継ぎ目)
    Unit("cta2", "サブスク3つで、月いくら?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S033.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
