#!/usr/bin/env python3
"""「ヤケに心理学に詳しいずんだもん」用の**絵で見せる**場面部品(縦型ショート)。

2026-09-04 ユーザー指摘(Z001 最終版): 「もっとイラストつかって。よくわからん画面に出てる図」

scenes_fp の図(箱2つと「<」の比較・「体 + 持ち物 → 全部主人のもの」の式・
「2世紀前半 → いま」の矢印・語だけのヒーロー)は、お金の動画の**数の図**。
数が無いこのチャンネルでは、語を箱に入れても絵にならない。
ここでは**場面そのもの**(電車・上司・カレンダー・鍵・メモ・本・1900年前の人)を
ベクターのピクトグラムで描き、ずんだもんを視聴者の代わりとして同じ絵の中に置く。

部品の約束(scenes_fp と同じ):
- painter(fig, t) を返す。t は anim 窓の進行(0〜1)。着地後の動きは動画内時刻で回す
- 白い板は scenes_fp.card() と同じ矩形(CARD_L/R/TOP/BOT)。板の外に絵を置かない
- 色は fplib の役割トークンだけ(赤=変えられない/鍵、緑=自分で変えられる、墨=輪郭)
- **尻の止め絵を作らない**(check_design M1): ピクトの塊は float_dy で流し、鍵は beat で脈打つ

ライセンス: すべてこのファイルで描く図形。外部のイラスト素材は使っていない。
"""
import math

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Ellipse, FancyBboxPatch, PathPatch, Polygon

import fplib as F
import shortlib as S
import scenes_fp as sf
from scenes_fp import (CARD_L, CARD_R, CARD_TOP, CARD_BOT, CARD_CY, INK, RED,
                       CONNECT, card, drop_shadow, head_title, float_dy, beat, tri)

AR = S.H / S.W                 # 高さの割合を幅の割合に直す係数(正方形を正方形に描く)
CARD = F.CARD
EDGE = sf.CARD_EDGE_STRONG
GREEN = F.GAIN if hasattr(F, "GAIN") else "#2f7d4a"
SKIN = "#f6dcc2"
NIGHT = "#2c3550"              # 電車の窓の外(夜)
LIGHT = "#f2c96b"              # 街の灯り・月
SUIT = "#3a3a44"               # 上司のスーツ
TUNIC = "#efe6d2"              # 1900年前の人の服
PURPLE = "#6b4a8a"             # 主人の帯

_ease, _back = sf._ease, sf._back

# 板の中の定位置。**立ち絵は左、絵は右**に固定して、カットが替わっても構図が跳ねないようにする
POSE_CX, POSE_H = 0.27, 0.34
POSE_TOP = CARD_TOP - 0.03
PICT_CX = 0.66
PICT_CY = CARD_CY + 0.015


# ---------------------------------------------------------------- 基本図形
def _rect(fig, x, y, w, h, fc=CARD, ec=INK, lw=3.0, z=2.3, r=0.012, a=1.0):
    fig.add_artist(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
        transform=fig.transFigure, facecolor=fc, edgecolor=ec, linewidth=lw,
        zorder=z, alpha=a, mutation_aspect=sf._ma()))


def _circ(fig, cx, cy, r, fc=CARD, ec=INK, lw=3.0, z=2.3, a=1.0):
    """r は**高さの割合**。横は AR で補正して真円にする。"""
    fig.add_artist(Ellipse((cx, cy), 2 * r * AR, 2 * r, transform=fig.transFigure,
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, alpha=a))


def _poly(fig, pts, fc=CARD, ec=INK, lw=3.0, z=2.3, a=1.0):
    fig.add_artist(Polygon(pts, closed=True, transform=fig.transFigure,
                           facecolor=fc, edgecolor=ec, linewidth=lw,
                           joinstyle="round", zorder=z, alpha=a))


def _line(fig, pts, color=INK, lw=4.0, z=2.4, a=1.0):
    xs, ys = zip(*pts)
    fig.add_artist(Line2D(xs, ys, transform=fig.transFigure, color=color,
                          linewidth=lw, solid_capstyle="round",
                          solid_joinstyle="round", zorder=z, alpha=a))


def _txt(fig, x, y, s, fs, color=INK, z=2.5, a=1.0, max_w=0.4, raw=False, **kw):
    kw.setdefault("ha", "center")
    kw.setdefault("va", "center")
    # raw=True: 桁区切りを入れない(「1900年前」を「1,900年前」にしない)
    return S.text_fit(fig, x, y, s if raw else F.fmt_disp(s), fontsize=fs, max_w=max_w,
                      color=color, zorder=z, alpha=a, **kw)


def _pop(t, start, dur=0.22):
    return _back((t - start) / dur)


def _fade(t, start, dur=0.16):
    return _ease((t - start) / dur)


def _drift():
    """着地後の塊の縦流れ(速度一定)。M1 対策。"""
    return float_dy(amp=0.0042, period=1.6)


