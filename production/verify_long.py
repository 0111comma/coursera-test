#!/usr/bin/env python3
"""焼き上がった長尺のmp4そのものを測る検収ゲート(2026-08-22)。

なぜ台本のゲートと別に要るか:
  この日に見つかった不具合は、**どれも台本を読んでも出てこなかった**。
    - 字幕帯より上の画素が15〜20秒まったく変わらない(静止)
    - 真のピークが -0.2 dBTP しかなく、YouTube側の再エンコードで歪む
    - サムネの金の行が左右の立ち絵を突き抜けている
  出来上がったファイルを開いて数えるだけで出た。**だから出荷前に必ず測る。**

使い方:
    python3 production/verify_long.py videos/L001-nisa-son
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def ffprobe_dur(mp4):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "json", str(mp4)])
    try:
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return None


def loudness(mp4):
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(mp4), "-af",
         "loudnorm=I=-14:TP=-1.5:print_format=summary", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    g = lambda k: (re.search(rf"{k}:\s*(-?[\d.]+)", err) or [None, None])[1]
    return g("Input Integrated"), g("Input True Peak"), g("Input LRA")


def static_runs(vdir):
    """字幕帯より上が変わらないまま続く区間を、**実フレーム**から測る。"""
    import numpy as np
    from PIL import Image
    work = vdir / "output" / "work"
    pngs = sorted(work.glob("frame_*.png"),
                  key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)])
    if not pngs:
        return None
    byu = {}
    for p in pngs:
        byu.setdefault(int(re.findall(r"frame_(\d+)_", p.name)[0]), []).append(p)

    def top(p):
        a = np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
        return a[: int(a.shape[0] * 0.74)]

    worst, cur, start = 0, None, None
    runs = []
    for u in sorted(byu):
        last = byu[u][-1]
        if cur is not None:
            d = (np.abs(top(cur) - top(last)).max(axis=2) > 8).mean()
            if d < 0.001:                       # 画面が変わっていない
                if start is None:
                    start = u - 1
                cur = last
                continue
        if start is not None:
            runs.append((start, u - 1))
            start = None
        cur = last
    if start is not None:
        runs.append((start, max(byu)))
    return runs


def main():
    for arg in sys.argv[1:]:
        vdir = Path(arg).resolve()
        vid = vdir.name.split("-")[0]
        mp4 = vdir / "output" / f"{vid}.mp4"
        print(f"\n=== {vdir.name} ===")
        if not mp4.exists():
            print("  [NG] mp4が無い")
            continue
        bad = []
        d = ffprobe_dur(mp4)
        print(f"  尺: {d:.1f}秒({d/60:.2f}分) / {mp4.stat().st_size/1e6:.1f}MB")
        i, tp, lra = loudness(mp4)
        print(f"  音: 統合 {i} LUFS / 真のピーク {tp} dBTP / LRA {lra} LU")
        if i and abs(float(i) + 14) > 1.0:
            bad.append(f"統合ラウドネスが -14 から {float(i)+14:+.1f} LU ずれている")
        if tp and float(tp) > -0.4:
            bad.append(f"真のピーク {tp} dBTP。ヘッドルームが無く再エンコードで歪む")
        runs = static_runs(vdir)
        if runs is None:
            print("  静止: 中間フレームが無いので測れない(work/を消したあと)")
        else:
            longest = max((b - a + 1 for a, b in runs), default=0)
            print(f"  静止: 変わらない区間 {len(runs)}個 / 最長 {longest}ユニット連続")
            if longest >= 4:
                bad.append(f"画面が変わらないまま {longest}ユニット続く区間がある")
        th = vdir / "output" / "thumbnail.png"
        if th.exists():
            import numpy as np
            from PIL import Image
            a = np.asarray(Image.open(th).convert("RGB"), dtype=np.int16)
            h, w, _ = a.shape
            band = a[int(h * 0.62):int(h * 0.74)]
            r, g, b = band[:, :, 0], band[:, :, 1], band[:, :, 2]
            gold = (r > 200) & (g > 140) & (g < 215) & (b < 95)
            xs = np.where(gold.any(axis=0))[0]
            if len(xs):
                lo, hi = xs.min() / w, xs.max() / w
                print(f"  サムネの金の行: {lo*100:.1f}%〜{hi*100:.1f}%(空き帯 25.5%〜77.3%)")
                if lo < 0.255 or hi > 0.773:
                    bad.append("サムネの金の行が立ち絵に重なっている")
        else:
            bad.append("thumbnail.png が無い")
        print("  → " + ("合格" if not bad else "不合格: " + " / ".join(bad)))
        if bad:
            globals().setdefault("_ng", []).append(vdir.name)
    if globals().get("_ng"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
