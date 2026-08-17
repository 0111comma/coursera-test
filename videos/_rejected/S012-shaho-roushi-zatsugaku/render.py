#!/usr/bin/env python3
"""S012: 会社は460万円出しているのに、手取りは315万円。差の145万円はどこへ行くのか。

ループ66でユーザー判定「S12面白くない」。診断:
  旧版のオチは「社会保険料は会社も同じ額を払っている」だった。
  事実として正しいが**豆知識**で、見た人の何も変わらない(実害がない)。
  同じ計算から、実害のある問いが1つ取れる:
  **会社が出した額のうち、自分の手元にいくら残るのか。** 答えは69%。

この動画が答える問い(1つだけ):
  会社があなたに出している額のうち、手元に残るのはいくらか。→ 69%(145万円が差)

鎖(L1):
  400万円 −59万円 −26万円 = 315万円(手取り)
  400万円 +60万円 = 460万円(会社の支出)
  460万円 −315万円 = 145万円 → 315/460 = 69%

図の型(figure-forms.md):
- 主役は「出した額」と「残る額」の全体と部分 → 固有シーン nokoru()。
  460万円を1本の帯にし、そのうち手取りぶんだけを塗る。
  差が「別の棒」ではなく「同じ帯の中の残り」に見えることが要点
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
BADGE = "年収400万円・東京都の概算"

INCOME = 4_000_000
ME = INCOME * (0.183 / 2 + 0.0985 / 2 + 0.0023 / 2 + 0.005)
CO = INCOME * (0.183 / 2 + 0.0985 / 2 + 0.0023 / 2 + 0.0085)
KAISHA = INCOME + CO
TEDORI = 3_154_429        # verify.py が計算した手取り
assert round(ME / 10_000) == 59 and round(CO / 10_000) == 60, "verify.pyと不一致"
assert round(KAISHA / 10_000) == 460
assert round(TEDORI / 10_000) == 315
assert round((KAISHA - TEDORI) / 10_000) == 145
assert round(TEDORI / KAISHA * 100) == 69

SURFACE_INK = "#1a1a19"   # 帯の中に置く文字(背景色で抜く)


def nokoru(step):
    """固有シーン: 会社が出した460万円という1本の帯と、そのうち手元に残る部分。

    棒を2本並べると「別々の額」に見えてしまう。ここで見せたいのは
    **同じ1つの額の、内訳**なので、帯は1本にして中を塗り分ける。
    塗られていない部分の長さが、そのまま差の145万円になる。

    step=1 帯と手取りぶん / step=2 差を出す / step=3 割合を出す
    """
    X0, X1 = 0.10, 0.90
    Y, H = 0.600, 0.078
    r = TEDORI / KAISHA                    # 0.6856…
    xm = X0 + (X1 - X0) * r

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "会社が出した460万円の中身", ha="center",
                 color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        # 帯ぜんぶ = 会社が出した額
        fig.patches.append(Rectangle((X0, Y), X1 - X0, H, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.55))
        fig.text(0.50, Y + H + 0.034, "会社が出す 460万円", ha="center", va="center",
                 color=INK_2, fontsize=30)
        # そのうち手元に残る部分
        fig.patches.append(Rectangle((X0, Y), (xm - X0) * a, H, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        if a > 0.5:
            fig.text((X0 + xm) / 2, Y + H / 2, "手取り 315万円", ha="center", va="center",
                     color=SURFACE_INK, fontsize=31, fontweight="black")
        if step >= 2:
            b = sc.clamp01(t * 2.2 - 0.3)
            fig.patches.append(Rectangle((xm, Y), (X1 - xm), H, transform=fig.transFigure,
                                         facecolor=EMPH, edgecolor="none", alpha=0.95 * b))
            fig.text((xm + X1) / 2, Y - 0.040, "差 145万円", ha="center", va="center",
                     color=EMPH, fontsize=30, alpha=b,
                     path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=2))
        if step >= 3:
            c = sc.clamp01(t * 2 - 0.3)
            fig.text(0.50, 0.762, "手元に残るのは 69%", ha="center", va="center",
                     color=INK, fontsize=46, alpha=c,
                     path_effects=stroke_fx(INK, outline=outline_for(46), fatten=2.5))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("会社は460万円", "手取りは315万円", BADGE, BRAND, size=86, sub_fs=44),
    "nazo__cover": sc.cover("会社が出した額のうち、手元に残るのは?", "69%",
                            "差は145万円", "年収400万円で計算", BRAND, main_size=200),
    "nenshu": sc.card("だれで計算するか", "年収400万円の人", "(東京都・介護保険なしの概算)",
                      BADGE, BRAND, main_size=52, head_fs=36),
    "jiten": sc.card("いつの制度か", "2026年度の料率", "(制度が変わると額も変わる)",
                     BADGE, BRAND, main_size=56, head_fs=36),
    "hikareru": sc.card("明細でいちばん大きい行", "社会保険料", "(年金・健康保険・雇用保険)",
                        BADGE, BRAND, main_size=62, head_fs=34),
    "hoken": sc.bars2("その人の年間の金額",
                      ("年収", 400, "400万円"),
                      ("社会保険料", 59, "59万円"),
                      BADGE, BRAND, ymax=430),
    "zei": sc.bars2("さらに引かれるもの",
                    ("社会保険料", 59, "59万円"),
                    ("所得税と住民税", 26, "26万円"),
                    BADGE, BRAND, ymax=66),
    "tedori": sc.bars2("引かれたあとに残る額",
                       ("年収", 400, "400万円"),
                       ("手取り", 315, "315万円"),
                       BADGE, BRAND, ymax=430),
    "meisai": sc.card("ここまでは", "明細に載る", "(引かれた額が書いてある)",
                      BADGE, BRAND, main_size=62, head_fs=34),
    "toi": sc.quiz("ここからが本題", "会社はいくら", "出しているのか?", "", BADGE, BRAND),
    "kaisha": sc.card("もう一人いる", "会社", "(あなたと同額を、別に負担している)",
                      BADGE, BRAND, main_size=84, head_fs=34,
                      ask="あなたの明細、見たことある?"),
    "sessuu": sc.card("この仕組みの名前", "労使折半", "(ろうしせっぱん・半分ずつ)",
                      BADGE, BRAND, main_size=72, head_fs=34),
    "kaishagaku": sc.bars2("社会保険料を払っている人",
                           ("あなた", 59, "59万円"),
                           ("会社", 60, "60万円"),
                           BADGE, BRAND, ymax=66),
    "jinkenhi": sc.bars2("会社から見た年間の費用",
                         ("あなたの年収", 400, "400万円"),
                         ("会社が出す額", 460, "460万円"),
                         BADGE, BRAND, gap="差 60万円", ymax=480),
    "nokoru1": nokoru(1),
    "nokoru2": nokoru(2),
    "nokoru3": nokoru(3),
    "shime": sc.hero("明細に見えるのは", "その一部", BADGE, BRAND, size=92, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行:
#   入口=給料(全員が持つ明細。専門語ではない)
#   予想「引かれてるのは、明細に書いてある額だけ」
#   → 結論「会社が出した460万円のうち、手元に残るのは315万円=69%」
#   オチ=自分の人件費と手取りの差が145万円だと分かる(見方の変更)
UNITS = [
    Unit("nazo", "会社はあなたに460万円。でも手取りは315万円。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("nenshu", "まず、年収400万円の人で見るのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("jiten", "これは2026年度の料率で計算した。", anim=1.2, speed=1.15),
    Unit("hikareru", "その人の給料から、社会保険料が引かれる。", anim=1.4, speed=1.15),
    Unit("hoken", "その社会保険料は、年59万円。", anim=1.4, speed=1.15),
    Unit("zei", "さらに所得税と住民税で、年26万円。", anim=1.4, speed=1.15),
    Unit("tedori", "だから手取りは、さっきの315万円。", anim=1.4, speed=1.15),
    Unit("meisai", "つまりここまでは、明細で分かるのだ。", anim=1.4, speed=1.15),
    Unit("toi", "では、会社はいくら出しているのか。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kaisha", "実は社会保険料を、会社も払っている。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("sessuu", "これを【労使折半】、半分ずつというのだ。", anim=1.4, speed=1.15),
    Unit("kaishagaku", "その会社の負担も、年60万円ある。", anim=1.4, speed=1.15),
    Unit("jinkenhi", "つまり年収400万円の人に、460万円。", anim=1.4, face="surprised",
         speed=1.1, intonation=1.2),
    Unit("nokoru1", "その460万円のうち、手取りは315万円。", anim=1.6, speed=1.1),
    Unit("nokoru2", "差の145万円は、税と社会保険料なのだ。", anim=1.6,
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("nokoru3", "会社が出した額の、69%しか残らない。", anim=1.6, face="surprised",
         speed=1.1, intonation=1.25),
    Unit("shime", "明細に見えるのは、その一部なのだ。", anim=1.0, pad=0.15,
         face="smug", speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S012.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
