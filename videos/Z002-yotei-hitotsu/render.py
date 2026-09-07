#!/usr/bin/env python3
"""Z002「今週のカレンダーに、出なくていい予定が1つある」

チャンネル「ヤケに心理学に詳しいずんだもん」の2本目。企画書は plan.md。
型は docs/channel-zunda/strategy.md §8 の #11(場面型)。

**Z001 の反省をここに書いておく(2026-09-07 ユーザー指摘):**

> 「このショート動画に込められるメッセージは一つだよ? なんでこんな詰め込もうとしてるの??」

Z001 は「誰が言った/なぜ残った/誰が評価した」の3問に事実の鎖で全部答えにいって、
学説史の年表になった(60カット3分)。**この本のメッセージは1つだけ:**

    時間が足りないんじゃない。予定に取られてる。今週、1件消せ。

学びの3問は、この1つを深くするためだけに使う(plan.md §1.7 にカット上限を書いた:
誰が言った4 / なぜ残った2 / 誰が評価した2)。**この線に乗らないカットは、面白くても入れない。**

型を Z001 と散らす(strategy §8「同じ型を連続する3本のうち2本以上に入れない」):
Z001 は否定型・エピクテトス。Z002 は**場面型・セネカ**。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S  # noqa: E402
import fplib as F     # noqa: E402

F.POSE_DIR = ROOT / "assets" / "character-zunda"

TITLE = "足りないのは時間?"
BADGE = "※ 出典: セネカ『人生の短さについて』1.3–1.4・3.1(西暦49年ごろ)"
F.use_fp_theme(TITLE, speaker=3, badge=BADGE)      # 3 = ずんだもん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402
import scenes_zunda as sz  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 → 判定
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("今週のカレンダー、出なくていい予定が1つ入ってない?",
                           "今週", "予定でびっしり",
                           name="03_troubled", main_lab="いまのあなた",
                           alt_val="1件消す", alt_lab="あなたはどっち?",
                           disclaimer="※ 出典: セネカ『人生の短さについて』1.3–1.4・3.1(西暦49年ごろ)"),
    "ichinen": sz.calendar_one("03_troubled", "1年", "×", bubble="終わってた"),
    "tarinai": sz.thinking_loop("03_troubled", ),
    "hantei": sz.calendar_pair("02_point"),
    "torareru": sz.bubble_locked("04_surprised", "予定に取られてる"),
    "kesu": sz.calendar_one("02_point", "今週", "×", bubble="1件消せる"),

    # ---- 幕3 誰が言った(4カット)
    "seneca": sz.ancient_person("04_surprised", "西暦49年", "セネカ"),
    "nero": sz.emperor("04_surprised", "皇帝ネロ", bubble="家庭教師"),
    "isogashii": sz.boss_sheet("03_troubled", "国の財政"),
    "quote1": sz.quote_card("短いんじゃない|多くを失ってるんだ", "『人生の短さについて』1.3"),

    # ---- 幕4 なぜ残った(2カット)
    "shahon": sz.copyists("04_surprised"),
    "ambro": sz.book_now("02_point", "11世紀の1冊", bubble="ここから100以上"),

    # ---- 幕5 誰が評価した(2カット)
    "montaigne": sz.ancient_person("05_happy", "16世紀", "モンテーニュ"),
    "essai": sz.book_now("05_happy", "『エセー』", bubble="手本はセネカ"),

    # ---- 幕6 もう一文 → 動作 → 締め
    "quote2": sz.quote_card("財産は誰にも分けないのに|人生は人に分けてしまう", "『人生の短さについて』3.1"),
    "waketa": sz.calendar_pair("03_troubled"),
    "kesu2": sz.calendar_one("02_point", "今週", "×", bubble="出なくていい1件"),
    "henshin": sz.memo_tag("02_point", "欠席の返信"),
    "owari": sz.go_home("05_happy"),
}

UNITS = [
    # ---- 幕1 場面 → 判定(6)
    Unit("toi", "今週のカレンダー、出なくていい予定が1つ入ってない?", anim=1.7, cover=True,
         se="pop", speed=1.28, intonation=1.25, pad=0.06, chara="none"),
    Unit("ichinen", "気づいたら1年終わってた、って毎年言ってるでしょ。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.06, chara="none"),
    Unit("tarinai", "時間が足りないって、あなたも思ってるよね。", anim=1.7, speed=1.30,
         intonation=1.25, pad=0.05, chara="none"),
    Unit("hantei", "でも足りてないのは、時間じゃないの。", anim=1.7, speed=1.28,
         intonation=1.2, pad=0.08, chara="none"),
    Unit("torareru", "予定に取られてるだけ。", anim=1.9,
         se="don", speed=1.28, intonation=1.3, pad=0.12, chara="none"),
    Unit("kesu", "カレンダーは、入れるものじゃなくて消せるものなの。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- 幕3 誰が言った(4)
    Unit("seneca", "これを言ったのがセネカ。西暦49年のローマの政治家ね。", anim=1.7,
         speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("nero", "セネカは、皇帝ネロの家庭教師。", anim=1.5,
         speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("isogashii", "国の財政まで動かしてた、ローマでいちばん忙しい側の人間。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("quote1", "その人が書いてる。「短いんじゃない、多くを失ってるんだ」。", anim=1.9,
         se="don", speed=1.28, intonation=1.25, pad=0.12, chara="none"),

    # ---- 幕4 なぜ残った(2)
    Unit("shahon", "この本が残ったのは、写本1冊のおかげなの。", anim=1.7,
         speed=1.30, intonation=1.25, pad=0.05, chara="none"),
    Unit("ambro", "11世紀の1冊から、いまの100以上が写された。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- 幕5 誰が評価した(2)
    Unit("montaigne", "その書き方を手本にしたのが、モンテーニュ。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("essai", "『エセー』の書き方は、セネカから来てるんだよ。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),

    # ---- 幕6 もう一文 → 動作 → 締め(5)
    Unit("quote2", "セネカはこうも書いてる。「財産は誰にも分けないのに」。", anim=1.7,
         speed=1.28, intonation=1.2, pad=0.05, chara="none"),
    Unit("waketa", "「人生のほうは、人に分けてしまう」って。", anim=1.9,
         se="don", speed=1.28, intonation=1.25, pad=0.12, chara="none"),
    Unit("kesu2", "あなたの今週も、人に分けた予定で埋まってない?", anim=1.7,
         speed=1.30, intonation=1.25, pad=0.06, chara="none"),
    Unit("henshin", "出なくていい1件を選んで、今週のうちに消して。", anim=1.7,
         speed=1.30, intonation=1.2, pad=0.05, chara="none"),
    Unit("owari", "自分で消せない会議なら、欠席の返信を1件送るだけでいい。", anim=1.7,
         speed=1.28, intonation=1.2, pad=0.05, chara="none"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z002.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
