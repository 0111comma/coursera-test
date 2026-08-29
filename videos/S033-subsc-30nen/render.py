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

# **立ち絵はカバーと締め、それに本編の1か所だけ。**(2026-08-24)
# ユーザー指摘:「この女の人出しすぎだね。参考のペンギンは3、4回しか出てない」
# 参考(BANK ACADEMY)の実測: 本編19フレーム中、キャラは1フレームだけ。
# 直前の版は 24カット中17カット(71%)がキャラだった。本編は図で埋める。
SCENES = {
    # ---- カバー(キャラ 1/4)
    # 読点「、」は欧文の列挙では中黒「・」(字間が締まる)。表情は問いに合わせ
    # 「考え込む」ポーズ(2026-08-29 批評ループ。微笑みは問いと矛盾していた)
    "namae": sf.person("01_base", height=0.62, top=0.855),
    "namae__cover": sf.cover("Netflix・Spotify", "Amazonプライム", "3つで月いくら?",
                             name="03_troubled"),

    # ---- 表を出しっぱなしにして、**赤枠を1行ずつ下に動かす**(参考の主武器)
    # build=最初のカットだけ行を順に着地させる。from_row=赤枠がすべってくる出発点
    "hyo_n": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=0, from_row=2, title="30代がよく持つ3つ"),
    "hyo_s": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=1, from_row=0, title="30代がよく持つ3つ"),
    "hyo_q": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=None, title="3つで月いくら?"),
    "hyo_a": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=2, build=True, title="30代がよく持つ3つ"),
    "hyo_g": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=3, from_row=0, title="30代がよく持つ3つ"),

    "waru": sf.formula("3162円 ÷ 30日", "= 1日あたり", name=None),
    "hi": sf.hero("105円", "1日あたり。缶コーヒー1本より安い", name=None),
    "obi": sf.arrow("35歳", "65歳", "いま", "積むのをやめる",
                    title="30年、つづけると"),
    "kikan": sf.hero("360か月", "35歳から65歳までの30年", name=None),
    "shiki1": sf.formula("3162円 × 360か月", "= 30年で出ていく額", name=None),

    # ---- 本編で唯一の立ち絵(キャラ 2/4)。いちばん刺す一行に置く
    "toi_oboe": sf.person_bubble("03_troubled", "114万円…?"),

    "hondai": sf.hero("114万円", "これを、積んだら?", name=None),
    "tsumu": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=0, title="同じ3162円を積んだら"),
    "katei": sf.hero("年5%", "あくまで仮定。元本保証ではありません", name=None),
    # prev_highlight=0: 赤が「貯める側」から「運用側」へクロスフェードで移る
    # (静止画切り替えだと「色を塗り間違えた」ように見える。2026-08-29)
    "fueru": sf.bars([("ただ貯める", 1_138_320, "114万円"),
                      ("年5%と仮定", 2_631_602, "263万円")],
                     highlight=1, prev_highlight=0, title="同じ3162円を積んだら"),
    "yaji": sf.arrow("114万円", "263万円", "出ていく", "積んだら",
                     title="同じ3162円が"),
    "gyaku": sf.arrow("出ていく", "入ってくる", "いままで", "これから",
                      title="お金の向きが変わる"),

    # ---- 1つでいい
    "hyo_x": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=None, title="全部やめなくていい"),
    "hyo_1": sf.table(["", "月額"],
                    [["Netflix", "1590円"],
                     ["Spotify", "1080円"],
                     ["Amazonプライム", "492円"],
                     ["合計", "3162円"]],
                    highlight=1, from_row=3, title="使っていない1つだけ"),
    "hitotsu": sf.hero("1080円", "使っていない1つ", name=None),
    "hitotsu2": sf.bars([("出したお金", 388_800, "約39万円"),
                         ("年5%と仮定", 898_839, "約90万円")],
                        highlight=1, title="1つ止めたら"),
    "shiki2": sf.formula("月額 × 360か月", "= 30年で出ていく額", name=None),

    # ---- 締め(キャラ 3/4・4/4)
    "meisai": sf.person_bubble("03_troubled", "明細チェック"),
    "cta2": sf.cta("", "02_point", show_comment=True),
}

# 「運用は年5%と仮定」の免責は、運用の話が画面に出るまで先頭の一文だけにする
# (0秒目から出すと後半のひねりを自分でネタバレする。2026-08-29 批評ループ)。
# tsumu(年5%の棒が出る)以降は全文のまま。
for _k in ("namae", "hyo_n", "hyo_s", "hyo_q", "hyo_a", "hyo_g",
           "waru", "hi", "obi", "kikan", "shiki1", "toi_oboe", "hondai"):
    SCENES[_k] = sf.badge_head(SCENES[_k])

UNITS = [
    Unit("namae", "NetflixにSpotify、", anim=1.0, cover=True,
         se="pop", speed=1.0, intonation=1.3, chara="none"),
    Unit("hyo_a", "Amazonプライムですね。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo_q", "この3つ、月いくら払ってますか?", anim=1.0, speed=1.0,
         intonation=1.25, chara="none"),
    Unit("hyo_n", "1590円、1080円、492円。", anim=1.0, speed=1.05, chara="none"),
    Unit("hyo_g", "合わせて月【3162円】です。", anim=1.0, se="don", speed=1.0,
         intonation=1.2, chara="none"),
    Unit("waru", "1日にするとたった【105円】。", anim=1.0, speed=1.05, chara="none"),
    Unit("hi", "缶コーヒーより安い金額です。", anim=1.0, speed=1.1, chara="none"),
    Unit("obi", "これを35歳から65歳まで。", anim=1.2, speed=1.05, chara="none"),
    Unit("kikan", "30年、【360か月】続けると。", anim=1.0, speed=1.05, chara="none"),
    Unit("shiki1", "出ていくお金は【114万円】。", anim=1.0, se="impact", se_at=0.1,
         speed=0.95, intonation=1.3, chara="none"),
    Unit("toi_oboe", "無意識に114万、払いますか?", anim=1.0, speed=1.0,
         intonation=1.25, pad=0.35, chara="none"),

    Unit("hondai", "ここからが今日の本題です。", anim=1.0, speed=1.1, chara="none"),
    Unit("tsumu", "このお金を積んだらどうなるか。", anim=1.2, speed=1.05, chara="none"),
    Unit("katei", "年5%で運用できたと仮定します。", anim=1.0, speed=1.05, chara="none"),
    Unit("fueru", "すると【263万円】になります。", anim=1.2, se="don",
         speed=1.0, intonation=1.25, chara="none"),
    Unit("yaji", "【114万円】が【263万円】に。", anim=1.2, speed=1.0,
         intonation=1.2, chara="none"),
    Unit("gyaku", "出ていくお金が、入ってくる側に。", anim=1.2, se="impact",
         se_at=0.2, speed=1.0, intonation=1.2, pad=0.35, chara="none"),

    Unit("hyo_x", "3つ全部やめなくていいんです。", anim=1.0, speed=1.1, chara="none"),
    Unit("hyo_1", "使ってないものを【1つ】だけ。", anim=1.0, speed=1.05, chara="none"),
    Unit("hitotsu", "【1080円】のものを1つ止めれば。", anim=1.0, speed=1.05,
         chara="none"),
    Unit("hitotsu2", "30年で【約90万円】になります。", anim=1.2, se="don",
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
