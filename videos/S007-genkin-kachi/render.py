#!/usr/bin/env python3
"""S007: 物価上昇と現金100万円の実質価値。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジは全編「物価率は例・2026年8月時点」。
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, style_axes, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "物価率は例・2026年8月時点"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
def real_man(rate: float, years: int) -> float:
    return 100 / (1 + rate) ** years

V20_2 = real_man(0.02, 20)     # 67.30
V20_16 = real_man(0.016, 20)   # 72.80
V10_2 = real_man(0.02, 10)     # 82.03
V30_2 = real_man(0.02, 30)     # 55.21
assert round(V20_2) == 67 and round(V20_16) == 73
assert round(V10_2) == 82 and round(V30_2) == 55, "verify.pyと不一致"


# ---- シーン ----

def _hero7(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=104, sub_fs=32):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(67 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}万円", 118 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "20年後の100万円", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "67万円", 132)
    fig.text(0.5, 0.435, "金額は減らないのに", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "物価は年率2%の例で計算", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero7(fig, "67万円", "20年後の現金100万円の価値", sub_alpha=clamp01(t), size=118)


def scene_herazu(fig, t):
    fig.text(0.5, 0.90, "タンス預金なら", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.64, "100万円", ha="center", va="center", color=INK, fontsize=76,
             path_effects=stroke_fx(INK, outline=outline_for(76), fatten=3))
    fig.text(0.5, 0.52, "20年後も 100万円のまま", ha="center", va="center",
             color=INK_2, fontsize=32, alpha=clamp01(t * 2 - 0.4))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_kaeru(fig, t):
    fig.text(0.5, 0.90, "でも物価が上がると", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.5, 0.62, "同じ100万円で", ha="center", va="center", color=INK, fontsize=42,
             path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
    fig.text(0.5, 0.52, "買える量が減る", ha="center", va="center", color=EMPH,
             fontsize=52 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(52), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_nichigin(fig, t):
    _hero7(fig, "年率2%", "日銀の物価安定の目標", sub_alpha=clamp01(t * 2 - 0.4))


def scene_tsuzuku(fig, t):
    # 実質価値の曲線が下がり始める(0〜20年)
    ax = fig.add_axes([0.14, 0.44, 0.74, 0.37])
    style_axes(ax)
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 110)
    ax.set_xticks([0, 10, 20])
    ax.set_xticklabels(["いま", "10年", "20年"])
    ax.set_yticks([50, 100])
    ax.set_yticklabels(["50万", "100万"])
    e = ease_in_out(clamp01(t))
    xs = [i * 0.5 for i in range(int(40 * e) + 1)]
    ys = [real_man(0.02, 0) / (1.02 ** x) * 1 for x in xs]
    ax.plot(xs, ys, color=SERIES_1, linewidth=4, solid_capstyle="round")
    fig.text(0.5, 0.90, "物価2%が続くと(実質価値)", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ochi(fig, t):
    _hero7(fig, "約67万円", "20年後に買える量(実質価値)", sub_alpha=clamp01(t * 2 - 0.4), size=100)


def scene_chokkin(fig, t):
    _hero7(fig, "年率1.6%", "直近の物価上昇(2026年6月CPI)", sub_alpha=clamp01(t * 2 - 0.4), size=96)


def scene_sore16(fig, t):
    _hero7(fig, "約73万円", "年率1.6%が20年続いた場合", sub_alpha=clamp01(t * 2 - 0.4), size=100)


def scene_meimei(fig, t):
    fig.text(0.5, 0.90, "この現象の名前", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "見えない目減り", ha="center", va="center", color=EMPH,
             fontsize=60 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(60), fatten=3))
    fig.text(0.5, 0.47, "(インフレによる実質価値の低下)", ha="center", va="center",
             color=MUTED, fontsize=24, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_kinri(fig, t):
    fig.text(0.5, 0.90, "預金でも同じ", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.5, 0.62, "金利 < 物価上昇", ha="center", va="center", color=INK, fontsize=52,
             alpha=a, path_effects=stroke_fx(INK, outline=outline_for(52), fatten=2))
    fig.text(0.5, 0.50, "なら、実質は目減り", ha="center", va="center", color=EMPH,
             fontsize=38, alpha=clamp01(t * 2 - 0.8),
             path_effects=stroke_fx(EMPH, outline=outline_for(38), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "100万円の実質価値(物価2%)", ha="center", color=INK, fontsize=36,
             path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.42), 0.73, 0.36, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.30, 0.73, "年数", ha="center", color=MUTED, fontsize=28)
    fig.text(0.64, 0.73, "実質価値", ha="center", color=MUTED, fontsize=28)
    rows = [("10年後", "約82万円"), ("20年後", "約67万円"), ("30年後", "約55万円")]
    for i, (n, v) in enumerate(rows):
        yy = 0.66 - i * 0.07
        fig.text(0.30, yy, n, ha="center", color=MUTED, fontsize=28)
        fig.text(0.64, yy, v, ha="center", color=INK, fontsize=32)
    fig.text(0.46, 0.44, "物価が年率2%で上がり続けた場合の例", ha="center",
             color=MUTED, fontsize=24)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "あなたは現金派?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["現金派", "預金派", "投資もしてる", "考えたことない"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=31, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.40, "▼ コメントで教えて ▼", ha="center", va="center",
             color=MUTED, fontsize=30, alpha=clamp01(t * 2 - 1.0))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_edamame(fig, t):
    # H1/H5: キャラ自虐(枝豆をタンスに隠す=現金退蔵の比喩)。命名の直後の緩和(H3)
    fig.text(0.5, 0.90, "ここだけの話", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.62, "枝豆もタンス派", ha="center", va="center", color=INK,
             fontsize=50 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(50), fatten=2))
    fig.text(0.5, 0.51, "(ボクの貯蔵方法なのだ。豆は減らないが…)", ha="center", va="center",
             color=MUTED, fontsize=24, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_loop_back(fig, t):
    # E5/E6: 冒頭と同構図の67万円でループ(→「67万円。」)
    scene_hero_full(fig, t)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "herazu": scene_herazu,
    "kaeru": scene_kaeru,
    "nichigin": scene_nichigin,
    "tsuzuku": scene_tsuzuku,
    "ochi": scene_ochi,
    "chokkin": scene_chokkin,
    "sore16": scene_sore16,
    "meimei": scene_meimei,
    "kinri": scene_kinri,
    "hayami": scene_hayami,
    "edamame": scene_edamame,
    "chips": scene_chips,
    "loop_back": scene_loop_back,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【67万円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "20年後の、現金100万円の【価値】。", anim=0.8, speed=1.2),
    Unit("herazu", "金額は、100万円のまま【減らない】。", anim=1.2, speed=1.15),
    Unit("kaeru", "でも物価が上がると、【買える量】が減る。", anim=1.4,
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("nichigin", "日銀の目標は、物価上昇【年率2%】。", anim=1.0, speed=1.15),
    Unit("tsuzuku", "2%が20年続くと、100万円は…", anim=1.6,
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("ochi", "約【67万円】ぶんの価値に、目減りするのだ。", anim=1.2,
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("chokkin", "直近の物価上昇は、【年率1.6%】。", anim=1.0, speed=1.15),
    Unit("sore16", "それでも20年で、約【73万円】ぶんに。", anim=1.0, speed=1.15),
    Unit("meimei", "これが、タンス預金の、【見えない目減り】。", anim=1.4, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04),
    # H1/H5: キャラ自虐(緊張→緩和)。枝豆=タンス預金の比喩で本筋に接続
    Unit("edamame", "ボクも枝豆を、タンスに隠す派なのだ。", anim=1.2,
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("kinri", "金利が物価より低いと、実質は【目減り】。", anim=1.4, pad=0.3, speed=1.15),
    Unit("hayami", "【早見表】で、年数別に見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "あなたは、現金派?", anim=1.4, pad=0.15,  # E7+N1
         speed=1.15, intonation=1.2),
    # E5/E6: サゲ(→冒頭「67万円。」に接続)
    Unit("loop_back", "そのまま20年たつと、こうなるのだ。", anim=0.8, pad=0.1,
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S007.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
