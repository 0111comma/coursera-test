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
BADGE = "※ 出典: セネカ『人生の短さについて』1.3・1.4・3.1(西暦49年ごろ)"
F.use_fp_theme(TITLE, speaker=3, badge=BADGE)      # 3 = ずんだもん

from shortlib import Unit, render_video, require_voicevox  # noqa: E402
import scenes_fp as sf  # noqa: E402
import scenes_zunda as sz  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"

SCENES = {
    # ---- 幕1 場面 → 判定
    "toi": sf.person("03_troubled", height=0.46),
    "toi__cover": sf.cover("今週の予定、自分が出なくていい会議が1件ない?",
                           "今週", "予定でびっしり",
                           name="03_troubled", main_lab="いまのあなた",
                           alt_val="1件消す", alt_lab="あなたはどっち?",
                           disclaimer="※ 出典: セネカ『人生の短さについて』1.3・1.4・3.1(西暦49年ごろ)"),
    "gisshiri": sz.calendar_pair("03_troubled", left=("月", "×"), right=("火", "×")),
    "tarinai": sz.thinking_loop("03_troubled"),
    "hantei": sz.calendar_one("02_point", "今週", "?", bubble="足りないのは?"),
    "watashi": sz.bubble_locked("04_surprised", "こっちが渡してる"),
    "toi2": sz.calendar_one("03_troubled", "水", "?", bubble="回らない?"),

    # ---- 幕2 誰が言った
    "dashita": sz.memo_tag("02_point", "辞めろ、と書いた"),
    "seneca": sz.ancient_person("04_surprised", "古代ローマ", "セネカ"),
    "korushika": sz.ancient_person("03_troubled", "追放先の島", "呼び戻された"),
    "nazedasu": sz.emperor("04_surprised", "皇帝の家", bubble="なんで呼んだ?"),
    "riyuu": sz.emperor("02_point", "家庭教師に", bubble="勉強を教える役"),
    "nero": sz.emperor("04_surprised", "その息子", bubble="のちの皇帝"),
    "migiude": sz.boss_sheet("03_troubled", "国の仕事"),
    "isogashii": sz.thinking_loop("03_troubled"),
    "yakunin": sz.boss_sheet("04_surprised", "役人あて"),
    "tegami": sz.memo_tag("04_surprised", "手紙の一言"),
    "hon": sz.book_now("03_troubled", "手紙が本に", bubble="いまも読める"),

    # ---- 幕3 引用(1.3 / 1.4)
    "hajimari": sz.book_now("02_point", "はじめの一行", bubble="時間の話"),
    "quote1": sz.quote_card("多くを浪費してる", "『人生の短さについて』1.3"),
    "dare": sz.bubble_locked("04_surprised", "浪費してるのは"),
    "quote1b": sz.quote_card("自分たちがそうした", "『人生の短さについて』1.4"),

    # ---- 幕4 なぜ残った
    "nokotta": sz.book_now("04_surprised", "いまも読める", bubble="なんで?"),
    "shahon": sz.copyists("01_base"),
    "tsugi": sz.book_now("01_base", "手で写す", bubble="写本"),
    "ambro": sz.book_now("02_point", "11世紀", bubble="いちばん古い"),
    "hyakusatsu": sz.book_now("02_point", "100冊以上", bubble="ここから広がった"),

    # ---- 幕5 誰が評価した(**予定を実際に消した実例**)
    "yonda": sz.ancient_person("05_happy", "16世紀", "モンテーニュ"),
    "yameta": sz.calendar_one("05_happy", "職", "×", bubble="手放した"),
    "essai": sz.book_now("05_happy", "塔の上で", bubble="『エセー』"),
    "tehon": sz.book_now("02_point", "手本は", bubble="セネカの書き方"),

    # ---- 幕6 もう一文 → 動作 → 締め
    "iu2": sz.ancient_person("02_point", "セネカ", "財産のこと"),
    "quote2": sz.quote_card("誰にも分けない", "『人生の短さについて』3.1"),
    "waketa": sz.quote_card("時間なら分け与える", "『人生の短さについて』3.1"),
    "kesu1": sz.calendar_pair("03_troubled", left=("木", "×"), right=("金", "×")),
    "kesu2": sz.calendar_one("02_point", "今週", "×", bubble="1件だけ消す"),
    "henshin": sz.memo_tag("02_point", "「欠席」"),
    "owari": sz.go_home("05_happy"),
}

