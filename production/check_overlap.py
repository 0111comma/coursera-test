#!/usr/bin/env python3
"""レイアウト衝突と画面外へのはみ出しの機械チェック(ループ㊵ / はみ出しはループ71)。

目視でしか見つけられなかった不具合を恒久的に潰すためのゲート。
各動画の render.py の SCENES を実際に描画し、すべての Text/Patch の
描画範囲を測って、次の3つの禁止領域との重なりを検出する。

  1. 立ち絵(CHARA_RECTS["bl"] = x 0.000-0.342 / y 0.245-0.465)
  2. 注記バッジ(draw_badge。右上 y=0.83 付近)
  3. 字幕帯(画面下部 y<0.245)

さらに **画面の外にはみ出していないか**(ループ71)。
S016 の締めの見出し「いまの積立額は、証券会社の画面で見られます」が
左右どちらも画面外に切れたまま、**11本のゲートを全部通って納品された**。
ユーザー指摘:「なんでこういうのが全ゲート合格してるわけ?」
重なりだけを見ていて、**枠の外に出ていること**を誰も見ていなかった。

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
CHARA = (0.000, 0.245, 0.342, 0.465)     # 立ち絵(bl)。縦型
SUBTITLE = (0.000, 0.000, 1.000, 0.245)  # 字幕帯。縦型


def zones_for_format():
    """立ち絵と字幕帯の占有域を、いまの画面比から出す。

    ここを縦型の値で固定したまま横型を通すと、
    フッターのチャンネル名(y=0.036)まで「字幕帯に重なる」と言い出す。
    **占有域は shortlib のレイアウト定数から引く**(use_landscape が書き換える)。
    """
    if S.W == 1920:
        r = S.CHARA_RECTS["br"]                      # 横型は右下に置く
        chara = (r[0], r[1], r[0] + r[2], r[1] + r[3])
        # 字幕は SUBTITLE_Y を上端に2行ぶん下へ伸びる。その下端はフッターの上まで
        band_top = S.SUBTITLE_Y + 0.030
        subtitle = (0.000, S.BRAND_XY[1] + 0.018, 1.000, band_top)
        return chara, subtitle
    return CHARA, SUBTITLE
# バッジは draw_badge のアンカー(0.90, 0.83)で実体を特定し、実測範囲を禁止領域にする
BADGE_ANCHOR = (0.90, 0.83)
FOOTER_ANCHOR = (0.5, 0.045)

SAMPLE_T = (0.35, 0.7, 1.0)
MARGIN = 0.004   # 数px以内のかすりは許容
OUT_MARGIN = 0.002  # 画面外へのはみ出しは、ほぼゼロ許容


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

    chara_zone, subtitle_zone = zones_for_format()
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

            # 図形(棒・枠)と座標軸も判定する。文字だけ見ていると
            # グラフ本体が立ち絵に食い込む不具合を見逃す(ループ㊵の積み残し)
            shapes = []
            for pat in list(fig.patches):
                e = pat.get_window_extent(renderer)
                shapes.append(("図形", (e.x0 / W, e.y0 / H, e.x1 / W, e.y1 / H)))
            for ax in list(fig.axes):
                pos = ax.get_position()
                if pos.width > 0.9 and pos.height > 0.9:
                    continue          # new_canvas() の全面背景アックスは判定対象外
                e = ax.get_tightbbox(renderer)
                if e is None:
                    continue
                shapes.append(("グラフ", (e.x0 / W, e.y0 / H, e.x1 / W, e.y1 / H)))
            for label, box in shapes:
                if box[3] - box[1] <= 0 or box[2] - box[0] <= 0:
                    continue
                zones = []
                if has_chara:
                    zones.append(("立ち絵", chara_zone))
                if badge_box is not None:
                    zones.append(("バッジ", badge_box))
                for name, zone in zones:
                    if _overlap(box, zone) > 0:
                        issues.append((key, t, name, f"<{label}>"))

            # 画面外へのはみ出し(ループ71)。文字も図形も、枠の中に収まっていること
            for label, box in shapes:
                if box[2] - box[0] <= 0:
                    continue
                if box[0] < -OUT_MARGIN or box[2] > 1 + OUT_MARGIN:
                    issues.append((key, t, "画面外(左右)", f"<{label}>"))
                elif box[1] < -OUT_MARGIN or box[3] > 1 + OUT_MARGIN:
                    issues.append((key, t, "画面外(上下)", f"<{label}>"))

            for art in list(fig.texts):
                txt = art.get_text()
                if not txt.strip() or art is badge_art:
                    continue
                if anchored_at(art, FOOTER_ANCHOR):      # ブランド表記は意図した位置
                    continue
                if art.get_alpha() is None or art.get_alpha() >= 0.15:
                    b = box_of(art)
                    if b[0] < -OUT_MARGIN or b[2] > 1 + OUT_MARGIN:
                        issues.append((key, t, "画面外(左右)",
                                       txt.replace("\n", "/")[:28]))
                    elif b[1] < -OUT_MARGIN or b[3] > 1 + OUT_MARGIN:
                        issues.append((key, t, "画面外(上下)",
                                       txt.replace("\n", "/")[:28]))
                if art.get_alpha() is not None and art.get_alpha() < 0.15:
                    continue
                box = box_of(art)
                zones = [("字幕帯", subtitle_zone)]
                if has_chara:
                    zones.append(("立ち絵", chara_zone))
                if badge_box is not None:
                    zones.append(("バッジ", badge_box))
                for name, zone in zones:
                    if _overlap(box, zone) > 0:
                        issues.append((key, t, name, txt.replace("\n", "/")[:28]))

            # 図の中の文字どうしの重なり(ループ53)。立ち絵・バッジ・字幕との衝突しか
            # 見ていなかったので、「税金はゼロ」と「損 50万円」が重なったまま通った
            labels = []
            for art in list(fig.texts):
                txt = art.get_text()
                if not txt.strip() or art is badge_art:
                    continue
                if anchored_at(art, FOOTER_ANCHOR):
                    continue
                if art.get_alpha() is not None and art.get_alpha() < 0.15:
                    continue
                labels.append((txt.replace("\n", "/")[:14], box_of(art), art.get_position()))
            for i in range(len(labels)):
                for j in range(i + 1, len(labels)):
                    (t1, b1, p1), (t2, b2, p2) = labels[i], labels[j]
                    # draw_glow_text は同じ文字を同じ位置に重ね描きするので除く
                    if t1 == t2 or (abs(p1[0] - p2[0]) < 1e-9 and abs(p1[1] - p2[1]) < 1e-9):
                        continue
                    if _overlap(b1, b2) > 0:
                        issues.append((key, t, "文字どうし", f"「{t1}」と「{t2}」"))
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
