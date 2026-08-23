#!/usr/bin/env python3
"""新デザインの場面部品(縦型ショート用)。

競合の分解(competitor-shorts-teardown-2026-08-23.md)から:
- **1カット1.6〜1.8秒**。絵は頻繁に差し替える
- 図(表)は出しっぱなしにしてよいが、**そのあいだ赤枠を1行ずつ動かす**
- 数字はその語だけ色を変える(【】で囲む)
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import fplib as F
import shortlib as S

RED = "#e03131"
INK = "#2b2b28"
SUB = "#6b6459"


def person(name: str, height: float = 0.58, top: float = 0.855):
    """キャラだけ。いちばん基本の絵。"""
    def painter(fig, t):
        F.draw_pose(fig, name, top=top, height=height)
    return painter


def person_bubble(name: str, text: str, height: float = 0.54, top: float = 0.855):
    """キャラ + 吹き出し(視聴者の心の声を代弁する。競合の70.8%の技法)。"""
    def painter(fig, t):
        F.draw_pose(fig, name, cx=0.58, top=top, height=height)
        x, y = 0.26, top - 0.08
        fig.add_artist(plt.Rectangle((x - 0.20, y - 0.055), 0.40, 0.11,
                                     transform=fig.transFigure, facecolor="#ffffff",
                                     edgecolor=INK, linewidth=3.0, zorder=2.5))
        S.text_fit(fig, x, y, text, ha="center", va="center", color=INK,
                   fontsize=38, max_w=0.36, zorder=2.6)
    return painter


def cover(line1: str, line2: str, line3: str, name: str = "01_base"):
    """カバー。**3段で役割を分ける**(誰向け / いつの話 / 何をしろ)。

    競合はここを 0〜5% に置き、そのあと上部の帯に縮小して残していた。
    2026-08-23 の下見で、帯とキャラが窮屈だったので全面を黄色にして上に寄せた。
    """
    def painter(fig, t):
        F.hide_chrome(fig)          # 全面カバー。帯とバッジは重ねない
        fig.add_artist(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                                     facecolor="#f7c130", edgecolor="none", zorder=1.5))
        S.text_fit(fig, 0.5, 0.935, line1, ha="center", va="center",
                   color="#7a5b12", fontsize=62, max_w=0.86, zorder=2.4)
        S.draw_rich_text(fig, 0.5, 0.845, line2, 104, base_color="#ffffff",
                         emph_color="#fff3b0", outline=16.0, wrap=12,
                         line_h=0.055, block_fit=0.92)
        fig.add_artist(plt.Rectangle((0.05, 0.680), 0.90, 0.100,
                                     transform=fig.transFigure, facecolor="#ef5a7a",
                                     edgecolor="none", zorder=2.4))
        S.text_fit(fig, 0.5, 0.730, line3, ha="center", va="center",
                   color="#ffffff", fontsize=84, max_w=0.86, zorder=2.5)
        F.draw_pose(fig, name, top=0.66, height=0.62)
    return painter


def table(headers, rows, highlight=None, title=""):
    """表。**行を赤枠で1つずつ光らせる**(競合の33〜45%の型)。

    rows = [(左のセル, 右のセル), ...]
    highlight = 強調する行の添字(0始まり)。None なら枠なし。
    """
    n = len(rows)
    def painter(fig, t):
        top, bot = 0.775, 0.775 - 0.088 * (n + 1)
        left, right = 0.06, 0.94
        split = left + (right - left) * 0.30
        rh = (top - bot) / (n + 1)
        fig.add_artist(plt.Rectangle((left, bot), right - left, top - bot,
                                     transform=fig.transFigure, facecolor="#fffdf7",
                                     edgecolor="#cfc4ae", linewidth=2.5, zorder=2.0))
        # 見出し
        hy = top - rh / 2
        fig.add_artist(plt.Rectangle((left, top - rh), right - left, rh,
                                     transform=fig.transFigure, facecolor="#f6ecd8",
                                     edgecolor="none", zorder=2.1))
        S.text_fit(fig, (left + split) / 2, hy, headers[0], ha="center", va="center",
                   color=INK, fontsize=40, max_w=0.24, zorder=2.3)
        S.text_fit(fig, (split + right) / 2, hy, headers[1], ha="center", va="center",
                   color=INK, fontsize=40, max_w=0.58, zorder=2.3)
        for i, (a, b) in enumerate(rows):
            y0 = top - rh * (i + 2)
            yc = y0 + rh / 2
            if i % 2 == 0:
                fig.add_artist(plt.Rectangle((left, y0), right - left, rh,
                                             transform=fig.transFigure,
                                             facecolor="#fdf8ee", edgecolor="none", zorder=2.05))
            S.text_fit(fig, (left + split) / 2, yc, a, ha="center", va="center",
                       color="#b32020", fontsize=46, max_w=0.24, zorder=2.3)
            S.text_fit(fig, split + 0.02, yc, b, ha="left", va="center",
                       color=INK, fontsize=38, max_w=0.58, zorder=2.3)
            if highlight == i:
                fig.add_artist(plt.Rectangle((left, y0), right - left, rh,
                                             transform=fig.transFigure, facecolor="none",
                                             edgecolor=RED, linewidth=7.0, zorder=2.6))
        if title:
            S.text_fit(fig, 0.5, top + 0.048, title, ha="center", va="center",
                       color=SUB, fontsize=38, max_w=0.9, zorder=2.3)
    return painter


def bars(items, highlight=None, title="", ymax=None):
    """棒。items = [(見出し, 値, 棒の上の語句), ...]"""
    vals = [v for _, v, _ in items]
    top = ymax or max(vals) * 1.22
    def painter(fig, t):
        ax = fig.add_axes([0.12, 0.36, 0.76, 0.38], zorder=2.0)
        ax.set_facecolor("none")
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(0, top)
        n = len(items)
        for i, (lab, v, note) in enumerate(items):
            col = RED if highlight == i else "#9aa0a6"
            ax.bar(i, v * min(1.0, t * 1.6), width=0.52, color=col, zorder=2.1)
            ax.text(i, -top * 0.07, lab, ha="center", va="top", fontsize=30, color=INK)
            ax.text(i, v * min(1.0, t * 1.6) + top * 0.03, note, ha="center", va="bottom",
                    fontsize=40, color=RED if highlight == i else INK, fontweight="bold")
        ax.set_xlim(-0.7, n - 0.3)
        if title:
            S.text_fit(fig, 0.5, 0.788, title, ha="center", va="center",
                       color=SUB, fontsize=38, max_w=0.9, zorder=2.3)
    return painter


def hero(main: str, sub: str = "", name: str = None):
    """大きい数字を1つ。必要ならキャラも添える。"""
    def painter(fig, t):
        y = 0.60 if name else 0.55
        S.draw_rich_text(fig, 0.5, y, main, 150, base_color="#b32020",
                         emph_color="#b32020", outline=10.0, wrap=9,
                         line_h=0.08, block_fit=0.88)
        if sub:
            S.text_fit(fig, 0.5, y - 0.11, sub, ha="center", va="center",
                       color=SUB, fontsize=36, max_w=0.86)
        if name:
            # バッジ(y≈0.876)より下に置く。上に置くと打消し表示が隠れる
            F.draw_pose(fig, name, cx=0.80, top=0.845, height=0.22)
    return painter


def cta(line: str, name: str = "02_point", show_button: bool = False):
    """締めの定型カット。競合は結論のあと**4カット**使っていた。"""
    def painter(fig, t):
        # 立ち絵は上に寄せ、ボタンは**体に重ねない**。灰色の板だと
        # 置き忘れの矩形に見えるので、角丸の黒 + 白文字にする
        F.draw_pose(fig, name, top=0.855, height=0.44)
        if show_button:
            fig.add_artist(FancyBboxPatch((0.30, 0.325), 0.40, 0.075,
                                          boxstyle="round,pad=0,rounding_size=0.037",
                                          transform=fig.transFigure, facecolor="#1f1f1f",
                                          edgecolor="none", zorder=2.5))
            S.text_fit(fig, 0.5, 0.3625, "チャンネル登録", ha="center", va="center",
                       color="#ffffff", fontsize=40, max_w=0.34, zorder=2.6)
        if line:
            S.text_fit(fig, 0.5, 0.30, line, ha="center", va="center",
                       color=SUB, fontsize=34, max_w=0.86, zorder=2.3)
    return painter
