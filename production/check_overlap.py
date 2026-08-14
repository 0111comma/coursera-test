#!/usr/bin/env python3
"""レイアウト衝突の機械チェック(ループ㊵)。

目視でしか見つけられなかった不具合を恒久的に潰すためのゲート。
各動画の render.py の SCENES を実際に描画し、すべての Text/Patch の
描画範囲を測って、次の3つの禁止領域との重なりを検出する。

  1. 立ち絵(CHARA_RECTS["bl"] = x 0.000-0.342 / y 0.245-0.465)
  2. 注記バッジ(draw_badge。右上 y=0.83 付近)
  3. 字幕帯(画面下部 y<0.245)

重なると「文字の上に立ち絵が乗る」「バッジと見出しが重なる」といった
読めない画面になる。人が見る前にここで落とす。

使い方:
    python3 production/check_overlap.py                    # 全動画
    python3 production/check_overlap.py videos/S010-...    # 1本だけ
"""
import importlib.util
import sys
import warnings
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

import matplotlib
matplotlib.use("Agg")
import shortlib as S  # noqa: E402

# 禁止領域(figure座標 x0, y0, x1, y1)
CHARA = (0.000, 0.245, 0.342, 0.465)     # 立ち絵(bl)
SUBTITLE = (0.000, 0.000, 1.000, 0.245)  # 字幕帯
# バッジは draw_badge のアンカー(0.90, 0.83)で実体を特定し、実測範囲を禁止領域にする
BADGE_ANCHOR = (0.90, 0.83)
FOOTER_ANCHOR = (0.5, 0.045)

SAMPLE_T = (0.35, 0.7, 1.0)
MARGIN = 0.004   # 数px以内のかすりは許容


def _overlap(a, b):
    """2矩形の重なり面積(figure座標)。"""
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 - x0 <= MARGIN or y1 - y0 <= MARGIN:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"m_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    mod = _load(render_py)
    scenes = getattr(mod, "SCENES", {})
    units = getattr(mod, "UNITS", [])
    # カバー(*__cover)は立ち絵を出さないので立ち絵判定から外す
    cover_keys = {k for k in scenes if k.endswith("__cover")}
    used = {u.scene for u in units} | cover_keys

    issues = []
    for key in sorted(used):
        painter = scenes.get(key)
        if painter is None:
            continue
        has_chara = key not in cover_keys
        for t in SAMPLE_T:
            fig = S.new_canvas()
            painter(fig, t)
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            W, H = fig.canvas.get_width_height()
            def anchored_at(art, anchor):
                x, y = art.get_position()
                return abs(x - anchor[0]) < 1e-6 and abs(y - anchor[1]) < 1e-6

            def box_of(art):
                e = art.get_window_extent(renderer=renderer)
                return (e.x0 / W, e.y0 / H, e.x1 / W, e.y1 / H)

            badge_art = next((a for a in fig.texts if anchored_at(a, BADGE_ANCHOR)), None)
            badge_box = box_of(badge_art) if badge_art is not None else None

            for art in list(fig.texts):
                txt = art.get_text()
                if not txt.strip() or art is badge_art:
                    continue
                if anchored_at(art, FOOTER_ANCHOR):      # ブランド表記は意図した位置
                    continue
                if art.get_alpha() is not None and art.get_alpha() < 0.15:
                    continue
                box = box_of(art)
                zones = [("字幕帯", SUBTITLE)]
                if has_chara:
                    zones.append(("立ち絵", CHARA))
                if badge_box is not None:
                    zones.append(("バッジ", badge_box))
                for name, zone in zones:
                    if _overlap(box, zone) > 0:
                        issues.append((key, t, name, txt.replace("\n", "/")[:28]))
            S.plt.close(fig)
    return issues


def main():
    warnings.filterwarnings("ignore")
    S.setup_fonts()
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())

    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        # 同じ (scene, zone, text) は1件にまとめる
        uniq = sorted({(k, z, s) for k, _t, z, s in issues})
        if uniq:
            total += len(uniq)
            print(f"[NG] {vdir.name}")
            for k, z, s in uniq:
                print(f"       {k:<14} {z}に重なる: 「{s}」")
        else:
            print(f"[OK] {vdir.name}")

    print()
    if total:
        print(f"結果: {total}件の重なりを検出。テキストのy座標を動かして解消すること。")
        sys.exit(1)
    print("結果: 重なりなし")


if __name__ == "__main__":
    main()
