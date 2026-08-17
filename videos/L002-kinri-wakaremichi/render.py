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


def _bars(upto, highlight=None):
    """分かれ目の棒を、左から upto 本ぶんだけ出す。"""
    items = [(_LABEL[y], BE[y], f"{BE[y]:.2f}%") for y in _YEARS[:upto]]
    return sl.barsN("上がる時期ごとの分かれ目", items, BADGE, BRAND,
                    ymax=24, highlight=highlight)


SCENES = {
    # ---- 第0章 冒頭(欲求の場面から入る)
    "ie": sl.hero("3000万円を、35年で借りる", "※ 金利は2026年8月の水準・概算",
                  BADGE, BRAND, size=76, sub_fs=32),
    "ie__cover": sl.cover("変動金利は、何%まで上がったら固定金利に負けるのか",
                          "3.83%", "5年後に上がる場合", "2026年8月の金利で計算", BRAND,
                          main_size=200),
    "mayoi": sl.card("借りる前の分かれ道", "変動金利か、固定金利か",
                     "※ 決めるのは、契約する前の一度だけ",
                     BADGE, BRAND, main_size=62, head_fs=32),
    "kotae5": sl.hero("5年後なら 3.83%", "※ そこまで上がると並ぶ", BADGE, BRAND,
                      size=96, sub_fs=32),
    "hitotsu": sl.card("ただし", "1つの数字では答えられない", "※ 上がる時期で変わる",
                       BADGE, BRAND, main_size=56, head_fs=32),
    "yotei": sl.card("これから確かめること", "5つの章", "(所要 約9分)",
                     BADGE, BRAND, main_size=88, head_fs=32),

    "dare": sl.card("だれの話か", "これから借りる人", "※ すでに借りた人は第6章へ",
                    BADGE, BRAND, main_size=88, head_fs=32),
    "zentei": sl.card("この動画の前提", "団信・手数料は含まない", "※ 金利だけで比べる",
                      BADGE, BRAND, main_size=72, head_fs=32),

    # ---- 第1章 上がらなかったら
    "ch1": sl.chapter(1, "上がらない前提", "そもそも今の金利で、いくら違うのか?",
                      BADGE, BRAND),
    "kinri": sl.barsN("いまの金利",
                      [("変動金利", 1.025, "1.025%"), ("固定金利", 3.140, "3.14%")],
                      BADGE, BRAND, ymax=3.8, highlight=1),
    "maitsuki": sl.barsN("毎月の返済額",
                         [("変動金利", 85036, "8万5036円"),
                          ("固定金利", 117812, "11万7812円")],
                         BADGE, BRAND, ymax=140000, highlight=1),
    "sougaku": sl.compare2("35年ぶんの総返済額",
                           ("変動金利", [("元金3000万", 3000, MUTED_BAR),
                                     ("利息571万", 571, GOLD)], "3571万円"),
                           ("固定金利", [("元金3000万", 3000, MUTED_BAR),
                                     ("利息1948万", 1948, GOLD)], "4948万円"),
                           BADGE, BRAND, note_l="※ 上がらなかった場合", note_r="※ 最後まで同じ"),
    "sa1377": sl.hero("差 1377万円", "※ 4948万 − 3571万", BADGE, BRAND,
                      size=104, sub_fs=32),

    "risoku": sl.barsN("35年で払う利息だけを比べる",
                       [("変動金利", 571, "571万円"), ("固定金利", 1948, "1948万円")],
                       BADGE, BRAND, ymax=2300, highlight=1),
    "bai": sl.hero("利息が 3.4倍ちがう", "※ 1948万 ÷ 571万", BADGE, BRAND,
                   size=104, sub_fs=32),

    # ---- 第1章の追加(毎月の中身)
    "genri": sl.card("この借り方の名前", "元利均等返済", "※ 毎月の額が一定になる方式",
                     BADGE, BRAND, main_size=96, head_fs=32),
    "uchi1": sl.barsN("1回目の8万5036円の中身",
                      [("利息", 25625, "2万5625円"), ("元金", 59411, "5万9411円")],
                      BADGE, BRAND, ymax=72000, highlight=0),
    "uchi2": sl.barsN("最終回の8万5036円の中身",
                      [("利息", 73, "73円"), ("元金", 84963, "8万4963円")],
                      BADGE, BRAND, ymax=100000, highlight=0),
    "juu": sl.card("だから最初のうちは", "利息を返している", "※ 元金はなかなか減らない",
                   BADGE, BRAND, main_size=82, head_fs=32),

    "naze0": sl.card("なぜ1つで答えられないか", "上がる時期で変わる",
                     "※ 早く上がるほど、痛い",
                     BADGE, BRAND, main_size=76, head_fs=32),

    # ---- 第2章 上がったら
    "ch2": sl.chapter(2, "上がった場合", "1%上がると、何が起きるのか?", BADGE, BRAND),
    "up1": sl.barsN("変動金利が1%上がると",
                    [("いま", 85036, "8万5036円"), ("1%上がると", 99764, "9万9764円")],
                    BADGE, BRAND, ymax=115000, highlight=1),
    "up2": sl.hero("毎月 +1万4728円", "※ 年にすると +17万6736円", BADGE, BRAND,
                   size=92, sub_fs=34),
    "kowai": sl.card("よくある結び", "「上がったら怖い」", "※ ここで終わる解説が多い",
                     BADGE, BRAND, main_size=76, head_fs=32),
    "toi2": sl.card("でも知りたいのは", "何%で負けるのか", "※ 怖いかどうかではなく",
                    BADGE, BRAND, main_size=76, head_fs=32,
                    ask="あなたは、何年で返し終える見込みですか?"),

    "minaoshi": sl.card("変動金利が見直されるのは", "年2回", "※ 基準金利の見直しのタイミング",
                        BADGE, BRAND, main_size=120, head_fs=32),

    # ---- 第2章の追加(5年ルール・125%ルール)
    "gonen": sl.card("よくある安心材料", "5年ルール", "※ 毎月の額は5年ごとにしか変わらない",
                     BADGE, BRAND, main_size=104, head_fs=32),
    "hyaku25": sl.barsN("毎月の額はどこまで上がるか",
                        [("いま", 85036, "8万5036円"),
                         ("1%上がると", 99764, "9万9764円"),
                         ("125%の上限", 106295, "10万6295円")],
                        BADGE, BRAND, ymax=125000, highlight=2),
    "mibarai": sl.card("減らなかった分は", "未払利息として残る", "※ 消えるわけではない",
                       BADGE, BRAND, main_size=72, head_fs=32),
    "kawaranai": sl.hero("総額は変わらない", "※ 毎月の額の見え方が変わるだけ",
                         BADGE, BRAND, size=110, sub_fs=32),

    # ---- 第3章 分かれ目
    "ch3": sl.chapter(3, "分かれ目", "何%まで上がったら、固定金利と並ぶのか?",
                      BADGE, BRAND),
    "sagasu": sl.card("やること", "並ぶ金利を探す", "※ 総返済額が4948万円になる点",
                      BADGE, BRAND, main_size=96, head_fs=32),
    "sagasu2": sl.barsN("その金利まで上げたときの総返済額",
                        [("3.14%まで", 4581, "4581万円"), ("3.50%まで", 4769, "4769万円"),
                         ("3.83%まで", 4945, "4945万円")],
                        BADGE, BRAND, ymax=5600, highlight=2),
    "be5": _bars(2, highlight=1),
    "be5b": sl.hero("5年後なら 3.83%", "※ 固定金利より高い", BADGE, BRAND,
                    size=96, sub_fs=32),
    "naze": sl.card("固定金利より高い理由", "先に安く返しているから",
                    "※ 最初の5年ぶんの貯金がある",
                    BADGE, BRAND, main_size=62, head_fs=32),
    "be10": _bars(3, highlight=2),

    "katei3": sl.card("この計算の仮定", "上がったら、下がらない",
                      "※ 実際は上下する。目安であって予測ではない",
                      BADGE, BRAND, main_size=72, head_fs=32),

    # ---- 第4章 逃げ切り
    "ch4": sl.chapter(4, "逃げ切り", "遅く上がると、どうなるのか?", BADGE, BRAND),
    "be15": _bars(4, highlight=3),
    "be20": _bars(5, highlight=4),
    "be25": _bars(6, highlight=5),
    "kyokusen": sl.curve("上がる時期と、分かれ目の金利",
                         _YEARS, [BE[y] for y in _YEARS], BADGE, BRAND,
                         xlabel="金利が上がる時期(年後)", ylabel="分かれ目の金利(%)",
                         marks=[(5, BE[5], "3.83%"), (15, BE[15], "6.94%")],
                         hline=V.RATE_FIX, hline_label="固定金利 3.14%", yfmt="{:.0f}"),
    "hayaku": sl.hero("負けるには、早く上がる必要がある", "※ 遅いほど耐える",
                      BADGE, BRAND, size=68, sub_fs=34),

    # ---- 第4章の追加(なぜ遅いほど耐えるのか)
    "zandaka": sl.barsN("そのときに残っている借金",
                        [("5年後", 2634, "2634万円"), ("10年後", 2250, "2250万円"),
                         ("15年後", 1845, "1845万円"), ("20年後", 1418, "1418万円")],
                        BADGE, BRAND, ymax=3100),
    "riyuu4": sl.card("だから遅いほど耐える", "上がる対象が小さい",
                      "※ 15年後の残高は、借りた額の61%",
                      BADGE, BRAND, main_size=76, head_fs=32),

    "genjitsu": sl.card("この数字をどう読むか", "20年逃げれば、まず届かない",
                        "※ 11.04%や21.90%は現実味が薄い",
                        BADGE, BRAND, main_size=62, head_fs=32),

    # ---- 第5章 繰上返済
    "ch5": sl.chapter(5, "繰上返済", "繰り上げて返すと、分かれ目は動くのか?",
                      BADGE, BRAND),
    "kuriage": sl.card("試すこと", "5年目に300万円", "※ 返済額を軽くする方式",
                       BADGE, BRAND, main_size=88, head_fs=32),
    "kuriage2": sl.barsN("5年後に上がる場合の分かれ目",
                         [("そのまま", BE[5], "3.83%"),
                          ("300万円 繰上", BE_PREPAY, "4.26%")],
                         BADGE, BRAND, ymax=5.2, highlight=1),
    "kuriage3": sl.hero("分かれ目が 0.43%上がる", "※ 耐えられる幅がひろがる",
                        BADGE, BRAND, size=76, sub_fs=32),

    # ---- 第5章の追加(2つの方式)
    "houshiki": sl.compare2("繰上返済の2つの方式",
                            ("返済額軽減", [("毎月が下がる", 60, GOLD),
                                        ("期間はそのまま", 100, MUTED_BAR)], "この動画の前提"),
                            ("期間短縮", [("毎月はそのまま", 100, MUTED_BAR),
                                      ("期間が縮む", 60, GOLD)], "利息はより減る"),
                            BADGE, BRAND,
                            note_l="※ 月々を楽にしたい人向け", note_r="※ 総額を減らしたい人向け"),

    # ---- 第6章 すでに借りている人
    "ch6": sl.chapter(6, "借りたあとの人", "すでに変動で借りている人は、どう読むのか?",
                      BADGE, BRAND),
    "sudeni": sl.card("読み替えかた", "残り年数で見る", "※ 上がる時期を残り年数に置きかえる",
                      BADGE, BRAND, main_size=88, head_fs=32),
    "nokori": sl.table("残り年数ごとの目安",
                       ["返し終えるまで", "耐えられる金利"],
                       [("あと30年", "3.83%"), ("あと25年", "4.96%"),
                        ("あと20年", "6.94%"), ("あと15年", "11.04%")],
                       BADGE, BRAND),
    "hiyou": sl.card("借り換えには", "費用がかかる", "※ 手数料・保証料・登記費用など",
                     BADGE, BRAND, main_size=96, head_fs=32),
    "sonobun": sl.card("だからその費用も", "分かれ目に足す", "※ この表は費用を含んでいない",
                       BADGE, BRAND, main_size=82, head_fs=32),

    # ---- 締め(自分の場合を読み取れるようにする)
    "hyo": sl.table("上がる時期ごとの分かれ目",
                    ["金利が上がる時期", "分かれ目の金利"],
                    [(_LABEL[y], f"{BE[y]:.2f}%") for y in _YEARS],
                    BADGE, BRAND),
    "hyo2": sl.table("上がる時期ごとの分かれ目",
                     ["金利が上がる時期", "分かれ目の金利"],
                     [(_LABEL[y], f"{BE[y]:.2f}%") for y in _YEARS],
                     BADGE, BRAND, highlight=3, reveal_rows=False),
    "jibun": sl.card("自分の場合の読み方", "返し終える年数を当てる",
                     "※ その行より低ければ、変動金利が残る",
                     BADGE, BRAND, main_size=62, head_fs=32),
    "kateii": sl.card("この表の前提", "そこまで上がって、続く",
                      "※ 実際の金利は上下する。予測ではない",
                      BADGE, BRAND, main_size=62, head_fs=32),
    "zentei2": sl.card("前提その2", "5年ルールは総額を変えない", "※ 見え方が変わるだけ",
                       BADGE, BRAND, main_size=62, head_fs=32),
    "zentei3": sl.card("前提その3", "固定金利は商品で違う", "※ ここはフラット35の水準",
                       BADGE, BRAND, main_size=72, head_fs=32),
    "tejun": sl.checklist("決めかたの手順", ["返し終える年数を決める",
                                        "その行の金利を見る",
                                        "そこまで上がると思うか考える"],
                          BADGE, BRAND, lit=3),
    "shime": sl.hero("選ぶのは、契約の前だけ", "※ 2026年8月時点の金利です",
                     BADGE, BRAND, size=80, sub_fs=32),
}

