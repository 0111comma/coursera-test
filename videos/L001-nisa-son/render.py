#!/usr/bin/env python3
"""L001(長尺・横型): NISAで損したらどうなるのか。

企画書は plan.md、数値は verify.py。

**この台本はループ71のフェーズ12で作り直したもの。**
初版は155ユニット・6章で、ユーザー判定は「ゴミ」だった。
`production/check_long.py` で26件の不合格が出たので、その全部を直してある。
根拠は docs/research/longform-loop-2026-08/ の 01〜11。要点だけ書くと:

  冒頭  答えの金額を15秒以内、図を20秒以内に出す。定義は冒頭に置かない(02)
        章の切れ目を45〜75秒に置かない(01/02)
  構成  章は4つ。1章100〜130秒。章札は前章の問いを繰り返さず**答えの側**を予告する(03)
  中身  各章の出口に**損得の判定**を置く。問いは判定ではない(07)
        判定の直前に pad 0.6 の**止め**を置く。BGMもそこで切れる(04/08)
  画面  数字は**図の上で言う**。図の無い時間を25秒以上続けない(06)
        図が主役の回は**立ち絵を消す**(09)
  締め  免責を終了画面の枠(最後の20秒)に置かない。次に見るものを名指しする(10)

この動画が答える問い(1つだけ):
  NISAで損したとき、課税口座で損したときより不利になるのか。いくら不利なのか。
答え:
  不利になる額 = min(NISAの損, 課税口座の利益) × 20.315%
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402

S.use_landscape()      # ← new_canvas より前に1回だけ。話速も 1.15 に下がる(05)

from shortlib import Unit, render_video, require_voicevox, MUTED_BAR, GOLD  # noqa: E402
import scenes_long as sl  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年8月時点・仮定の金額での計算"

# verify.py と同じ計算をここでも回して、画面の数字とずれていないことを確かめる
ZEI = 0.15 + 0.15 * 0.021 + 0.05


def zei(gain):
    return int(gain * ZEI)


assert abs(ZEI - 0.20315) < 1e-9
assert zei(200_000) == 40_630
assert zei(400_000) == 81_260
assert zei(100_000) == 20_315
assert zei(40_000) == 8_126

# ---------------------------------------------------------------- シーン

_L20 = [("損20万", 20, MUTED_BAR), ("益20万", 20, GOLD)]
_L30 = [("損30万", 30, MUTED_BAR), ("益10万", 10, GOLD)]
_L10 = [("損10万", 10, MUTED_BAR), ("益30万", 30, GOLD)]

_TE = ["損益通算は1年", "確定申告が要る", "売却は税に無関係", "投資枠は翌年・簿価"]

_TABLE_ROWS = [("損だけの年", "0円", "0円", "0円"),
               ("利益だけの年", "40,630円", "0円", "得 40,630円"),
               ("損と利益がある年", "0円", "40,630円", "損 40,630円")]
_TABLE_HEAD = ["どんな年か", "課税口座だけ", "NISAを使うと", "差"]

SCENES = {
    # ---- 冒頭(0〜45秒。「損は税金を消せる」を先に渡してから、NISAの例外に落とす)
    "son": sl.hero("株で20万円の損", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, size=120, sub_fs=32),
    "son__cover": sl.cover("株で損したら、税金はどうなるのか?", "40,630円",
                           "もうけた株の税金が消える。ただしNISAは別",
                           "2026年8月時点の制度", BRAND),
    "sousai0": sl.compare2("その年に売った2本",
                           ("もうけた株", [("益20万", 20, GOLD)], ""),
                           ("損した株", [("損20万", 20, MUTED_BAR)], ""), BADGE, BRAND),
    "sousai1": sl.compare2("その年に売った2本",
                           ("もうけた株", [("益20万", 20, GOLD)], "税 40,630円"),
                           ("損した株", [("損20万", 20, MUTED_BAR)], ""), BADGE, BRAND,
                           note_l="※ 売った年にかかる"),
    "sousai2": sl.compare2("2本を合わせた後",
                           ("差し引いた後", [("残り 0円", 0.4, MUTED_BAR)], "税 0円"),
                           ("消えた税", [("40,630円", 20, GOLD)], ""), BADGE, BRAND,
                           note_l="※ 同じ年どうしに限る", note_r="※ 確定申告が要る場合あり"),
    "rei0": sl.compare2("ある1年を切り出すと",
                        ("すべて課税口座", _L20, ""),
                        ("NISAで損", _L20, ""), BADGE, BRAND),
    "rei1": sl.compare2("ある1年を切り出すと",
                        ("すべて課税口座", _L20, "税 0円"),
                        ("NISAで損", _L20, ""), BADGE, BRAND,
                        note_l="※ 相殺できる"),
    "rei2": sl.compare2("ある1年を切り出すと",
                        ("すべて課税口座", _L20, "税 0円"),
                        ("NISAで損", _L20, "税 40,630円"), BADGE, BRAND,
                        note_l="※ 相殺できる", note_r="※ 相殺できない"),
    "reigai": sl.card("この差し引きが", "使えない口座", "※ 損が無かったことになる",
                      BADGE, BRAND, main_size=88, head_fs=32),
    "sorenisa": sl.card("その口座の名前", "NISA", "※ 利益が非課税になる、あの口座",
                        BADGE, BRAND, main_size=150, head_fs=32),
    "jouken": sl.card("適用範囲", "限定的", "※ 毎年起きるわけではない",
                      BADGE, BRAND, main_size=140, head_fs=32),
    "yotei": sl.card("この動画の道すじ", "4つの章", "(所要 約9分)",
                     BADGE, BRAND, main_size=82, head_fs=32),

    # ---- 第1章 引けない損(旧2章の税率 + 旧3章)
    "ch1": sl.chapter(1, "引けない損", "NISAの損は、利益から引けるのか?",
                      BADGE, BRAND, total=4),
    "zeiritsu": sl.card("利益にかかる税率", "20.315%",
                        "(2026年8月時点・申告分離課税)",
                        BADGE, BRAND, main_size=110, head_fs=32),
    "uchiwake": sl.barsN("3つを足すと20.315%",
                         [("所得税", 15, "15%"), ("住民税", 5, "5%"),
                          ("復興特別所得税", 0.315, "0.315%")],
                         BADGE, BRAND, ymax=17),
    "keisan1": sl.band("利益と、そこから引かれる税", "利益 20万円", 0.79685,
                       "手元 15万9370円", "税 40,630円", BADGE, BRAND, show_rest=True),
    "tsuusan": sl.card("この仕組みの名前", "損益通算", "(そんえきつうさん)",
                       BADGE, BRAND, main_size=104, head_fs=32),
    "tsuusan2": sl.card("使える範囲", "1年ごと", "※ またぐには別の仕組み",
                        BADGE, BRAND, main_size=130, head_fs=32),
    "sashihiki": sl.compare2("差し引きの前と、後",
                             ("差し引く前", _L20, ""),
                             ("差し引いた後", [("残り 0円", 0.4, MUTED_BAR)], "税 0円"),
                             BADGE, BRAND, note_r="※ 課税対象が消える"),
    "hikenai": sl.card("答え", "引けない", "(税金の計算に、入れてもらえない)",
                       BADGE, BRAND, main_size=118, head_fs=32),
    "riyuu2": sl.card("NISAの損の扱い", "無いものとされる", "※ 課税口座の損とはここが違う",
                      BADGE, BRAND, main_size=76, head_fs=32),
    "keisan2": sl.band("引く相手がいないと、こうなる", "相殺なしの課税対象", 0.79685,
                       "手元 15万9370円", "税 40,630円", BADGE, BRAND, show_rest=True),
    "kouza": sl.card("課税口座の種類", "特定口座と一般口座", "※ NISA口座はこれとは別の口座",
                     BADGE, BRAND, main_size=62, head_fs=32),
    "gensen": sl.card("源泉徴収あり", "証券会社が納める", "※ 選ぶのは口座を開くとき",
                      BADGE, BRAND, main_size=72, head_fs=32),

    # ---- 第2章 来年の利益
    "ch2": sl.chapter(2, "来年の利益", "来年の利益からは、引けるのか?",
                      BADGE, BRAND, total=4),
    "kurikoshi": sl.card("もうひとつの仕組み", "繰越控除", "※ くりこしこうじょ",
                         BADGE, BRAND, main_size=104, head_fs=32),
    "kurikoshi2": sl.card("繰越控除とは", "損の持ち越し", "※ 上限は3年ぶん",
                          BADGE, BRAND, main_size=100, head_fs=32),
    "nen1": sl.timeline("2年で見ると",
                        [("1年目", "損 40万円", "税 0円", False),
                         ("2年目", "利益 40万円", "", False)], BADGE, BRAND),
    "nen2": sl.timeline("2年で見ると",
                        [("1年目", "損 40万円", "税 0円", False),
                         ("2年目", "利益 40万円", "税 0円", False)], BADGE, BRAND,
                        arrow=(0, 1), note="※ 矢印を使うには確定申告が要る"),
    "nen3": sl.timeline("2年で見ると",
                        [("1年目", "損 40万円", "税 0円", False),
                         ("2年目", "利益 40万円", "税 81,260円", True)], BADGE, BRAND,
                        note="※ 矢印が無い = 繰り越せない"),
    "san2": sl.timeline("繰り越せる範囲",
                        [("1年目", "損 40万円", "繰り越す", False),
                         ("2年目", "利益 10万円", "引ける", False),
                         ("3年目", "利益 10万円", "引ける", False),
                         ("4年目", "利益 10万円", "引ける", False),
                         ("5年目", "利益 10万円", "引けない", True)], BADGE, BRAND,
                        note="繰り越せるのは、損が出た年の翌年から3年"),
    "shinkoku": sl.card("使うための条件", "確定申告", "※ 期限後の申告では使えない",
                        BADGE, BRAND, main_size=130, head_fs=32),
    "san1": sl.timeline("繰り越せる範囲",
                        [("1年目", "損 40万円", "繰り越す", True),
                         ("2年目", "利益 10万円", "引ける", False),
                         ("3年目", "利益 10万円", "引ける", False),
                         ("4年目", "利益 10万円", "引ける", False)], BADGE, BRAND),
    "nikai": sl.barsN("2年つづいた場合",
                      [("1年目の差", 40630, "40,630円"), ("2年目の差", 40630, "40,630円"),
                       ("2年の合計", 81260, "81,260円")],
                      BADGE, BRAND, ymax=95000, highlight=2),

    # ---- 第3章 効く範囲
    "ch3": sl.chapter(3, "効く範囲", "この不利は、いくらまで効くのか?",
                      BADGE, BRAND, total=4),
    "onaji": sl.card("ここまでの前提", "損も利益も20万円", "※ 実際は額がそろわない",
                     BADGE, BRAND, main_size=72, head_fs=32),
    "pat1": sl.compare2("損のほうが大きい年",
                        ("その年の中身", _L30, ""),
                        ("相殺できた分", [("10万円まで", 10, GOLD)], "差 20,315円"),
                        BADGE, BRAND, note_r="※ 余りは翌年に持ち越せない"),
    "pat2": sl.compare2("大小を入れ替えた年",
                        ("その年の中身", _L10, ""),
                        ("相殺できた分", [("10万円まで", 10, GOLD)], "差 20,315円"),
                        BADGE, BRAND, note_r="※ 残る利益20万円には課税"),
    "nashi": sl.compare2("片側しか無い年",
                         ("NISAの損", [("損100万", 100, MUTED_BAR)], ""),
                         ("課税口座の利益", [("0円", 0.5, GOLD)], "差 0円"),
                         BADGE, BRAND, note_r="※ もともと払う税が無い"),
    "kousiki": sl.hero("上限は小さいほう", "※ 差はその20.315%",
                       BADGE, BRAND, size=110, sub_fs=32),
    "sorotta": sl.card("効く条件", "2つがそろった年", "※ 片方だけなら差は0円",
                       BADGE, BRAND, main_size=76, head_fs=32,
                       ask="あなたは、口座を2つ使っていますか?"),

    # ---- 第4章 自分の場合 + 締め
    "ch4": sl.chapter(4, "自分の場合", "自分の場合は、どう出すのか?",
                      BADGE, BRAND, total=4),
    "jibun": sl.card("自分の場合", "小さいほう × 0.20315", "※ 同じ年の中で見ること",
                     BADGE, BRAND, main_size=56, head_fs=32),
    "jibun2": sl.barsN("ならべて、小さいほうを取る",
                       [("NISAの損", 4, "4万円"), ("課税口座の利益", 12, "12万円")],
                       BADGE, BRAND, ymax=14, highlight=0),
    "kawaru": sl.card("この動画の時点", "2026年8月", "※ 税制改正で変わります",
                      BADGE, BRAND, main_size=104, head_fs=32),
    "te1": sl.checklist("使うときの手順", _TE, BADGE, BRAND, lit=1),
    "te2": sl.checklist("使うときの手順", _TE, BADGE, BRAND, lit=2),
    "te3": sl.checklist("使うときの手順", _TE, BADGE, BRAND, lit=3),
    "te4": sl.checklist("使うときの手順", _TE, BADGE, BRAND, lit=4),
    "waku2": sl.timeline("投資枠が戻る時期",
                         [("売った年", "戻る投資枠", "0円", False),
                          ("翌年", "戻る投資枠", "100万円", True)], BADGE, BRAND,
                         note="※ 簿価(取得価額)ベース。売却額ではない"),
    "matome": sl.table("3つの場合", _TABLE_HEAD, _TABLE_ROWS, BADGE, BRAND),
    "matome2": sl.table("3つの場合", _TABLE_HEAD, _TABLE_ROWS, BADGE, BRAND,
                        highlight=1, reveal_rows=False),
    "matome3": sl.table("3つの場合", _TABLE_HEAD, _TABLE_ROWS, BADGE, BRAND,
                        highlight=2, reveal_rows=False),
    "tsugi": sl.card("1分で見たいとき", "税金の20.315%", "※ 概要欄のショートで図だけを出しています",
                     BADGE, BRAND, main_size=88, head_fs=32),
    "shime": sl.hero("税は理由にならない", "※ 課税口座では逆に効く",
                     BADGE, BRAND, size=76, sub_fs=32),
}

# ---------------------------------------------------------------- 台本
#
# 表記の決めごと:
#   - 図が主役のユニットは chara="none"(09)。文字カードでは立ち絵を出す
#   - 章の出口の判定の直前に pad=0.6(04)。BGMもそこで切れる(08)
#   - 接続語のあとに読点を打たない(04b。本多勝一の読点2原則に当たらないため)

UNITS = [
    # ===== 冒頭(0〜約45秒)
    #
    # **順序がいちばん大事なところ。** ユーザー指摘(ループ71):
    #   「15秒で見たくなくなる。他の株で損したら儲かった株の税金を払わなくていいことを
    #     基本的に人は知らない。これは初心者向けの動画なんだから」
    #
    # 前の版は「NISA口座がマイナス」で始めて5.8秒で40630円を出した。
    # だが**損が利益と相殺できることを知らない人**には、その金額の意味が無い。
    # 「引けない」と言われても、引けるのが普通だと知らなければ何も起きない。
    # だから **得の話(損は税金を消せる)を先に渡してから、NISAの例外に落とす。**
    Unit("son", "株を売って、20万円の損が出たとする。", anim=1.4, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("son", "その損は、ただ消えるだけだと思っていないか。", anim=0.0,
         face="troubled", speed=1.1, intonation=1.2),
    Unit("sousai0", "でも同じ年に、別の株で20万円もうけていたとする。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("sousai1", "そのもうけには、ふつう40630円の税金がかかるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("sousai2", "ところが損と差し引くと、その40630円が消えるのだ。", anim=1.6,
         se="impact", se_at=0.32, speed=1.0, intonation=1.3, chara="none"),
    Unit("sousai2", "つまり損した株が、税金を減らしてくれるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("reigai", "ただしこの差し引きが、使えない口座があるのだ。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("sorenisa", "その口座の名前が、NISAなのだ。", anim=1.4,
         se="don", speed=1.0, intonation=1.25),
    Unit("rei2", "だからNISAで損した年は、40630円を払うのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("yotei", "だから4つの章で、その条件を確かめていくのだ。", anim=1.4,
         face="happy", speed=1.15, pad=0.6),
    Unit("rei2", "まず消せたはずの40630円を、覚えておくのだ。",
         anim=0.0, speed=1.05, intonation=1.2, chara="none"),

    # ===== 第1章 引けない損(約100〜125秒)
    Unit("ch1", "では第1章。その値段の出どころを、確かめていくのだ。", anim=1.4,
         se="pop", speed=1.1),
    Unit("zeiritsu", "まず株や投資信託の利益には、20.315%かかるのだ。", anim=1.4,
         speed=1.1),
    Unit("zeiritsu", "その投資信託とは、たくさんの銘柄をまとめた商品のこと。", anim=0.0,
         speed=1.05),
    Unit("uchiwake", "そしてこれを分けると、所得税と住民税と復興特別所得税になるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("uchiwake", "そのうち所得税と住民税で、20%を占めるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("uchiwake", "まず所得税が、15%。", anim=0.0, speed=1.1, chara="none"),
    Unit("uchiwake", "そして住民税が、5%。", anim=0.0, speed=1.1, chara="none"),
    Unit("uchiwake", "さらに復興特別所得税が、0.315%。", anim=0.0,
         speed=1.1, chara="none"),
    Unit("keisan1", "だから20万円の利益なら、税金は40630円になるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("keisan1", "そして手元に残るのが、15万9370円のほうなのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("kouza", "ちなみに課税口座には、特定口座と一般口座があるのだ。", anim=1.4,
         speed=1.05),
    Unit("gensen", "そしてその特定口座には、源泉徴収ありという選び方があるのだ。", anim=1.4,
         speed=1.05),
    Unit("gensen", "その源泉徴収ありとは、証券会社が代わりに納めてくれること。", anim=0.0,
         speed=1.1),
    Unit("tsuusan", "ではもし、同じ年に損も出ていたらどうなるのか。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("tsuusan", "その損は、利益から引けるのだ。", anim=0.0, speed=1.1),
    Unit("sashihiki", "そして引くことを、損益通算と呼ぶのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("sashihiki", "たとえば利益20万円と損20万円が、同じ年にあるとする。",
         anim=0.0, speed=1.05, chara="none"),
    Unit("tsuusan2", "ただし引けるのは、同じ年の中だけなのだ。", anim=1.4,
         face="smug", speed=1.1),
    Unit("sashihiki", "その差し引きの後に残るのは、0円なのだ。", anim=0.0,
         speed=1.1, chara="none"),
    Unit("sashihiki", "だから税金も、0円になるのだ。", anim=0.0,
         se="pop", speed=1.1, chara="none"),
    Unit("sashihiki", "つまり課税口座では、損が節税の材料になるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("hikenai", "ではNISAの損は、どう扱われるのだろうか。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("hikenai", "答えは、引けない。", anim=0.0,
         se="impact", se_at=0.20, speed=1.0, intonation=1.3),
    Unit("riyuu2", "その損は、無いものとされるのだ。", anim=1.4, speed=1.05),
    Unit("riyuu2", "そしてその損を引けないのは、利益に税金をかけないからなのだ。", anim=0.0,
         speed=1.05),
    Unit("riyuu2", "だから引く相手も、そこにはいないのだ。", anim=0.0, speed=1.1),
    Unit("keisan2", "そして課税口座の利益20万円だけが、まるごと残るのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("keisan2", "その利益にかかる税金が、40630円なのだ。", anim=0.0,
         speed=1.05, chara="none", pad=0.6),
    Unit("rei2", "つまり引けなかった損の値段が、40630円になるのだ。", anim=1.4,
         se="don", speed=1.0, intonation=1.25, chara="none"),

    # ===== 第2章 来年の利益(約100〜125秒)
    Unit("ch2", "では第2章。同じ額を、翌年もう一度払う話をするのだ。", anim=1.4,
         se="pop", speed=1.1),
    Unit("kurikoshi", "まず課税口座には、繰越控除という仕組みもあるのだ。", anim=1.4,
         speed=1.05),
    Unit("kurikoshi2", "その繰越控除とは、損を来年に持ち越すことなのだ。", anim=1.4,
         face="happy", speed=1.05),
    Unit("nen1", "たとえば1年目に、40万円の損が出たとする。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("nen1", "そして2年目には、40万円の利益を出したとする。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("nen2", "その課税口座なら、1年目の損を2年目から引けるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("nen2", "だから2年目の税金も、0円になるのだ。", anim=0.0,
         se="pop", speed=1.1, chara="none"),
    Unit("san1", "そして持ち越せるのは、3年ぶんまでなのだ。", anim=1.4,
         speed=1.1, chara="none"),
    Unit("san1", "たとえば毎年10万円の利益なら、3年かけて引いていくのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("san2", "でも4年目を過ぎると、余った損は消えるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("san2", "だから引き切れるかどうかは、その後の利益で決まるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("shinkoku", "ただし繰越控除には、確定申告が要るのだ。", anim=1.4,
         speed=1.1),
    Unit("shinkoku", "その申告は、損が出た年から毎年出し続けるのだ。", anim=0.0,
         speed=1.05),
    Unit("shinkoku", "だから1年出し忘れると、その権利を失うのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("nen3", "ではNISAの損は、来年に持ち越せるのだろうか。", anim=1.4,
         face="troubled", speed=1.1, chara="none"),
    Unit("nen3", "その答えも、持ち越せないのだ。", anim=0.0,
         se="impact", se_at=0.20, speed=1.0, intonation=1.3, chara="none"),
    Unit("nen3", "だから2年目の利益40万円に、81260円かかるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("nikai", "では毎年おなじことが起きると、どうなるのか。", anim=1.4,
         speed=1.1, chara="none"),
    Unit("nikai", "まず1年目の差が、40630円。", anim=0.0, speed=1.1, chara="none"),
    Unit("nikai", "そして2年目の差も、40630円。", anim=0.0, speed=1.1, chara="none"),
    Unit("nikai", "だから合わせると、81260円になるのだ。", anim=0.0,
         speed=1.05, chara="none", pad=0.6),
    Unit("nikai", "つまり2年つづくと、差は2倍になるのだ。", anim=0.0,
         se="don", speed=1.0, intonation=1.25, chara="none"),

    # ===== 第3章 効く範囲(約100〜125秒)
    Unit("ch3", "では第3章。その差の上限を、額を動かして見るのだ。", anim=1.4,
         se="pop", speed=1.1),
    Unit("onaji", "まずここまでの例は、損も利益も同じ額だったのだ。", anim=1.4,
         speed=1.05),
    Unit("onaji", "そこでその額を、動かしてみるのだ。", anim=0.0,
         face="smug", speed=1.1),
    Unit("pat1", "たとえば損が30万円で、利益が10万円の年を考えるのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("pat1", "その相殺に使えるのは、小さいほうの10万円まで。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("pat1", "だから差は、20315円になるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("pat1", "そして余った損の20万円は、そのまま消えるのだ。", anim=0.0,
         face="troubled", speed=1.05, chara="none"),
    Unit("pat2", "では逆に、損が10万円で利益が30万円の年はどうか。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("pat2", "その相殺に使えるのも、小さいほうの10万円まで。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("pat2", "だから差はやはり、20315円なのだ。", anim=0.0,
         se="pop", speed=1.05, chara="none"),
    Unit("kousiki", "つまり差の上限を決めるのは、小さいほうなのだ。", anim=1.4,
         speed=1.05),
    Unit("nashi", "では課税口座に利益が無い年は、どうなるのか。", anim=1.4,
         speed=1.1, chara="none"),
    Unit("nashi", "その年は、引く相手がそもそもいないのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("nashi", "だから課税口座でも、税金は0円なのだ。", anim=0.0,
         speed=1.1, chara="none"),
    Unit("nashi", "つまりその年の差は、0円になるのだ。", anim=0.0,
         se="pop", speed=1.05, chara="none"),
    Unit("sorotta", "だからこの不利が効くのは、2つがそろった年だけなのだ。",
         anim=1.4, face="smug", speed=1.05, pad=0.6),
    Unit("pat1", "つまり余分に払うのは、小さいほうの2割ほどなのだ。", anim=0.0,
         se="don", speed=1.0, intonation=1.25, chara="none"),

    # ===== 第4章 自分の場合 + 締め(約100〜125秒)
    Unit("ch4", "では第4章。自分の年の明細から、その額を拾いにいくのだ。", anim=1.4,
         se="pop", face="happy", speed=1.1),
    Unit("jibun", "まずNISAの損と、課税口座の利益をならべるのだ。", anim=1.4,
         speed=1.05),
    Unit("jibun", "そして小さいほうに、0.20315をかけるのだ。", anim=0.0,
         face="smug", speed=1.05),
    Unit("jibun2", "たとえばNISAの損が、4万円だとする。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("jibun2", "そして同じ年の課税口座の利益が、12万円だとする。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("jibun2", "その小さいほうは、損の4万円のほうなのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("jibun2", "だから余分に払うのは、8126円になるのだ。", anim=0.0,
         se="impact", se_at=0.28, speed=1.05, chara="none"),
    Unit("jibun2", "そして使うのは、かけ算だけなのだ。", anim=0.0,
         speed=1.1, chara="none"),
    Unit("te1", "そして使うときの手順も、4つだけ押さえておくのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("te1", "まず1つめ。損益通算を使えるのは、同じ年の中だけ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("te2", "そして2つめ。繰越控除には、確定申告が要るのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("te2", "その源泉徴収ありの口座でも、申告は要るのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("te3", "そして3つめ。NISAで売っても、税の計算は動かない。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("te3", "だから売る時期を、税金で決めなくていいのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("te4", "そして4つめ。売っても投資枠が戻るのは、翌年なのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("te4", "その投資枠とは、NISAで買える金額の上限のこと。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("waku2", "たとえば100万円で買ったものが、値下がりしたとする。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("waku2", "そして80万円で売っても、翌年に戻る投資枠は100万円ぶん。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("kawaru", "ちなみにこの制度は、2026年8月時点の内容なのだ。", anim=1.4,
         speed=1.05),
    Unit("kawaru", "そしてその制度は毎年変わるので、そのときに確かめてほしいのだ。",
         anim=0.0, face="troubled", speed=1.05),
    Unit("matome", "では3つの場合を、表にまとめるのだ。", anim=1.4,
         speed=1.1, chara="none"),
    Unit("matome", "まず損だけの年は、どちらも0円で同じ。", anim=0.0,
         speed=1.1, chara="none"),
    Unit("matome2", "そして利益だけの年は、40630円の得になる。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("matome3", "でも損と利益がある年は、40630円の損になる。", anim=1.4,
         speed=1.05, chara="none", pad=0.6),
    Unit("matome3", "つまり得も損も、同じ40630円なのだ。", anim=0.0,
         se="don", speed=1.0, intonation=1.25, chara="none"),
    Unit("matome3", "その向きがちがうだけで、額は同じなのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("shime", "だからNISAで売っても、税金の話は動かないのだ。", anim=1.4,
         face="smug", speed=1.05),
    Unit("tsugi", "そしてこの税金の20.315%は、概要欄のショートでも見られるのだ。", anim=1.4,
         face="happy", speed=1.1),
    Unit("tsugi", "そのショートなら、利益と手取りの図だけを1分で見られるのだ。", anim=0.0,
         speed=1.1),
    Unit("shime", "だから売る損得の判断に、税金は持ちこまなくていいのだ。", anim=1.4,
         face="happy", puchun=True, speed=1.05, intonation=1.2),
]

# ---------------------------------------------------------------- チャプター

CHAPTER_MARKS_TITLES = [
    "NISAで損したら、いくら損するのか",
    "第1章 NISAの損は、利益から引けるのか",
    "第2章 来年の利益からは、引けるのか",
    "第3章 この不利は、いくらまで効くのか",
    "第4章 自分の場合は、どう出すのか",
]
# 章の先頭ユニットは台本から拾う。手で添字を書くと、台本を直したとき必ずずれる
_first = {}
for _i, _u in enumerate(UNITS):
    _first.setdefault(_u.scene, _i)
CHAPTER_MARKS = list(zip(
    [0] + [_first[f"ch{k}"] for k in range(1, 5)], CHAPTER_MARKS_TITLES))
assert [i for i, _ in CHAPTER_MARKS] == sorted(i for i, _ in CHAPTER_MARKS)

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "L001.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    lines = sl.chapter_lines(result["unit_secs"], CHAPTER_MARKS)
    (OUTDIR / "chapters.txt").write_text("\n".join(lines) + "\n")
    print("chapters:")
    for ln in lines:
        print("  " + ln)
    print(f"mp4: {result['mp4']}")
