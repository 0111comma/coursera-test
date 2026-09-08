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
BADGE = "※ 出典: セネカ『人生の短さについて』1.3・1.4・3.1"
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
                           disclaimer="※ 出典: セネカ『人生の短さについて』1.3・1.4・3.1"),
    "gisshiri": sz.calendar_pair("03_troubled", left=("月", "×"), right=("火", "×")),
    "tarinai": sz.thinking_loop("03_troubled"),
    "hantei": sz.calendar_one("02_point", "今週", "?", bubble="入れたの誰?"),
    "joushi": sz.boss_sheet("04_surprised", "上司のせい?"),
    "watashi": sz.bubble_locked("04_surprised", "自分で入れた"),
    "toi2": sz.calendar_one("03_troubled", "今週", "?", bubble="どれをやめる?"),

    # ---- 幕2 誰が言った(6)
    "dashita": sz.memo_tag("02_point", "手放せ、と"),
    "seneca": sz.ancient_person("04_surprised", "ストア派", "セネカ"),
    "paulinus": sz.boss_sheet("03_troubled", "食料の長官"),
    "kaite": sz.memo_tag("04_surprised", "手放せ、と"),
    "uekomi": sz.boss_sheet("04_surprised", "街が飢える"),
    "uekomi2": sz.thinking_loop("03_troubled"),
    "migiude": sz.emperor("04_surprised", "皇帝ネロ", bubble="先生だった人"),
    "migiude2": sz.boss_sheet("03_troubled", "皇帝の右腕"),
    "hon": sz.book_now("03_troubled", "『対話篇』の一篇", bubble="いまも読める"),

    # ---- 幕3 引用(5)
    "hajimari": sz.book_now("02_point", "本の出だし", bubble="人生は短い、と嘆く"),
    "kaesu": sz.ancient_person("02_point", "セネカが返す", "1.3"),
    "quote1": sz.quote_card("多くを浪費してる", "『人生の短さについて』1.3"),
    "dare": sz.bubble_locked("04_surprised", "浪費してるのは"),
    "occupati": sz.boss_sheet("03_troubled", "他人の用事"),
    "quote1b": sz.quote_card("自分たちで短くした", "『人生の短さについて』1.4"),

    # ---- 幕4 なぜ残った(4)。**how ではなく why** を言う(批評パネル high)
    "nokotta": sz.book_now("04_surprised", "いまも読める", bubble="なんで?"),
    "shahon": sz.copyists("01_base", years=""),
    "miuchi": sz.book_now("01_base", "異教徒なのに", bubble="修道院では身内"),
    "todoita": sz.book_now("02_point", "写し継がれた", bubble="あなたに届くまで"),

    # ---- 幕5 誰が評価した(3)。**予定を実際に消した実例**
    "yonda": sz.ancient_person("05_happy", "『エセー』", "モンテーニュ"),
    "yameta": sz.calendar_one("05_happy", "職", "×", bubble="37歳で手放した"),
    "chuui": sz.calendar_one("02_point", "今週", "×", bubble="あなたは1件"),

    # ---- 幕6 もう一文 → 動作 → 締め(8)
    "iu2": sz.ancient_person("02_point", "セネカ", "財産の話"),
    "zaisan": sz.boss_sheet("03_troubled", "分けられる?"),
    "quote2": sz.quote_card("誰にも分けない", "『人生の短さについて』3.1"),
    "waketa": sz.quote_card("時間なら分け与える", "『人生の短さについて』3.1"),
    "kesu1": sz.calendar_pair("03_troubled", left=("木", "×"), right=("金", "×")),
    "kesu2": sz.calendar_one("02_point", "今週", "×", bubble="1件だけ消す"),
    "henshin": sz.memo_tag("02_point", "「欠席します」"),
    "owari": sz.go_home("05_happy"),
}