# 速度・抑揚は Z001 と同じ帯。**1カット3.0秒以内**(check_tempo)なので1文は目安25字まで。
# 長い文は割る。割るときは絵も変える(同じ絵が4.5秒続くと check_tempo が落ちる)
_F = dict(anim=1.7, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_S = dict(anim=1.5, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_D = dict(anim=1.9, se="don", speed=1.28, intonation=1.28, pad=0.12, chara="none")


def U(scene, sub, **kw):
    d = dict(_F)
    d.update(kw)
    return Unit(scene, sub, **d)


UNITS = [
    # ---- 幕1 場面 → 判定(6)。**原著の向きは能動**(1.4「自分たちがそうした」)なので
    #      「予定に取られてる」(他人のせい)にしない。plan §11「会社を悪者にしない」にも合う
    U("toi", "今週の予定、自分が出なくていい会議が1件ない?", cover=True, se="pop",
      speed=1.28, intonation=1.25, pad=0.06),
    U("gisshiri", "会議も予定もぎっしりで、時間が足りないよね。"),
    U("tarinai", "足りてないのは時間じゃなくて、予定のほうだよ。"),
    U("hantei", "予定に時間を渡してるのは、自分のほう。", **_S),
    U("watashi", "時間を取られてるんじゃない。自分から渡してる。", **_D),
    U("toi2", "その会議、自分がいないと本当に回らない?"),

    # ---- 幕2 誰が言った(11)。企画書の上限は4カットだったが、**この本が実在の役人に
    #      「その仕事は辞めろ」と宛てた手紙**だという事実を足した。これが無いと
    #      締めの動作(今週1件消す)がずんだもんの思いつきに見える(批評パネル high)
    U("dashita", "会議に出るな、って手紙に書いた人がいるの。"),
    U("seneca", "手紙を書いたのはセネカ。古代ローマの政治家ね。"),
    # 執筆年の通説の根拠は、コルシカからの召還(西暦49年)。plan §10 の前提表と対応
    U("korushika", "セネカが島流し先のコルシカから戻ったのが、西暦49年ごろ。"),
    U("nazedasu", "コルシカから戻して、何をさせたと思う?", **_S),
    U("riyuu", "答えは、皇帝の家の家庭教師。", **_S),
    U("nero", "その息子が、のちの皇帝ネロになる。", **_S),
    U("migiude", "ネロが即位したあとは、セネカが皇帝の右腕。"),
    U("isogashii", "皇帝のとなりだよ。あなたより忙しいと思わない?"),
    U("yakunin", "その忙しい人が、役人あてに手紙を書いた。"),
    U("tegami", "手紙にあるのは、「仕事は辞めろ」の一言。", **_S),
    U("hon", "手紙は本になった。『人生の短さについて』。"),

    # ---- 幕3 引用(4)。1.3 の定訳は「浪費」(perdere = 自分で使いつぶす)。
    #      「失う/取られる」だと主張が逆を向く(日本語パネル high)
    U("hajimari", "人生の話じゃなく、時間の話から始まるの。あなたと同じ。"),
    U("quote1", "「時間が足りないんじゃない。多くを浪費してるんだ」。", **_D),
    U("dare", "浪費してるのは、ほかでもない自分の人生。"),
    U("quote1b", "「短い人生をもらったんじゃない。自分たちがそうした」。"),

    # ---- 幕4 なぜ残った(5)
    U("nokotta", "その人生の話、いまも読めるのはなんで?"),
    U("shahon", "だって、印刷が無い時代。手で書き写した写本しかない。"),
    U("tsugi", "写本を1000年ぶん、人の手で受け継いだの。"),
    U("ambro", "いちばん古い写本は、11世紀の1冊だけ。", **_S),
    U("hyakusatsu", "その1冊から広がって、いまは100冊以上。すごくない?"),

    # ---- 幕5 誰が評価した(4)。**予定を実際に消した実例**にした(批評パネル high)
    U("yonda", "100冊あったから、モンテーニュも読めたの。"),
    U("yameta", "モンテーニュは37歳で裁判所の仕事を手放した。できる?"),
    U("essai", "手放したあと塔にこもって、『エセー』を書いたの。"),
    U("tehon", "エセーが手本にしたのは、セネカの書き方。"),

    # ---- 幕6 もう一文 → 動作 → 締め(7)
    U("iu2", "あなたの財産の話も、セネカは書いてる。", **_S),
    U("quote2", "「財産なら、誰にも分け与えないだろう」。", **_S),
    U("waketa", "なのに財産じゃなく人生の時間なら、平気で分け与えるって。", **_D),
    U("kesu1", "あなたの今週も、分け与えた時間で埋まってない?"),
    U("kesu2", "出なくていい1件を選んで、今週のうちに消して。"),
    U("henshin", "今週のうちに消せない会議なら、「欠席」って返信して。"),
    U("owari", "返信は1件でいい。あなたの時間は、そこから戻る。"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z002.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