# ---------------------------------------------------------------- ピクトグラム
def pict_lock(fig, cx, cy, h, a=1.0, z=2.6, color=RED, pulse=True):
    """南京錠 = 「自分では変えられない」の印。cy は錠の中心。"""
    if a <= 0.01:
        return
    s = beat(period=1.8, amp=0.06) if pulse else 1.0
    h = h * s
    bw, bh = h * 0.80 * AR, h * 0.58
    by = cy - h * 0.48
    _rect(fig, cx - bw / 2, by, bw, bh, fc=color, ec=INK, lw=3.0, z=z, r=0.010, a=a)
    # 鍵穴
    _circ(fig, cx, by + bh * 0.58, h * 0.07, fc=CARD, ec=CARD, lw=0, z=z + 0.1, a=a)
    _rect(fig, cx - h * 0.028 * AR, by + bh * 0.22, h * 0.056 * AR, bh * 0.36,
          fc=CARD, ec=CARD, lw=0, z=z + 0.1, r=0.003, a=a)
    # つる(半円)
    fig.add_artist(Arc((cx, by + bh), bw * 0.62, h * 0.70, theta1=0, theta2=180,
                       transform=fig.transFigure, edgecolor=INK, linewidth=h * 110,
                       zorder=z - 0.1, alpha=a))


def pict_check(fig, cx, cy, h, a=1.0, z=2.6, color=GREEN):
    """緑のチェック = 「自分で変えられる」の印。"""
    if a <= 0.01:
        return
    s = beat(period=1.8, amp=0.06)
    h = h * s
    _circ(fig, cx, cy, h * 0.5, fc=color, ec=INK, lw=3.0, z=z, a=a)
    _line(fig, [(cx - h * 0.22 * AR, cy - h * 0.02), (cx - h * 0.05 * AR, cy - h * 0.20),
                (cx + h * 0.24 * AR, cy + h * 0.18)], color=CARD, lw=h * 70, z=z + 0.1, a=a)


def pict_cross(fig, cx, cy, h, a=1.0, z=2.6, color=RED, lw=None):
    """赤い×。"""
    if a <= 0.01:
        return
    lw = lw or h * 60
    d = h * 0.5
    _line(fig, [(cx - d * AR, cy - d), (cx + d * AR, cy + d)], color=color, lw=lw, z=z, a=a)
    _line(fig, [(cx - d * AR, cy + d), (cx + d * AR, cy - d)], color=color, lw=lw, z=z, a=a)


def pict_boss(fig, cx, yb, h, a=1.0, z=2.4, mood="angry"):
    """上司。スーツ+ネクタイ+つり上がった眉。yb は足元(=板の下辺側)。"""
    if a <= 0.01:
        return
    r = h * 0.17                            # 頭の半径
    hy = yb + h - r                         # 頭の中心
    # 体(台形のスーツ)
    sw = h * 0.62 * AR
    _poly(fig, [(cx - sw / 2, yb), (cx + sw / 2, yb),
                (cx + sw * 0.34, hy - r * 0.9), (cx - sw * 0.34, hy - r * 0.9)],
          fc=SUIT, ec=INK, lw=3.0, z=z, a=a)
    # シャツの三角とネクタイ
    _poly(fig, [(cx - sw * 0.14, hy - r * 0.9), (cx + sw * 0.14, hy - r * 0.9),
                (cx, hy - r * 0.9 - h * 0.22)], fc=CARD, ec=INK, lw=2.0, z=z + 0.05, a=a)
    _poly(fig, [(cx - sw * 0.05, hy - r * 0.95), (cx + sw * 0.05, hy - r * 0.95),
                (cx + sw * 0.045, hy - r * 0.9 - h * 0.20), (cx, hy - r * 0.9 - h * 0.24),
                (cx - sw * 0.045, hy - r * 0.9 - h * 0.20)],
          fc=RED, ec=INK, lw=1.5, z=z + 0.1, a=a)
    # 頭・髪
    _circ(fig, cx, hy, r, fc=SKIN, ec=INK, lw=3.0, z=z + 0.1, a=a)
    fig.add_artist(Arc((cx, hy + r * 0.05), 2 * r * AR * 1.02, 2 * r * 1.02, theta1=15,
                       theta2=165, transform=fig.transFigure, edgecolor=INK,
                       linewidth=h * 60, zorder=z + 0.2, alpha=a))
    # 眉・目・口
    ex = r * 0.42 * AR
    if mood == "angry":
        _line(fig, [(cx - ex - r * 0.2 * AR, hy + r * 0.36), (cx - ex + r * 0.15 * AR, hy + r * 0.20)],
              lw=h * 22, z=z + 0.3, a=a)
        _line(fig, [(cx + ex + r * 0.2 * AR, hy + r * 0.36), (cx + ex - r * 0.15 * AR, hy + r * 0.20)],
              lw=h * 22, z=z + 0.3, a=a)
        _line(fig, [(cx - r * 0.30 * AR, hy - r * 0.42), (cx + r * 0.30 * AR, hy - r * 0.36)],
              lw=h * 16, z=z + 0.3, a=a)
    else:
        _line(fig, [(cx - r * 0.25 * AR, hy - r * 0.40), (cx + r * 0.25 * AR, hy - r * 0.40)],
              lw=h * 14, z=z + 0.3, a=a)
    _circ(fig, cx - ex, hy + r * 0.05, r * 0.09, fc=INK, ec=INK, lw=0, z=z + 0.3, a=a)
    _circ(fig, cx + ex, hy + r * 0.05, r * 0.09, fc=INK, ec=INK, lw=0, z=z + 0.3, a=a)


