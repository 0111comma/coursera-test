#!/usr/bin/env python3
"""S012: 4月から6月の残業は、9月から1年ぶん引かれる。

企画書は plan.md、数値は verify.py。

この動画が答える問い(1つだけ):
  4月から6月に残業すると、手取りはいくら減るのか。それは取り返せるのか。
答え:
  年6万8112円ひかれて、増える年金は年2631円。取り返すのに26年 = 91歳。

この人の欲求(ループ67):
  **残業代で手取りを増やしたい。でも知らないうちに引かれるのは嫌だ。**
  前の企画(会社も同じ額を払っている / 会社の460万円)は会社の財布の話で、
  視聴者の身に何も起きなかった。同じ社会保険料でも、こちらは自分の手取りが動く。

図の型(figure-forms.md):
- 主役は「いつ決まって、いつ効くか」という**時間の対応** → 固有シーン koyomi()
- 損得の判定は**自分の寿命の上の点** → 固有シーン nenrei()(S011で合格した型)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "標準報酬月額34万→38万・東京都の概算"

SURFACE_INK = "#1a1a19"

# verify.py と同じ計算をここでも回して、画面の数字とずれていないことを確かめる
SA = 40_000
TSUKI = SA * (0.183 / 2 + 0.0985 / 2 + 0.0023 / 2)
NENKAN = TSUKI * 12
NENKIN = SA * 5.481 / 1000 * 12
assert round(SA * 0.183 / 2) == 3_660
assert round(SA * 0.0985 / 2) == 1_970
assert round(TSUKI) == 5_676 and round(NENKAN) == 68_112
assert round(NENKIN) == 2_631
assert round(65 + NENKAN / NENKIN) == 91


def koyomi(step):
    """固有シーン: 12ヶ月の暦の上に「決まる期間」と「効く期間」を並べる。

    この動画の要は「4〜6月に決まって、9月から1年効く」という**時間のズレ**なので、
    位置(横軸=月)そのものが意味を持つ形にする。
    step=1 4〜6月を光らせる / step=2 9月からの1年を帯で出す
    """
    X0, X1 = 0.10, 0.90
    Y, H = 0.640, 0.070
    W = (X1 - X0) / 12

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "いつ決まって、いつ効くのか", ha="center",
                 color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        for k in range(12):
            m = k + 1
            on = step >= 1 and m in (4, 5, 6)
            x = X0 + W * k
            fig.patches.append(Rectangle((x + 0.004, Y), W - 0.008, H,
                                         transform=fig.transFigure,
                                         facecolor=GOLD if on else MUTED_BAR,
                                         edgecolor="none",
                                         alpha=(0.95 * a) if on else 0.35))
            fig.text(x + W / 2, Y + H / 2, str(m), ha="center", va="center",
                     color=SURFACE_INK if on else INK_2, fontsize=24,
                     fontweight="black" if on else "normal")
        fig.text((X0 + X1) / 2, Y + H + 0.036, "決まる期間",
                 ha="center", va="center", color=GOLD, fontsize=30, alpha=a,
                 path_effects=stroke_fx(GOLD, outline=outline_for(30), fatten=1.8))
        if step >= 2:
            b = sc.clamp01(t * 2.2 - 0.3)
            # 9月(k=8)から翌年8月まで = 12ヶ月ぶんを、暦の下に1本の帯で
            fig.patches.append(Rectangle((X0 + W * 8, Y - 0.062), W * 4, 0.040,
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=0.95 * b))
            fig.text((X0 + X1) / 2, Y - 0.108, "ひかれる期間",
                     ha="center", va="center", color=EMPH, fontsize=30, alpha=b,
                     path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=1.8))
            fig.text((X0 + X1) / 2, Y - 0.180, "9月から翌年8月",
                     ha="center", va="center", color=INK, fontsize=34, alpha=b,
                     path_effects=stroke_fx(INK, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


def nenrei(step):
    """固有シーン: 65歳から伸びる帯の上に、平均寿命と「取り返す年齢」を打つ。

    S011(年金)でご合格をいただいた図と同じ型。
    **損得が自分の寿命の上で決まる**ことを、位置で見せる。
    step=1 65歳から81歳まで / step=2 91歳の点を打つ
    """
    X0, X1 = 0.10, 0.90
    Y, H = 0.600, 0.062
    A0, A1 = 65, 95

    def px(age):
        return X0 + (X1 - X0) * (age - A0) / (A1 - A0)

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "何歳で取り返せるのか", ha="center", color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        fig.patches.append(Rectangle((X0, Y), X1 - X0, H, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.35))
        # 65歳から平均寿命81歳までに受け取れる分
        fig.patches.append(Rectangle((X0, Y), (px(91) - X0) * a, H,
                                     transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        # 図に出す数値は、声でも言うものだけにする(規則6)。
        # 平均寿命81歳と、そこまでの受取額42,094円は概要欄に回した
        for age, label in ((65, "65歳"), (91, "91歳")):
            fig.text(px(age), Y - 0.040, label, ha="center", va="center",
                     color=INK_2, fontsize=27, alpha=a)
        fig.text((X0 + px(91)) / 2, Y + H + 0.038, "年金を受け取る期間",
                 ha="center", va="center", color=INK_2, fontsize=27, alpha=a)
        if step >= 2:
            b = sc.clamp01(t * 2.2 - 0.3)
            fig.patches.append(Rectangle((px(91) - 0.006, Y - 0.020), 0.012, H + 0.040,
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=0.95 * b))
            fig.text((X0 + X1) / 2, 0.500, "ここで、やっと並ぶ",
                     ha="center", va="center", color=INK, fontsize=40, alpha=b,
                     path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2.4))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


def tsumi():
    """固有シーン: 厚生年金と健康保険を積み上げて、合計の高さを作る。

    「合わせて5676円」を文字カードで出すと、足し算が画面に無い。
    2つの棒を**積む**ことで、合計がその2つでできていることを高さで見せる。
    """
    X, W = 0.50, 0.30
    Y0, HMAX = 0.545, 0.205
    TOTAL = 5_676

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "毎月ふえる額の内訳", ha="center", color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        h1 = HMAX * (3_660 / TOTAL) * a
        h2 = HMAX * (1_970 / TOTAL) * a
        fig.patches.append(Rectangle((X - W / 2, Y0), W, h1, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        fig.patches.append(Rectangle((X - W / 2, Y0 + h1 + 0.004), W, h2,
                                     transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
        if a > 0.5:
            fig.text(X, Y0 + h1 / 2, "3660円", ha="center", va="center",
                     color=SURFACE_INK, fontsize=30, fontweight="black")
            fig.text(X, Y0 + h1 + h2 / 2 + 0.004, "1970円", ha="center", va="center",
                     color=INK, fontsize=30, fontweight="black")
        fig.text(X, Y0 + HMAX + 0.046, "5676円", ha="center", va="center",
                 color=INK, fontsize=50, alpha=sc.clamp01(t * 2 - 0.5),
                 path_effects=stroke_fx(INK, outline=outline_for(50), fatten=2.6))
        fig.text(X, Y0 - 0.040, "厚生年金 + 健康保険", ha="center", va="center",
                 color=INK_2, fontsize=27, alpha=a)
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("4月〜6月の残業", "※ 標準報酬月額34万→38万で計算", BADGE, BRAND,
                    size=88, sub_fs=34),
    "nazo__cover": sc.cover("残業したのに、手取りが減るのはいつ?", "9月",
                            "決めたのは4〜6月", "会社員向け", BRAND, main_size=210),
    "riyuu": sc.card("減る理由は", "社会保険料", "(2026年度の料率で計算)",
                     BADGE, BRAND, main_size=76, head_fs=36),
    "koyomi1": koyomi(1),
    "koyomi2": koyomi(2),
    "rei": sc.card("たとえば", "ふだん34万円の人", "(標準報酬月額の等級で決まる)",
                   BADGE, BRAND, main_size=66, head_fs=36),
    "heikin": sc.bars2("4月〜6月の平均",
                       ("ふだん", 34, "34万円"),
                       ("残業した年", 38, "38万円"),
                       BADGE, BRAND, gap="差 4万円", ymax=42),
    "sa": sc.card("かかる対象", "4万円ぶん", "(9月から翌年8月まで)",
                  BADGE, BRAND, main_size=104, head_fs=36),
    "kosei": sc.bars2("毎月ふえる額",
                      ("厚生年金", 3660, "3660円"),
                      ("健康保険", 1970, "1970円"),
                      BADGE, BRAND, ymax=4200),
    "kenko": sc.bars2("毎月ふえる額",
                      ("厚生年金", 3660, "3660円"),
                      ("健康保険", 1970, "1970円"),
                      BADGE, BRAND, ymax=4200),
    "gokei": tsumi(),
    "nenkan": sc.hero("1年で 6万8112円", "※ 5676円 × 12", BADGE, BRAND,
                      size=88, sub_fs=36),
    "nenkin": sc.card("見返りもある", "将来の年金", "(厚生年金の報酬比例部分)",
                      BADGE, BRAND, main_size=82, head_fs=36,
                      ask="あなたの明細、9月から変わってた?"),
    "nenkingaku": sc.hero("年 2631円", "※ 亡くなるまで、毎年", BADGE, BRAND,
                          size=140, sub_fs=36),
    "warizan": sc.reveal("26年", "取り返すのにかかる年数",
                         "6万8112円 ÷ 2631円", BADGE, BRAND, size=150),
    "nenrei1": nenrei(1),
    "nenrei2": nenrei(2),
    "tegata": sc.card("見返りはもう1つ", "手当もふえる",
                      "(傷病手当金・出産手当金も標準報酬月額で決まる)",
                      BADGE, BRAND, main_size=96, head_fs=36,
                      ask="あなたの明細、9月から変わってた?"),
    # 尺の都合で「傷病手当金・出産手当金もふえる」はナレーションに入れられなかった。
    # 判定を和らげる材料なので、締めの画面と概要欄・固定コメントに必ず置く(W8)
    "shime": sc.hero("寄せるなら7月から", "※ 傷病手当金・出産手当金もふえます",
                     BADGE, BRAND, size=96, sub_fs=30),
}

# ネタ選定ゲート(F1/F3/F4/F5):
#   欲求「残業代で手取りを増やしたい。知らないうちに引かれるのは嫌だ」
#   予想「残業した月のぶんが引かれるだけでしょ」
#   → 結論「4〜6月で決まった保険料が、9月から1年ひかれる。年6万8112円」
#   決められること「残業を4〜6月に寄せるか、7月以降に寄せるか」
UNITS = [
    Unit("nazo", "4月から6月に残業すると、手取りが減るのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("riyuu", "その正体は、社会保険料なのだ。", anim=1.4, speed=1.1),
    Unit("koyomi1", "その社会保険料は、いま4月から6月で決まる。", anim=1.6, speed=1.05),
    Unit("koyomi2", "そして次の9月から、ひかれはじめるのだ。", anim=1.6,
         face="surprised", se="impact", se_at=0.34, speed=1.05, intonation=1.2),
    Unit("koyomi2", "それが、まる1年つづくのだ。", anim=0.0, speed=1.1),
    Unit("rei", "たとえば月34万円の人が、残業したとする。", anim=1.4, speed=1.05),
    Unit("heikin", "すると4月から6月は、平均38万円になった。", anim=1.6, speed=1.05),
    Unit("sa", "その差4万円に、厚生年金と健康保険がかかる。", anim=1.4, speed=1.05),
    Unit("kosei", "まず厚生年金が、毎月3660円ふえる。", anim=1.6, speed=1.1),
    Unit("kenko", "そして健康保険が、毎月1970円ふえる。", anim=0.0, speed=1.1),
    Unit("gokei", "合わせて毎月、5676円ふえるのだ。", anim=1.4, speed=1.1),
    Unit("nenkan", "それが1年で、6万8112円になるのだ。", anim=1.6,
         puchun=True, se="don", face="surprised", speed=1.05, intonation=1.2),
    Unit("nenkin", "でも65歳から、年金がふえるのだ。", anim=1.4, face="happy", speed=1.1),
    Unit("nenkingaku", "その額は、毎年2631円なのだ。", anim=1.4, speed=1.05),
    Unit("warizan", "6万8112円を2631円で割ると、26年。", anim=1.6,
         face="troubled", speed=1.0, intonation=1.2),
    Unit("nenrei1", "つまり65歳から、26年かかるのだ。", anim=1.6, speed=1.1),
    Unit("nenrei2", "だから、91歳まで生きる計算なのだ。", anim=1.6,
         puchun=True, se="don", speed=1.0, intonation=1.25),
    Unit("shime", "その残業を選べるなら、7月からなのだ。", anim=1.0, pad=0.15,
         face="smug", speed=1.05, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S012.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
