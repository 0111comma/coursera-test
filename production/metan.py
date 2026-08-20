"""四国めたん立ち絵(VOICEVOX公式ポートレート+トークボブ)。

素材: assets/metan/portrait.png(300×500・透過。GitHub VOICEVOX/voicevox_resource 由来)。
音声クレジット「VOICEVOX:四国めたん」で商用可(assets/metan/policy.md 原文)。
キャラクター利用は東北ずん子ガイドライン準拠。

静止画のため口パクは無い。会話の見せ方は duo-skit-2026-08.md の調査どおり:
  - 話しているとき: トークボブ(音声RMS連動で小さく上下)+呼吸
  - 話していないとき: 減光(alpha)+呼吸だけ
坂本アヒル様のパーツ分割PSDが手に入ったら zunda.py と同じ方式に置き換える。
"""
import math
from pathlib import Path

import numpy as np

ASSET = Path(__file__).resolve().parent / "assets" / "metan" / "portrait.png"
_CACHE: dict[str, "np.ndarray"] = {}

# 全身(300×500)のままだとずんだもん(バストアップ素材)より画面上で小さすぎるので、
# 上半身(頭〜腰)でクロップして大きさを揃える(duo_metan.png での目視結果)
CROP_H = 290
ART_W, ART_H = 300, CROP_H


def _img(flip: bool = False):
    key = "flip" if flip else "base"
    if key not in _CACHE:
        from PIL import Image
        arr = np.asarray(Image.open(ASSET).convert("RGBA"))[:CROP_H]
        if flip:
            arr = arr[:, ::-1].copy()
        _CACHE[key] = arr
    return _CACHE[key]


def talk_bob_px(t: float, talking: bool) -> float:
    """トークボブ: 話している間だけ約4Hzで最大6px(素材500px基準)上下する。"""
    if not talking:
        return 0.0
    return 6.0 * abs(math.sin(2.0 * math.pi * 2.0 * t))


def draw_metan(ax, dy_px: float = 0.0, alpha: float = 1.0, flip: bool = False):
    """立ち絵を描く。ax=専用オーバーレイaxes(縦横比は呼び出し側のrectで合わせる)。
    dy_px: 上下(素材500px基準) / alpha: 減光(非話者=0.72) / flip: 左右反転"""
    arr = _img(flip)
    h, w = arr.shape[:2]
    ax.imshow(arr, extent=[0, w, h, 0], interpolation="bilinear", aspect="auto", alpha=alpha)
    ax.set_xlim(0, w)
    ax.set_ylim(h - dy_px, -dy_px)
    ax.autoscale(False)
