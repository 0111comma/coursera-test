#!/usr/bin/env python3
"""L001(長尺・横型): NISAで損したらどうなるのか。

企画書は plan.md、数値は verify.py。設計の型は docs/research/longform-design.md。

この動画が答える問い(1つだけ):
  NISAで損したとき、課税口座で損したときより不利になるのか。いくら不利なのか。
答え:
  不利になる額 = min(NISAの損, 課税口座の利益) × 20.315%

長尺の型(longform-design §2):
  各章は「章の問い → 前提 → 数字を1本の鎖で積む → **損得の判定** → 次の章の問い」。
  90秒に1回「で、結局どっちが得なのか」の答えが返ってくる状態にする。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
import shortlib as S  # noqa: E402

S.use_landscape()      # ← new_canvas より前に1回だけ

from shortlib import Unit, render_video, require_voicevox, MUTED_BAR, GOLD, EMPH  # noqa: E402
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

# ---------------------------------------------------------------- シーン

_L20 = [("損20万", 20, MUTED_BAR), ("益20万", 20, GOLD)]
_L30 = [("損30万", 30, MUTED_BAR), ("益10万", 10, GOLD)]
_L10 = [("損10万", 10, MUTED_BAR), ("益30万", 30, GOLD)]

# 図に置くのは道標(9文字以内)。文はナレーションが言う。
# 長い文字列を図に貼るとナレーションと同義になり、かえって読みにくくなる(Mayer冗長性)
_TE = ["損益通算は1年", "確定申告が要る", "売却は税に無関係", "枠は翌年・簿価", "口座は移せない"]

SCENES = {
    # ---- 第0章 冒頭
    "toi": sl.hero("含み損のとき", "※ 金額はすべて仮定の例です",
                   BADGE, BRAND, size=140, sub_fs=32),
    "toi__cover": sl.cover("NISAで損したら、いくら損するのか?", "40,630円",
                           "同じ年に課税口座で利益があると", "2026年8月時点の制度", BRAND),
    "nakatta": sl.card("税金の計算では", "無かったこと", "(NISAの損は、そう扱われる)",
                       BADGE, BRAND, main_size=88, head_fs=32),
    "kazei_wa": sl.card("課税口座の損は", "引ける", "※ 特定口座・一般口座のこと",
                        BADGE, BRAND, main_size=110, head_fs=32),
    "furi": sl.card("向きが逆になる", "NISAが不利", "※ 損が出た年にかぎる",
                    BADGE, BRAND, main_size=96, head_fs=32),
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
    "kotae": sl.hero("差 40,630円", "※ 200,000円 × 20.315%", BADGE, BRAND,
                     size=104, sub_fs=32),
    "jouken": sl.card("適用範囲", "限定的", "※ 毎年起きるわけではない",
                      BADGE, BRAND, main_size=140, head_fs=32),
    "yotei": sl.card("これから確かめること", "6つの章", "(所要 約9分)",
                     BADGE, BRAND, main_size=82, head_fs=32),
    "jiten": sl.card("いつの制度か", "2026年8月時点", "(税制は毎年変わる)",
                     BADGE, BRAND, main_size=72, head_fs=32),
    "dareni": sl.card("だれの話か", "口座を2つ持つ人", "※ 片方だけなら関係しない",
                      BADGE, BRAND, main_size=72, head_fs=32),
    "jisan": sl.card("出どころ", "自前の計算", "※ 検証コードはリポジトリに置いています",
                     BADGE, BRAND, main_size=96, head_fs=32),

    # ---- 第2章の追加(口座の種類)
    "toushin": sl.card("投資信託とは", "まとめ買いの箱", "※ 1本に多数の銘柄が入る",
                       BADGE, BRAND, main_size=88, head_fs=32),
    "kouza": sl.card("課税口座の種類", "特定口座と一般口座", "※ NISA口座はこれとは別枠",
                     BADGE, BRAND, main_size=62, head_fs=32),
    "gensen": sl.card("源泉徴収あり", "証券会社が納める", "※ 選ぶのは口座を開くとき",
                      BADGE, BRAND, main_size=72, head_fs=32),
    "raku": sl.card("ふだんの手間", "ゼロ", "※ 明細を見る機会も無くなる",
                    BADGE, BRAND, main_size=130, head_fs=32),

    # ---- 第3章の追加(なぜそうなるのか)
    "naze": sl.card("制度の筋", "利益を見ないから", "※ だから損も同じ扱いになる",
                    BADGE, BRAND, main_size=76, head_fs=32),
    "hyouri": sl.hero("表と裏", "※ 得の側と、損の側",
                      BADGE, BRAND, size=160, sub_fs=32),

    # ---- 第5章の追加(3年続いたら)
    "sannen": sl.barsN("毎年くり返した場合",
                       [("1年目", 40630, "40,630円"), ("2年目", 40630, "40,630円"),
                        ("3年目", 40630, "40,630円")],
                       BADGE, BRAND, ymax=48000),
    "sannen2": sl.hero("3年で 121,890円", "※ 40,630円 × 3", BADGE, BRAND,
                       size=92, sub_fs=32),

    # ---- 第6章の追加(選べない)
    "erabenai": sl.checklist("この不利への備え", _TE, BADGE, BRAND, lit=5),

    # ---- 第4章の追加(3年の意味)
    "san1": sl.timeline("繰り越せる範囲",
                        [("1年目", "損 40万円", "繰り越す", True),
                         ("2年目", "利益 10万円", "引ける", False),
                         ("3年目", "利益 10万円", "引ける", False),
                         ("4年目", "利益 10万円", "引ける", False)], BADGE, BRAND),
    "san2": sl.timeline("繰り越せる範囲",
                        [("1年目", "損 40万円", "繰り越す", False),
                         ("2年目", "利益 10万円", "引ける", False),
                         ("3年目", "利益 10万円", "引ける", False),
                         ("4年目", "利益 10万円", "引ける", False),
                         ("5年目", "利益 10万円", "引けない", True)], BADGE, BRAND,
                        note="繰り越せるのは、損が出た年の翌年から3年"),

    # ---- 自分の場合の出し方
    "jibun": sl.card("自分の場合", "小さいほう × 0.20315", "※ 同じ年の中で見ること",
                     BADGE, BRAND, main_size=56, head_fs=32),
    "jibun2": sl.barsN("ならべて、小さいほうを取る",
                       [("NISAの損", 4, "4万円"), ("課税口座の利益", 12, "12万円")],
                       BADGE, BRAND, ymax=14, highlight=0),
    "jibun3": sl.hero("40,000円 × 20.315%", "= 8,126円",
                      BADGE, BRAND, size=72, sub_fs=54),

    # ---- 第1章 NISAは何をしてくれるのか
    "ch1": sl.chapter(1, "NISAの役割", "NISAは、お金を増やしてくれるのか?",
                      BADGE, BRAND),
    "fueru": sl.card("よくある思いこみ", "NISAだと増える", "※ 本当にそうなのか",
                     BADGE, BRAND, main_size=76, head_fs=32),
    "fuyasu": sl.card("増やしているもの", "運用", "※ 器と中身は別のもの",
                      BADGE, BRAND, main_size=130, head_fs=32),
    "hikanai": sl.card("NISAの働き", "税を取らない", "※ 増やす働きは無い",
                       BADGE, BRAND, main_size=100, head_fs=32),
    "hikaku_r": sl.barsN("同じ利益でも、残る額がちがう",
                         [("課税口座 手取り", 15.94, "15万9370円"),
                          ("NISA 手取り", 20.0, "20万円")],
                         BADGE, BRAND, ymax=23, highlight=1),
    "sagaku": sl.hero("差 40,630円", "※ 得の側", BADGE, BRAND, size=104, sub_fs=36),
    "hijoukazei": sl.card("非課税がかかる先", "利益", "※ 元本にはかからない",
                          BADGE, BRAND, main_size=140, head_fs=32),
    "genpon": sl.card("元本の扱い", "守られない", "※ 値下がりは同じように起きる",
                      BADGE, BRAND, main_size=104, head_fs=32),
    "ch1_out": sl.hero("器か、中身か", "※ 中身の成績は別の話",
                       BADGE, BRAND, size=140, sub_fs=32),

    # ---- 第2章 税金の決まり方と損益通算
    "ch2": sl.chapter(2, "税の決まり方", "そもそも、株の税金はどう決まるのか?",
                      BADGE, BRAND),
    "zeiritsu": sl.card("利益にかかる税率", "20.315%",
                        "(2026年8月時点・申告分離課税)",
                        BADGE, BRAND, main_size=110, head_fs=32),
    "uchiwake": sl.barsN("3つを足すと20.315%",
                         [("所得税", 15, "15%"), ("住民税", 5, "5%"),
                          ("復興特別所得税", 0.315, "0.315%")],
                         BADGE, BRAND, ymax=17),
    "keisan1": sl.band("利益と、そこから引かれる税", "利益 20万円", 0.79685,
                       "手元 15万9370円", "税 40,630円", BADGE, BRAND, show_rest=True),
    "son_toshi": sl.card("では、損した年は", "どうなるのか", "(税金は、どう計算されるのか)",
                         BADGE, BRAND, main_size=76, head_fs=32),
    "tsuusan": sl.card("この仕組みの名前", "損益通算", "(そんえきつうさん)",
                       BADGE, BRAND, main_size=104, head_fs=32),
    "tsuusan2": sl.card("使える範囲", "1年ごと", "※ またぐには別の仕組み",
                        BADGE, BRAND, main_size=130, head_fs=32),
    "sashihiki": sl.compare2("差し引きの前と、後",
                             ("差し引く前", _L20, ""),
                             ("差し引いた後", [("残り 0円", 0.4, MUTED_BAR)], "税 0円"),
                             BADGE, BRAND, note_r="※ 課税対象が消える"),
    "zairyou": sl.hero("損 = 節税の材料", "※ 課税口座にかぎった話",
                       BADGE, BRAND, size=104, sub_fs=32),

    # ---- 第3章 NISAだと引けない
    "ch3": sl.chapter(3, "引けない損", "NISAの損は、利益から引けるのか?", BADGE, BRAND),
    "hikenai": sl.card("答え", "引けない", "(税金の計算に、入れてもらえない)",
                       BADGE, BRAND, main_size=118, head_fs=32),
    "riyuu1": sl.card("NISAの利益には", "税金がかからない", "(だから得をする)",
                      BADGE, BRAND, main_size=72, head_fs=32),
    "riyuu2": sl.card("NISAの損の扱い", "無いものとされる", "※ 引く相手になれない",
                      BADGE, BRAND, main_size=76, head_fs=32),
    "aite": sl.card("残るもの", "利益だけ", "※ 20万円がまるごと課税対象に",
                    BADGE, BRAND, main_size=120, head_fs=32),
    "keisan2": sl.band("引く相手がいないと、こうなる", "課税される利益 20万円", 0.79685,
                       "手元 15万9370円", "税 40,630円", BADGE, BRAND, show_rest=True),
    "nedan": sl.hero("差 40,630円", "※ 200,000円 × 20.315%", BADGE, BRAND,
                     size=104, sub_fs=32),
    "ch3_out": sl.hero("消えた損", "※ 税の計算に入らない", BADGE, BRAND,
                       size=150, sub_fs=32),

    # ---- 第4章 来年も引けない
    "ch4": sl.chapter(4, "来年の利益", "来年の利益からは、引けるのか?", BADGE, BRAND),
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
    "nedan2": sl.hero("差 81,260円", "※ 400,000円 × 20.315%", BADGE, BRAND,
                      size=104, sub_fs=32),
    "shinkoku": sl.card("使うための条件", "確定申告", "※ 出し忘れた年で権利が切れる",
                        BADGE, BRAND, main_size=130, head_fs=32),

    # ---- 第5章 いくらまで効くのか
    "ch5": sl.chapter(5, "効く範囲", "この不利は、いくらまで効くのか?",
                      BADGE, BRAND),
    "onaji": sl.card("ここまでの前提", "損も利益も20万円", "※ ここから額を動かす",
                     BADGE, BRAND, main_size=72, head_fs=32),
    "pat1": sl.compare2("損のほうが大きい年",
                        ("その年の中身", _L30, ""),
                        ("相殺できた分", [("10万円まで", 10, GOLD)], "差 20,315円"),
                        BADGE, BRAND, note_r="※ 余った損20万円は消える"),
    "pat2": sl.compare2("利益のほうが大きい年",
                        ("その年の中身", _L10, ""),
                        ("相殺できた分", [("10万円まで", 10, GOLD)], "差 20,315円"),
                        BADGE, BRAND, note_r="※ 残る利益20万円には課税"),
    "kousiki": sl.hero("上限は小さいほう", "※ 差はその20.315%",
                       BADGE, BRAND, size=110, sub_fs=32),
    "nashi": sl.compare2("片側しか無い年",
                         ("NISAの損", [("損100万", 100, MUTED_BAR)], ""),
                         ("課税口座の利益", [("0円", 0.5, GOLD)], "差 0円"),
                         BADGE, BRAND, note_r="※ もともと払う税が無い"),
    "sorotta": sl.card("効く条件", "2つがそろった年", "※ 片方だけなら差は0円",
                       BADGE, BRAND, main_size=76, head_fs=32,
                       ask="あなたは、口座を2つ使っていますか?"),
    "ch5_out": sl.hero("小さいほう × 20.315%", "※ 単位は円",
                       BADGE, BRAND, size=80, sub_fs=32),

    # ---- 第6章 どう備えるのか
    "ch6": sl.chapter(6, "備え方", "この不利に、どう備えるのか?", BADGE, BRAND),
    "te1": sl.checklist("この不利への備え", _TE, BADGE, BRAND, lit=1),
    "te2": sl.checklist("この不利への備え", _TE, BADGE, BRAND, lit=2),
    "te3": sl.checklist("この不利への備え", _TE, BADGE, BRAND, lit=3),
    "waku1": sl.checklist("この不利への備え", _TE, BADGE, BRAND, lit=4),
    "waku2": sl.timeline("枠が戻る時期",
                         [("売った年", "戻る枠", "0円", False),
                          ("翌年", "戻る枠", "100万円", True)], BADGE, BRAND,
                         note="※ 簿価(取得価額)ベース。売却額ではない"),
    "ch6_out": sl.hero("大事なのは条件", "※ 制度の good/bad の話ではない",
                       BADGE, BRAND, size=110, sub_fs=30),

    # ---- 締め
    "matome": sl.table("3つの場合",
                       ["どんな年か", "課税口座だけ", "NISAを使うと", "差"],
                       [("損だけの年", "0円", "0円", "0円"),
                        ("利益だけの年", "40,630円", "0円", "得 40,630円"),
                        ("損と利益がある年", "0円", "40,630円", "損 40,630円")],
                       BADGE, BRAND),
    "matome2": sl.table("3つの場合",
                        ["どんな年か", "課税口座だけ", "NISAを使うと", "差"],
                        [("損だけの年", "0円", "0円", "0円"),
                         ("利益だけの年", "40,630円", "0円", "得 40,630円"),
                         ("損と利益がある年", "0円", "40,630円", "損 40,630円")],
                        BADGE, BRAND, highlight=1, reveal_rows=False),
    "matome3": sl.table("3つの場合",
                        ["どんな年か", "課税口座だけ", "NISAを使うと", "差"],
                        [("損だけの年", "0円", "0円", "0円"),
                         ("利益だけの年", "40,630円", "0円", "得 40,630円"),
                         ("損と利益がある年", "0円", "40,630円", "損 40,630円")],
                        BADGE, BRAND, highlight=2, reveal_rows=False),
    "taishou": sl.hero("得も損も 40,630円", "※ 向きが逆なだけ",
                       BADGE, BRAND, size=88, sub_fs=32),
    "kawaru": sl.card("この動画の時点", "2026年8月", "※ 税制改正で変わります",
                      BADGE, BRAND, main_size=104, head_fs=32),
    "shime": sl.hero("売却の判断に、税は不要", "※ 課税口座では逆に効く",
                     BADGE, BRAND, size=76, sub_fs=32),
}

# ---------------------------------------------------------------- 台本

UNITS = [
    # ===== 第0章 冒頭(答えを先に出し切る。longform-design §1)
    Unit("toi", "NISA口座が、マイナスになっているとする。", anim=1.4, cover=True,
         se="pop", speed=1.05, intonation=1.25),
    Unit("toi", "そのマイナスは、税金の足しにならないのか。", anim=0.0,
         face="troubled", speed=1.1, intonation=1.2),
    Unit("nakatta", "でもその損は、税金では【無かったこと】になる。", anim=1.4,
         speed=1.1, intonation=1.2),
    Unit("kazei_wa", "でも課税口座なら、そうではないのだ。", anim=1.4, speed=1.1),
    Unit("kazei_wa", "その課税口座とは、NISAではない普通の口座のこと。", anim=0.0, speed=1.05),
    Unit("kazei_wa", "その課税口座の損は、同じ年の利益から引けるのだ。", anim=0.0, speed=1.1),
    Unit("furi", "だからNISAのほうが、不利になる場合があるのだ。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("rei0", "たとえば、こういう年を考えてみるのだ。", anim=1.4, speed=1.15),
    Unit("rei0", "その年は、NISAで20万円の損、課税口座で20万円の利益。", anim=0.0, speed=1.05),
    Unit("rei1", "まず全部が課税口座なら、この年の税金は0円。", anim=1.4, speed=1.1),
    Unit("rei2", "でもNISAを使っていると、40630円かかるのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.34, speed=1.05, intonation=1.25),
    Unit("kotae", "その差の40630円が、今日の答えなのだ。", anim=1.4,
         puchun=True, se="don", speed=1.05, intonation=1.2),
    Unit("jouken", "ただしこれは、条件がそろった年だけの話なのだ。", anim=1.4, speed=1.1),
    Unit("yotei", "その条件を、6つの章で確かめていくのだ。", anim=1.4, face="happy",
         speed=1.15),
    Unit("jiten", "ちなみに、これは2026年8月時点の制度なのだ。", anim=1.2, speed=1.15),
    Unit("dareni", "この話が関係するのは、口座を2つ使っている人。", anim=1.4, speed=1.1),
    Unit("dareni", "その2つとは、NISAと課税口座のことなのだ。", anim=0.0, speed=1.1),

    # ===== 第1章 NISAは何をするのか
    Unit("ch1", "では第1章。NISAは、お金を増やしてくれるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("fueru", "まずNISAだと増える、と思っている人は多いのだ。", anim=1.4, speed=1.1),
    Unit("fuyasu", "でも実際に増やしているのは、運用のほうなのだ。", anim=1.4, speed=1.1),
    Unit("fuyasu", "そのNISAは器であって、中身ではないのだ。", anim=0.0, speed=1.1),
    Unit("hikanai", "つまりNISAがしているのは、利益に税金を取らないこと。", anim=1.4,
         face="smug", speed=1.05, intonation=1.2),
    Unit("hikaku_r", "では、20万円の利益が出た年で比べてみるのだ。", anim=1.6, speed=1.1),
    Unit("hikaku_r", "その課税口座なら、手元に残るのは15万9370円。", anim=0.0, speed=1.05),
    Unit("hikaku_r", "一方のNISAなら、20万円がそのまま残るのだ。", anim=0.0, speed=1.1),
    Unit("sagaku", "その差の40630円が、非課税の中身なのだ。", anim=1.4,
         speed=1.05, intonation=1.2),
    Unit("hijoukazei", "つまり非課税とは、利益にかかる話なのだ。", anim=1.4, speed=1.1),
    Unit("hijoukazei", "その非課税は、入れた金額にかかる話ではないのだ。", anim=0.0, speed=1.1),
    Unit("genpon", "だから元本、つまり入れたお金は守られないのだ。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("ch1_out", "そのNISAは、増やす仕組みではないのだ。", anim=1.4,
         speed=1.05, intonation=1.2),
    Unit("ch1_out", "では、その税金はどう決まるのだろうか。", anim=0.0, speed=1.15),

    # ===== 第2章 税金の決まり方
    Unit("ch2", "では第2章。株や投資信託の税金は、どう決まるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("toushin", "その投資信託とは、お金をまとめて運用する商品のこと。", anim=1.4,
         speed=1.05),
    Unit("zeiritsu", "その株や投資信託の利益には、20.315%かかるのだ。", anim=1.6,
         se="pop", speed=1.05, intonation=1.2),
    Unit("uchiwake", "その内訳は、所得税と住民税と、復興特別所得税なのだ。", anim=1.6,
         speed=1.05),
    Unit("uchiwake", "その所得税が、15%なのだ。", anim=0.0, speed=1.15),
    Unit("uchiwake", "そして住民税が、5%かかるのだ。", anim=0.0, speed=1.15),
    Unit("uchiwake", "そして復興特別所得税が、0.315%なのだ。", anim=0.0, speed=1.1),
    Unit("keisan1", "たとえば20万円の利益なら、税金は40630円。", anim=1.6, speed=1.1),
    Unit("keisan1", "その手元に残るのが、さっきの15万9370円。", anim=0.0, speed=1.1),
    Unit("kouza", "ちなみに課税口座には、特定口座と一般口座があるのだ。", anim=1.4,
         speed=1.05),
    Unit("kouza", "そのどちらも、利益には税金がかかるのだ。", anim=0.0, speed=1.15),
    Unit("gensen", "その特定口座には、源泉徴収ありという選び方がある。", anim=1.4, speed=1.05),
    Unit("gensen", "その源泉徴収ありとは、証券会社が税金を引いてくれること。", anim=0.0,
         speed=1.0),
    Unit("raku", "だから自分で申告しなくても、税金は納まるのだ。", anim=1.4, speed=1.1),
    Unit("raku", "ただしそのぶん、損の話には気づきにくいのだ。", anim=0.0,
         face="troubled", speed=1.1),
    Unit("son_toshi", "では、損をした年はどうなるのだろうか。", anim=1.4, speed=1.15),
    Unit("tsuusan", "その課税口座には、【損益通算】という仕組みがある。", anim=1.6,
         se="pop", speed=1.05, intonation=1.2),
    Unit("tsuusan", "その損益通算とは、損を利益から引くことなのだ。", anim=0.0, speed=1.1),
    Unit("tsuusan2", "つまり同じ年の中で、差し引きができるのだ。", anim=1.4, speed=1.1),
    Unit("sashihiki", "では、さっきの損20万円と利益20万円で見るのだ。", anim=1.6, speed=1.05),
    Unit("sashihiki", "その2つを差し引きすると、残る利益は0円。", anim=0.0, speed=1.1),
    Unit("sashihiki", "だからこの年の税金も、0円になるのだ。", anim=0.0, speed=1.1),
    Unit("zairyou", "つまり損は、税金を減らす材料になるのだ。", anim=1.4,
         face="happy", speed=1.05, intonation=1.2),
    Unit("zairyou", "ただしそれは、課税口座での話なのだ。", anim=0.0, speed=1.15),
    Unit("son_toshi", "では、NISAの損はどうなるのだろうか。", anim=1.2, speed=1.15),

    # ===== 第3章 NISAだと引けない
    Unit("ch3", "では第3章。NISAの損は、利益から引けるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("hikenai", "答えは、引けない。", anim=1.6, face="surprised",
         se="impact", se_at=0.30, speed=1.0, intonation=1.3),
    Unit("riyuu1", "そのNISAの利益には、税金がかからないのだ。", anim=1.4, speed=1.1),
    Unit("riyuu2", "その代わり、NISAの損も無いものとされるのだ。", anim=1.4, speed=1.1),
    Unit("riyuu2", "つまり税金の世界では、そこで何も起きていない。", anim=0.0, speed=1.1),
    Unit("rei2", "では、さっきの年をもう一度見てみるのだ。", anim=1.4, speed=1.15),
    Unit("rei2", "その年は、NISAで20万円の損、課税口座で20万円の利益。", anim=0.0,
         speed=1.05),
    Unit("aite", "でもNISAの損は、引く相手になれないのだ。", anim=1.4, speed=1.1),
    Unit("aite", "だから課税口座の利益20万円だけが、残るのだ。", anim=0.0, speed=1.1),
    Unit("keisan2", "その20万円に、20.315%がかかるのだ。", anim=1.6, speed=1.1),
    Unit("keisan2", "つまり税金は、さっきと同じ40630円。", anim=0.0, speed=1.1),
    Unit("nedan", "でも全部が課税口座なら0円だったので、差は40630円。", anim=1.6,
         puchun=True, se="don", face="surprised", speed=1.0, intonation=1.25),
    Unit("nedan", "その40630円が、損を引けないことの値段なのだ。", anim=0.0, speed=1.1),
    Unit("naze", "では、なぜそうなっているのだろうか。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("naze", "そのNISAは、利益に課税しない仕組みだからなのだ。", anim=0.0, speed=1.05),
    Unit("hyouri", "だから利益を見ないなら、損も見ないのだ。", anim=1.4, speed=1.1),
    Unit("hyouri", "つまり非課税には、表と裏があるのだ。", anim=0.0, speed=1.1),
    Unit("ch3_out", "その裏側で、引けるはずだった損が消えているのだ。", anim=1.4, speed=1.05),
    Unit("ch3_out", "では、来年の利益からも引けないのだろうか。", anim=0.0, speed=1.15),

    # ===== 第4章 来年も引けない
    Unit("ch4", "では第4章。来年の利益からは、引けるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kurikoshi", "その課税口座には、【繰越控除】という仕組みもある。", anim=1.6,
         se="pop", speed=1.05, intonation=1.2),
    Unit("kurikoshi2", "その繰越控除とは、損を翌年に持ち越すことなのだ。", anim=1.4, speed=1.1),
    Unit("kurikoshi2", "そして持ち越せるのは、3年ぶんまでなのだ。", anim=0.0, speed=1.15),
    Unit("nen1", "たとえば1年目に、40万円の損が出たとする。", anim=1.6, speed=1.1),
    Unit("nen1", "その年に利益が無ければ、税金は0円。", anim=0.0, speed=1.15),
    Unit("nen1", "そして2年目に、40万円の利益が出たとする。", anim=0.0, speed=1.1),
    Unit("nen2", "その課税口座なら、1年目の損をここで引けるのだ。", anim=1.6, speed=1.05),
    Unit("nen2", "だから2年目の税金も、0円になるのだ。", anim=0.0, speed=1.1),
    Unit("nen3", "でもNISAの損は、持ち越せないのだ。", anim=1.6, face="troubled", speed=1.1),
    Unit("nen3", "だから2年目の40万円に、そのままかかるのだ。", anim=0.0, speed=1.1),
    Unit("nen3", "その税金が、40万円の20.315%で81260円。", anim=0.0, speed=1.05),
    Unit("nedan2", "つまり課税口座なら0円だったので、差は81260円。", anim=1.6,
         puchun=True, se="don", face="surprised", speed=1.0, intonation=1.25),
    Unit("nedan2", "だから時間をまたいでも、やはり引けないのだ。", anim=0.0, speed=1.1),
    Unit("san1", "では、その3年ぶんとは何なのだろうか。", anim=1.8, speed=1.15),
    Unit("san1", "たとえば1年目の損40万円を、繰り越したとする。", anim=0.0, speed=1.1),
    Unit("san1", "その2年目から4年目の利益からは、引けるのだ。", anim=0.0, speed=1.1),
    Unit("san2", "でも5年目の利益からは、もう引けないのだ。", anim=1.8,
         face="troubled", speed=1.1),
    Unit("san2", "だからその5年目の利益10万円は、まるごと課税される。", anim=0.0, speed=1.05),
    Unit("san2", "その税金が、20315円になるのだ。", anim=0.0, speed=1.1),
    Unit("shinkoku", "ちなみに繰越控除を使うには、確定申告が要るのだ。", anim=1.4, speed=1.1),
    Unit("shinkoku", "その確定申告は、損が出た年から毎年出し続けるのだ。", anim=0.0, speed=1.05),
    Unit("shinkoku", "では、この不利はいくらまで効くのだろうか。", anim=0.0, speed=1.15),

    # ===== 第5章 いくらまで効くのか
    Unit("ch5", "では第5章。この不利は、いくらまで効くのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("onaji", "まずここまでの例は、損も利益も20万円だった。", anim=1.4, speed=1.1),
    Unit("onaji", "では、額がちがうとどうなるのだろうか。", anim=0.0, speed=1.15),
    Unit("pat1", "たとえばNISAで30万円の損、課税口座で10万円の利益。", anim=1.6, speed=1.05),
    Unit("pat1", "その引ける相手は、10万円しかないのだ。", anim=0.0, speed=1.1),
    Unit("pat1", "だから差は、10万円の20.315%で20315円。", anim=0.0, speed=1.05),
    Unit("pat2", "逆に、損10万円で利益30万円ならどうなるか。", anim=1.6, speed=1.1),
    Unit("pat2", "その引ける損が、10万円しかないのだ。", anim=0.0, speed=1.1),
    Unit("pat2", "だから差は、やはり20315円になるのだ。", anim=0.0, speed=1.1),
    Unit("kousiki", "つまり引けなくなるのは、小さいほうの額までなのだ。", anim=1.6,
         face="smug", se="pop", speed=1.05, intonation=1.2),
    Unit("nashi", "では、課税口座に利益が無い年はどうなるか。", anim=1.6, speed=1.15),
    Unit("nashi", "その引く相手がいないので、差は0円なのだ。", anim=0.0, speed=1.1),
    Unit("nashi", "だからNISAで100万円損しても、差は0円のまま。", anim=0.0, speed=1.05),
    Unit("sorotta", "つまり不利になるのは、2つがそろった年だけなのだ。", anim=1.4, speed=1.05),
    Unit("sorotta", "その2つとは、NISAの損と課税口座の利益なのだ。", anim=0.0, speed=1.05),
    Unit("sannen", "では、同じ年が3年続いたらどうなるか。", anim=1.6, speed=1.15),
    Unit("sannen", "その1年目に40630円、2年目にも40630円。", anim=0.0, speed=1.05),
    Unit("sannen", "そして3年目にも、また40630円かかるのだ。", anim=0.0, speed=1.1),
    Unit("sannen2", "つまり合わせると、3年で121890円になるのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.3, speed=1.0, intonation=1.25),
    Unit("sannen2", "その1年ぶんは小さいが、積もると効いてくるのだ。", anim=0.0, speed=1.05),
    Unit("ch5_out", "だからその年は、小さいほうの額の20.315%を余分に払う。", anim=1.6,
         puchun=True, se="don", speed=1.0, intonation=1.2),
    Unit("ch5_out", "では、これにどう備えればいいのだろうか。", anim=0.0, speed=1.15),

    # ===== 第6章 どうすればいいのか
    Unit("ch6", "では第6章。この不利に、どう備えるのか。", anim=1.6,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("ch6", "その備えとは、損益通算と繰越控除の使い方なのだ。", anim=0.0, speed=1.05),
    Unit("te1", "まず1つめ。損益通算が使えるのは、同じ年の中だけ。", anim=1.6, speed=1.05),
    Unit("te1", "その年をまたぐには、繰越控除が要るのだ。", anim=0.0, speed=1.15),
    Unit("te2", "そして2つめ。どちらも確定申告をして使うのだ。", anim=1.6, speed=1.1),
    Unit("te2", "その源泉徴収ありの口座でも、申告が要るのだ。", anim=0.0, speed=1.1),
    Unit("te3", "そして3つめ。NISAで売っても、税の話は動かない。", anim=1.6, speed=1.05),
    Unit("te3", "その課税口座で売るのとは、意味がちがうのだ。", anim=0.0, speed=1.1),
    Unit("waku1", "そして4つめ。売っても、枠が戻るのは翌年なのだ。", anim=1.6, speed=1.05),
    Unit("waku2", "たとえば100万円で買って、80万円で売ったとする。", anim=1.6, speed=1.05),
    Unit("waku2", "その年に、枠は戻ってこないのだ。", anim=0.0, speed=1.15),
    Unit("waku2", "そして翌年に戻るのは、買った値段の100万円ぶん。", anim=0.0, speed=1.05),
    Unit("erabenai", "そして5つめ。どちらの口座で損が出るかは、選べない。", anim=1.6,
         speed=1.05),
    Unit("erabenai", "その同じ商品を持っていても、口座は分かれているのだ。", anim=0.0,
         speed=1.05),
    Unit("erabenai", "だからあとから、振り替えることもできないのだ。", anim=0.0, speed=1.1),
    Unit("ch6_out", "つまり使うかどうかではなく、いつ効くかを知っておく。", anim=1.4,
         face="smug", speed=1.05, intonation=1.2),

    # ===== 締め
    Unit("matome", "では、3つの場合を表にまとめるのだ。", anim=1.8, speed=1.15),
    Unit("matome", "まず損だけの年は、どちらも0円で同じ。", anim=0.0, speed=1.1),
    Unit("matome2", "そして利益だけの年は、40630円の得になる。", anim=1.4,
         face="happy", speed=1.1),
    Unit("matome3", "そして損と利益がある年は、40630円の損になる。", anim=1.4,
         face="troubled", speed=1.1),
    Unit("taishou", "つまり得も損も、同じ40630円なのだ。", anim=1.6,
         puchun=True, se="don", speed=1.05, intonation=1.25),
    Unit("taishou", "その向きがちがうだけで、額は同じなのだ。", anim=0.0, speed=1.1),
    Unit("jibun", "では、自分の場合はどう出せばいいのか。", anim=1.4, face="happy",
         speed=1.15),
    Unit("jibun", "まずNISAの損と、課税口座の利益をならべるのだ。", anim=0.0, speed=1.1),
    Unit("jibun", "その小さいほうに、0.20315を掛けるのだ。", anim=0.0, speed=1.05),
    Unit("jibun2", "たとえば損4万円の年を、考えてみるのだ。", anim=1.6, speed=1.1),
    Unit("jibun2", "その同じ年の課税口座の利益が、12万円だとする。", anim=0.0, speed=1.05),
    Unit("jibun2", "その小さいほうは、損の4万円のほうなのだ。", anim=0.0, speed=1.1),
    Unit("jibun3", "だから余分に払うのは、8126円になるのだ。", anim=1.6,
         se="pop", speed=1.05, intonation=1.2),
    Unit("jisan", "ちなみにこの動画の金額は、すべて今の制度で計算したのだ。", anim=1.4,
         speed=1.05),
    Unit("jisan", "その計算に使ったのは、税率と足し算と掛け算だけ。", anim=0.0, speed=1.05),
    Unit("kawaru", "ただし制度は、毎年変わるのだ。", anim=1.4, speed=1.15),
    Unit("kawaru", "その制度は、2026年8月時点の内容なのだ。", anim=0.0, speed=1.15),
    Unit("kawaru", "だから使うときには、そのときの制度を確かめてほしいのだ。", anim=0.0,
         speed=1.05),
    Unit("shime", "つまりNISAで売っても、税金の話は動かないのだ。", anim=1.4,
         speed=1.05, intonation=1.2),
    Unit("shime", "だから売るかどうかは、税金と切り離して決める。", anim=0.0,
         speed=1.05, intonation=1.2),
    Unit("shime", "その判断に、税金を持ちこまなくていいのだ。", anim=0.0, pad=0.2,
         face="smug", speed=1.05, intonation=1.15, pitch=-0.03),
]

# チャプター(概要欄に貼る)。章題ではなく**問い**にする(longform-design §4a)
CHAPTER_MARKS_TITLES = [
    "NISAで損したら、いくら損するのか",
    "第1章 NISAは、お金を増やしてくれるのか",
    "第2章 そもそも株の税金は、どう決まるのか",
    "第3章 NISAの損は、利益から引けるのか",
    "第4章 来年の利益からは、引けるのか",
    "第5章 この不利は、いくらまで効くのか",
    "第6章 この不利に、どう備えるのか",
    "まとめ 3つの場合と、自分の場合の出し方",
]
# 章の先頭ユニットは台本から拾う。手で添字を書くと、台本を直したとき必ずずれる
_first = {}
for _i, _u in enumerate(UNITS):
    _first.setdefault(_u.scene, _i)
CHAPTER_MARKS = list(zip(
    [0] + [_first[f"ch{k}"] for k in range(1, 7)] + [_first["matome"]],
    CHAPTER_MARKS_TITLES))
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
