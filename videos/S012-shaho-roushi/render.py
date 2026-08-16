#!/usr/bin/env python3
"""S012: 給料から引かれる社会保険料は、会社も同じ額を払っている。

基準作は S011(年金)。プレイブックの8行を埋めてから作った:
  入口=給料(全員が持っている明細) / 予想「引かれてるのはこの額だけ」
  → 結論「同じ額をもう一人分、会社が払っている」
  オチ=自分の人件費が460万円だと分かる(見方の変更)

図の型(figure-forms.md):
- 主役は「見えている負担」と「見えていない負担」の対称 → 固有シーン meisai()。
  上=明細に載る本人負担、下=載らない会社負担。同じ幅で向かい合わせ、
  下側を後から出すことで「もう半分あった」を形で見せる
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
assert round(ME / 10_000) == 59 and round(CO / 10_000) == 60, "verify.pyと不一致"
assert round((INCOME + CO) / 10_000) == 460


def meisai(show_company=False, show_total=False):
    """固有シーン: 明細に載る負担と、載らない負担。

    上の帯=あなたが引かれている額(明細に載る)。下の帯=会社が払っている額(載らない)。
    同じ幅・同じ縦位置の基準線で向かい合わせ、下を後から出す。
    「見えていないほうが同じだけある」ことを、形の対称で見せる。
    """
    Y = 0.700          # 明細の帯
    H = 0.070

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "社会保険料は、だれが払うのか", ha="center",
                 color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        # 上: 本人負担(明細に載る)
        fig.patches.append(Rectangle((0.17, Y), 0.66, H, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        fig.text(0.50, Y + H / 2, "あなた 59万円", ha="center", va="center", color=SURFACE_INK,
                 fontsize=34, fontweight="black")
        fig.text(0.50, Y + H + 0.030, "給与明細に載る", ha="center", va="center",
                 color=INK_2, fontsize=26)
        # 下: 会社負担(明細に載らない)
        if show_company:
            fig.patches.append(Rectangle((0.17, Y - H - 0.014), 0.66, H * a,
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=0.95))
            fig.text(0.50, Y - H - 0.014 + H * a / 2, "会社 60万円", ha="center", va="center",
                     color=SURFACE_INK, fontsize=34, alpha=a, fontweight="black")
            fig.text(0.50, Y - H - 0.052, "給与明細には載らない", ha="center", va="center",
                     color=EMPH, fontsize=27, alpha=a,
                     path_effects=stroke_fx(EMPH, outline=outline_for(27), fatten=2))
        if show_total:
            fig.text(0.50, 0.500, "ぜんぶで 119万円", ha="center", va="center", color=INK,
                     fontsize=40, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2.5))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SURFACE_INK = "#1a1a19"   # 帯の中に置く文字(背景色で抜く)

SCENES = {
    "nazo": sc.hero("その保険料", "見えているのは半分", BADGE, BRAND, size=86, sub_fs=42),
    "nazo__cover": sc.cover("給料から引かれる保険料、実は半分?", "もう半分",
                            "会社が払っている", "はじめての人向け", BRAND, main_size=130),
    "nenshu": sc.card("だれで計算するか", "年収400万円の人", "(東京都・介護保険なしの概算)",
                      BADGE, BRAND, main_size=52, head_fs=36),
    "hikare": sc.bars2("その人の年間の金額",
                       ("年収", 400, "400万円"),
                       ("引かれる保険料", 59, "59万円"),
                       BADGE, BRAND, ymax=430),
    "uchiwake": sc.card("その59万円の中身", "年金と健康保険", "(あとは雇用保険など)",
                        BADGE, BRAND, main_size=52, head_fs=34),
    "naze": sc.card("なぜ引かれるのか", "そなえるため", "(病気や老後に、みんなで出し合う)",
                    BADGE, BRAND, main_size=58, head_fs=34),
    "tesuji": sc.bars2("毎月の給料で見ると",
                      ("月の給料", 33.3, "33万円"),
                      ("引かれる分", 4.9, "4万9千円"),
                      BADGE, BRAND, ymax=36),
    "tesuji2": sc.bars2("毎月の給料で見ると",
                        ("月の給料", 33.3, "33万円"),
                        ("引かれる分", 4.9, "4万9千円"),
                        BADGE, BRAND, ymax=36),
    "sessuu": sc.card("この仕組みの名前", "労使折半", "(ろうしせっぱん)",
                      BADGE, BRAND, main_size=72, head_fs=34),
    "kosei": sc.card("いちばん大きいのが", "厚生年金", "(給料の9.15%)",
                     BADGE, BRAND, main_size=62, head_fs=34),
    "kingaku": sc.bars2("その9.15%を金額にすると",
                       ("年収", 400, "400万円"),
                       ("厚生年金", 36.6, "36万6千円"),
                       BADGE, BRAND, ymax=430),
    "ritsu": sc.card("その料率は", "給料の9.15%", "(2026年度・会社と半分ずつ)",
                     BADGE, BRAND, main_size=62, head_fs=34),
    "toi": sc.quiz("ここからが本題", "この保険料を", "払っているのは誰?", "", BADGE, BRAND),
    "kaisha": sc.card("会社も出している", "同じ9.15%", "(これを労使折半という)",
                      BADGE, BRAND, main_size=62, head_fs=34,
                      ask="あなたの明細、見たことある?"),
    "meisai1": meisai(show_company=True),
    "meisai2": meisai(show_company=True),
    "goukei": meisai(show_company=True, show_total=True),
    "jinkenhi": sc.bars2("会社から見た年間の費用",
                         ("あなたの年収", 400, "400万円"),
                         ("会社が出す額", 460, "460万円"),
                         BADGE, BRAND, gap="差 60万円", ymax=480),
    "imi": sc.card("会社から見ると", "460万円の人", "(見えていないだけで、払われている)",
                   BADGE, BRAND, main_size=58, head_fs=34),
    "shime": sc.hero("見えているのは", "いつも半分", BADGE, BRAND, size=92, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行:
#   入口=給料(全員が持つ明細。専門語ではない)
#   予想「引かれてるのは、明細に書いてある額だけ」→ 結論「同じ額をもう一人分、会社が払っている」
#   オチ=自分の人件費が460万円だと分かる(見方の変更)。主語は自分の給料
UNITS = [
    Unit("nazo", "給料から引かれる保険料は、半分だけなのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("nenshu", "まず、年収400万円の人で見るのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("hikare", "その人が引かれる保険料は、年59万円。", anim=1.4, speed=1.15),
    Unit("uchiwake", "その中身は、年金と健康保険なのだ。", anim=1.4, speed=1.15),
    Unit("naze", "これは、病気や老後にそなえるお金。", anim=1.4, speed=1.15),
    Unit("tesuji", "たとえば月の給料が、33万円だとする。", anim=1.4, speed=1.15),
    Unit("tesuji2", "そこから毎月、4万9千円が引かれるのだ。", anim=1.4, speed=1.15),
    Unit("kosei", "その中でいちばん大きいのが、厚生年金。", anim=1.4, speed=1.15),
    Unit("ritsu", "その料率は、いま給料の9.15%。", anim=1.4, speed=1.15),
    Unit("kingaku", "つまり年に、36万6千円が引かれる。", anim=1.4, speed=1.15),
    Unit("toi", "その保険料、誰が払っているのだと思う?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kaisha", "その厚生年金、会社も9.15%出している。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("sessuu", "これを【労使折半】、半分ずつというのだ。", anim=1.4, speed=1.15),
    Unit("meisai1", "その折半は、健康保険でも同じなのだ。", anim=1.4, speed=1.15),
    Unit("meisai2", "だから会社の負担も、年60万円ある。", anim=1.4, speed=1.15),
    Unit("goukei", "合わせると、年119万円が払われている。", anim=1.6,
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("jinkenhi", "つまり年収400万円の人に、460万円。", anim=1.4, face="surprised",
         speed=1.1, intonation=1.2),
    Unit("shime", "明細の保険料は、半分しか見えていないのだ。", anim=1.0, pad=0.15,
         face="smug", speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S012.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