def pict_person(fig, cx, yb, h, a=1.0, z=2.4, color=CONNECT, face=None, tunic=False,
                laurel=False):
    """人の影絵。tunic=True で1900年前の服、laurel=True で主人(月桂冠と紫の帯)。"""
    if a <= 0.01:
        return
    r = h * 0.16
    hy = yb + h - r
    bw = h * 0.50 * AR
    if tunic:
        _poly(fig, [(cx - bw / 2, yb), (cx + bw / 2, yb),
                    (cx + bw * 0.30, hy - r * 0.95), (cx - bw * 0.30, hy - r * 0.95)],
              fc=TUNIC, ec=INK, lw=3.0, z=z, a=a)
        if laurel:
            _rect(fig, cx - bw / 2, yb, bw, h * 0.09, fc=PURPLE, ec=INK, lw=2.0, z=z + 0.05,
                  r=0.004, a=a)
        _circ(fig, cx, hy, r, fc=SKIN, ec=INK, lw=3.0, z=z + 0.1, a=a)
        if laurel:
            fig.add_artist(Arc((cx, hy + r * 0.15), 2 * r * AR * 1.15, 2 * r * 1.05, theta1=20,
                               theta2=160, transform=fig.transFigure, edgecolor=GREEN,
                               linewidth=h * 40, zorder=z + 0.25, alpha=a))
        else:
            fig.add_artist(Arc((cx, hy + r * 0.05), 2 * r * AR * 1.02, 2 * r * 1.02, theta1=20,
                               theta2=160, transform=fig.transFigure, edgecolor="#7a5a3a",
                               linewidth=h * 50, zorder=z + 0.2, alpha=a))
        ex = r * 0.40 * AR
        _circ(fig, cx - ex, hy, r * 0.09, fc=INK, ec=INK, lw=0, z=z + 0.3, a=a)
        _circ(fig, cx + ex, hy, r * 0.09, fc=INK, ec=INK, lw=0, z=z + 0.3, a=a)
        _line(fig, [(cx - r * 0.22 * AR, hy - r * 0.42), (cx + r * 0.22 * AR, hy - r * 0.42)],
              lw=h * 14, z=z + 0.3, a=a)
    else:
        _rect(fig, cx - bw / 2, yb, bw, h - r * 1.9, fc=color, ec=color, lw=0, z=z, r=0.02, a=a)
        _circ(fig, cx, hy, r, fc=color, ec=color, lw=0, z=z, a=a)
    if face:
        _txt(fig, cx, hy, face, h * 300, color=CARD if not tunic else INK, z=z + 0.4, a=a,
             fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)


