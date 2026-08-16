#!/usr/bin/env python3
"""S015: 給料から引かれている住民税は、去年の所得で決まっている。

企画書は plan.md。基準作 S011 の8行を埋めてから作った。

P-0(persona.md): ショートは選ばれない。興味ゼロの人に押し込まれる。
入口は「給料から引かれる住民税」= 明細を見たことがあれば必ず載っている物(F5)。

図の型(figure-forms.md):
- 主役は「去年の年収」と「今年払う税」が別の年にあること → 固有シーン okure()。
  横位置=時間。左に去年、右に今年を置き、矢印で結ぶ。
  会社を辞めた場合は右の年の収入をゼロにしても、税の箱はそのまま残る。
  時間のずれが横の位置だけで分かる(Tversky の一致性)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, MUTED_BAR, EMPH, SURFACE,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年収400万円・独身・東京都の概算"

TOTAL = 176_700     # 年の住民税(verify.py)
assert int(TOTAL / 10_000) == 17, "verify.pyと不一致"


def okure(show_tax=False, retired=False, note=""):
    """固有シーン: 去年の年収が、今年の住民税になる。

    横位置=時間。左の箱が「去年の年収」、右の箱が「今年はらう住民税」。
    retired にすると右の年の収入がゼロになるが、税の箱は消えない。
    「収入がない年に、去年ぶんの請求が来る」を位置だけで見せる。
    """
    YB, HB = 0.690, 0.085          # 箱の下端と高さ
    LX, RX, BW = 0.14, 0.56, 0.30  # 左箱・右箱の左端と幅

    def painter(fig, t):
        from matplotlib.patches import Rectangle, FancyArrow
        fig.text(0.5, 0.905, "去年の年収が、今年の住民税になる", ha="center",
                 color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.2)
        for x, head in ((LX, "去年"), (RX, "今年")):
            fig.text(x + BW / 2, YB + HB + 0.030, head, ha="center", va="center",
                     color=INK_2, fontsize=29)
        # 左: 去年の年収
        fig.patches.append(Rectangle((LX, YB), BW, HB, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
        fig.text(LX + BW / 2, YB + HB / 2, "年収400万円", ha="center", va="center",
                 color=SURFACE, fontsize=33, fontweight="black")
        # 右: 今年はらう住民税
        if show_tax:
            fig.add_artist(FancyArrow(0.455, YB + HB / 2, 0.085, 0, width=0.004,
                                      head_width=0.016, head_length=0.020,
                                      transform=fig.transFigure, color=MUTED,
                                      alpha=0.8 * a, length_includes_head=True))
            fig.patches.append(Rectangle((RX, YB), BW, HB * a, transform=fig.transFigure,
                                         facecolor=EMPH, edgecolor="none", alpha=0.95))
            fig.text(RX + BW / 2, YB + HB * a / 2, "住民税17万円", ha="center", va="center",
                     color=SURFACE, fontsize=33, alpha=a, fontweight="black")
        if retired:
            fig.text(RX + BW / 2, YB - 0.038, "今年の収入はゼロ", ha="center", va="center",
                     color=EMPH, fontsize=28, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(28), fatten=1.8))
        if note:
            fig.text(0.5, 0.487, note, ha="center", va="center", color=EMPH,
                     fontsize=34, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("その住民税", "去年の給料の分", BADGE, BRAND, size=96, sub_fs=42),
    "nazo__cover": sc.cover("その住民税、なぜこの額?", "去年の分",
                            "辞めた翌年も請求が来る", "はじめての人向け", BRAND, main_size=140),
    "nenshu": sc.card("だれで計算するか", "年収400万円の人", "(独身・東京都・扶養なしの概算)",
                      BADGE, BRAND, main_size=52, head_fs=34),
    "gaku": sc.bars2("その人の1年ぶんの金額",
                     ("年収", 400, "400万円"),
                     ("住民税", 17.67, "17万円"),
                     BADGE, BRAND, ymax=430),
    "maitsuki": sc.card("毎月の給料からは", "約1万4700円", "(12ヶ月に分けて天引きされる)",
                        BADGE, BRAND, main_size=62, head_fs=34),
    "kyonen": okure(show_tax=True),
    "toha": sc.card("その住民税とは", "住む街に払う税", "(市区町村と都道府県に分かれる)",
                    BADGE, BRAND, main_size=58, head_fs=34),
    "rokugatsu": sc.card("金額が決まるのは", "毎年6月", "(前の年の1月〜12月の所得で計算)",
                         BADGE, BRAND, main_size=76, head_fs=34,
                         ask="あなたの去年の年収、いくら?"),
    "zure": okure(show_tax=True),
    "toi": sc.quiz("ここからが本題", "会社を辞めた年は", "どうなる?", "", BADGE, BRAND),
    "kubi": okure(show_tax=True, retired=True),
    "gaku2": okure(show_tax=True, retired=True),
    "bunkatsu": sc.stack("自分で払う場合", 4, "四角ひとつが1回ぶん", "6月から4回",
                         BADGE, BRAND, cols=4),
    "ikkai": sc.card("1回あたりの額は", "およそ4万4千円", "(年の住民税を4回に分けた額)",
                     BADGE, BRAND, main_size=58, head_fs=34),
    "harau": okure(show_tax=True, retired=True, note="収入なしでも来る"),
    "dake": sc.card("この話が効く人", "辞めただけでない", "(収入が減った人にも同じことが起きる)",
                    BADGE, BRAND, main_size=62, head_fs=34),
    "sagatta": sc.bars2("収入が減っても",
                        ("去年の年収", 400, "400万円"),
                        ("今年の年収", 240, "下がった"),
                        BADGE, BRAND, ymax=430),
    "mama": okure(show_tax=True, note="税金は去年のまま"),
    "shime": sc.hero("住民税の正体", "去年の請求書", BADGE, BRAND, size=96, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行は plan.md 参照:
#   入口=給料から引かれる住民税(明細に必ず載っている。専門語ではない)
#   予想「住民税は今の給料にかかっている」→ 結論「去年の給料で決まっている」
#   オチ=実害(辞めた翌年、収入ゼロでも17万円の請求)+ 見方の変更(去年の請求書)
UNITS = [
    Unit("nazo", "給料から引かれる住民税は、去年の分なのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("nenshu", "まず、年収400万円の人で見るのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("gaku", "その人がはらう住民税は、年17万円。", anim=1.4, speed=1.15),
    Unit("maitsuki", "つまり毎月の給料からは、約1万4700円。", anim=1.4, speed=1.15),
    Unit("kyonen", "その額は、去年の年収で決まるのだ。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.15),
    Unit("toha", "その住民税とは、住む街に払う税金。", anim=1.4, speed=1.15),
    Unit("rokugatsu", "その計算は6月に決まり、6月から引かれる。", anim=1.4, speed=1.15),
    Unit("zure", "つまり、いつも1年おくれなのだ。", anim=1.4, speed=1.15),
    Unit("toi", "では、会社を辞めた年はどうなる?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kubi", "その年の収入がゼロでも、請求は来る。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("gaku2", "その額が、さっきの17万円なのだ。", anim=1.4, speed=1.15),
    Unit("bunkatsu", "しかも6月から、4回に分けて届くのだ。", anim=1.4, speed=1.15),
    Unit("ikkai", "つまり1回あたり、およそ4万4千円。", anim=1.4, speed=1.15),
    Unit("harau", "その17万円を、収入がない年にはらう。", anim=1.6, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("dake", "でもこれは、辞めた人だけの話ではない。", anim=1.4, speed=1.15),
    Unit("sagatta", "たとえば給料が下がっても、同じなのだ。", anim=1.4, speed=1.15),
    Unit("mama", "その年の税金は、去年のままだから。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("shime", "住民税は、去年の請求書なのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S015.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
