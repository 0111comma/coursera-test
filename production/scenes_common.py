"""再利用シーンビルダー(S010〜のバッチ制作用)。

painter(fig, t) を返すファクトリ群。デザイン規格は shortlib のトークンに従う。
量産型対策(format-variation.md 層C)として、各動画は最低1つ固有シーンを持つこと。
"""
from shortlib import (
    ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD, SERIES_1,
)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def clamp01(x):
    return max(0.0, min(1.0, x))


def hero_count(value: float, fmt: str, badge: str, brand: str, size: int = 112, decimals: int = 0,
               lead: str = ""):
    """冒頭の数字カウントアップ。fmt例: "{:,.0f}万円"

    lead: 数字の上に出す「前置き」= 視聴者の課題を自分ごと化する問い(ループ㊳・P1)。
    音声のフックは数字のまま(結果フックが最強)、画面で「これはあなたの話」を同時に伝える。
    """
    def painter(fig, t):
        appear = ease_out_back(clamp01(t * 3.4))
        scale = 0.25 + 0.75 * appear
        v = value * ease_out(clamp01(t * 1.15))
        if lead:
            fig.text(0.5, 0.775, lead, ha="center", va="center", color=INK, fontsize=42,
                     path_effects=stroke_fx(INK, outline=outline_for(42), fatten=2))
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
         head_fs: int = 34, ask: str = ""):
    """見出し+ポップインする主役語+補足の汎用カード。

    ask: 中盤に重ねる二人称の問い(P4)。締めの4択と同趣旨の問いを先出しし、
    視聴者に「自分はどうだろう」と考えさせながら最後まで見せる。
    """
    def painter(fig, t):
        fig.text(0.5, 0.90, headline, ha="center", color=INK_2, fontsize=head_fs)
        if ask:
            fig.text(0.5, 0.845, ask, ha="center", color=EMPH, fontsize=31,
                     alpha=clamp01(t * 1.6 - 0.5))
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
    """まとめ表(ループ㊱で再設計。調査36ソース)。rows=[(名前, 値), ...] 5行推奨。

    - タイトルは名詞句でなく「結論を述べる文」(Assertion-Evidence法)
    - 枠・「スクショ用」ラベルは廃止(非データインク/ベイト構文)。密度と出典で保存価値を作る
    - 値は右揃え・太字・ラベルの約1.4倍(桁比較の定石)。強調はfocalの1セルのみ
    - 行はナレーションに合わせ順に点灯(セグメント化原理)
    - note には出典・時点(・仮定)を必ず入れる(スクショは単独で流通するため)
    """
    def painter(fig, t):
        fig.text(0.5, 0.885, title, ha="center", color=INK, fontsize=40,
                 path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2))
        y0 = 0.795
        dy = 0.066
        xl, xr = 0.14, 0.86
        for i, (n, v) in enumerate(rows):
            a = clamp01(t * 2.4 - i * 0.35)
            if a <= 0:
                continue
            y = y0 - i * dy
            f = (focal == i)
            fig.text(xl, y, n, ha="left", va="center", alpha=a,
                     color=INK if f else INK_2, fontsize=29)
            fig.text(xr, y, v, ha="right", va="center", alpha=a,
                     color=EMPH if f else INK, fontsize=40,
                     path_effects=stroke_fx(EMPH if f else INK,
                                            outline=outline_for(40), fatten=2) if f else None)
            if i < len(rows) - 1:
                fig.add_artist(plt.Line2D([xl, xr], [y - dy / 2, y - dy / 2],
                                          transform=fig.transFigure, color=MUTED,
                                          linewidth=1, alpha=0.35 * a))
        if note:
            fig.text(0.5, y0 - len(rows) * dy - 0.005, note, ha="center",
                     color=INK_2, fontsize=26, alpha=clamp01(t * 2.4 - len(rows) * 0.35))
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
