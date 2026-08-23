#!/usr/bin/env python3
"""白背景のイラストから背景だけを抜いて、透過PNGにする。

**しきい値で「白い画素を消す」やり方は使えない。**
キャラの白いブラウスやハイライトまで一緒に消える(2026-08-23に実際に確認)。
外周から繋がっている白だけを、塗りつぶし(flood fill)でたどって消す。

使い方:
    python3 production/cutout.py assets/character/01_base.jpg
    python3 production/cutout.py assets/character/*.jpg
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

THRESH = 232      # これ以上明るい画素を「背景候補」とみなす
FEATHER = 1       # 境界をやわらげる画素数
KEEP_MIN = 0.010  # 囲まれた白のうち、この割合以上だけ「服」として残す


def cutout(src: Path, thresh: int = THRESH) -> Path:
    im = Image.open(src).convert("RGB")
    A = np.asarray(im, dtype=np.uint8)
    H, W, _ = A.shape
    light = A.min(axis=2) >= thresh          # 明るい画素

    # 外周から繋がっている明るい画素だけを背景とする(幅優先で塗る)
    bg = np.zeros((H, W), dtype=bool)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and light[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))

    # **外周から届かない「囲まれた白」も背景のことがある。**
    # 2026-08-23に実物で確認: 髪と肩のあいだの隙間、腕と身頃のあいだが
    # 白いまま残り、動画の実寸ではっきり見えた。
    # ただし**白いVネックのインナーも囲まれた白**なので、全部消すと服が抜ける。
    # 実測すると、インナーは1.13%・隙間は0.59%以下だったので、
    # **大きい囲み(=服)だけ残して、小さい囲みは背景として消す**。
    rest = light & ~bg
    seen = np.zeros((H, W), dtype=bool)
    for sy in range(H):
        for sx in range(W):
            if not rest[sy, sx] or seen[sy, sx]:
                continue
            seen[sy, sx] = True
            qq = deque([(sy, sx)])
            px = []
            while qq:
                y, x = qq.popleft()
                px.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and rest[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        qq.append((ny, nx))
            if len(px) < KEEP_MIN * H * W:          # 小さい囲みは背景
                for y, x in px:
                    bg[y, x] = True

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    if FEATHER:
        from PIL import ImageFilter
        alpha = np.asarray(Image.fromarray(alpha).filter(
            ImageFilter.GaussianBlur(FEATHER)), dtype=np.uint8)
    out = np.dstack([A, alpha])
    dst = src.with_suffix(".png")
    Image.fromarray(out, "RGBA").save(dst)
    return dst, bg.mean() * 100, (~bg).mean() * 100


def main():
    for a in sys.argv[1:]:
        p = Path(a)
        dst, bgpct, subpct = cutout(p)
        im = Image.open(dst)
        al = np.asarray(im)[:, :, 3]
        ys, xs = np.where(al > 128)
        print(f"{p.name} → {dst.name}")
        print(f"   背景 {bgpct:.1f}% / 被写体 {subpct:.1f}%")
        print(f"   被写体の範囲 x {xs.min()/im.width:.3f}〜{xs.max()/im.width:.3f}"
              f" / y {ys.min()/im.height:.3f}〜{ys.max()/im.height:.3f}")


if __name__ == "__main__":
    main()
