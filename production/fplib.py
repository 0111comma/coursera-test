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
from matplotlib.patches import Ellipse
import numpy as np
from PIL import Image

import shortlib as S

ROOT = Path(__file__).resolve().parent.parent
POSE_DIR = ROOT / "assets" / "character"
FONT_DIR = ROOT / "assets" / "fonts"

# **丸ゴシック**。競合のテロップはこれで、Noto Sans CJK の角ばった字形とは
# 別物に見える(2026-08-23、ユーザー指摘「まずフォントどうにかして」)。
# M PLUS Rounded 1c は SIL Open Font License 1.1。assets/fonts/README.md 参照
FONT_FAMILY = "Rounded Mplus 1c Black"

# ---- 配色(競合の実測値に寄せた)
CREAM = "#f3e7d3"          # 背景。明るさ 0.75 前後
DOT = "#faf1e2"            # 背景のドット
BAND = "#f9cb45"           # 上部のタイトル帯(下側)
BAND_LO = "#eda520"        # 帯の上側。**縦のグラデーション**にする
BAND_INK = "#3b2c10"       # 帯の文字
TELOP = "#ffffff"          # テロップの本文
TELOP_EMPH = "#ffd93d"     # テロップの強調(数字)
TELOP_EDGE = "#7b2d00"     # テロップの縁。**stroke_fx が黒を焼いていて、この色は
                           # 使われていなかった**(2026-08-23に接続)
TELOP_SHADOW = (3.0, -4.0, "#4a2a05", 0.42)   # 下に落ちる影。背景から浮かせる
INK_DARK = "#2b2b28"

TITLE = ""                 # 上部の帯に出す文字(use_fp_theme で設定)
BADGE = ""                 # 仮定の明示(戦略§6-2「利回りは仮定と明示」)
_POSE_CACHE: dict[str, Image.Image] = {}


def use_fp_theme(title: str, speaker: int = 14, badge: str = ""):
    """明るい背景・大きい字幕・上部のタイトル帯に切り替える。

    speaker=14 は冥鳴ひまり(2026-08-23 決定)。
    """
    global TITLE, BADGE
    TITLE = title
    BADGE = badge
    S.SURFACE = CREAM
    S.INK = INK_DARK
    S.DEFAULT_SPEAKER = speaker
    # 字幕: 3.8% → 5.7%(競合の実測)。2行を常用するので折り返しも広げる
    S.SUB_FS = 84
    S.SUB_WRAP = 11
    S.SUB_BLOCK_FIT = 0.86
    S.SUB_LINE_H = 0.052
    S.SUBTITLE_Y = 0.235
    S.STROKE_EDGE = TELOP_EDGE
    S.STROKE_SHADOW = TELOP_SHADOW
    S.new_canvas = _canvas
    S.draw_subtitle = _subtitle
    S.save_frame = _save_frame
    _setup_font()


def _setup_font():
    """丸ゴシックを登録して、この動画のあいだだけ既定にする。
    **shortlib.setup_fonts() は触らない**(既存30本の見た目を変えないため)。"""
    from matplotlib import font_manager
    files = sorted(FONT_DIR.glob("MPLUSRounded1c-*.ttf"))
    if not files:
        raise SystemExit(f"丸ゴシックが無い: {FONT_DIR}/MPLUSRounded1c-900.ttf")
    for f in files:
        font_manager.fontManager.addfont(str(f))
    plt.rcParams["font.family"] = FONT_FAMILY
    plt.rcParams["font.weight"] = 900        # Black の1ウェイトしかない


CHROME_GID = "fp_chrome"   # 帯・バッジ。ゲートの集計から外す印


