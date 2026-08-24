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
    # ---- 掴み: サービス名を2つに割って出す
    "namae": sf.person("01_base", height=0.50, top=0.855),
    "namae__cover": sf.cover("Netflix、Spotify", "Amazonプライム", "3つで月いくら?"),
    "namae2": sf.person("02_point", height=0.50, top=0.855),
    "toi1": sf.person("01_base", height=0.62),

    "hyo": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=3, title="30代がよく持つ3つ"),
    "hyo2": sf.hero("3162円", "3つ合わせて", name="02_point"),
    "waru": sf.formula("3162円 ÷ 30日", "= 1日あたり"),
    "kan": sf.person_bubble("01_base", "缶コーヒー以下"),
    "nagai": sf.person("02_point", height=0.62),
    "kikan": sf.hero("360か月", "35歳から65歳までの30年", name="02_point"),
    "shiki1": sf.formula("3162円 × 360か月", "= 30年で出ていく額"),
    "deru": sf.hero("114万円", "30年で出ていく額", name="03_troubled"),
    "hondai": sf.person("02_point"),

    # ---- 反転
    "tameru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                       ("年5%と仮定", 2_631_602, "263万円")],
                      highlight=0, title="同じ3162円を積んだら"),
    "katei": sf.person("01_base"),
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, title="同じ3162円を積んだら"),
    "fue": sf.hero("263万円", "30年後", name="04_surprised"),
    "gyaku": sf.person("04_surprised"),

    # ---- 1つでいい
    "zenbu": sf.person_bubble("01_base", "3つとも?"),
    "tomeru": sf.person_bubble("02_point", "使ってない1つ"),
    "hitotsu": sf.hero("1080円", "使っていない1つ", name="02_point"),
    "hitotsu2": sf.bars([("出したお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, title="1つ止めたら"),
    "shiki2": sf.formula("月額 × 360か月", "= 30年で出ていく額"),
    "meisai": sf.person_bubble("03_troubled", "明細チェック"),
    "cta2": sf.cta("", "02_point", show_comment=True),
}

# ---------------------------------------------------------------------------
# **台詞は外部の添削を通したものをそのまま使う。**(2026-08-24)
# ユーザーの判断:「お前が作ってるルールがカスでバカだから、ちゃんとした
# プロットが作れねえんだろ。お前がまず作ったプロットを向こうが添削するだけで
# よっぽどいいものができる」
# 日本語を縛るゲート(flow / teinei / bunsho など)には**合わせない**。
# 合わせると「114万円が」「114万円を」の連呼のような壊れた文になる。
UNITS = [
    Unit("namae", "NetflixにSpotify、", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    Unit("namae2", "Amazonプライムですね。", anim=1.0, speed=1.05, chara="none"),
    Unit("toi1", "この3つ、月いくら払ってますか?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("hyo", "1590円、1080円、492円。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo2", "合わせて月【3162円】です。", anim=1.0, se="don", speed=1.0,
         intonation=1.2, chara="none"),
    Unit("waru", "1日にするとたった【105円】。", anim=1.0, speed=1.05, chara="none"),
    Unit("kan", "缶コーヒーより安い金額です。", anim=1.0, speed=1.1, chara="none"),
    Unit("nagai", "これを35歳から65歳まで。", anim=1.0, speed=1.05, chara="none"),
    Unit("kikan", "30年、【360か月】続けると。", anim=1.0, speed=1.05, chara="none"),
    Unit("shiki1", "出ていくお金は【114万円】。", anim=1.0, se="impact", se_at=0.1,
         speed=0.95, intonation=1.3, chara="none"),
    Unit("deru", "無意識に114万、払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.35, chara="none"),

    Unit("hondai", "ここからが今日の本題です。", anim=1.0, speed=1.1, chara="none"),
    Unit("tameru", "このお金を積んだらどうなるか。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("katei", "年5%で運用できたと仮定します。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("fueru", "すると【263万円】になります。", anim=1.0, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("fue", "【114万円】が【263万円】に。", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("gyaku", "出ていくお金が、入ってくる側に。", anim=1.0, se="impact",
         se_at=0.2, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    Unit("zenbu", "3つ全部やめなくていいんです。", anim=1.0, speed=1.1, chara="none"),
    Unit("tomeru", "使ってないものを【1つ】だけ。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hitotsu", "【1080円】のものを1つ止めれば。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hitotsu2", "30年で【約90万円】になります。", anim=1.0, se="don",
         speed=1.0, intonation=1.25, pad=0.3, chara="none"),
    Unit("shiki2", "自分の額は月額×360ですよ。", anim=1.0, speed=1.05, chara="none"),
    Unit("meisai", "まずは明細を開いてみませんか?", anim=1.0, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("cta2", "あなたのサブスク、月いくら?", anim=1.0, speed=1.0,
         intonation=1.3, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S033.mp4", speaker=108, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
