#!/usr/bin/env python3
"""L002(長尺・横型): 変動金利は、いつ・何%まで上がったら固定金利に負けるのか。

企画書は plan.md、数値は verify.py。設計の型は docs/research/longform-design.md。

この人の欲求(ループ67・ユーザー指摘そのもの):
  **家を買いたい。でも、金利で損はしたくない。**
  だからこれは「金利の解説」ではなく、**借りる前の人が選べるようになる**ための動画。
  分かれ目の数字を出すこと自体は目的ではない。**自分の場合を判定できること**が目的。

視聴後に決められること:
  変動金利で借りるか、固定金利で借りるかを選べる。
  自分が何年で返し終える見込みかを表に当てて、その年数なら何%まで耐えられるかを読み取れる。

答え(自前計算):
  借りた直後 3.14% / 5年後 3.83% / 10年後 4.96% /
  15年後 6.94% / 20年後 11.04% / 25年後 21.90%
  → **変動金利が負けるには、早く上がる必要がある。**
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402

S.use_landscape()      # ← new_canvas より前に1回だけ
S.use_duo()            # ← 二人会話(duo-skit-2026-08.md)

from shortlib import Unit, render_video, require_voicevox, MUTED_BAR, GOLD, EMPH  # noqa: E402
import scenes_long as sl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "3000万円・35年・2026年8月の金利での概算"

# verify.py の計算をそのまま使う(画面の数字とずれないように)
N = V.YEARS * 12
M_VAR = V.monthly(V.PRINCIPAL, V.RATE_VAR, N)
M_FIX = V.monthly(V.PRINCIPAL, V.RATE_FIX, N)
TOTAL_VAR, TOTAL_FIX = M_VAR * N, V.total_fixed()
BE = {y: V.solve_break_even(y) for y in (0, 5, 10, 15, 20, 25)}
BE_PREPAY = V.solve_break_even(5, prepay=3_000_000, prepay_at_years=5)
assert round(M_VAR) == 85_036 and round(M_FIX) == 117_812
assert BE[5] == 3.83 and BE[10] == 4.96 and BE[15] == 6.94
assert BE[20] == 11.04 and BE[25] == 21.90 and BE_PREPAY == 4.26

_YEARS = [0, 5, 10, 15, 20, 25]
_LABEL = {0: "直後", 5: "5年後", 10: "10年後", 15: "15年後", 20: "20年後", 25: "25年後"}


SCENES = {
    # ---- 冒頭(0〜40秒)
    "ie": sl.hero("3000万円を借りる", "※ 35年・2026年8月の金利での概算",
                  BADGE, BRAND, size=96, sub_fs=32),
    "ie__cover": sl.cover("変動金利は、何%まで上がったら固定金利に負けるのか?",
                          "3.83%", "5年後に上がる場合", "2026年8月の金利で計算", BRAND,
                          main_size=200),
    "kinri": sl.barsN("いまの金利",
                      [("変動金利", 1.025, "1.025%"), ("固定金利", 3.140, "3.14%")],
                      BADGE, BRAND, ymax=3.8, highlight=1),
    "maitsuki": sl.barsN("毎月の返済額",
                         [("変動金利", 85036, "8万5036円"),
                          ("固定金利", 117812, "11万7812円")],
                         BADGE, BRAND, ymax=140000, highlight=1),
    "sougaku": sl.compare2("総返済額",
                           ("変動金利", [("元金3000万", 3000, MUTED_BAR),
                                     ("利息571万", 571, GOLD)], "3571万円"),
                           ("固定金利", [("元金3000万", 3000, MUTED_BAR),
                                     ("利息1948万", 1948, GOLD)], "4948万円"),
                           BADGE, BRAND, note_l="※ 上がらなかった場合", note_r="※ 最後まで同じ"),
    "kowai": sl.card("よくある結び", "「上がったら怖い」", "※ 怖さは金額にならない",
                     BADGE, BRAND, main_size=76, head_fs=32),
    "kariru": sl.barsN("この動画で使う数字",
                       [("借りる元金", 3000, "3000万円")], BADGE, BRAND, ymax=5400),
    "sog2": sl.barsN("最後まで払い切ったときの合計",
                     [("変動金利", 3571, "3571万円")], BADGE, BRAND, ymax=5400),
    "sog3": sl.barsN("最後まで払い切ったときの合計",
                     [("変動金利", 3571, "3571万円"), ("固定金利", 4948, "4948万円")],
                     BADGE, BRAND, ymax=5400, highlight=1),
    "be1": sl.barsN("上がる時期でどこまで動くか",
                    [("直後", BE[0], f"{BE[0]:.2f}%")], BADGE, BRAND, ymax=24),
    "be2": sl.barsN("上がる時期でどこまで動くか",
                    [("直後", BE[0], f"{BE[0]:.2f}%"), ("5年後", BE[5], f"{BE[5]:.2f}%")],
                    BADGE, BRAND, ymax=24, highlight=1),
    "be3": sl.barsN("上がる時期でどこまで動くか",
                    [("直後", BE[0], f"{BE[0]:.2f}%"), ("5年後", BE[5], f"{BE[5]:.2f}%"),
                     ("10年後", BE[10], f"{BE[10]:.2f}%")],
                    BADGE, BRAND, ymax=24, highlight=2),
    "yotei": sl.card("進め方", "4つの章", "(所要 約6分)",
                     BADGE, BRAND, main_size=110, head_fs=32),

    # ---- 第1章 上がらない前提
    "ch1": sl.chapter(1, "上がらない前提", "そもそも今の金利で、いくら違うのか?",
                      BADGE, BRAND),
    "genri": sl.card("返し方の名前", "元利均等返済", "※ もう1つ元金均等という方式もある",
                     BADGE, BRAND, main_size=96, head_fs=32),
    "uchi1": sl.barsN("1回目の8万5036円の中身",
                      [("利息", 25625, "2万5625円"), ("元金", 59411, "5万9411円")],
                      BADGE, BRAND, ymax=72000, highlight=0),
    "uchi1b": sl.barsN("1回目の8万5036円の中身",
                       [("利息", 25625, "2万5625円"), ("元金", 59411, "5万9411円")],
                       BADGE, BRAND, ymax=72000, highlight=1),
    "uchi2": sl.barsN("最終回の8万5036円の中身",
                      [("利息", 73, "73円"), ("元金", 84963, "8万4963円")],
                      BADGE, BRAND, ymax=100000, highlight=0),
    "risoku": sl.barsN("35年で上乗せされる金額",
                       [("変動金利", 571, "571万円"), ("固定金利", 1948, "1948万円")],
                       BADGE, BRAND, ymax=2300, highlight=1),
    "bai": sl.hero("3.4倍", "※ 1948万 ÷ 571万", BADGE, BRAND,
                   size=190, sub_fs=34),
    "za1": sl.barsN("変動金利のまま返した場合の残高",
                    [("5年後", 2634, "2634万円")], BADGE, BRAND, ymax=3100),
    "za2": sl.barsN("変動金利のまま返した場合の残高",
                    [("5年後", 2634, "2634万円"), ("10年後", 2250, "2250万円")],
                    BADGE, BRAND, ymax=3100, highlight=1),
    "zandaka": sl.barsN("変動金利のまま返した場合の残高",
                        [("5年後", 2634, "2634万円"), ("10年後", 2250, "2250万円"),
                         ("20年後", 1418, "1418万円")],
                        BADGE, BRAND, ymax=3100, highlight=2),
    "juu": sl.card("前半の中身", "利息", "※ 先に返すほど効く理由",
                   BADGE, BRAND, main_size=150, head_fs=32),

    # ---- 第2章 上がった場合
    "ch2": sl.chapter(2, "上がった場合", "1%上がると、何が起きるのか?", BADGE, BRAND),
    "up1a": sl.barsN("毎月の返済額はどう動くか",
                     [("いま", 85036, "8万5036円")], BADGE, BRAND, ymax=115000),
    "up1": sl.barsN("毎月の返済額はどう動くか",
                    [("いま", 85036, "8万5036円"), ("1%上がると", 99764, "9万9764円")],
                    BADGE, BRAND, ymax=115000, highlight=1),
    "up2": sl.barsN("ふえるぶんを、月と年でくらべる",
                    [("毎月ぶん", 14728, "1万4728円"), ("年ぶん", 176742, "17万6742円")],
                    BADGE, BRAND, ymax=200000, highlight=1),
    "sou35": sl.barsN("払い切るまでの合計をならべる",
                      [("変動金利のまま", 3571, "3571万円"),
                       ("1%上がったまま", 4190, "4190万円"),
                       ("固定金利", 4948, "4948万円")],
                      BADGE, BRAND, ymax=5400, highlight=1),
    "gonen": sl.card("よくある安心材料", "5年の据え置き", "※ 採用しない金融機関もある",
                     BADGE, BRAND, main_size=104, head_fs=32),
    "hy1": sl.barsN("毎月8万5036円がどこまで動くか",
                    [("いま", 85036, "8万5036円"), ("1%上がると", 99764, "9万9764円")],
                    BADGE, BRAND, ymax=125000, highlight=1),
    "hyaku25": sl.barsN("毎月8万5036円がどこまで動くか",
                        [("いま", 85036, "8万5036円"),
                         ("1%上がると", 99764, "9万9764円"),
                         ("125%の上限", 106295, "10万6295円")],
                        BADGE, BRAND, ymax=125000, highlight=2),
    "mibarai": sl.card("残るもの", "未払利息", "※ 最後にまとめて請求される場合がある",
                       BADGE, BRAND, main_size=150, head_fs=32),
    "kawaranai": sl.hero("総額は変わらない", "※ 上限は先送りにするだけ",
                         BADGE, BRAND, size=110, sub_fs=30),

    # ---- 第3章 分かれ目
    "ch3": sl.chapter(3, "分かれ目", "何%まで上がったら、固定金利と並ぶのか?",
                      BADGE, BRAND),
    "sagasu": sl.card("探し方", "二分法", "※ 上下から挟んで詰める方法",
                      BADGE, BRAND, main_size=150, head_fs=32,
                      ask="あなたは、何年で返し終える見込みですか?"),
    "naze": sl.card("なぜ3.14%を超えるか", "先取りの差額",
                    "※ 5年ぶんの差額 約197万円",
                    BADGE, BRAND, main_size=72, head_fs=32),
    "katei3": sl.card("計算の仮定", "下がらない", "※ この表は上限側の目安",
                      BADGE, BRAND, main_size=140, head_fs=32),

    # ---- 第4章 逃げ切り
    "ch4": sl.chapter(4, "逃げ切り", "遅く上がると、どうなるのか?", BADGE, BRAND),
    "sakidori": sl.barsN("安く返せた5年ぶんの差額",
                         [("5年ぶんの差額", 197, "197万円")], BADGE, BRAND, ymax=260),
    "ky1": sl.curve("何年後に上がったかで変わる線",
                    _YEARS, [BE[y] for y in _YEARS], BADGE, BRAND,
                    xlabel="金利が上がる時期(年後)", ylabel="分かれ目の金利(%)",
                    reveal=0.45, marks=[(5, BE[5], "3.83%")],
                    hline=V.RATE_FIX, hline_label="固定金利 3.14%", yfmt="{:.0f}"),
    "ky2": sl.curve("何年後に上がったかで変わる線",
                    _YEARS, [BE[y] for y in _YEARS], BADGE, BRAND,
                    xlabel="金利が上がる時期(年後)", ylabel="分かれ目の金利(%)",
                    reveal=0.72, marks=[(5, BE[5], "3.83%"), (15, BE[15], "6.94%")],
                    hline=V.RATE_FIX, hline_label="固定金利 3.14%", yfmt="{:.0f}"),
    "kyokusen": sl.curve("何年後に上がったかで変わる線",
                         _YEARS, [BE[y] for y in _YEARS], BADGE, BRAND,
                         xlabel="金利が上がる時期(年後)", ylabel="分かれ目の金利(%)",
                         marks=[(5, BE[5], "3.83%"), (15, BE[15], "6.94%")],
                         hline=V.RATE_FIX, hline_label="固定金利 3.14%", yfmt="{:.0f}"),
    "riyuu4": sl.card("効き方が変わる理由", "残高の大きさ", "※ 残高 × 金利 で効く",
                      BADGE, BRAND, main_size=104, head_fs=32),
    "kuriage2": sl.barsN("先に返すと分かれ目はどう動くか",
                         [("そのまま", BE[5], "3.83%"),
                          ("先に300万円", BE_PREPAY, "4.26%")],
                         BADGE, BRAND, ymax=5.2, highlight=1),
    "genjitsu": sl.card("読みかた", "後半ほど遠のく", "※ 表の数字は仮定であって予測ではない",
                        BADGE, BRAND, main_size=120, head_fs=32),
    "zentei2": sl.card("この計算の前提", "5年の据え置き", "※ 採用しない金融機関もある",
                       BADGE, BRAND, main_size=120, head_fs=32),
    "jibun": sl.card("読む場所", "返済し終える年数", "※ 先に返す予定も入れて考える",
                     BADGE, BRAND, main_size=76, head_fs=32),
    "hyo": sl.table("上がる時期ごとの分かれ目",
                    ["金利が上がる時期", "分かれ目の金利"],
                    [(_LABEL[y], f"{BE[y]:.2f}%") for y in _YEARS],
                    BADGE, BRAND),
    "tejun1": sl.checklist("決めかたの手順", ["年数を決める", "行の金利を見る", "届くか考える"],
                           BADGE, BRAND, lit=1),
    "tejun2": sl.checklist("決めかたの手順", ["年数を決める", "行の金利を見る", "届くか考える"],
                           BADGE, BRAND, lit=2),
    "tejun": sl.checklist("決めかたの手順", ["年数を決める", "行の金利を見る", "届くか考える"],
                          BADGE, BRAND, lit=3),
    "hyo2": sl.table("自分はどの行を見るか",
                     ["金利が上がる時期", "分かれ目の金利"],
                     [(_LABEL[y], f"{BE[y]:.2f}%") for y in _YEARS],
                     BADGE, BRAND, highlight=3, reveal_rows=False),
    "shime": sl.hero("決めるのは、いま", "※ 2026年8月時点の金利です",
                     BADGE, BRAND, size=120, sub_fs=32),
}

UNITS = [
    # ============ 冒頭(0〜40秒)KGI=視聴維持100%
    Unit("ie", "家のローン、選び方で1377万円の損?", anim=1.2, cover=True,
         se="pop", speed=1.05, intonation=1.3),
    Unit("kariru", "まず、3000万円を借りるとするのだ。", anim=1.4, speed=1.05, chara="none"),
    Unit("kariru", "3000万円を、35年かけて返すのよ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("sog2", "35年ぶんの総額なら、変動金利で3571万円よ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("sog3", "固定金利なら、総額は4948万円なのだ。", anim=1.4, speed=1.05, chara="none"),
    Unit("sougaku", "4948万円との差は、1377万円なのだ。", anim=0.0,
         se="don", speed=1.0, intonation=1.3, face="surprised", chara="none"),
    Unit("sougaku", "1377万円を、変動金利が得しているのよ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("kowai", "でも変動金利は、あとから上がることがあるのだな。", anim=1.4,
         face="troubled", speed=1.05),
    Unit("kowai", "もし上がったら、何%で固定金利に負けるのかしら。", anim=0.0,
         speaker=2, face="troubled", speed=1.05),
    Unit("be2", "もし5年後に上がるなら、答えは出せるわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("be2", "5年後の分かれ目は、3.83%なのだ。", anim=0.0,
         se="impact", se_at=0.30, speed=1.0, intonation=1.25, chara="none"),
    Unit("yotei", "その分かれ目を、4つの章で確かめるわね。", anim=1.4,
         speaker=2, face="happy", speed=1.1, pad=0.6),

    # ============ 第1章 上がらない前提
    Unit("ch1", "では第1章。上がらないままなら、いくら得なのか。", anim=1.4,
         speaker=2, se="pop", speed=1.1),
    Unit("kinri", "まず、いまの変動金利を1.025%とするわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("kinri", "変動金利とは、あとから動く金利のことよ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("kinri", "一方の固定金利なら、3.14%なのだ。", anim=0.0, speed=1.05, chara="none"),
    Unit("kinri", "固定金利とは、最後まで動かない金利のことよ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("maitsuki", "では変動金利と固定金利で、毎月の返済額を出すわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("maitsuki", "変動金利なら、毎月8万5036円よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("maitsuki", "固定金利なら、毎月11万7812円なのだ。", anim=0.0, speed=1.05, chara="none"),
    Unit("maitsuki", "毎月で3万2776円もちがうのだ。", anim=0.0,
         face="surprised", speed=1.05, chara="none"),
    Unit("genri", "この返し方は、元利均等というのよ。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("genri", "元利均等とは、毎月の額が変わらない返し方よ。", anim=0.0,
         speaker=2, speed=1.05),
    Unit("genri", "毎月の額が同じなら、家計は立てやすいのだな。", anim=0.0, speed=1.05),
    Unit("uchi1", "毎月8万5036円の中身を、割ってみるわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("uchi1", "中身のうち、はじめの月は利息が2万5625円なの。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("uchi1", "2万5625円も利息に消えるのは、重いのだ。", anim=0.0,
         face="troubled", speed=1.05, chara="none"),
    Unit("uchi1b", "利息をのぞくと、借金が減るのは5万9411円よ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("uchi2", "そして最後の月には、利息は73円まで減るの。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("uchi2", "利息が73円なら、後半は元金ばかりなのだな。", anim=0.0,
         face="happy", speed=1.05, chara="none"),
    Unit("uchi2", "元金のほうは、8万4963円まで育っているわ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("risoku", "では35年ぶんの利息を、金利ごとに並べるわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("risoku", "変動金利の利息は、571万円よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("risoku", "固定金利の利息は、1948万円なのだ。", anim=0.0, speed=1.05, chara="none"),
    Unit("bai", "利息だけで、3.4倍もちがうのだ。", anim=1.4,
         se="don", face="surprised", speed=1.05, chara="none"),
    Unit("za1", "そこで、のこる借金も年ごとに見ておくわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("za1", "まず5年後にのこるのは、2634万円よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("za2", "では10年たつと、どうなるのだ?", anim=1.4,
         speed=1.05, chara="none"),
    Unit("za2", "10年たつと、2250万円までのこりが減るわ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("zandaka", "では20年たつと、どうなるのだ?", anim=1.4,
         speed=1.05, chara="none"),
    Unit("zandaka", "20年たつと、1418万円までのこるわ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("juu", "1377万円の差は、金利が上がらなければ動かないの。", anim=1.4,
         speaker=2, speed=1.05, pad=0.6),
    Unit("sougaku", "1377万円が、上がらないままの得なのだ。", anim=1.4,
         speed=1.05, chara="none"),

    # ============ 第2章 上がった場合
    Unit("ch2", "では第2章。金利が上がると、毎月がどうなるか。", anim=1.4,
         speaker=2, se="pop", speed=1.1),
    Unit("up1a", "まず1%上がった場合を、見てみるわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("up1", "1%上がると、毎月は9万9764円にふえるわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("up1", "毎月で、1万4728円ふえるのだ。", anim=0.0,
         face="troubled", speed=1.05, chara="none"),
    Unit("up2", "1万4728円は、年で17万6742円よ。", anim=1.4,
         speaker=2, se="impact", se_at=0.28, speed=1.05, chara="none"),
    Unit("up2", "17万6742円は、家族旅行が消える額なのだ。", anim=0.0,
         face="troubled", speed=1.05, chara="none"),
    Unit("gonen", "そのふえかたには、決まりがあるの。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("hy1", "まず1つめは、5年ごとの見直しなの。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("hy1", "5年は据え置きなら、すぐには効かないのだな。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("hyaku25", "そしてもう1つが、前の1.25倍までの上限よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("hyaku25", "1.25倍の上限は、10万6295円までなのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("mibarai", "上限は、利息を消してくれないの。", anim=1.4,
         speaker=2, face="troubled", speed=1.05),
    Unit("mibarai", "はみ出した利息は、未払い利息として残るのよ。", anim=0.0,
         speaker=2, speed=1.05),
    Unit("mibarai", "残った未払い利息は、あとで払うのだな。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("hyaku25", "その未払いは、10万6295円で止めたぶんなのよ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("sou35", "では1%上がったまま、35年ぶんを見るわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("sou35", "その35年ぶんの総額は、4190万円よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("sou35", "4190万円でも、まだ固定金利の4948万円より安いのだ。", anim=0.0,
         face="happy", speed=1.05, chara="none"),
    Unit("kawaranai", "だから5年の据え置きは、総額を減らさないの。", anim=1.4,
         speaker=2, speed=1.05, pad=0.6, chara="none"),
    Unit("kawaranai", "その上限があっても、払う総額は変わらないのだ。", anim=1.4,
         se="don", speed=1.05, chara="none"),

    # ============ 第3章 分かれ目
    Unit("ch3", "では第3章。その総額が、固定金利と並ぶ%を探すわ。", anim=1.4,
         speaker=2, se="pop", speed=1.1),
    Unit("sagasu", "その探し方は、総返済額が並ぶ金利を見ることよ。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("sagasu", "総返済額が並んだところが、分かれ目なのだな。", anim=0.0, speed=1.05),
    Unit("be1", "ではいますぐ上がるなら、分かれ目は3.14%。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("be1", "3.14%は、いまの固定金利と同じ数字なのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("be2", "3.14%は、5年後に上がるなら3.83%まで動くの。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("be2", "3.83%までなら、変動金利が得な分かれ目なのだ。", anim=0.0,
         face="happy", speed=1.05, chara="none"),
    Unit("be3", "その分かれ目は、10年後に上がるなら4.96%よ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("be3", "4.96%は、いまの固定金利の1.5倍を超える高さなのだ。", anim=0.0,
         face="surprised", speed=1.05, chara="none"),
    Unit("naze", "その理由は、上がるまでの年に安く返せるからよ。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("naze", "だから安く返したぶんが、貯金になるのだな。", anim=0.0, speed=1.05),
    Unit("sakidori", "貯金は、5年ぶんで197万円になるの。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("sakidori", "197万円を先に受け取っているようなものなのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("katei3", "その先取りの前提には、条件が1つあるの。", anim=1.4,
         speaker=2, face="troubled", speed=1.05),
    Unit("katei3", "条件は、上がったあと最後まで下がらないことよ。", anim=0.0,
         speaker=2, speed=1.05),
    Unit("katei3", "なので下がらない前提の、きびしめな見方なのだな。", anim=0.0,
         speed=1.05, pad=0.6),
    Unit("be2", "だから3.83%までなら、変動金利が得なのだ。", anim=1.4,
         se="don", speed=1.05, chara="none"),

    # ============ 第4章 逃げ切り + 自分の場合
    Unit("ch4", "では第4章。得になる時期を、あとにずらすわ。", anim=1.4,
         speaker=2, se="pop", speed=1.1),
    Unit("ky1", "ずらすと、10年後の分かれ目は4.96%だったわね。", anim=1.6,
         speaker=2, speed=1.05, chara="none"),
    Unit("ky1", "4.96%まで耐えられるのは、ずいぶん広いのだ。", anim=0.0,
         face="surprised", speed=1.05, chara="none"),
    Unit("ky2", "そして15年後まで上がらなければ、もっと広いわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("ky2", "15年後なら、6.94%まで耐えられるのだ。", anim=0.0,
         face="surprised", speed=1.05, chara="none"),
    Unit("kyokusen", "そのとおり。遅く上がるほど、分かれ目は上に動くの。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("za2", "では、なぜ遅いほど耐えられるのだ?", anim=1.4,
         face="troubled", speed=1.05, chara="none"),
    Unit("za2", "それは、10年後にはのこりが2250万円だからよ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("riyuu4", "そののこりが少ないほど、金利の効きは弱まるの。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("riyuu4", "だから同じだけ上がっても、遅いほど痛くないのだな。", anim=0.0, speed=1.05),
    Unit("kuriage2", "その効きは、先に返しておくともっと弱まるわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("kuriage2", "たとえば5年目に、300万円を先に返した場合よ。", anim=0.0,
         speaker=2, speed=1.05, chara="none"),
    Unit("kuriage2", "300万円で、分かれ目は4.26%まで上がるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("genjitsu", "でもその時期は、誰にも選べないの。", anim=1.4,
         speaker=2, face="troubled", speed=1.05),
    Unit("genjitsu", "では選べないなら、どこで決めればいいのだ?", anim=0.0,
         face="troubled", speed=1.05),
    Unit("zentei2", "まず、この計算は2026年8月の例なの。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("zentei2", "計算のもとは変わるから、そのつど確かめるのだ。", anim=0.0,
         face="troubled", speed=1.05),
    Unit("jibun", "だから自分が何年で返すかを、見るのよ。", anim=1.4,
         speaker=2, speed=1.05),
    Unit("hyo", "その年数ごとの分かれ目を、表にまとめたわ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("hyo", "自分の年数の行を見れば、耐えられる%が分かるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("tejun1", "その行の見つけ方を、3つの手順にするわね。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("tejun1", "まず借入額と年数を、明細で確かめるのだ。", anim=0.0,
         speed=1.05, chara="none"),
    Unit("tejun2", "年数を決めたら、表の行を見るのよ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("tejun", "そして分かれ目まで耐えられるかを、考えるのだ。", anim=1.4,
         speed=1.05, pad=0.6, chara="none"),
    Unit("hyo2", "その%を自分で出せれば、もう迷わないのだ。", anim=1.4,
         se="don", speed=1.05, chara="none"),

    # ============ 締め
    Unit("shime", "そこが変動金利の、得と損の分かれ目よ。", anim=1.4,
         speaker=2, speed=1.05, chara="none"),
    Unit("hyo2", "そして5年後なら、3.83%が分かれ目なのだ。", anim=1.4,
         speed=1.05, chara="none"),
    Unit("shime", "その分かれ目の手前の話は、概要欄のショート版にあるわ。", anim=1.4,
         speaker=2, face="happy", speed=1.05, chara="none"),
    Unit("shime", "自分の分かれ目を、今日読んでみるのだ。", anim=0.0,
         face="happy", speed=1.05),
    Unit("hyo2", "3.83%まで耐えられるなら、変動金利が得なのだ。", anim=1.4,
         se="don", speed=1.05, chara="none"),
]


CHAPTER_MARKS_TITLES = [
    "変動金利は何%まで上がったら固定に負けるのか",
    "第1章 上がらないままなら、いくら得か",
    "第2章 1%上がると、毎月はどうなるか",
    "第3章 何%で固定に並ぶのか",
    "第4章 遅く上がると、どこまで耐えられるか",
]
_first = {}
for _i, _u in enumerate(UNITS):
    _first.setdefault(_u.scene, _i)
CHAPTER_MARKS = list(zip(
    [0] + [_first[f"ch{k}"] for k in range(1, 5)], CHAPTER_MARKS_TITLES))
assert [i for i, _ in CHAPTER_MARKS] == sorted(i for i, _ in CHAPTER_MARKS)

BANDS = list(zip(
    [i for i, _ in CHAPTER_MARKS],
    ["今日の問い", "第1章 いまの差", "第2章 上がると", "第3章 分かれ目", "第4章 逃げ切り"],
    ["#fab219", "#c39bff", "#ff7a6b", "#5aa9ff", "#3ecf8e"],
))


if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "L002.mp4", bands=BANDS)
    print(f"total: {result['total_sec']:.1f}s")
    lines = sl.chapter_lines(result["unit_secs"], CHAPTER_MARKS)
    (OUTDIR / "chapters.txt").write_text("\n".join(lines) + "\n")
    print("chapters:")
    for ln in lines:
        print("  " + ln)
    print(f"mp4: {result['mp4']}")