def _canvas(t_global: float = 0.0):
    fig = plt.figure(figsize=S.FIGSIZE, dpi=S.DPI)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1], zorder=-10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # ドット(競合と同じ質感)
    # **大きく・まばらに**(競合の実測: 間隔が幅の約5.3%、半径が約1.0%)。
    # 0.024/0.0065 は目が細かすぎて、網目の生地のように見えていた
    step = 0.053
    r = 0.0100
    j = 0
    y = 0.0
    while y < 1.0:
        x = (j % 2) * step / 2
        while x < 1.0:
            # **円で描くと縦に伸びる**(軸は0〜1だが画面は1080×1920)。
            # 楕円で縦横比を打ち消して、競合と同じ真円にする
            ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * S.W / S.H,
                                 color=DOT, zorder=-9))
            x += step
        y += step * (S.W / S.H)
        j += 1
    # 上部のタイトル帯。**単色の板ではなく縦のグラデーション**にする。
    # 帯とバッジは全フレーム共通の装飾なので gid で印を付けて、
    # 図のゲート(figure/align/overlap)の集計から外す。印が無いと
    # 「15字以上の文字列が2個」が全ユニットで鳴り、本当の指摘が埋もれる
    from matplotlib.colors import LinearSegmentedColormap
    h = 0.098
    bax = fig.add_axes([0, 1 - h, 1, h], zorder=3.0)
    bax.imshow(np.linspace(1, 0, 64).reshape(-1, 1), aspect="auto", extent=(0, 1, 0, 1),
               cmap=LinearSegmentedColormap.from_list("fpband", [BAND_LO, BAND]))
    bax.axis("off")
    bax.set_gid(CHROME_GID)
    if TITLE:
        # 白抜き + 濃い縁 + 影(競合と同じ)。濃い字を黄色に乗せるより遠くで読める
        S.text_fit(fig, 0.5, 1 - h / 2, TITLE, ha="center", va="center",
                   color="#ffffff", fontsize=44, max_w=0.92, zorder=3.1,
                   path_effects=S.stroke_fx("#ffffff", outline=7.0)).set_gid(CHROME_GID)
    if BADGE:
        # 仮定の明示。**画面のどこかに常に出しておく**(戦略§6-2)
        S.text_fit(fig, 0.5, 1 - h - 0.026, BADGE, ha="center", va="center",
                   color="#8a7f6c", fontsize=26,
                   max_w=0.92, zorder=3.1).set_gid(CHROME_GID)
    return fig


def hide_chrome(fig):
    """帯・バッジを消す。カバーとサムネは全面を使うので、上から重ねない。
    帯は zorder 3.0 でカバーの黄色(1.5)より上にいるため、消さないと
    カバーの1行目に文字が重なる(check_overlap がループ72で検出)。"""
    for art in list(fig.artists) + list(fig.texts) + list(fig.axes):
        if art.get_gid() == CHROME_GID:
            art.remove()


def _subtitle(fig, text: str, pop: float = 1.0, tag: str | None = None):
    """大きい縁取りテロップ。**帯は敷かない**(競合は背景の上に直接置いている)。

    3行以上になったら**上に伸ばす**。下に伸ばすと Shorts のUI(下12〜15%)に入る。
    2行目・3行目の位置は2行のときと同じになるので、行数が変わってもブレない。
    (2026-08-23。ユーザー指示「文字制限かけて何言ってるかよくわからない文章に
     なるなら文字制限かけない方がいい」を受け、長い文も描けるようにした)
    """
    n = len(S.wrap_plain(text.replace("【", "").replace("】", ""), S.SUB_WRAP))
    step = S.SUB_LINE_H * (S.SUB_FS * pop / 40)
    y = S.SUBTITLE_Y + max(0, n - 2) * step
    S.draw_rich_text(fig, 0.5, y, text, S.SUB_FS * pop,
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
        im = Image.open(p).convert("RGBA")
        # **透明の余白を切り落とす。** 切り抜きPNGは1024×1024の中に人物が
        # 浮いているので、そのまま置くと軸の枠だけが画面外にはみ出し、
        # check_overlap が「画面外」を毎シーン鳴らす(絵は見えていないのに)。
        box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if box:
            im = im.crop(box)
        _POSE_CACHE[name] = _fade_bottom(im)
    return _POSE_CACHE[name]


def _fade_bottom(im: Image.Image, frac: float = 0.07) -> Image.Image:
    """絵の下端を透明へ落とす。

    素材は腰のあたりで真横に切れているので、そのまま置くと
    ドットの背景の上に**硬い水平の切り口**が出る(2026-08-23の見比べ)。
    """
    a = np.asarray(im.getchannel("A"), dtype=np.float32)
    h = a.shape[0]
    n = max(1, int(h * frac))
    ramp = np.linspace(1.0, 0.0, n, dtype=np.float32)[:, None]
    a[h - n:] *= ramp
    out = im.copy()
    out.putalpha(Image.fromarray(a.astype("uint8"), mode="L"))
    return out


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