UNITS = [
    # ===== 第0章 冒頭 — 欲求の場面から入る(ループ67 Y3)
    Unit("ie", "家を買うとき、3000万円を35年で借りるとする。", anim=1.4, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("mayoi", "その借り方で、まず迷うのが金利の選び方。", anim=1.4, speed=1.1),
    Unit("mayoi", "つまり変動金利か、固定金利かなのだ。", anim=0.0, speed=1.1),
    Unit("mayoi", "でも損はしたくないから、迷って当然なのだ。", anim=0.0,
         face="troubled", speed=1.1),
    Unit("kotae5", "その答えを先に言うと、3.83%が分かれ目。", anim=1.6,
         face="surprised", se="impact", se_at=0.34, speed=1.05, intonation=1.25),
    Unit("kotae5", "その3.83%まで変動金利が上がると、並ぶのだ。", anim=0.0, speed=1.05),
    Unit("hitotsu", "ただしこれは、5年後に上がった場合の話。", anim=1.4, speed=1.1),
    Unit("hitotsu", "つまり1つの数字では、答えられないのだ。", anim=0.0, speed=1.1),
    Unit("naze0", "なぜ1つの数字で答えられないのだろうか。", anim=1.4, speed=1.15),
    Unit("naze0", "その理由は、上がる時期で変わるからなのだ。", anim=0.0, speed=1.05),
    Unit("naze0", "つまり早く上がるほど、痛いのだ。", anim=0.0, speed=1.1),
    Unit("dare", "この話は、これから借りる人に向けたものなのだ。", anim=1.4, speed=1.05),
    Unit("dare", "でもすでに借りた人は、第6章で読み替えるのだ。", anim=0.0, speed=1.05),
    Unit("zentei", "その計算には、団信や手数料を含めていないのだ。", anim=1.4, speed=1.05),
    Unit("zentei", "つまり金利だけで、くらべているのだ。", anim=0.0, speed=1.1),
    Unit("yotei", "その上がる時期を、6つの章で動かしていくのだ。", anim=1.4,
         face="happy", speed=1.05),

    # ===== 第1章 上がらなかったら
    Unit("ch1", "では第1章。いまの金利で、いくら違うのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kinri", "まず変動金利から見ると、いま年1.025%なのだ。", anim=1.6, speed=1.05),
    Unit("kinri", "そして固定金利のほうが、いま年3.14%なのだ。", anim=0.0, speed=1.1),
    Unit("maitsuki", "その変動金利なら、毎月8万5036円。", anim=1.6, speed=1.05),
    Unit("maitsuki", "一方の固定金利は、毎月11万7812円なのだ。", anim=0.0, speed=1.05),
    Unit("genri", "その毎月が一定になる借り方を、元利均等返済という。", anim=1.4,
         speed=1.0),
    Unit("uchi1", "でもその中身は、一定ではないのだ。", anim=1.6, speed=1.1),
    Unit("uchi1", "その1回目は、利息が2万5625円。", anim=0.0, speed=1.05),
    Unit("uchi1", "そして元金のほうは、5万9411円しか減らない。", anim=0.0, speed=1.05),
    Unit("uchi2", "ところが最後の1回では、利息が73円になる。", anim=1.6, speed=1.05),
    Unit("uchi2", "その元金は、8万4963円まで増えている。", anim=0.0, speed=1.05),
    Unit("juu", "つまり最初のうちは、利息を返しているのだ。", anim=1.4, speed=1.05),
    Unit("juu", "だから元金は、なかなか減らないのだ。", anim=0.0,
         face="troubled", speed=1.1),
    Unit("juu", "この話は、あとの章でもう一度使うのだ。", anim=0.0, speed=1.1),
    Unit("sougaku", "その毎月を35年ぶん積むと、こうなるのだ。", anim=1.8, speed=1.05),
    Unit("sougaku", "その変動金利なら、3571万円になるのだ。", anim=0.0, speed=1.1),
    Unit("sougaku", "一方の固定金利なら、4948万円になるのだ。", anim=0.0, speed=1.05),
    Unit("risoku", "その差を、利息だけで見てみるのだ。", anim=1.8, speed=1.1),
    Unit("risoku", "変動金利の利息は、571万円。", anim=0.0, speed=1.1),
    Unit("risoku", "一方の固定金利は、1948万円なのだ。", anim=0.0, speed=1.05),
    Unit("bai", "つまり利息が、3.4倍ちがうのだ。", anim=1.6,
         se="pop", speed=1.05, intonation=1.2),
    Unit("bai", "その差は、家をもう一部屋ぶん買える額なのだ。", anim=0.0, speed=1.05),
    Unit("sa1377", "その差の金額が、1377万円なのだ。", anim=1.6,
         puchun=True, se="don", face="surprised", speed=1.0, intonation=1.25),
    Unit("sa1377", "ただしこれは、変動金利が上がらなかった場合。", anim=0.0, speed=1.05),
    Unit("sa1377", "その前提が崩れたら、話は変わるのだ。", anim=0.0, speed=1.1),
    Unit("sa1377", "では、上がったらどうなるのだろうか。", anim=0.0, speed=1.15),

    # ===== 第2章 上がったら
    Unit("ch2", "では第2章。1%上がると、何が起きるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("up1", "その変動金利が1%上がったとする。", anim=1.6, speed=1.1),
    Unit("up1", "するとその毎月が、9万9764円になるのだ。", anim=0.0, speed=1.05),
    Unit("up2", "つまり毎月、1万4728円ふえる。", anim=1.6,
         face="surprised", se="impact", se_at=0.3, speed=1.05, intonation=1.2),
    Unit("up2", "その1年ぶんは、17万6736円になるのだ。", anim=0.0, speed=1.05),
    Unit("minaoshi", "ちなみに変動金利が見直されるのは、年2回。", anim=1.4, speed=1.05),
    Unit("minaoshi", "その見直しで、基準になる金利が動くのだ。", anim=0.0, speed=1.05),
    Unit("gonen", "でも上がっても、毎月はすぐ変わらないのだ。", anim=1.4, speed=1.1),
    Unit("gonen", "その仕組みを、5年ルールというのだ。", anim=0.0, speed=1.1),
    Unit("gonen", "つまり毎月の額は、5年ごとにしか見直さない。", anim=0.0, speed=1.05),
    Unit("hyaku25", "そして見直すときも、上限があるのだ。", anim=1.8, speed=1.1),
    Unit("hyaku25", "その上限は、いまの1.25倍まで。", anim=0.0, speed=1.1),
    Unit("hyaku25", "だから10万6295円より上には、すぐ行かない。", anim=0.0, speed=1.05),
    Unit("mibarai", "でも、減らなかった分は消えないのだ。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("mibarai", "その分は、未払利息として残るのだ。", anim=0.0, speed=1.1),
    Unit("kawaranai", "つまり最後まで払う額は、変わらないのだ。", anim=1.6,
         puchun=True, se="don", face="surprised", speed=1.0, intonation=1.25),
    Unit("kawaranai", "その5年ルールが変えるのは、見え方だけなのだ。", anim=0.0, speed=1.05),
    Unit("kowai", "だから上がったら怖い、とよく言われるのだ。", anim=1.4, speed=1.1),
    Unit("kowai", "でも、そこで終わってしまうことが多いのだ。", anim=0.0,
         face="troubled", speed=1.1),
    Unit("toi2", "つまり知りたいのは、何%で負けるのかなのだ。", anim=1.4, speed=1.05),
    Unit("toi2", "では、その何%を探しにいくのだ。", anim=0.0, speed=1.15),

    # ===== 第3章 分かれ目
    Unit("ch3", "では第3章。何%で、固定金利と並ぶのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("sagasu", "まず4948万円になる金利を、探すのだ。", anim=1.4, speed=1.05),
    Unit("sagasu", "その4948万円は、固定金利の総額なのだ。", anim=0.0, speed=1.05),
    Unit("sagasu2", "まず5年後に、3.14%まで上げてみるのだ。", anim=1.8, speed=1.05),
    Unit("sagasu2", "その総額は4581万円で、まだ足りない。", anim=0.0, speed=1.05),
    Unit("sagasu2", "そこで3.50%まで、上げてみるのだ。", anim=0.0, speed=1.1),
    Unit("sagasu2", "するとその総額は、4769万円になる。", anim=0.0, speed=1.05),
    Unit("sagasu2", "それでもまだ、4948万円には届かないのだ。", anim=0.0, speed=1.05),
    Unit("sagasu2", "そして3.83%まで上げると、4945万円になる。", anim=0.0, speed=1.05),
    Unit("be5", "つまり5年後の分かれ目は、3.83%なのだ。", anim=1.8, speed=1.05),
    Unit("be5b", "その答えが、さっきの3.83%なのだ。", anim=1.6, speed=1.05),
    Unit("naze", "でも3.83%は、固定金利の3.14%より高い。", anim=1.4,
         face="troubled", speed=1.0),
    Unit("naze", "その理由は、先に安く返しているからなのだ。", anim=0.0, speed=1.05),
    Unit("naze", "つまり最初の5年ぶん、貯金ができている。", anim=0.0, speed=1.05),
    Unit("be10", "では10年後に上がる場合は、どうなるか。", anim=1.8, speed=1.1),
    Unit("be10", "その分かれ目は、4.96%まで上がるのだ。", anim=0.0,
         se="pop", speed=1.05, intonation=1.2),
    Unit("be10", "では、もっと遅く上がったらどうなるのか。", anim=0.0, speed=1.15),

    # ===== 第4章 逃げ切り
    Unit("katei3", "ただしこの計算は、上がったら下がらない仮定。", anim=1.4,
         speed=1.05),
    Unit("katei3", "でも実際には、上下をくり返すのだ。", anim=0.0, speed=1.1),
    Unit("katei3", "だからこれは目安であって、予測ではないのだ。", anim=0.0, speed=1.05),
    Unit("ch4", "では第4章。遅く上がると、どうなるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("be15", "まず15年後に、上がる場合を見るのだ。", anim=1.8, speed=1.1),
    Unit("be15", "その分かれ目は、6.94%になるのだ。", anim=0.0, speed=1.05),
    Unit("be20", "そして20年後なら、どうなるだろうか。", anim=1.8, speed=1.1),
    Unit("be20", "その分かれ目は、11.04%まで上がるのだ。", anim=0.0,
         face="surprised", speed=1.05, intonation=1.2),
    Unit("be25", "さらに25年後まで、逃げたとする。", anim=1.8, speed=1.1),
    Unit("be25", "するとその分かれ目は、21.90%になるのだ。", anim=0.0,
         puchun=True, se="don", face="surprised", speed=1.0, intonation=1.25),
    Unit("zandaka", "では、なぜ遅いほど耐えるのだろうか。", anim=1.8, speed=1.15),
    Unit("zandaka", "その理由は、残っている借金の大きさなのだ。", anim=0.0, speed=1.05),
    Unit("zandaka", "その5年後の残高は、まだ2634万円もある。", anim=0.0, speed=1.05),
    Unit("zandaka", "でも15年後には、1845万円まで減るのだ。", anim=0.0, speed=1.05),
    Unit("riyuu4", "つまり上がる対象そのものが、小さくなっている。", anim=1.4, speed=1.05),
    Unit("riyuu4", "その15年後の残高は、借りた額の61%なのだ。", anim=0.0, speed=1.05),
    Unit("riyuu4", "だから同じ1%でも、効き方がちがうのだ。", anim=0.0,
         face="smug", speed=1.05),
    Unit("kyokusen", "その6つを線でつなぐと、こうなるのだ。", anim=2.2, speed=1.1),
    Unit("kyokusen", "つまり遅く上がるほど、分かれ目は高くなる。", anim=0.0, speed=1.05),
    Unit("genjitsu", "では、この数字をどう読めばいいのだろうか。", anim=1.4, speed=1.15),
    Unit("genjitsu", "その11.04%や21.90%は、現実味が薄いのだ。", anim=0.0, speed=1.05),
    Unit("genjitsu", "つまり20年逃げ切れば、まず届かないのだ。", anim=0.0,
         face="smug", speed=1.05, intonation=1.2),
    Unit("hayaku", "だから負けるには、早く上がる必要があるのだ。", anim=1.6,
         face="smug", speed=1.0, intonation=1.2),
    Unit("hayaku", "では、繰り上げて返すとどうなるのだろうか。", anim=0.0, speed=1.15),

    # ===== 第5章 繰上返済
    Unit("ch5", "では第5章。繰り上げて返すと、分かれ目は動くのか。", anim=1.6,
         speed=1.05, intonation=1.2, pause_scale=1.3),
    Unit("kuriage", "たとえば5年目に、300万円を繰り上げるとする。", anim=1.4, speed=1.05),
    Unit("kuriage", "その方式は、毎月の額を軽くするほうなのだ。", anim=0.0, speed=1.05),
    Unit("kuriage2", "すると分かれ目が、4.26%に上がるのだ。", anim=1.8,
         se="pop", speed=1.05, intonation=1.2),
    Unit("kuriage3", "つまり3.83%から、0.43%ぶん上がった。", anim=1.6, speed=1.05),
    Unit("kuriage3", "だから耐えられる幅が、ひろがるのだ。", anim=0.0, speed=1.1),
    Unit("kuriage3", "つまり繰り上げるほど、変動金利は有利になる。", anim=0.0, speed=1.05),
    Unit("houshiki", "ただし繰上返済には、2つの方式があるのだ。", anim=1.8, speed=1.05),
    Unit("houshiki", "その1つが、いま使った返済額軽減。", anim=0.0, speed=1.1),
    Unit("houshiki", "もう1つは、期間短縮という方式なのだ。", anim=0.0, speed=1.1),
    Unit("houshiki", "その期間短縮のほうが、利息はより減るのだ。", anim=0.0, speed=1.05),
    Unit("houshiki", "でも毎月の額は、そのまま変わらないのだ。", anim=0.0, speed=1.1),
    Unit("kuriage3", "では、すでに借りている人はどう読むのか。", anim=0.0, speed=1.15),

    # ===== 第6章 すでに借りている人
    Unit("ch6", "では第6章。すでに変動金利で借りている人へ。", anim=1.6,
         speed=1.05, intonation=1.2, pause_scale=1.3),
    Unit("sudeni", "その人は、上がる時期を残り年数に置きかえる。", anim=1.4, speed=1.05),
    Unit("nokori", "たとえば、あと30年で返し終える人。", anim=2.0, speed=1.1),
    Unit("nokori", "その人の目安が、さっきの3.83%なのだ。", anim=0.0, speed=1.05),
    Unit("nokori", "そしてあと20年なら、6.94%まで耐えるのだ。", anim=0.0, speed=1.05),
    Unit("nokori", "つまり残りが短いほど、変動金利が残りやすい。", anim=0.0,
         face="smug", speed=1.05),
    Unit("nokori", "その表は、これから借りる人のものと同じなのだ。", anim=0.0, speed=1.05),
    Unit("nokori", "だから残り年数さえ分かれば、読めるのだ。", anim=0.0, speed=1.1),
    Unit("hiyou", "ただし借り換えには、費用がかかるのだ。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("hiyou", "その費用は、手数料と保証料と登記費用など。", anim=0.0, speed=1.05),
    Unit("hiyou", "その費用は、借りる先によって変わるのだ。", anim=0.0, speed=1.1),
    Unit("sonobun", "だから見積もりを取って、この表に足すのだ。", anim=1.4, speed=1.05),
    Unit("sonobun", "この表には、その費用が入っていないのだ。", anim=0.0, speed=1.05),
    Unit("sonobun", "では、自分の場合はどう読めばいいのか。", anim=0.0, speed=1.15),

    # ===== 締め — 自分の場合を判定できるようにする(ループ67 Y3)
    Unit("hyo", "その6つを、表にまとめるのだ。", anim=2.0, speed=1.15),
    Unit("jibun", "まず自分が、何年で返し終える見込みか考える。", anim=1.4,
         face="happy", speed=1.05),
    Unit("jibun", "その年数の行を、この表から探すのだ。", anim=0.0, speed=1.1),
    Unit("jibun", "つまり返し終える年数が、読む場所を決めるのだ。", anim=0.0, speed=1.05),
    Unit("hyo2", "たとえば15年で返せそうなら、6.94%の行。", anim=1.6, speed=1.05),
    Unit("hyo2", "その6.94%より低いと思うなら、変動金利が残る。", anim=0.0,
         speed=1.0, intonation=1.2),
    Unit("hyo2", "でも超えると思うなら、固定金利のほうなのだ。", anim=0.0, speed=1.05),
    Unit("kateii", "ただしこの表は、そこまで上がって続く前提。", anim=1.4, speed=1.05),
    Unit("kateii", "その前提のとおりに動くとは、限らないのだ。", anim=0.0, speed=1.05),
    Unit("kateii", "だからこれは目安であって、予測ではないのだ。", anim=0.0, speed=1.05),
    Unit("zentei2", "そして前提が、あと2つあるのだ。", anim=1.4, speed=1.1),
    Unit("zentei2", "その1つが、さっきの5年ルールなのだ。", anim=0.0, speed=1.1),
    Unit("zentei2", "つまり毎月の見え方は変わっても、総額は変わらない。", anim=0.0,
         speed=1.05),
    Unit("zentei3", "そしてもう1つは、固定金利が商品でちがうこと。", anim=1.4, speed=1.05),
    Unit("zentei3", "その3.14%は、フラット35の水準なのだ。", anim=0.0, speed=1.05),
    Unit("zentei3", "だから借りる先で、この表はずれるのだ。", anim=0.0, speed=1.05),
    Unit("tejun", "つまりこの手順は、3つにまとめられるのだ。", anim=1.8, speed=1.1),
    Unit("tejun", "まず、何年で返し終える見込みかを決める。", anim=0.0, speed=1.05),
    Unit("tejun", "そして、その年数の行の金利を見るのだ。", anim=0.0, speed=1.05),
    Unit("tejun", "そして、そこまで上がると思うかを考える。", anim=0.0, speed=1.05),
    Unit("tejun", "その3つで、自分の答えが出せるのだ。", anim=0.0,
         face="smug", speed=1.05, intonation=1.2),
    Unit("shime", "その選択をするのは、契約する前の一度だけ。", anim=1.4,
         speed=1.05, intonation=1.2),
    Unit("shime", "だから借りる前に、この行だけは決めておくのだ。", anim=0.0, pad=0.2,
         face="smug", speed=1.05, intonation=1.15, pitch=-0.03),
]

# チャプター(概要欄に貼る)。章題ではなく**問い**にする(longform-design §4a)
CHAPTER_TITLES = [
    "変動金利は何%で固定金利に負けるのか",
    "第1章 いまの金利で、いくら違うのか",
    "第2章 1%上がると、何が起きるのか",
    "第3章 何%で、固定金利と並ぶのか",
    "第4章 遅く上がると、どうなるのか",
    "第5章 繰り上げて返すと、分かれ目は動くのか",
    "まとめ 自分の場合の読み方",
]
_first = {}
for _i, _u in enumerate(UNITS):
    _first.setdefault(_u.scene, _i)
CHAPTER_MARKS = list(zip(
    [0] + [_first[f"ch{k}"] for k in range(1, 6)] + [_first["hyo"]], CHAPTER_TITLES))
assert [i for i, _ in CHAPTER_MARKS] == sorted(i for i, _ in CHAPTER_MARKS)

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "L002.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    lines = sl.chapter_lines(result["unit_secs"], CHAPTER_MARKS)
    (OUTDIR / "chapters.txt").write_text("\n".join(lines) + "\n")
    print("chapters:")
    for ln in lines:
        print("  " + ln)
    print(f"mp4: {result['mp4']}")