# 速度・抑揚は Z001 と同じ帯。**1カット3.0秒以内**(check_tempo)。
# 尺の推定は Z001 の実測(972字 / 112.2秒 = 8.66字/秒)を使う
_F = dict(anim=1.7, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_S = dict(anim=1.5, speed=1.30, intonation=1.22, pad=0.05, chara="none")
_D = dict(anim=1.9, se="don", speed=1.28, intonation=1.28, pad=0.12, chara="none")


def U(scene, sub, **kw):
    d = dict(_F)
    d.update(kw)
    return Unit(scene, sub, **d)


# 2026-09-07 批評パネル(high 9件)で畳んだ版。いちばん重かったのは
# **学びの3幕が21カット(全体の53%)**で、企画書 §1.7 が自分で置いた12カットの上限を
# 破っていたこと。Z001 が学説史の年表になったのと同じ形。6/4/3 に畳んで、
# 落としたネタ(コルシカからの召還・11世紀の写本・100冊以上)は次の1本に回す。
#
# ほかに直した high:
#   - 原文に無い文言をカギカッコで「書いた」と断定していた(「辞めなよ」「その仕事は辞めろ」)
#   - 宛先が「ある役人」のままで、**「自分がいないと回らない」への答え**を捨てていた
#     (パウリヌスはローマ中の食料をあずかる長官。止まれば街が飢える)
#   - 「なんで残ったの?」に how しか答えていなかった(写本の経路)。why を言う
#   - 100冊の写本のおかげでモンテーニュが読めた、は時代が合わない(16世紀は活版)
#   - BADGE の「西暦49年ごろ」が執筆年の断定になっていた
#   - 締めの「時間が取り戻せる」は plan §11 で自分に禁じた効果の断定
UNITS = [
    # ---- 幕1 場面 → 判定(7)
    U("toi", "今週の予定、自分が出なくていい会議が1件ない?", cover=True, se="pop",
      speed=1.28, intonation=1.25, pad=0.06),
    U("gisshiri", "会議も打ち合わせもぎっしりで、時間が足りないよね。"),
    U("tarinai", "時間の問題じゃないの。予定が多すぎるんだよ。"),
    U("hantei", "予定を入れたの、自分だよね。", **_S),
    U("joushi", "その予定、上司が勝手に入れた? 自分でいいよって言ったよね。"),
    U("watashi", "入れたのも自分、受けたのも自分。上司は関係ないの。", **_D),
    U("toi2", "じゃあどれをやめる? 同じ悩みに答えた昔の本があるの。"),

    # ---- 幕2 誰が言った(8)。**宛先の職**が、視聴者の反論(自分がいないと回らない)への答え
    U("dashita", "その本、忙しすぎる役人に仕事は手放せって書いてあるの。"),
    U("seneca", "手放せって書いたのはセネカ。ローマの政治家で、ストア派の哲学者。"),
    U("paulinus", "パウリヌスって人に書いたの。ローマの食糧長官、食べ物の責任者ね。"),
    U("uekomi", "その食糧長官が止まったら、街が飢えるでしょ?"),
    U("uekomi2", "食糧長官って、自分がいないと本当に回らない仕事だよね。", **_S),
    U("kaite", "食糧長官にまで、セネカは手放せって書いたの。"),
    U("migiude", "手放せって言うセネカは暇な人? 逆で、あの暴君ネロの先生ね。", **_S),
    U("migiude2", "ネロが皇帝になってからは政治顧問。うちの上司より忙しい。"),
    U("hon", "そのセネカが書いた『人生の短さについて』。『対話篇』の一篇ね。"),

    # ---- 幕3 引用(6)。1.1 は「人生は短い」と嘆く側から始まり、1.3 でセネカが返す
    U("hajimari", "本の出だしは、人生は短いって嘆く人の話。あなたと同じ。"),
    U("kaesu", "嘆く人にセネカが、人生は短くないよって返すの。", **_S),
    U("quote1", "「人生が短いんじゃない。多くを浪費してるんだ」。"),
    U("dare", "浪費してるのは自分。使いつぶしてるのは、自分の人生。", **_D),
    U("occupati", "人生を他人の用事で埋めてる人を、セネカは多忙な人って呼ぶの。"),
    U("quote1b", "「短い人生をもらったんじゃない。自分たちで短くしたんだ」。"),

    # ---- 幕4 なぜ残った(4)。**how ではなく why**(修道院が写す本に選び続けた理由)
    U("nokotta", "てか、セネカの一言がなんであなたに届いてるの?"),
    U("shahon", "だって昔は印刷が無いから、修道院で手で写した本だけ残るの。"),
    U("miuchi", "キリスト教じゃないのに、修道院では身内あつかいだったの。"),
    U("todoita", "だからセネカの写本だけは作られ続けて、あなたにも届いたの。"),

    # ---- 幕5 誰が評価した(3)。**予定を実際に消した実例**
    U("yonda", "セネカを読んだのがモンテーニュ。随筆『エセー』を書いた人ね。"),
    U("yameta", "で、37歳でボルドー高等法院、つまり裁判所の仕事を辞めた。"),
    U("chuui", "そこまでしろとは言わないの。あなたは1件でいい。", **_S),

    # ---- 幕6 もう一文 → 動作 → 締め(8)。**山は動作のカットに置く**
    U("iu2", "で、やめる1件の選び方。セネカの財産の話がヒントなの。", **_S),
    U("zaisan", "財産なら、誰かにぽんと分け与えられる? 無理だよね。"),
    U("quote2", "「財産なら、誰にも分け与えないだろう」。", **_S),
    U("waketa", "なのに時間だと、平気で人に分け与えちゃうよね、って。", **_S),
    U("kesu1", "あなたの今週も、人に分け与えた時間で埋まってない?"),
    U("kesu2", "出なくていい1件を選んで、今週のうちに消す。", **_D),
    U("henshin", "自分で消せない会議なら、「欠席します」って返事して。"),
    U("owari", "返事は一言でいい。1件ぶんの時間が、自分に戻ってくる。"),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "Z002.mp4", speaker=3, chara=False)
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
