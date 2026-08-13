"""再利用シーンビルダー(S010〜のバッチ制作用)。

painter(fig, t) を返すファクトリ群。デザイン規格は shortlib のトークンに従う。
量産型対策(format-variation.md 層C)として、各動画は最低1つ固有シーンを持つこと。
"""
from shortlib import (
    ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)
from matplotlib.patches import FancyBboxPatch


def clamp01(x):
    return max(0.0, min(1.0, x))


def hero_count(value: float, fmt: str, badge: str, brand: str, size: int = 112, decimals: int = 0):
    """冒頭の数字カウントアップ。fmt例: "{:,.0f}万円" """
    def painter(fig, t):
        appear = ease_out_back(clamp01(t * 3.4))
        scale = 0.25 + 0.75 * appear
        v = value * ease_out(clamp01(t * 1.15))
        draw_glow_text(fig, 0.5, 0.62, fmt.format(round(v, decimals) if decimals else round(v)),
                       size * max(scale, 0.05))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def hero(main: str, sub: str, badge: str, brand: str, size: int = 108, sub_fs: int = 32):
    def painter(fig, t):
        draw_glow_text(fig, 0.5, 0.62, main, size)
        fig.text(0.5, 0.51, sub, ha="center", va="center",
                 color=INK_2, fontsize=sub_fs, alpha=clamp01(t * 2))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def cover(top: str, main: str, bottom: str, note: str, brand: str, main_size: int = 128):
    def painter(fig, t):
        fig.text(0.5, 0.795, top, ha="center", va="center", color=INK_2,
                 fontsize=44, path_effects=stroke_fx(INK_2, outline=outline_for(44), fatten=1.5))
        draw_glow_text(fig, 0.5, 0.615, main, main_size)
        fig.text(0.5, 0.435, bottom, ha="center", va="center", color=INK,
                 fontsize=42, path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
        fig.text(0.5, 0.88, note, ha="center", va="center", color=INK_2, fontsize=28)
        draw_footer_brand(fig, brand)
    return painter


def card(headline: str, main: str, sub: str, badge: str, brand: str,
         main_color=EMPH, main_size: int = 54, sub_color=INK_2, sub_fs: int = 30,
         head_fs: int = 34):
    """見出し+ポップインする主役語+補足の汎用カード。"""
    def painter(fig, t):
        fig.text(0.5, 0.90, headline, ha="center", color=INK_2, fontsize=head_fs)
        a = clamp01(t * 2)
        fig.text(0.5, 0.62, main, ha="center", va="center", color=main_color,
                 fontsize=main_size * max(ease_out_back(a), 0.05), alpha=a,
                 path_effects=stroke_fx(main_color, outline=outline_for(main_size), fatten=2.5))
        if sub:
            fig.text(0.5, 0.50, sub, ha="center", va="center",
                     color=sub_color, fontsize=sub_fs, alpha=clamp01(t * 2 - 0.8))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def quiz(headline: str, line1: str, line2: str, note: str, badge: str, brand: str):
    def painter(fig, t):
        fig.text(0.5, 0.88, headline, ha="center", color=INK, fontsize=36,
                 path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
        fig.text(0.5, 0.66, line1, ha="center", va="center", color=INK_2, fontsize=38)
        fig.text(0.5, 0.575, line2, ha="center", va="center", color=INK, fontsize=44,
                 path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
        a = clamp01(t * 2 - 0.5)
        fig.text(0.5, 0.44, "?", ha="center", va="center", color=EMPH,
                 fontsize=110 * max(ease_out_back(a), 0.05), alpha=a,
                 path_effects=stroke_fx(EMPH, outline=outline_for(110), fatten=4))
        if note:
            fig.text(0.5, 0.33, note, ha="center", va="center", color=INK_2, fontsize=28)
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def reveal(main: str, sub: str, formula: str, badge: str, brand: str, size: int = 96):
    """フリーズ演出つきリベール用(金額グロー+補足+根拠式)。"""
    def painter(fig, t):
        draw_glow_text(fig, 0.5, 0.64, main, size)
        fig.text(0.5, 0.53, sub, ha="center", va="center",
                 color=INK_2, fontsize=32, alpha=clamp01(t * 2 - 0.3))
        if formula:
            fig.text(0.5, 0.445, formula, ha="center", va="center",
                     color=INK_2, fontsize=28, alpha=clamp01(t * 2 - 0.7))
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def hayami(title: str, rows: list, note: str, badge: str, brand: str,
           col1: str = "", col2: str = "", focal: int | None = None):
    """スクショ枠つき早見表。rows=[(名前, 値), ...] 最大5行。"""
    def painter(fig, t):
        fig.text(0.5, 0.88, title, ha="center", color=INK, fontsize=34,
                 path_effects=stroke_fx(INK, outline=outline_for(34), fatten=2))
        top = 0.80
        h = 0.075 + 0.062 * len(rows) + (0.05 if note else 0.0) + 0.04
        fig.patches.append(FancyBboxPatch(
            (0.075, top - h), 0.77, h, boxstyle="round,pad=0.012",
            transform=fig.transFigure, fill=False, edgecolor=INK_2,
            linewidth=2.5, linestyle=(0, (6, 5))))
        fig.text(0.095, top + 0.015, "スクショ用", ha="left", color=EMPH,
                 fontsize=24, alpha=clamp01(t))
        y = top - 0.045
        if col1 or col2:
            fig.text(0.30, y, col1, ha="center", color=MUTED, fontsize=27)
            fig.text(0.66, y, col2, ha="center", color=MUTED, fontsize=27)
            y -= 0.062
        for i, (n, v) in enumerate(rows):
            f = (focal == i)
            fig.text(0.30, y, n, ha="center", color=INK_2 if f else MUTED, fontsize=27)
            fig.text(0.66, y, v, ha="center", color=INK, fontsize=29,
                     path_effects=stroke_fx(INK, outline=outline_for(29), fatten=1.5) if f else None)
            y -= 0.062
        if note:
            fig.text(0.60, y + 0.01, note, ha="center", color=INK_2, fontsize=26)
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter


def chips(question: str, options: list, badge: str, brand: str, q_fs: int = 48):
    def painter(fig, t):
        fig.text(0.5, 0.76, question, ha="center", color=INK, fontsize=q_fs,
                 path_effects=stroke_fx(INK, outline=outline_for(q_fs), fatten=3))
        for i, c in enumerate(options):
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
        draw_badge(fig, badge)
        draw_footer_brand(fig, brand)
    return painter
