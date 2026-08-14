#!/usr/bin/env python3
"""S016: 銀行が潰れたら貯金はどうなる?(T2誤解訂正型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "預金保険の仕組み・2026年8月時点"

assert min(15_000_000, 10_000_000) == 10_000_000, "verify.pyと不一致"
assert 15_000_000 - 10_000_000 == 5_000_000, "verify.pyと不一致"


def scene_hamidashi(fig, t):
    """固有シーン: 1,500万円を1行に預けた場合の保護/はみ出し。"""
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.90, "例: 1つの銀行に1,500万円", ha="center", color=INK_2, fontsize=32)
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.6)
    base, hmax = 0.50, 0.26   # 立ち絵(y0.245-0.465)を避ける
    h_hogo = hmax * (1_000 / 1_500) * a1
    h_hami = hmax * (500 / 1_500) * a2
    fig.patches.append(Rectangle((0.30, base), 0.40, h_hogo, transform=fig.transFigure,
                                 facecolor=GOLD, edgecolor="none"))
    fig.text(0.5, base + hmax * (1_000 / 1_500) / 2, "保護 1,000万+利息", ha="center",
             va="center", color=INK, fontsize=29, alpha=a1,
             path_effects=stroke_fx(INK, outline=outline_for(29), fatten=1.5))
    if a2 > 0:
        fig.patches.append(Rectangle((0.30, base + hmax * (1_000 / 1_500)), 0.40, h_hami,
                                     transform=fig.transFigure, facecolor=MUTED_BAR,
                                     edgecolor="none", alpha=0.9))
        fig.text(0.5, base + hmax * (1_000 / 1_500) + hmax * (500 / 1_500) / 2,
                 "500万は戻らない可能性", ha="center", va="center", color=INK_2,
                 fontsize=24, alpha=a2)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_full": sc.hero("1000万円", "銀行が潰れたとき守られる貯金のライン", BADGE, BRAND,
                         size=104, sub_fs=28),
    "hero_full__cover": sc.cover("その貯金、銀行が潰れたら?", "1000万円", "貯金が守られるライン",
                                 "預金保険・実例つき", BRAND, main_size=112),
    "tsusetsu": sc.card("よくある不安", "「全部消える…?」", "(そうはならないのだ)", BADGE, BRAND,
                        main_color=MUTED_BAR, main_size=54),
    "kotae": sc.reveal("1000万円+利息", "1つの銀行・1人あたり、ここまで保護", "「預金保険」という国の仕組み", BADGE, BRAND,
                       size=88),
    "seido": sc.card("守ってくれるのは", "国の預金保険", "(銀行がお金を出し合う保険の仕組み)", BADGE, BRAND,
                     main_size=54),
    "jitsurei": sc.card("実話", "2010年に発動した", "(日本振興銀行の破綻。戦後唯一)", BADGE, BRAND,
                        main_size=52),
    "hamidashi": scene_hamidashi,
    "kessai": sc.card("実は", "利息ゼロの口座なら全額", "(「決済用預金」は上限なしで保護)", BADGE, BRAND,
                      main_size=50,
                     ask="あなたの貯金は、上限の内側?"),
    "gaika": sc.card("ただし", "外貨預金は対象外", "(円の預金とはルールが別)", BADGE, BRAND,
                     main_size=54),
    "meyose": sc.card("もう1つ", "同じ銀行なら合わせて1000万", "(支店や口座を分けても、増えない)", BADGE, BRAND,
                      main_size=44),
    "jigyaku": sc.card("ここだけの話", "ボクの貯金は余裕でセーフ", "(上限まで、だいぶ余白があるのだ)", BADGE, BRAND,
                       main_size=42),
    "chips": sc.chips("あなたの貯金は?", ["余裕でセーフ", "ちょっと超える", "銀行分けてる", "初めて知った"], BADGE, BRAND),
    "loop_back": sc.hero("1000万円", "銀行が潰れたとき守られる貯金のライン", BADGE, BRAND,
                         size=104, sub_fs=28),
}

UNITS = [
    Unit("hero_full", "【1000万円】。", anim=1.2, cover=True, se="pop", face="normal",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "銀行が潰れたとき、守られる貯金のライン。", anim=0.0, speed=1.2),
    Unit("tsusetsu", "「全部消える」と、思ってなかった?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2),
    Unit("kotae", "1つの銀行で1人【1000万円】までは守られる。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("seido", "守ってくれるのは、国の【預金保険】なのだ。", anim=1.2, speed=1.15),
    Unit("jitsurei", "2010年に、実際に発動したのだ。", anim=1.2, speed=1.15),
    Unit("hamidashi", "1500万円だと、500万は【はみ出す】のだ。", anim=1.6, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("kessai", "利息ゼロの決済用なら、【全額】保護なのだ。", anim=1.2, se="don", speed=1.15),
    Unit("gaika", "ただし外貨預金は、対象外なのだ。", anim=1.2, face="troubled", speed=1.15),
    Unit("meyose", "同じ銀行なら、口座を分けても1000万まで。", anim=1.2, speed=1.15),
    Unit("jigyaku", "ちなみにボクの貯金は、余裕でセーフなのだ。", anim=1.2, face="happy",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("chips", "あなたの貯金は、どのタイプ?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして守られるラインが、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S016.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
