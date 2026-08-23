#!/usr/bin/env python3
"""新デザイン(自前キャラ・明るい背景)のテーマ。

competitor-shorts-teardown-2026-08-23.md の実測にもとづく:

| | 競合(@bankacademy) | 旧デザイン |
|---|---|---|
| 画面の明るさ | 0.771 | 0.141 |
| 字幕1行の高さ | 5.7%(2行常用) | 3.8% |
| 上部 | タイトル帯を固定 | なし |

**既存30本を壊さないため、shortlib は直さずに、ここから差し替える。**
`use_fp_theme()` を render.py の先頭で1回呼ぶ。
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import shortlib as S

ROOT = Path(__file__).resolve().parent.parent
POSE_DIR = ROOT / "assets" / "character"

# ---- 配色(競合の実測値に寄せた)
CREAM = "#f3e7d3"          # 背景。明るさ 0.75 前後
DOT = "#faf1e2"            # 背景のドット
BAND = "#f7c130"           # 上部のタイトル帯
BAND_INK = "#3b2c10"       # 帯の文字
TELOP = "#ffffff"          # テロップの本文
TELOP_EMPH = "#ffd93d"     # テロップの強調(数字)
TELOP_EDGE = "#8a3b00"     # テロップの縁(濃く・太く。実測で細いと読めなかった)
INK_DARK = "#2b2b28"

TITLE = ""                 # 上部の帯に出す文字(use_fp_theme で設定)
_POSE_CACHE: dict[str, Image.Image] = {}


def use_fp_theme(title: str, speaker: int = 14):
    """明るい背景・大きい字幕・上部のタイトル帯に切り替える。

    speaker=14 は冥鳴ひまり(2026-08-23 決定)。
    """
    global TITLE
    TITLE = title
    S.SURFACE = CREAM
    S.INK = INK_DARK
    S.DEFAULT_SPEAKER = speaker
    # 字幕: 3.8% → 5.7%(競合の実測)。2行を常用するので折り返しも広げる
    S.SUB_FS = 84
    S.SUB_WRAP = 11
    S.SUB_BLOCK_FIT = 0.86
    S.SUB_LINE_H = 0.052
    S.SUBTITLE_Y = 0.235
    S.new_canvas = _canvas
    S.draw_subtitle = _subtitle
    S.save_frame = _save_frame


def _canvas(t_global: float = 0.0):
    fig = plt.figure(figsize=S.FIGSIZE, dpi=S.DPI)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=-10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # ドット(競合と同じ質感)
    step = 0.024
    r = 0.0065
    j = 0
    y = 0.0
    while y < 1.0:
        x = (j % 2) * step / 2
        while x < 1.0:
            ax.add_patch(plt.Circle((x, y), r, color=DOT, zorder=-9))
            x += step
        y += step * (S.W / S.H)
        j += 1
    # 上部のタイトル帯(途中から見た人にも何の話か分かる)
    h = 0.098
    fig.add_artist(plt.Rectangle((0, 1 - h), 1, h, transform=fig.transFigure,
                                 facecolor=BAND, edgecolor="none", zorder=3.0))
    if TITLE:
        S.text_fit(fig, 0.5, 1 - h / 2, TITLE, ha="center", va="center",
                   color=BAND_INK, fontsize=44, fontweight="bold", max_w=0.92, zorder=3.1)
    return fig


def _subtitle(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """大きい縁取りテロップ。**帯は敷かない**(競合は背景の上に直接置いている)。"""
    S.draw_rich_text(fig, 0.5, S.SUBTITLE_Y, text, S.SUB_FS * pop,
                     base_color=TELOP, emph_color=TELOP_EMPH,
                     wrap=S.SUB_WRAP, line_h=S.SUB_LINE_H, block_fit=S.SUB_BLOCK_FIT,
                     outline=13.0)


def _save_frame(fig, path: Path, facecolor: str = None):
    fig.savefig(path, dpi=S.DPI, facecolor=facecolor or CREAM)
    plt.close(fig)


# ---------------------------------------------------------------- キャラ

def pose(name: str) -> Image.Image:
    if name not in _POSE_CACHE:
        p = POSE_DIR / f"{name}.png"
        if not p.exists():
            raise SystemExit(f"立ち絵がない: {p}")
        _POSE_CACHE[name] = Image.open(p).convert("RGBA")
    return _POSE_CACHE[name]


def draw_pose(fig, name: str, cx: float = 0.5, top: float = 0.78, height: float = 0.46,
              scale: float = 1.0):
    """キャラを図の上に置く。**画面中央に大きく**(競合の型)。

    top は絵の上端(figure座標)、height は絵の高さ(figure座標)。
    """
    im = pose(name)
    h = height * scale
    w = h * (im.width / im.height) * (S.H / S.W)
    ax = fig.add_axes([cx - w / 2, top - h, w, h], zorder=2.0)
    ax.imshow(np.asarray(im))
    ax.axis("off")
    return ax
