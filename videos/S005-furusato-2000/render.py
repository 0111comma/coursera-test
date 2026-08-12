#!/usr/bin/env python3
"""S005: ふるさと納税の実質2000円と上限の罠。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジは全編「上限は目安・2026年8月時点」。
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_out_back, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, EMPH,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "上限は目安・2026年8月時点"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
INCOME = 4_000_000
SHAHO = INCOME * (0.0985 / 2 + 0.0023 / 2 + 0.183 / 2 + 0.0050)
SHOTOKU = INCOME - (INCOME * 0.20 + 440_000)
SHOTOKUWARI = int((SHOTOKU - 430_000 - SHAHO) // 1000 * 1000) * 0.10 - 2_500  # 171,700
DONATION = 40_000
base = DONATION - 2_000
total_deduct = base * 0.05 * 1.021 + base * 0.10 + base * (0.90 - 0.05 * 1.021)
limit = SHOTOKUWARI * 0.20 / (0.90 - 0.05 * 1.021) + 2_000

assert round(total_deduct) == 38_000
assert abs(limit - 42_000) < 2_000, limit  # 総務省目安42,000円と整合
SOUMU = [("300万円", "2万8千円"), ("400万円", "4万2千円"), ("500万円", "6万1千円"),
         ("600万円", "7万7千円"), ("700万円", "10万8千円")]


# ---- シーン ----

def _hero5(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=104, sub_fs=32):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(sub_alpha))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = round(2000 * ease_out(clamp01(t * 1.15)))
    draw_glow_text(fig, 0.5, 0.62, f"{v}円", 118 * max(scale, 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    fig.text(0.5, 0.795, "実質の自己負担", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "2000円", 132)
    fig.text(0.5, 0.435, "ただし上限あり", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "ふるさと納税・上限は目安", ha="center", va="center",
             color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero5(fig, "2000円", "ふるさと納税の実質の自己負担", sub_alpha=clamp01(t), size=118)


def scene_rei(fig, t):
    fig.text(0.5, 0.90, "たとえば", ha="center", color=INK_2, fontsize=34)
    draw_glow_text(fig, 0.5, 0.62, "寄付 4万円", 84 * max(ease_out_back(clamp01(t * 2)), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_modoru(fig, t):
    fig.text(0.5, 0.90, "翌年にかけて", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.70, "寄付 4万円", ha="center", va="center", color=MUTED, fontsize=40)
    a = clamp01(t * 2 - 0.3)
    fig.text(0.5, 0.62, "↓", ha="center", va="center", color=MUTED, fontsize=44, alpha=a)
    fig.text(0.5, 0.52, "税金が 3万8千円 安くなる", ha="center", va="center", color=INK,
             fontsize=40, alpha=a, path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2))
    fig.text(0.5, 0.44, "(所得税の還付 + 住民税の控除)", ha="center", va="center",
             color=MUTED, fontsize=24, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_sashihiki(fig, t):
    fig.text(0.5, 0.68, "4万円 − 3万8千円", ha="center", va="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    a = clamp01(t * 2 - 0.5)
    draw_glow_text(fig, 0.5, 0.52, "= 2000円", 80 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_henrei(fig, t):
    _hero5(fig, "+ 返礼品", "寄付額の3割が上限の品", sub_alpha=clamp01(t * 2 - 0.4), size=88)


def scene_but(fig, t):
    _hero5(fig, "上限あり", None, size=96)
    fig.text(0.5, 0.51, "ここからが本題なのだ", ha="center", va="center",
             color=INK_2, fontsize=30, alpha=clamp01(t * 2 - 0.6))


def scene_quiz(fig, t):
    fig.text(0.5, 0.90, "クイズ", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.68, "年収400万円・独身", ha="center", va="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    a = clamp01(t * 2 - 0.4)
    draw_glow_text(fig, 0.5, 0.52, "?", 110 * max(ease_out_back(a), 0.05))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ans(fig, t):
    _hero5(fig, "4万2千円", "総務省の目安(給与のみの場合)", sub_alpha=clamp01(t * 2 - 0.4))


def scene_wana(fig, t):
    fig.text(0.5, 0.90, "上限を超えた分は", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "控除 0円", ha="center", va="center", color=MUTED,
             fontsize=76 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(MUTED, outline=outline_for(76), fatten=2))
    fig.text(0.5, 0.47, "= 全額自己負担の寄付", ha="center", va="center", color=EMPH,
             fontsize=36, alpha=clamp01(t * 2 - 0.7),
             path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=2))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_kawaru(fig, t):
    fig.text(0.5, 0.90, "上限を決めるもの", ha="center", color=INK_2, fontsize=34)
    rows = [("年収", "高いほど上限も上がる"), ("家族構成", "扶養などで変わる")]
    for i, (a_, b) in enumerate(rows):
        al = clamp01(t * 2.5 - i * 0.6)
        y = 0.66 - i * 0.12
        fig.text(0.28, y, a_, ha="center", va="center", color=EMPH, fontsize=36, alpha=al,
                 path_effects=stroke_fx(EMPH, outline=outline_for(36), fatten=1.5))
        fig.text(0.42, y, "→", ha="center", va="center", color=MUTED, fontsize=36, alpha=al)
        fig.text(0.48, y, b, ha="left", va="center", color=INK, fontsize=31, alpha=al,
                 path_effects=stroke_fx(INK, outline=outline_for(31), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_kakunin(fig, t):
    fig.text(0.5, 0.90, "寄付の前に", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.60, "自分の上限を確認", ha="center", va="center", color=EMPH,
             fontsize=56 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(56), fatten=3))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "全額控除の目安(独身)", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.40), 0.73, 0.38, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.30, 0.735, "年収", ha="center", color=MUTED, fontsize=28)
    fig.text(0.64, 0.735, "上限の目安", ha="center", color=MUTED, fontsize=28)
    for i, (m, y_) in enumerate(SOUMU):
        yy = 0.675 - i * 0.055
        fig.text(0.30, yy, m, ha="center", color=MUTED, fontsize=27)
        fig.text(0.64, yy, y_, ha="center", color=INK, fontsize=30)
    fig.text(0.46, 0.425, "総務省の目安(給与のみ・他の控除なし)", ha="center",
             color=MUTED, fontsize=24)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "自分の上限、知ってた?", ha="center", color=INK, fontsize=44,
             path_effects=stroke_fx(INK, outline=outline_for(44), fatten=3))
    chips = ["毎年やってる", "今年から", "まだ", "上限知らなかった"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=30, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.40, "▼ コメントで教えて ▼", ha="center", va="center",
             color=MUTED, fontsize=30, alpha=clamp01(t * 2 - 1.0))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_ii_hito(fig, t):
    # H1/H3: 「超えた分はただの寄付」直後の過剰リアクション(関連ユーモア)
    fig.text(0.5, 0.90, "上限を超えると…", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.62, "ただの善意の人", ha="center", va="center", color=INK,
             fontsize=50 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(50), fatten=2))
    fig.text(0.5, 0.51, "(返礼品はもらえるが控除はない)", ha="center", va="center",
             color=MUTED, fontsize=25, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_loop_back(fig, t):
    # E5/E6: 冒頭と同構図の2000円でループ(→「2000円。」)
    scene_hero_full(fig, t)


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "rei": scene_rei,
    "modoru": scene_modoru,
    "sashihiki": scene_sashihiki,
    "henrei": scene_henrei,
    "but": scene_but,
    "quiz": scene_quiz,
    "ans": scene_ans,
    "wana": scene_wana,
    "kawaru": scene_kawaru,
    "kakunin": scene_kakunin,
    "hayami": scene_hayami,
    "ii_hito": scene_ii_hito,
    "chips": scene_chips,
    "loop_back": scene_loop_back,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ
UNITS = [
    Unit("hero_count", "【2000円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "ふるさと納税の、実質の自己負担。", anim=0.8, speed=1.2),
    Unit("rei", "たとえば、【4万円】寄付したとする。", anim=1.2, speed=1.15),
    Unit("modoru", "そのぶん税金が、【3万8千円】安くなる。", anim=1.6, speed=1.15),
    Unit("sashihiki", "差し引きの負担は、【2000円】だけ。", anim=1.4, speed=1.15, intonation=1.15),
    Unit("henrei", "そのうえで、【返礼品】がもらえるのだ。", anim=1.2, speed=1.15, intonation=1.2),
    Unit("but", "でもこれ、【上限】があるのだ。", anim=1.2, se="don",
         speed=1.1, intonation=1.2, pitch=-0.04),
    Unit("quiz", "年収400万円の独身なら…【いくら】まで?", anim=1.4,
         speed=1.15, intonation=1.25),
    Unit("ans", "目安は、【4万2千円】なのだ。", anim=1.2,
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("wana", "超えた分は、控除なしの【ただの寄付】。", anim=1.4,
         speed=1.1, intonation=1.15, pitch=-0.04),
    # H1/H3: 損失ビート直後の緩和(過剰リアクション)
    Unit("ii_hito", "うっかり、善意の人になるのだ。", anim=1.2,
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("kawaru", "上限は、年収や家族構成で【変わる】。", anim=1.4, speed=1.15),
    Unit("kakunin", "寄付の前に、自分の上限を【確認】なのだ。", anim=1.2, pad=0.3,
         speed=1.15, intonation=1.2),
    Unit("hayami", "【早見表】で、年収別の目安を見るのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "あなたの上限、知ってる?", anim=1.4, pad=0.15,  # E7+N1
         speed=1.15, intonation=1.2),
    # E5/E6: サゲ(→冒頭「2000円。」に接続)
    Unit("loop_back", "確認すれば、負担はこれだけなのだ。", anim=0.8, pad=0.1,
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S005.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
