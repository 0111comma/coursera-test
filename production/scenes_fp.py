#!/usr/bin/env python3
"""新デザインの場面部品(縦型ショート用)。

競合の分解(competitor-shorts-teardown-2026-08-23.md)から:
- **1カット1.6〜1.8秒**。絵は頻繁に差し替える
- 図(表)は出しっぱなしにしてよいが、**そのあいだ赤枠を1行ずつ動かす**
- 数字はその語だけ色を変える(【】で囲む)
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

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
        # **角丸 + しっぽ**。角の立った白い箱は、置き忘れの矩形に見える
        x, y = 0.26, top - 0.08
        fig.add_artist(FancyBboxPatch((x - 0.20, y - 0.055), 0.40, 0.11,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor="#ffffff",
                                      edgecolor=INK, linewidth=3.5, zorder=2.5))
        tail = plt.Polygon([[x + 0.14, y - 0.050], [x + 0.20, y - 0.098],
                            [x + 0.19, y - 0.044]],
                           transform=fig.transFigure, facecolor="#ffffff",
                           edgecolor=INK, linewidth=3.5, zorder=2.55,
                           joinstyle="miter")
        fig.add_artist(tail)
        # しっぽの付け根の線を白で塗りつぶして、吹き出しと一体に見せる
        fig.add_artist(plt.Rectangle((x + 0.135, y - 0.049), 0.060, 0.008,
                                     transform=fig.transFigure, facecolor="#ffffff",
                                     edgecolor="none", zorder=2.57))
        S.text_fit(fig, x, y, text, ha="center", va="center", color=INK,
                   fontsize=38, max_w=0.34, zorder=2.6)
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
        # 行を厚くして下に伸ばす。0.088だと表の下に空白が0.19ぶん残り、
        # 画面がすかすかに見えていた(2026-08-23の見比べ)
        # **字幕帯に食い込ませない。**(2026-08-24)
        # 0.105 × (行数+1) で下に伸ばすと、4行で bot=0.25 になり、
        # 2行字幕の上端(実測 y=0.2531)と重なる。実際 S033 で重なって
        # check_overlap が落とした。行数が増えたら**行を薄くして収める**。
        # 下限0.40 は3行字幕の上端(実測 y=0.3682)の上に取ってある。
        FLOOR = 0.40
        top = 0.775
        bot = max(FLOOR, top - 0.105 * (n + 1))
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


def timeline(start: int, empty: float, end: int, fill_label: str, gap_label: str,
             show_gap: bool = True, title: str = "", empty_label: str = ""):
    """年齢の帯。**お金が続く区間と、足りない区間を1本の線で見せる。**

    start=65 / empty=82 / end=95 のように渡す。
    show_gap=False なら足りない側をまだ塗らない(1拍ためる)。
    """
    def painter(fig, t):
        # 帯だけを宙に置くと上下が空く。**白いパネルに載せて1つの塊にする**
        fig.add_artist(FancyBboxPatch((0.05, 0.355), 0.90, 0.365,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor="#fffdf7",
                                      edgecolor="#e0d3ba", linewidth=3.0, zorder=2.1))
        x0, x1 = 0.11, 0.89
        y, h = 0.500, 0.115
        def px(age):
            return x0 + (x1 - x0) * (age - start) / (end - start)
        xm = px(empty)
        fig.add_artist(FancyBboxPatch((x0, y), xm - x0, h,
                                      boxstyle="round,pad=0,rounding_size=0.018",
                                      transform=fig.transFigure, facecolor="#3f9a5c",
                                      edgecolor="none", zorder=2.2))
        S.text_fit(fig, (x0 + xm) / 2, y + h / 2, fill_label, ha="center", va="center",
                   color="#ffffff", fontsize=34, max_w=(xm - x0) * 0.92, zorder=2.4)
        if show_gap:
            fig.add_artist(FancyBboxPatch((xm, y), x1 - xm, h,
                                          boxstyle="round,pad=0,rounding_size=0.018",
                                          transform=fig.transFigure, facecolor="#f4e0e0",
                                          edgecolor=RED, linewidth=4.0, hatch="//",
                                          zorder=2.2))
            S.text_fit(fig, (xm + x1) / 2, y + h / 2, gap_label, ha="center", va="center",
                       color=RED, fontsize=38, max_w=(x1 - xm) * 0.88, zorder=2.4)
        # 目盛の文字。**empty は端数を持てる**(81歳8か月のような値を丸めない)
        # 境目の札は、右端の札とぶつかりやすい。**近いときは左に寄せる**
        mid_ha, mid_x = "center", xm
        if x1 - xm < 0.26:
            mid_ha, mid_x = "right", xm - 0.012
        ticks = [(f"{start}歳", x0, "left"),
                 (empty_label or f"{empty:g}歳", mid_x, mid_ha),
                 (f"{end}歳", x1, "right")]
        for lab, x, ha in ticks:
            if not show_gap and lab == f"{end}歳":
                continue
            tick_x = xm if lab == (empty_label or f"{empty:g}歳") else x
            fig.add_artist(plt.Line2D([tick_x, tick_x], [y - 0.030, y],
                                      transform=fig.transFigure,
                                      color=INK, linewidth=3.0, zorder=2.3))
            S.text_fit(fig, x, y - 0.058, lab, ha=ha, va="center",
                       color=INK, fontsize=40, max_w=0.26, zorder=2.4)
        if title:
            S.text_fit(fig, 0.5, 0.668, title, ha="center", va="center",
                       color=SUB, fontsize=40, max_w=0.84, zorder=2.3)
    return painter


def people(total: int, hit: int, label: str, title: str = ""):
    """人の絵を並べて、割合を数で見せる。**棒より、割合は「何人のうち何人」が速い。**

    total=10 / hit=5 なら、10人のうち5人を赤くする。
    """
    def painter(fig, t):
        fig.add_artist(FancyBboxPatch((0.05, 0.395), 0.90, 0.315,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor="#fffdf7",
                                      edgecolor="#e0d3ba", linewidth=3.0, zorder=2.1))
        # **人数は声とそろえる。**声が「2人に1人」なのに絵が10人中5人だと、
        # 視聴者の頭の中で 5/10 = 1/2 の変換が起きる(2026-08-23のレビュー)
        x0, x1 = 0.10, 0.90
        span = min((x1 - x0) / total, 0.24)      # 人数が少ないときは大きくしすぎない
        left = 0.5 - span * total / 2
        cy = 0.520          # 見出しと頭がぶつからない高さ
        head_w = span * 0.42
        body_w = span * 0.50
        body_h = min(0.135, max(0.070, span * 0.62))
        n_lit = int(round(hit * min(1.0, t * 1.6)))
        for i in range(total):
            cx = left + span * (i + 0.5)
            col = RED if i < n_lit else "#c9c2b4"
            # 頭
            fig.add_artist(Ellipse((cx, cy + body_h * 0.62), head_w,
                                   head_w * S.W / S.H, transform=fig.transFigure,
                                   facecolor=col, edgecolor="none", zorder=2.3))
            # 胴
            fig.add_artist(FancyBboxPatch((cx - body_w / 2, cy - body_h * 0.5),
                                          body_w, body_h,
                                          boxstyle="round,pad=0,rounding_size=0.018",
                                          transform=fig.transFigure, facecolor=col,
                                          edgecolor="none", zorder=2.3))
        S.text_fit(fig, 0.5, 0.432, label, ha="center", va="center",
                   color=RED, fontsize=52, max_w=0.80, zorder=2.4)
        if title:
            S.text_fit(fig, 0.5, 0.672, title, ha="center", va="center",
                       color=SUB, fontsize=38, max_w=0.84, zorder=2.3)
    return painter


def formula(line: str, note: str = "", name: str = "02_point"):
    """持ち帰る式を1枚。**手順ではなく、その場で使える形**で置く。"""
    def painter(fig, t):
        if name:
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.315)
            top, bot = 0.495, 0.320
        else:
            top, bot = 0.660, 0.480
        fig.add_artist(FancyBboxPatch((0.06, bot), 0.88, top - bot,
                                      boxstyle="round,pad=0,rounding_size=0.030",
                                      transform=fig.transFigure, facecolor="#fffdf7",
                                      edgecolor=RED, linewidth=5.0, zorder=2.2))
        S.text_fit(fig, 0.5, (top + bot) / 2 + 0.012, line, ha="center", va="center",
                   color="#b32020", fontsize=64, max_w=0.80, zorder=2.4)
        if note:
            S.text_fit(fig, 0.5, bot + 0.030, note, ha="center", va="center",
                       color=SUB, fontsize=32, max_w=0.78, zorder=2.4)
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
                    fontsize=40, color=RED if highlight == i else INK)
        ax.set_xlim(-0.7, n - 0.3)
        if title:
            S.text_fit(fig, 0.5, 0.788, title, ha="center", va="center",
                       color=SUB, fontsize=38, max_w=0.9, zorder=2.3)
    return painter


def hero(main: str, sub: str = "", name: str = "01_base"):
    """大きい数字を1つ。**キャラを上、数字を白いカードで下**に置く。

    数字だけを宙に浮かせると、画面の上半分が空きっぱなしになる。
    競合は必ず絵で埋めている(2026-08-23の見比べ)。
    name=None にすると数字だけになる(figure が主役の場面用)。
    """
    def painter(fig, t):
        if name:
            # バッジ(y≈0.876)より下から。上に出すと打消し表示が髪で隠れる
            F.draw_pose(fig, name, cx=0.5, top=0.845, height=0.395)
            top, bot = 0.450, 0.285
        else:
            top, bot = 0.700, 0.420
        fig.add_artist(FancyBboxPatch((0.08, bot), 0.84, top - bot,
                                      boxstyle="round,pad=0,rounding_size=0.028",
                                      transform=fig.transFigure, facecolor="#fffdf7",
                                      edgecolor="#e0d3ba", linewidth=3.0, zorder=2.2))
        # 式は**カードの上のほう**に小さく、答えはその下に大きく。
        # 下に置くと数字の下端と重なった(2026-08-23)
        head = 0.038 if sub else 0.0
        if sub:
            S.text_fit(fig, 0.5, top - 0.028, sub, ha="center", va="center",
                       color=SUB, fontsize=34, max_w=0.74, zorder=2.4)
        S.draw_rich_text(fig, 0.5, (top - head + bot) / 2, main, 150,
                         base_color="#b32020", emph_color="#b32020", outline=10.0,
                         wrap=9, line_h=0.08, block_fit=0.74)
    return painter


def cta(line: str, name: str = "02_point", show_button: bool = False,
        show_comment: bool = False):
    """締めの定型カット。競合は結論のあと**4カット**使っていた。"""
    def painter(fig, t):
        # 立ち絵は上に寄せ、ボタンは**体に重ねない**。灰色の板だと
        # 置き忘れの矩形に見えるので、角丸の黒 + 白文字にする
        F.draw_pose(fig, name, top=0.855, height=0.40 if show_comment else 0.44)
        if show_button:
            fig.add_artist(FancyBboxPatch((0.30, 0.325), 0.40, 0.075,
                                          boxstyle="round,pad=0,rounding_size=0.037",
                                          transform=fig.transFigure, facecolor="#1f1f1f",
                                          edgecolor="none", zorder=2.5))
            S.text_fit(fig, 0.5, 0.3625, "チャンネル登録", ha="center", va="center",
                       color="#ffffff", fontsize=40, max_w=0.34, zorder=2.6)
        if show_comment:
            # **声が「コメントで」なら、画面もコメントを指す**(2026-08-23のレビュー)。
            # コメント欄は画面の下にあるので、しっぽを下に向ける
            bx, by, bw, bh = 0.30, 0.352, 0.40, 0.078
            cx = bx + bw / 2
            fig.add_artist(plt.Polygon([[cx - 0.036, by + 0.006], [cx, by - 0.048],
                                        [cx + 0.036, by + 0.006]],
                                       transform=fig.transFigure, facecolor="#ffffff",
                                       edgecolor=INK, linewidth=4.0, zorder=2.5))
            fig.add_artist(FancyBboxPatch((bx, by), bw, bh,
                                          boxstyle="round,pad=0,rounding_size=0.030",
                                          transform=fig.transFigure, facecolor="#ffffff",
                                          edgecolor=INK, linewidth=4.0, zorder=2.55))
            S.text_fit(fig, cx, by + bh / 2, "コメント", ha="center", va="center",
                       color=INK, fontsize=44, max_w=0.32, zorder=2.6)
        if line:
            S.text_fit(fig, 0.5, 0.30, line, ha="center", va="center",
                       color=SUB, fontsize=34, max_w=0.86, zorder=2.3)
    return painter
