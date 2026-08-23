#!/usr/bin/env python3
"""イラストから背景を抜いて透過PNGにする。**緑背景を推奨。**

## なぜ緑を勧めるのか(2026-08-23に実物で確かめた)

白背景だと「背景の白」と「キャラの白」が同じ色になり、**幾何だけでは判別できない**。
1枚目のキャラで実測した結果:

| 領域 | 面積 | 外の背景までの距離 | 本当は |
|---|---|---|---|
| 胸元のインナー | 11841px | 134px | 残す |
| 腕と腰のあいだ | 6150px | 141px | 消す |
| 髪のあいだ | 357px | 15px | 消す |
| 目の白 | 181px | 73px | 残す |

- **面積で切ると**、目(181px)より髪のあいだ(357px)が大きく、**目が消える**
- **距離で切ると**、髪のあいだ(15px)は消せるが、
  **腕と腰(141px)とインナー(134px)が区別できない**

つまり白背景では原理的に無理。**背景をキャラに無い色にすれば全部解決する。**

## 使い方

    python3 production/cutout.py assets/character/01_base.jpg

緑背景なら自動で緑を抜く。白背景しか無いときは距離の規則で近似する
(髪のあいだは消えるが、腕と体のあいだのような「奥の隙間」は残る)。
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

WHITE_TH = 232     # 白背景とみなす明るさ
GREEN_TOL = 70     # 緑背景からの許容色差
NEAR_EDGE = 40     # 白背景のとき「外に近い囲み」を背景とみなす距離(画素)
FEATHER = 1


def _flood_from_border(mask):
    """外周から繋がっている mask の画素だけを True にして返す。"""
    H, W = mask.shape
    out = np.zeros((H, W), dtype=bool)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if mask[y, x] and not out[y, x]:
                out[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if mask[y, x] and not out[y, x]:
                out[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True; q.append((ny, nx))
    return out


def _dist_from(mask):
    """mask からの最短距離(4近傍・幅優先)。"""
    H, W = mask.shape
    d = np.full((H, W), 10 ** 9, dtype=np.int32)
    d[mask] = 0
    q = deque(zip(*np.where(mask)))
    while q:
        y, x = q.popleft()
        nd = d[y, x] + 1
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and d[ny, nx] > nd:
                d[ny, nx] = nd; q.append((ny, nx))
    return d


def detect_bg_kind(A):
    """四隅を見て、緑背景か白背景かを決める。"""
    corners = np.concatenate([A[:12, :12].reshape(-1, 3), A[:12, -12:].reshape(-1, 3),
                              A[-12:, :12].reshape(-1, 3), A[-12:, -12:].reshape(-1, 3)])
    m = corners.mean(axis=0)
    if m[1] > m[0] + 40 and m[1] > m[2] + 40:
        return "green", m
    if m.min() >= WHITE_TH:
        return "white", m
    return "unknown", m


def cutout(src: Path):
    im = Image.open(src).convert("RGB")
    A = np.asarray(im, dtype=np.uint8)
    kind, corner = detect_bg_kind(A)

    if kind == "green":
        d = np.abs(A.astype(np.int16) - corner.astype(np.int16)).sum(axis=2)
        bg = d <= GREEN_TOL
        bg = _flood_from_border(bg) | bg          # 囲まれた緑も背景
        note = "緑背景(色で判定。目もインナーも自動で残る)"
    elif kind == "white":
        light = A.min(axis=2) >= WHITE_TH
        bg = _flood_from_border(light)
        # 外に近い囲み(髪のあいだ等)だけ背景に足す。**目は奥にあるので残る**
        dist = _dist_from(bg)
        rest = light & ~bg
        H, W = bg.shape
        seen = np.zeros((H, W), dtype=bool)
        for sy in range(H):
            for sx in range(W):
                if not rest[sy, sx] or seen[sy, sx]:
                    continue
                seen[sy, sx] = True
                q = deque([(sy, sx)]); px = []
                while q:
                    y, x = q.popleft(); px.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and rest[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
                if min(dist[y, x] for y, x in px) <= NEAR_EDGE:
                    for y, x in px:
                        bg[y, x] = True
        note = "白背景(近似。奥の隙間は残る。**緑背景を推奨**)"
    else:
        raise SystemExit(f"{src.name}: 背景が白でも緑でもない(四隅 {corner.round(0)})")

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    if FEATHER:
        alpha = np.asarray(Image.fromarray(alpha).filter(
            ImageFilter.GaussianBlur(FEATHER)), dtype=np.uint8)
    dst = src.with_suffix(".png")
    Image.fromarray(np.dstack([A, alpha]), "RGBA").save(dst)
    return dst, kind, note, bg.mean() * 100


def main():
    for a in sys.argv[1:]:
        p = Path(a)
        dst, kind, note, bgpct = cutout(p)
        print(f"{p.name} → {dst.name}  [{kind}] 背景 {bgpct:.1f}%")
        print(f"   {note}")


if __name__ == "__main__":
    main()
