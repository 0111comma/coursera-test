#!/usr/bin/env python3
"""S016: PER15倍は「利益15年分の値段」。数値は verify.py と照合。

図の型(figure-forms.md):
- 「利益が何年分か」は積み上がっている量。→ 同じ大きさのブロックを積む(stack)。
  個数そのものが意味を持つので、数えられる大きさで並べる
- 15倍と30倍の比較は、ブロックの数の違いで見せる(棒に置き換えない)
- 「利益が増えるとPERは下がる」も stack の個数で見せる

図に出した数字は必ず字幕でも言う(S010でのユーザー指摘)。
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
BADGE = "株価1500円・1株利益100円の例"

PRICE, EPS = 1_500.0, 100.0
assert PRICE / EPS == 15.0 and 3_000.0 / EPS == 30.0, "verify.pyと不一致"


def warizan(stage=3):
    """固有シーン: PERの割り算を、位置で見せる(段階的に足していく)。

    stage 1 = 1年ぶんの利益だけ / 2 = 株価の棒を足す / 3 = わり算の記号を足す。
    初心者向けなので、株価・利益・わり算を1回で全部出さない(ループ51)。
    左が右の何個分か、が PER。数字を並べるのではなく高さの比で見せる。
    """
    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "2つを並べてみる", ha="center", color=INK_2, fontsize=34)
        a = sc.clamp01(t * 2.2)
        base = 0.545
        # 右: 1年ぶんの利益(小さい棒)。まずこれだけを見せる
        fig.patches.append(Rectangle((0.62, base), 0.22, 0.015, transform=fig.transFigure,
                                     facecolor=EMPH, edgecolor="none", alpha=0.95))
        fig.text(0.73, base + 0.055, "もうけ100円", ha="center", va="center",
                 color=EMPH, fontsize=28,
                 path_effects=stroke_fx(EMPH, outline=outline_for(28), fatten=1.8))
        fig.text(0.73, base - 0.032, "年間のもうけ", ha="center", va="center",
                 color=INK_2, fontsize=25)
        if stage >= 2:
            h = 0.225 * (a if stage == 2 else 1.0)
            fig.patches.append(Rectangle((0.16, base), 0.22, h, transform=fig.transFigure,
                                         facecolor=GOLD, edgecolor="none", alpha=0.95))
            fig.text(0.27, base + h + 0.030, "株価1500円", ha="center", va="center",
                     color=INK, fontsize=30,
                     path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.8))
            fig.text(0.27, base - 0.032, "株の値段", ha="center", va="center",
                     color=INK_2, fontsize=25)
        if stage >= 3:
            fig.text(0.50, base + 0.100, "÷", ha="center", va="center",
                     color=INK_2, fontsize=48, alpha=a)
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("PER15倍", "何が15倍なのだ?", BADGE, BRAND, size=104, sub_fs=44),
    "nazo__cover": sc.cover("PER15倍って、何が15倍?", "PER", "答えは、利益15年分",
                            "はじめての人向け", BRAND, main_size=150),
    "teigi": sc.card("PERとは", "株のねだんの物差し", "(ピー・イー・アール、と読む)",
                     BADGE, BRAND, main_size=48, head_fs=36),
    "kabu": sc.card("株を買うということ", "会社の一部を持つ",
                    "(だから会社のもうけが関係する)", BADGE, BRAND,
                    main_size=52, head_fs=34),
    "eps": warizan(stage=1),
    "kakaku": warizan(stage=2),
    "warizan": warizan(stage=3),
    "kotae": sc.stack("株価1500円の内訳", 15, "1個ぶんのもうけは100円", "合計1500円",
                      BADGE, BRAND, cols=5),
    "imi": sc.card("言いかえると", "15年分の値段", "(利益が一定なら、の話)",
                   BADGE, BRAND, main_size=50, head_fs=34),
    "toi": sc.quiz("では、こちらは", "同じ利益100円で", "株価3000円", "", BADGE, BRAND),
    "sanju": sc.stack("株価3000円の内訳", 30, "1個ぶんのもうけは100円", "合計3000円",
                      BADGE, BRAND, cols=6),
    "takai": sc.card("30年分も払う理由", "期待が大きいから",
                     "(これから増えると見られている)", BADGE, BRAND,
                     main_size=52, head_fs=34, ask="あなたの持ち株は何年分?"),
    "fueru": sc.bars2("利益が2倍になると",
                      ("前のPER", 15, "15倍"),
                      ("利益が2倍のあと", 7.5, "7.5倍"),
                      BADGE, BRAND, gap="半分に", ymax=16),
    "gyaku": sc.card("PERが低くても", "安いとは限らない",
                     "(利益が減れば、あとから上がる)", BADGE, BRAND,
                     main_size=52, head_fs=34),
    "shime": sc.hero("PERは", "何年分か、を表す", BADGE, BRAND, size=96, sub_fs=40),
}

# ネタ選定ゲート(F1): 予想「PERは"割安さの点数"みたいなもの?」
#   → 結論「利益の何年分の値段か。低いほど安いとは限らない」
# ループ51(端折り禁止): 1文につき新しい数字は1つまで。専門用語は使う前に言い換える。
UNITS = [
    Unit("nazo", "【PER15倍】。何が15倍なのだ?", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("teigi", "PERとは、株の値段をはかる数字。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("kabu", "その株を買うのは、会社の一部を持つこと。", anim=1.4, speed=1.15),
    Unit("eps", "その会社のもうけは、ひと株100円とする。", anim=1.4, speed=1.15),
    Unit("kakaku", "一方その株の値段は、1500円だとするのだ。", anim=1.4, speed=1.15),
    Unit("warizan", "PERは、値段をもうけでわった数。", anim=1.4, speed=1.15),
    Unit("kotae", "つまり1500わる100で、15倍になる。", anim=1.6,
         se="don", speed=1.1, intonation=1.2),
    Unit("imi", "つまり利益の、15年分の値段ということ。", anim=1.4, speed=1.15),
    Unit("toi", "では同じ利益で、株価3000円ならどうなる?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("sanju", "答えは、利益の【30年分】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("takai", "30年分も払うのは、期待が大きいから。", anim=1.4, speed=1.15),
    Unit("fueru", "では、もうけが2倍になったら?", anim=1.4, face="happy",
         speed=1.15),
    Unit("gyaku", "PERは半分の、7.5倍まで下がるのだ。", anim=1.4, speed=1.15),
    Unit("shime", "だからPERは、低いほど安いとは限らない。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