def pict_calendar(fig, cx, cy, h, label, a=1.0, z=2.4, mark=None, sub=""):
    """日めくり。label は「今日」「明日」。mark は "×" / "?" / "check"。"""
    if a <= 0.01:
        return
    w = h * 0.82 * AR
    x, y = cx - w / 2, cy - h / 2
    _rect(fig, x, y, w, h, fc=CARD, ec=INK, lw=3.0, z=z, r=0.014, a=a)
    _rect(fig, x, y + h * 0.78, w, h * 0.22, fc=RED, ec=INK, lw=3.0, z=z + 0.05, r=0.014, a=a)
    _rect(fig, x, y + h * 0.70, w, h * 0.10, fc=RED, ec=RED, lw=0, z=z + 0.06, r=0.0, a=a)
    for dx in (-0.25, 0.25):
        _circ(fig, cx + w * dx, y + h * 0.89, h * 0.035, fc=CARD, ec=INK, lw=2.0, z=z + 0.1, a=a)
    _txt(fig, cx, y + h * 0.42, label, h * 300, z=z + 0.2, a=a, max_w=w * 0.9,
         fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
    if sub:
        _txt(fig, cx, y + h * 0.15, sub, h * 120, color=CONNECT, z=z + 0.2, a=a, max_w=w * 0.9)
    if mark == "×":
        pict_cross(fig, cx, y + h * 0.42, h * 0.62, a=a, z=z + 0.3)
    elif mark == "?":
        # 日付の**下**に置く(check_overlap: 右上に置くと「明日」の字と箱が重なる)
        _txt(fig, cx, y + h * 0.13, "?", h * 260, color=RED, z=z + 0.3, a=a,
             fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
    elif mark == "check":
        pict_check(fig, cx + w * 0.30, y + h * 0.60, h * 0.30, a=a, z=z + 0.3)


def pict_bubble(fig, cx, cy, w, h, text, a=1.0, z=2.5, tip=None, fs=None, color=INK,
                fc=CARD, ec=EDGE):
    """吹き出し(しっぽの先 tip は任意)。"""
    if a <= 0.01:
        return
    x, y = cx - w / 2, cy - h / 2
    drop_shadow(fig, x, y, w, h, r=0.025, z=z - 0.01, alpha=a)
    if tip:
        path = F.bubble_path(x, y, w, h, 0.025, tip=tip, side="bottom")
        fig.add_artist(PathPatch(path, transform=fig.transFigure, facecolor=fc,
                                 edgecolor=ec, linewidth=3.5, joinstyle="round",
                                 capstyle="round", zorder=z, alpha=a))
    else:
        _rect(fig, x, y, w, h, fc=fc, ec=ec, lw=3.5, z=z, r=0.025, a=a)
    if text:
        _txt(fig, cx, cy, text, fs or h * 260, color=color, z=z + 0.1, a=a, max_w=w * 0.86)


def pict_memo(fig, cx, cy, h, a=1.0, z=2.4, written=0.0, line_text="", pencil=True):
    """メモ帳。written(0〜1)だけ1行目が書かれる。"""
    if a <= 0.01:
        return
    w = h * 0.80 * AR
    x, y = cx - w / 2, cy - h / 2
    _rect(fig, x, y, w, h, fc=CARD, ec=INK, lw=3.0, z=z, r=0.012, a=a)
    # 上のリング
    for i in range(5):
        px = x + w * (0.14 + 0.18 * i)
        _circ(fig, px, y + h - h * 0.02, h * 0.03, fc=CONNECT, ec=INK, lw=1.5, z=z + 0.1, a=a)
    # 罫線
    for i in range(4):
        ly = y + h * (0.72 - 0.17 * i)
        _line(fig, [(x + w * 0.10, ly), (x + w * 0.90, ly)], color=sf._mix(INK, CARD, 0.80),
              lw=2.0, z=z + 0.05, a=a)
    # 書かれる1行(緑の太線が左から伸びる)
    if written > 0.01:
        ly = y + h * 0.72 + h * 0.05
        x1 = x + w * 0.12 + w * 0.72 * written
        _line(fig, [(x + w * 0.12, ly), (x1, ly)], color=GREEN, lw=h * 28, z=z + 0.2, a=a)
        if line_text and written >= 0.99:
            _txt(fig, x + w * 0.50, ly, line_text, h * 120, color=INK, z=z + 0.3, a=a,
                 max_w=w * 0.74)
        if pencil:
            pl = h * 0.34
            ang = math.radians(35)
            px, py = x1, ly + h * 0.02
            dxp, dyp = math.cos(ang) * pl * AR * 0.56, math.sin(ang) * pl
            _line(fig, [(px, py), (px + dxp, py + dyp)], color=LIGHT, lw=h * 46, z=z + 0.4, a=a)
            _line(fig, [(px, py), (px + dxp, py + dyp)], color=INK, lw=h * 46 + 4, z=z + 0.39, a=a)
            _line(fig, [(px, py), (px + dxp * 0.12, py + dyp * 0.12)], color=INK, lw=h * 46, z=z + 0.41, a=a)


def pict_book(fig, cx, cy, h, a=1.0, z=2.4, tag=""):
    """開いた本。tag はしおりの文字。"""
    if a <= 0.01:
        return
    w = h * 1.35 * AR
    x, y = cx - w / 2, cy - h / 2
    # 見開き2ページ
    for side in (-1, 1):
        px = cx if side > 0 else x
        pts = [(px, y + h * 0.08), (px + w / 2 * (1 if side > 0 else 1), y + h * 0.08)]
        _poly(fig, [(cx, y + h * 0.10), (cx + side * w / 2, y),
                    (cx + side * w / 2, y + h * 0.92), (cx, y + h * 0.82)],
              fc=CARD, ec=INK, lw=3.0, z=z, a=a)
        for i in range(4):
            fy = y + h * (0.66 - 0.14 * i)
            k = 0.58 - 0.14 * i * 0.0
            _line(fig, [(cx + side * w * 0.08, fy - (0.0 if side > 0 else 0.0)),
                        (cx + side * w * 0.42, fy - side * 0.0 - h * 0.05 * (1 if False else 0))],
                  color=sf._mix(INK, CARD, 0.72), lw=2.5, z=z + 0.1, a=a)
    # 背
    _line(fig, [(cx, y + h * 0.10), (cx, y + h * 0.82)], color=INK, lw=4.0, z=z + 0.2, a=a)
    if tag:
        tw = h * 0.46 * AR
        _rect(fig, cx - tw / 2, y + h * 0.80, tw, h * 0.20, fc=RED, ec=INK, lw=2.5, z=z + 0.3,
              r=0.008, a=a)
        _txt(fig, cx, y + h * 0.90, tag, h * 130, color=CARD, z=z + 0.4, a=a, max_w=tw * 0.9,
             raw=True, fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)


def pict_train(fig, x, y, w, h, a=1.0, z=1.95):
    """電車の中(夜)。窓・つり革・座席。板の中に敷く背景。"""
    if a <= 0.01:
        return
    # 窓(夜の街)
    wy, wh = y + h * 0.52, h * 0.36
    _rect(fig, x + w * 0.04, wy, w * 0.92, wh, fc=NIGHT, ec=INK, lw=3.0, z=z, r=0.012, a=a)
    rng = np.random.RandomState(7)
    for _ in range(14):
        lx = x + w * (0.08 + 0.84 * rng.rand())
        ly = wy + wh * (0.10 + 0.55 * rng.rand())
        _rect(fig, lx, ly, w * 0.018, h * 0.02, fc=LIGHT, ec=LIGHT, lw=0, z=z + 0.05, r=0.0,
              a=a * 0.9)
    # つり革(上の棒から3つ)
    bar_y = y + h * 0.97
    _line(fig, [(x + w * 0.04, bar_y), (x + w * 0.96, bar_y)], color=INK, lw=5.0, z=z + 0.1, a=a)
    for k in (0.25, 0.5, 0.75):
        sx = x + w * k
        sway = 0.006 * tri(period=1.6) * (1 if k != 0.5 else -1)
        _line(fig, [(sx, bar_y), (sx + sway, bar_y - h * 0.10)], color=INK, lw=4.0, z=z + 0.1, a=a)
        _circ(fig, sx + sway, bar_y - h * 0.135, h * 0.035, fc=CARD, ec=INK, lw=4.0, z=z + 0.1, a=a)
    # 座席
    _rect(fig, x + w * 0.04, y + h * 0.20, w * 0.92, h * 0.22, fc="#5f7fb8", ec=INK, lw=3.0,
          z=z, r=0.012, a=a)
    _rect(fig, x + w * 0.04, y + h * 0.36, w * 0.92, h * 0.06, fc="#4a6aa3", ec=INK, lw=2.0,
          z=z + 0.05, r=0.006, a=a)


def pict_moon(fig, cx, cy, r, a=1.0, z=2.4):
    if a <= 0.01:
        return
    _circ(fig, cx, cy, r, fc=LIGHT, ec=INK, lw=3.0, z=z, a=a)
    _circ(fig, cx + r * 0.55 * AR, cy + r * 0.25, r * 0.85, fc=CARD, ec=CARD, lw=0, z=z + 0.05, a=a)


def pict_gate(fig, cx, yb, h, a=1.0, z=2.4):
    """改札(2本の柱と緑の矢印)。"""
    if a <= 0.01:
        return
    pw = h * 0.16 * AR
    for side in (-1, 1):
        px = cx + side * h * 0.20 * AR - pw / 2
        _rect(fig, px, yb, pw, h, fc="#cfd6dd", ec=INK, lw=3.0, z=z, r=0.010, a=a)
        _rect(fig, px + pw * 0.15, yb + h * 0.80, pw * 0.70, h * 0.10, fc=GREEN, ec=INK, lw=2.0,
              z=z + 0.1, r=0.004, a=a)
    # 足元の矢印
    ay = yb + h * 0.06
    _line(fig, [(cx - h * 0.10 * AR, ay), (cx + h * 0.10 * AR, ay)], color=GREEN, lw=h * 30,
          z=z + 0.2, a=a)
    _poly(fig, [(cx + h * 0.06 * AR, ay + h * 0.09), (cx + h * 0.18 * AR, ay),
                (cx + h * 0.06 * AR, ay - h * 0.09)], fc=GREEN, ec=GREEN, lw=0, z=z + 0.2, a=a)


def pict_sheet(fig, cx, cy, h, text, a=1.0, z=2.4, stamp=True):
    """評価の紙。赤い判子つき。"""
    if a <= 0.01:
        return
    w = h * 0.74 * AR
    x, y = cx - w / 2, cy - h / 2
    _rect(fig, x, y, w, h, fc=CARD, ec=INK, lw=3.0, z=z, r=0.008, a=a)
    _txt(fig, cx, y + h * 0.78, text, h * 200, z=z + 0.2, a=a, max_w=w * 0.9,
         fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
    for i in range(3):
        ly = y + h * (0.56 - 0.14 * i)
        _line(fig, [(x + w * 0.12, ly), (x + w * 0.88, ly)], color=sf._mix(INK, CARD, 0.75),
              lw=2.5, z=z + 0.1, a=a)
    if stamp:
        _circ(fig, x + w * 0.72, y + h * 0.20, h * 0.11, fc="none", ec=RED, lw=4.0, z=z + 0.3, a=a)
        _txt(fig, x + w * 0.72, y + h * 0.20, "印", h * 120, color=RED, z=z + 0.3, a=a,
             fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)


def pict_swirl(fig, cx, cy, r, a=1.0, z=2.5, color=CONNECT):
    """ぐるぐる(同じ考えが回る)。動画内時刻で回転する。"""
    if a <= 0.01:
        return
    ang0 = (F.LAST_T * 200.0) % 360.0
    for k in range(3):
        th1 = ang0 + k * 120
        fig.add_artist(Arc((cx, cy), 2 * r * AR, 2 * r, theta1=th1, theta2=th1 + 80,
                           transform=fig.transFigure, edgecolor=color, linewidth=r * 90,
                           zorder=z, alpha=a))
        th = math.radians(th1 + 80)
        hx, hy = cx + r * AR * math.cos(th), cy + r * math.sin(th)
        tx, ty = -math.sin(th) * AR, math.cos(th)
        nx, ny = math.cos(th) * AR, math.sin(th)
        s = r * 0.22
        _poly(fig, [(hx + tx * s * 1.4, hy + ty * s * 1.4),
                    (hx + nx * s, hy + ny * s), (hx - nx * s, hy - ny * s)],
              fc=color, ec=color, lw=0, z=z, a=a)


# ---------------------------------------------------------------- 場面(painter)
def _panel(fig, t, title=""):
    # 板は立ち絵(zorder 2.0)より下に敷く(上辺のトップライトが頭に被らないように)
    card(fig, CARD_L, CARD_BOT, CARD_R - CARD_L, CARD_TOP - CARD_BOT, z=1.9)
    head_title(fig, title, t)


def _pose(fig, name, cx=POSE_CX, top=POSE_TOP, height=POSE_H, flip=False):
    F.draw_pose(fig, name, cx=cx, top=top, height=height, flip=flip)


def train_think(name="03_troubled", bubble="あの時…", title=""):
    """帰りの電車。ずんだもんが吹き出しで引きずっている。"""
    def painter(fig, t):
        _panel(fig, t, title)
        pict_train(fig, CARD_L + 0.02, CARD_BOT + 0.02, CARD_R - CARD_L - 0.04,
                   CARD_TOP - CARD_BOT - 0.05, a=_fade(t, 0.0, 0.14))
        _pose(fig, name, cx=0.36, height=POSE_H)
        p = _pop(t, 0.30)
        if p > 0.01:
            a = _fade(t, 0.30)
            dy = _drift()
            mouth = F.mouth_xy(name, 0.36, POSE_TOP, POSE_H)
            bw, bh = 0.34 * p, 0.10 * p
            cxb, cyb = 0.70, CARD_TOP - 0.10 + dy
            tip = F.tail_tip((cxb - bw / 2, cyb - bh / 2), mouth, max_len=0.06)
            pict_bubble(fig, cxb, cyb, bw, bh, bubble, a=a, tip=tip, fs=44)
    return painter


def with_pict(name, draw, title="", flip=False, pose_cx=POSE_CX):
    """左に立ち絵、右に絵。draw(fig, t, a, dy) が絵を描く。"""
    def painter(fig, t):
        _panel(fig, t, title)
        _pose(fig, name, cx=pose_cx, flip=flip)
        a = _fade(t, 0.08, 0.18)
        if a > 0.01:
            draw(fig, t, a, _drift())
    return painter


def calendar_pair(name="03_troubled", left=("今日", "×"), right=("明日", "?"), title=""):
    """今日と明日の日めくり。"""
    def draw(fig, t, a, dy):
        h = 0.16
        p1 = min(1.0, _pop(t, 0.08))
        p2 = min(1.0, _pop(t, 0.30))
        pict_calendar(fig, 0.55, PICT_CY + dy, h * p1, left[0], a=a, mark=left[1] if t > 0.45 else None)
        pict_calendar(fig, 0.80, PICT_CY + dy, h * p2, right[0], a=_fade(t, 0.30),
                      mark=right[1] if t > 0.62 else None)
    return with_pict(name, draw, title)


def calendar_one(name="03_troubled", label="明日", mark="×", title="", bubble=""):
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_calendar(fig, PICT_CX, PICT_CY - 0.035 + dy, 0.22 * p, label, a=a,
                      mark=mark if t > 0.50 else None)
        if bubble:
            pict_bubble(fig, PICT_CX, CARD_TOP - 0.04 + dy, 0.30, 0.065, bubble,
                        a=_fade(t, 0.55), fs=40)
    return with_pict(name, draw, title)


def bubble_locked(name="03_troubled", text="……", title=""):
    """言ってしまった一言に鍵がかかる(もう変えられない)。"""
    def draw(fig, t, a, dy):
        mouth = F.mouth_xy(name, POSE_CX, POSE_TOP, POSE_H)
        p = min(1.0, _pop(t, 0.08))
        bw, bh = 0.36 * p, 0.13 * p
        cxb, cyb = PICT_CX, PICT_CY + 0.05 + dy
        tip = F.tail_tip((cxb - bw / 2, cyb - bh / 2), mouth, max_len=0.07)
        pict_bubble(fig, cxb, cyb, bw, bh, text, a=a, tip=tip, fs=54, color=CONNECT)
        pict_lock(fig, cxb, cyb - 0.11 + dy, 0.12, a=_fade(t, 0.45))
    return with_pict(name, draw, title)


def thinking_loop(name="03_troubled", title=""):
    """考えても回るだけ(ぐるぐる+鍵)。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        r = 0.10 * p
        pict_bubble(fig, PICT_CX, PICT_CY + dy, 0.40 * p, 0.30 * p, "", a=a)
        pict_swirl(fig, PICT_CX, PICT_CY + 0.02 + dy, r, a=a)
        pict_lock(fig, PICT_CX, PICT_CY + 0.02 + dy, 0.075, a=_fade(t, 0.40), pulse=False)
    return with_pict(name, draw, title)


def boss_crowd(name="03_troubled", title=""):
    """上司の機嫌と、周りの評判。どちらにも鍵。"""
    def draw(fig, t, a, dy):
        p1 = min(1.0, _pop(t, 0.08))
        pict_boss(fig, 0.55, CARD_BOT + 0.05 + dy, 0.22 * p1, a=a)
        pict_lock(fig, 0.55, CARD_BOT + 0.315 + dy, 0.07, a=_fade(t, 0.40))
        a2 = _fade(t, 0.32)
        p2 = min(1.0, _pop(t, 0.32))
        for i, cx in enumerate((0.77, 0.85, 0.93)):
            pict_person(fig, cx, CARD_BOT + 0.05 + (0.025 if i == 1 else 0.0) + dy,
                        0.13 * p2, a=a2)
        pict_lock(fig, 0.85, CARD_BOT + 0.315 + dy, 0.07, a=_fade(t, 0.55))
        _txt(fig, 0.55, CARD_TOP - 0.028 + dy, "上司の機嫌", 36, color=CONNECT, z=2.6, a=a)
        _txt(fig, 0.85, CARD_TOP - 0.028 + dy, "周りの評判", 36, color=CONNECT, z=2.6, a=a2)
    return with_pict(name, draw, title)


def boss_sheet(name="03_troubled", text="評価", title=""):
    """上司が評価の紙に判子。鍵。"""
    def draw(fig, t, a, dy):
        p1 = min(1.0, _pop(t, 0.08))
        pict_boss(fig, 0.56, CARD_BOT + 0.05 + dy, 0.26 * p1, a=a, mood="flat")
        p2 = min(1.0, _pop(t, 0.28))
        pict_sheet(fig, 0.80, PICT_CY - 0.045 + dy, 0.21 * p2, text, a=_fade(t, 0.28))
        pict_lock(fig, 0.80, CARD_TOP - 0.045 + dy, 0.07, a=_fade(t, 0.50))
    return with_pict(name, draw, title)


def ask_what(name="01_base", locked=("機嫌", "評判", "評価"), title=""):
    """じゃあ変えられるのは? 鍵つきの3つは薄く、大きな「?」。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_bubble(fig, PICT_CX, PICT_CY + 0.06 + dy, 0.40 * p, 0.17 * p, "?", a=a, fs=120,
                    color=RED)
        for i, lab in enumerate(locked):
            cx = 0.52 + 0.14 * i
            ai = _fade(t, 0.25 + 0.08 * i) * 0.55
            pict_lock(fig, cx, CARD_BOT + 0.10 + dy, 0.07, a=ai, pulse=False)
            _txt(fig, cx, CARD_BOT + 0.035 + dy, lab, 34, color=CONNECT, z=2.6, a=ai)
    return with_pict(name, draw, title)


def tomorrow_line(name="02_point", title=""):
    """明日の日めくりに吹き出し+緑のチェック(唯一、自分で変えられるもの)。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_calendar(fig, PICT_CX, PICT_CY - 0.04 + dy, 0.22 * p, "明日", a=a,
                      mark="check" if t > 0.55 else None)
        pict_bubble(fig, PICT_CX + 0.02, CARD_TOP - 0.04 + dy, 0.30, 0.065, "なに言う?",
                    a=_fade(t, 0.35), fs=38)
    return with_pict(name, draw, title)


def who_silhouette(name="02_point", title=""):
    """誰が言い出した? 顔に「?」の影絵。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_person(fig, PICT_CX, CARD_BOT + 0.05 + dy, 0.24 * p, a=a, face="?")
        pict_bubble(fig, PICT_CX, CARD_TOP - 0.04 + dy, 0.26, 0.065, "誰?", a=_fade(t, 0.35), fs=40)
    return with_pict(name, draw, title)


def ancient_person(name="04_surprised", tag="1900年前", label="奴隷", title=""):
    """1900年前の人(貫頭衣)と札。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_person(fig, PICT_CX, CARD_BOT + 0.05 + dy, 0.24 * p, a=a, tunic=True)
        a2 = _fade(t, 0.40)
        _rect(fig, PICT_CX - 0.12, CARD_TOP - 0.075 + dy, 0.24, 0.058, fc=RED, ec=INK, lw=2.5,
              z=2.6, r=0.010, a=a2)
        _txt(fig, PICT_CX, CARD_TOP - 0.046 + dy, tag, 44, color=CARD, z=2.7, a=a2, raw=True,
             fontfamily=[F.NUM_FAMILY], fontweight=F.NUM_WEIGHT)
        _txt(fig, PICT_CX, CARD_BOT + 0.035 + dy, label, 40, color=CONNECT, z=2.6, a=a)
    return with_pict(name, draw, title)


def owned(name="04_surprised", title=""):
    """主人(月桂冠)が、奴隷の体も持ち物も持っている。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_person(fig, 0.84, CARD_BOT + 0.07 + dy, 0.26 * p, a=a, tunic=True, laurel=True)
        _txt(fig, 0.84, CARD_BOT + 0.035 + dy, "主人", 40, color=CONNECT, z=2.6, a=a)
        a2 = _fade(t, 0.28)
        p2 = min(1.0, _pop(t, 0.28))
        pict_person(fig, 0.55, CARD_BOT + 0.07 + dy, 0.18 * p2, a=a2, tunic=True)
        _txt(fig, 0.55, CARD_BOT + 0.035 + dy, "奴隷", 40, color=CONNECT, z=2.6, a=a2)
        # 持ち物(袋)は奴隷と主人のあいだの足元
        a3 = _fade(t, 0.45)
        bx, by = 0.69, CARD_BOT + 0.07 + dy
        _poly(fig, [(bx - 0.035, by), (bx + 0.035, by), (bx + 0.028, by + 0.05), (bx - 0.028, by + 0.05)],
              fc="#c9a46a", ec=INK, lw=2.5, z=2.5, a=a3)
        _line(fig, [(bx - 0.028, by + 0.05), (bx + 0.028, by + 0.05)], lw=5.0, z=2.55, a=a3)
        # 主人の手から2本の線(体と持ち物へ)
        a4 = _fade(t, 0.55)
        hx, hy = 0.78, CARD_BOT + 0.20 + dy
        _line(fig, [(hx, hy), (0.60, CARD_BOT + 0.16 + dy)], color=PURPLE, lw=4.0, z=2.45, a=a4)
        _line(fig, [(hx, hy), (bx, by + 0.05)], color=PURPLE, lw=4.0, z=2.45, a=a4)
        pict_lock(fig, 0.55, CARD_BOT + 0.315 + dy, 0.065, a=a4, pulse=False)
        _txt(fig, 0.62, CARD_TOP - 0.028 + dy, "体も持ち物も主人の", 34, color=CONNECT, z=2.6, a=a4)
    return with_pict(name, draw, title)


def slave_sees(name="05_happy", title=""):
    """奴隷は、自分で変えられることだけを見た(緑のチェックの吹き出し)。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_person(fig, 0.58, CARD_BOT + 0.06 + dy, 0.30 * p, a=a, tunic=True)
        _txt(fig, 0.58, CARD_BOT + 0.035 + dy, "奴隷", 40, color=CONNECT, z=2.6, a=a)
        a2 = _fade(t, 0.35)
        pict_bubble(fig, 0.80, PICT_CY + 0.06 + dy, 0.24, 0.16, "", a=a2)
        pict_check(fig, 0.80, PICT_CY + 0.06 + dy, 0.11, a=a2)
        for i, cx in enumerate((0.74, 0.86)):
            pict_lock(fig, cx, CARD_BOT + 0.10 + dy, 0.06, a=_fade(t, 0.20) * 0.35, pulse=False)
    return with_pict(name, draw, title)


def book_now(name="05_happy", tag="1900年前", title=""):
    """本になって今も残っている。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        pict_book(fig, PICT_CX, PICT_CY + 0.03 + dy, 0.19 * p, a=a, tag=tag)
        pict_bubble(fig, PICT_CX, CARD_BOT + 0.055 + dy, 0.28, 0.06, "いまも読める",
                    a=_fade(t, 0.40), fs=34)
    return with_pict(name, draw, title)


def tonight(name="02_point", title=""):
    """今夜(月)+ 明日の日めくり + 鉛筆。"""
    def draw(fig, t, a, dy):
        pict_moon(fig, 0.86, CARD_TOP - 0.07 + dy, 0.04, a=a)
        p = min(1.0, _pop(t, 0.08))
        pict_calendar(fig, 0.62, PICT_CY - 0.01 + dy, 0.24 * p, "明日", a=a,
                      mark="check" if t > 0.55 else None)
        pict_bubble(fig, 0.62, CARD_BOT + 0.065 + dy, 0.30, 0.065, "決めるだけ",
                    a=_fade(t, 0.40), fs=36)
    return with_pict(name, draw, title)


def memo_write(name="05_happy", line_text="", title=""):
    """メモに1行。書く線が伸びる。"""
    def draw(fig, t, a, dy):
        p = min(1.0, _pop(t, 0.08))
        w = min(1.0, max(0.0, (sf._prog(t) - 0.30) / 0.45))
        pict_memo(fig, PICT_CX, PICT_CY + dy, 0.28 * p, a=a, written=w, line_text=line_text)
    return with_pict(name, draw, title)


def go_home(name="05_happy", title=""):
    """改札を抜けて帰る。上司は後ろで薄く、鍵つき。"""
    def draw(fig, t, a, dy):
        pict_boss(fig, 0.57, CARD_BOT + 0.06 + dy, 0.17, a=a * 0.35)
        pict_lock(fig, 0.57, CARD_BOT + 0.29 + dy, 0.06, a=a * 0.45, pulse=False)
        p = min(1.0, _pop(t, 0.20))
        pict_gate(fig, 0.80, CARD_BOT + 0.05 + dy, 0.26 * p, a=_fade(t, 0.20))
    return with_pict(name, draw, title, flip=True)
