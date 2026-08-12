#!/usr/bin/env python3
"""S009: 高額療養費制度(医療費100万円の月の自己負担)。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジは全編「年収370〜770万の例・2026年8月時点」。
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, style_axes, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年収370〜770万の例・2026年8月時点"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
MEDICAL = 1_000_000
SANWARI = int(MEDICAL * 0.3)
CAP_NEW = int(85_800 + (MEDICAL - 286_000) * 0.01)
CAP_OLD = int(80_100 + (MEDICAL - 267_000) * 0.01)
PAYBACK = SANWARI - CAP_NEW
assert SANWARI == 300_000 and CAP_NEW == 92_940, "verify.pyと不一致"
assert CAP_OLD == 87_430 and CAP_NEW - CAP_OLD == 5_510, "verify.pyと不一致"
assert PAYBACK == 207_060, "verify.pyと不一致"


# ---- シーン ----

def _hero(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=104):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=32, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = 9.3 * ease_out(clamp01(t * 1.15))
    draw_glow_text(fig, 0.5, 0.62, f"{v:.1f}万円", 112 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "医療費100万円の月", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "9.3万円", 130)
    fig.text(0.5, 0.435, "3割負担=30万円ではない", ha="center", va="center", color=INK,
             fontsize=42, path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
    fig.text(0.5, 0.88, "年収370〜770万円の例・2026年8月改定後", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero(fig, "9.3万円", "医療費100万円の月に実際に払う額",
          sub_alpha=clamp01(t), size=112)


def scene_sanwari(fig, t):
    fig.text(0.5, 0.90, "健康保険の窓口負担は3割", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.66, "100万円 × 3割", ha="center", va="center", color=INK, fontsize=54,
             path_effects=stroke_fx(INK, outline=outline_for(54), fatten=2))
    a = clamp01(t * 2 - 0.4)
    fig.text(0.5, 0.52, "= 30万円?", ha="center", va="center", color=EMPH,
             fontsize=64 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(64), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_jougen(fig, t):
    # 30万円の棒が上限ラインでカットされるイメージ
    ax = fig.add_axes([0.20, 0.42, 0.60, 0.40])
    style_axes(ax)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 33)
    ax.set_xticks([1.0])
    ax.set_xticklabels(["自己負担"])
    ax.set_yticks([10, 20, 30])
    ax.set_yticklabels(["10万", "20万", "30万"])
    e = ease_in_out(clamp01(t * 1.4))
    h = 30 * e
    ax.add_patch(Rectangle((0.65, 0), 0.7, h, facecolor=MUTED_BAR, edgecolor="none"))
    a = clamp01(t * 2 - 1.0)
    if a > 0:
        ax.axhline(9.3, color=EMPH, linewidth=4, alpha=a)
        ax.text(1.02, 11.3, "月の上限", ha="center", color=EMPH, fontsize=30, alpha=a,
                path_effects=stroke_fx(EMPH, outline=outline_for(30), fatten=1.5))
    fig.text(0.5, 0.90, "でも実は…", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_meisho(fig, t):
    fig.text(0.5, 0.90, "この仕組みの名前", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "高額療養費制度", ha="center", va="center", color=EMPH,
             fontsize=58 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(58), fatten=3))
    fig.text(0.5, 0.47, "(公的医療保険にもとから付いている)", ha="center", va="center",
             color=MUTED, fontsize=24, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_quiz(fig, t):
    fig.text(0.5, 0.88, "クイズ: 医療費100万円の月", ha="center", color=INK, fontsize=36,
             path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
    fig.text(0.5, 0.66, "年収500万円の人の", ha="center", va="center", color=INK_2, fontsize=38)
    fig.text(0.5, 0.575, "自己負担の上限は?", ha="center", va="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    a = clamp01(t * 2 - 0.5)
    fig.text(0.5, 0.44, "?", ha="center", va="center", color=EMPH,
             fontsize=110 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(110), fatten=4))
    fig.text(0.5, 0.33, "(年収約370〜770万円の区分)", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ochi(fig, t):
    draw_glow_text(fig, 0.5, 0.64, "9万2940円", 96)
    fig.text(0.5, 0.53, "自己負担の上限(月)", ha="center", va="center",
             color=INK_2, fontsize=32, alpha=clamp01(t * 2 - 0.3))
    fig.text(0.5, 0.445, "85,800円+(100万円−28.6万円)×1%", ha="center", va="center",
             color=MUTED, fontsize=26, alpha=clamp01(t * 2 - 0.7))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_modoru(fig, t):
    # 30万払っても20.7万戻る
    ax = fig.add_axes([0.16, 0.42, 0.68, 0.40])
    style_axes(ax)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 33)
    ax.set_xticks([0.75, 2.25])
    ax.set_xticklabels(["窓口で3割", "最終的な負担"])
    ax.set_yticks([10, 20, 30])
    ax.set_yticklabels(["10万", "20万", "30万"])
    e = ease_in_out(clamp01(t * 1.6))
    ax.add_patch(Rectangle((0.40, 0), 0.7, 30, facecolor=MUTED_BAR, edgecolor="none"))
    ax.text(0.75, 31.2, "30万円", ha="center", color=INK, fontsize=28,
            path_effects=stroke_fx(INK, outline=outline_for(28), fatten=1.5))
    ax.add_patch(Rectangle((1.90, 0), 0.7, 9.3 * e, facecolor=GOLD, edgecolor="none"))
    a = clamp01(t * 2 - 0.8)
    if a > 0:
        ax.text(2.25, 9.3 + 1.9, "9万2940円", ha="center", color=INK, fontsize=28, alpha=a,
                path_effects=stroke_fx(INK, outline=outline_for(28), fatten=1.5))
    fig.text(0.5, 0.90, "20万7060円が戻ってくる", ha="center", color=EMPH, fontsize=36,
             alpha=clamp01(t * 2 - 1.0),
             path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_kaisei(fig, t):
    fig.text(0.5, 0.90, "2026年8月から", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.62, "上限額が改定", ha="center", va="center", color=EMPH,
             fontsize=62 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(62), fatten=3))
    fig.text(0.5, 0.49, "(7月の診療分までは旧上限)", ha="center", va="center",
             color=MUTED, fontsize=24, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_sengetsu(fig, t):
    fig.text(0.5, 0.88, "医療費100万円の月の上限", ha="center", color=INK, fontsize=36,
             path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
    fig.text(0.30, 0.70, "7月まで", ha="center", color=MUTED, fontsize=30)
    fig.text(0.30, 0.62, "8万7430円", ha="center", color=INK_2, fontsize=40)
    a = clamp01(t * 2 - 0.5)
    fig.text(0.50, 0.62, "→", ha="center", va="center", color=MUTED, fontsize=44, alpha=a)
    fig.text(0.70, 0.70, "8月から", ha="center", color=EMPH, fontsize=30, alpha=a)
    fig.text(0.70, 0.62, "9万2940円", ha="center", color=INK, fontsize=40, alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2))
    fig.text(0.5, 0.47, "+5510円", ha="center", va="center", color=EMPH,
             fontsize=40, alpha=clamp01(t * 2 - 1.0),
             path_effects=stroke_fx(EMPH, outline=outline_for(40), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "月の上限(2026年8月〜・70歳未満)", ha="center", color=INK, fontsize=34,
             path_effects=stroke_fx(INK, outline=outline_for(34), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.075, 0.36), 0.77, 0.44, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.095, 0.815, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.28, 0.755, "年収の目安", ha="center", color=MUTED, fontsize=27)
    fig.text(0.67, 0.755, "上限(基準額)", ha="center", color=MUTED, fontsize=27)
    rows = [
        ("約1160万円〜", "27万300円+1%"),
        ("約770〜1160万", "17万9100円+1%"),
        ("約370〜770万", "8万5800円+1%"),
        ("〜約370万円", "6万1500円"),
        ("住民税非課税", "3万6900円"),
    ]
    for i, (n, v) in enumerate(rows):
        yy = 0.695 - i * 0.062
        focal = (i == 2)
        fig.text(0.28, yy, n, ha="center", color=INK_2 if focal else MUTED, fontsize=27)
        fig.text(0.67, yy, v, ha="center", color=INK, fontsize=29,
                 path_effects=stroke_fx(INK, outline=outline_for(29), fatten=1.5) if focal else None)
    fig.text(0.46, 0.38, "「+1%」は医療費に応じた加算(概要欄参照)", ha="center",
             color=MUTED, fontsize=24)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_taishogai(fig, t):
    fig.text(0.5, 0.90, "ただし対象外もある", ha="center", color=INK_2, fontsize=34)
    items = ["差額ベッド代", "入院中の食事代"]
    for i, c in enumerate(items):
        a = clamp01(t * 2.4 - i * 0.5)
        if a <= 0:
            continue
        fig.text(0.5, 0.66 - i * 0.11, c, ha="center", va="center", color=INK,
                 fontsize=40, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor=SURFACE,
                           edgecolor=MUTED_BAR, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.42, "= 上限の外で自己負担", ha="center", va="center", color=EMPH,
             fontsize=34, alpha=clamp01(t * 2 - 1.0),
             path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_maina(fig, t):
    fig.text(0.5, 0.90, "窓口でいったん30万円…も避けられる", ha="center", color=INK_2, fontsize=30)
    a = clamp01(t * 2 - 0.2)
    fig.text(0.5, 0.64, "マイナ保険証", ha="center", va="center", color=INK,
             fontsize=54 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(54), fatten=3))
    fig.text(0.5, 0.52, "窓口の支払いも上限まで", ha="center", va="center", color=EMPH,
             fontsize=36, alpha=clamp01(t * 2 - 0.8),
             path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "この制度、知ってた?", ha="center", color=INK, fontsize=48,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=3))
    chips = ["知ってた", "初めて知った", "使ったことある", "家族に教える"]
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


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "sanwari": scene_sanwari,
    "jougen": scene_jougen,
    "meisho": scene_meisho,
    "quiz": scene_quiz,
    "ochi": scene_ochi,
    "modoru": scene_modoru,
    "kaisei": scene_kaisei,
    "sengetsu": scene_sengetsu,
    "hayami": scene_hayami,
    "taishogai": scene_taishogai,
    "maina": scene_maina,
    "chips": scene_chips,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【9万3千円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "医療費100万円の月に、実際に払う額。", anim=0.8, speed=1.2),
    Unit("sanwari", "3割負担なら、【30万円】のはずなのだ。", anim=1.2, speed=1.15),
    Unit("jougen", "でも医療費には、月の【上限】があるのだ。", anim=1.5,
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("meisho", "その名も、【高額療養費制度】。", anim=1.2, speed=1.1),
    Unit("quiz", "年収500万なら、いくらだと思う?", anim=1.4,
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("ochi", "上限は、【9万2940円】なのだ。", anim=1.4,
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("modoru", "上限を超えた分は、あとで【戻ってくる】のだ。", anim=1.6, speed=1.15),
    Unit("kaisei", "実は【今月】から、この上限が上がったのだ。", anim=1.2, se="don",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("sengetsu", "先月までなら、【8万7430円】だったのだ。", anim=1.4, speed=1.15),
    Unit("hayami", "年収別の上限は、【早見表】で見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("taishogai", "差額ベッド代と食事代は、【対象外】なのだ。", anim=1.4, speed=1.15),
    Unit("maina", "マイナ保険証なら、支払いも【上限まで】なのだ。", anim=1.2, speed=1.15),
    Unit("chips", "この制度、知ってた?コメントで教えてなのだ。", anim=1.4, pad=0.15,  # 即切りループ
         speed=1.15, intonation=1.15),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S009.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
