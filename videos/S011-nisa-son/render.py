#!/usr/bin/env python3
"""S011: NISAの損は、税金の計算に入らない。数値は verify.py と照合。

企画書は plan.md。旧S011(債券)はユーザー判定「純粋におもんない」で却下。
原因はオチが「途中で売らなければ元に戻る」= 安心で終わっていたこと(プレイブックF3)。
本数は結論に実害があるネタに差し替えた。

図の型(figure-forms.md):
- 主役は「利益と損が打ち消し合うか、片方だけ消えるか」→ 固有シーン sousai()。
  上向きの棒=利益、下向きの棒=損。NISAの場合は損の棒を消して、
  打ち消せないことを**形の欠落**で見せる
- 最後の比較は棒2本(税金0円 と 10万円)
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
BADGE = "利益50万円・損50万円の例"

PROFIT, LOSS, TAX = 500_000, 500_000, 0.20315
assert round(PROFIT * TAX) == 101_575, "verify.pyと不一致"
assert round(PROFIT * TAX / 10_000) == 10


def sousai(show_loss=True, nisa=False, show_tax=False):
    """固有シーン: 利益と損が打ち消し合う図。

    上向きの棒=利益、下向きの棒=損。共通の底(ゼロの線)を挟んで向かい合わせる。
    nisa=True のときは損の棒を薄く消し、**打ち消せないこと**を形の欠落で見せる
    (figure-forms.md「二者が非対称 → 同じ軸に2つ」)。
    """
    Y0 = 0.660          # ゼロの線
    H = 0.115

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "その年の成績", ha="center", color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.4)
        fig.add_artist(sc.plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                     color=MUTED, linewidth=1.5, alpha=0.6))
        fig.text(0.065, Y0, "ゼロ", ha="right", va="center", color=INK_2, fontsize=24)

        # 左: 利益(上向き)
        fig.patches.append(Rectangle((0.17, Y0), 0.24, H, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        fig.text(0.29, Y0 + H + 0.032, "利益 50万円", ha="center", va="center", color=INK,
                 fontsize=30, path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
        fig.text(0.29, Y0 - 0.032, "普通の口座", ha="center", va="center",
                 color=INK_2, fontsize=25)

        # 右: 損(下向き)。NISAのときは薄くして、計算に入らないことを見せる
        if show_loss:
            alpha = 0.16 if nisa else 0.95
            fig.patches.append(Rectangle((0.59, Y0 - H * a), 0.24, H * a,
                                         transform=fig.transFigure, facecolor=EMPH,
                                         edgecolor="none", alpha=alpha))
            fig.text(0.71, Y0 - H - 0.038, "損 50万円", ha="center", va="center",
                     color=INK_2 if nisa else INK, fontsize=30, alpha=0.45 if nisa else 1.0,
                     path_effects=stroke_fx(INK_2 if nisa else INK,
                                            outline=outline_for(30), fatten=1.8))
            fig.text(0.71, Y0 + 0.032, "NISA" if nisa else "普通の口座", ha="center",
                     va="center", color=INK_2, fontsize=26)
            if nisa:
                fig.text(0.71, Y0 - H / 2, "計算に入らない", ha="center", va="center",
                         color=EMPH, fontsize=27, alpha=a,
                         path_effects=stroke_fx(EMPH, outline=outline_for(27), fatten=2))
        if show_tax:
            txt = "税金 10万円" if nisa else "税金はゼロ"
            # 右下の「損 50万円」と食い合うので、合計は左の列の下に置く
            fig.text(0.29, 0.510, txt, ha="center", va="center",
                     color=EMPH if nisa else INK, fontsize=40, alpha=a,
                     path_effects=stroke_fx(EMPH if nisa else INK,
                                            outline=outline_for(40), fatten=2.5))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("NISAで損すると", "どうなるか", BADGE, BRAND, size=88, sub_fs=44),
    "nazo__cover": sc.cover("NISAで損したら、どうなる?", "なかったこと",
                            "税金が10万円ちがう", "はじめての人向け", BRAND, main_size=110),
    "futsu": sc.card("まず普通の口座の話", "利益には税金がかかる", "(利益から引かれる)",
                     BADGE, BRAND, main_size=48, head_fs=34),
    "rieki": sousai(show_loss=False),
    "zei": sc.bars2("50万円もうけた場合",
                    ("利益", 50, "50万円"),
                    ("引かれる税金", 10, "10万円"),
                    BADGE, BRAND, ymax=55),
    "son": sousai(show_loss=True),
    "tsusan": sousai(show_loss=True),
    "namae": sc.card("この足し引きを", "損益通算という", "(そんえきつうさん)",
                     BADGE, BRAND, main_size=54, head_fs=34),
    "zero": sousai(show_loss=True, show_tax=True),
    "toi": sc.quiz("では、こちらは", "損したほうが", "NISAだったら?", "", BADGE, BRAND),
    "nashi": sousai(show_loss=True, nisa=True),
    "kekka": sousai(show_loss=True, nisa=True, show_tax=True),
    "hikaku": sc.bars2("同じ損をしても、払う税金は",
                       ("どちらも普通の口座", 0.4, "ゼロ"),
                       ("損がNISAのとき", 10, "10万円"),
                       BADGE, BRAND, gap="この差", ymax=11),
    "riyu": sc.card("なぜそうなるか", "もうけも無税だから", "(だから損も、無いものとして扱う)",
                    BADGE, BRAND, main_size=46, head_fs=34,
                    ask="あなたは両方もってる?"),
    "shime": sc.hero("NISAは", "損した年だけ弱い", BADGE, BRAND, size=92, sub_fs=40),
}

# ネタ選定ゲート(F1/F3): 予想「NISAは税金がゼロだから、どう転んでも得では?」
#   → 結論「損した年は、普通の口座より税金が約10万円多くなることがある」
# F3: 結論が「大丈夫」で終わらないこと。ここでは実害(約10万円)で終わる
# G2: 1文につき新しい数字は1つまで / G3: 専門用語は使う前か直後に言い換える
UNITS = [
    Unit("nazo", "NISAで損すると、その損はなかったことになる。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("futsu", "まず、普通の口座の税金を見るのだ。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("rieki", "その口座で、50万円もうけたとする。", anim=1.4, speed=1.15),
    Unit("zei", "すると税金が、【10万円】引かれるのだ。", anim=1.4, speed=1.15),
    Unit("son", "でも同じ年に、別の株で50万円損したら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("tsusan", "その損と利益は、足し引きしていいのだ。", anim=1.4, speed=1.15),
    Unit("namae", "この足し引きを、【損益通算】というのだ。", anim=1.2, speed=1.15),
    Unit("zero", "その通算をすると、税金はゼロになるのだ。", anim=1.4, face="happy",
         se="don", speed=1.1, intonation=1.2),
    Unit("toi", "では損したほうが、NISAだったら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("nashi", "NISAの損は、この計算に入らないのだ。", anim=1.4, speed=1.15),
    Unit("kekka", "だから税金は、10万円かかったままになる。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34, speed=1.1, intonation=1.2, pitch=-0.05),
    Unit("hikaku", "同じ損なのに、こちらだけ10万円多いのだ。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("riyu", "もともとNISAは、税金と関係ない口座だから。", anim=1.2, speed=1.15),
    Unit("shime", "だから損した時の話も、知っておくのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S011.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
