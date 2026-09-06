#!/usr/bin/env python3
"""縦型ショートの下見ツール(VOICEVOX不要)。

render_video の emit と同じ合成(new_canvas → painter → draw_subtitle)を、
音声合成なしで再現する。批評ループ(見た目の検収)のためにある。
長尺には preview_long.py があるが、縦型ショートには焼く前に見る道具が
無かった。2〜3時間焼いてから見た目の欠陥を見つけるのでは遅い。

使い方:
    python3 production/preview_fp.py videos/S033-subsc-30nen <出力先> [--t 0.3,1.0]

出力: <出力先>/<unit番号>_<scene>_t<t>.png (540x960に縮小。批評用)
"""
import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_render_module(video_dir: Path):
    """render.py を __main__ ガードを踏まずに import する。"""
    sys.path.insert(0, str(video_dir))
    spec = importlib.util.spec_from_file_location("render_preview_target",
                                                  video_dir / "render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def estimate_duration(u) -> float:
    """字幕の字数から尺を推定(ショートは約7字/秒)。語ポップの時刻に使う。"""
    import re
    plain = re.sub(r"【|】", "", u.subtitle)
    return max(1.2, len(plain) / (7.0 * getattr(u, "speed", 1.0)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("outdir")
    ap.add_argument("--t", default="0.3,1.0",
                    help="各ユニットで描くアニメ進行度(カンマ区切り)")
    ap.add_argument("--units", default=None,
                    help="描くユニット番号(カンマ区切り。既定は全部)")
    ap.add_argument("--scale", type=int, default=540, help="出力の横px")
    args = ap.parse_args()

    video_dir = Path(args.video_dir).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    ts = [float(x) for x in args.t.split(",")]

    mod = load_render_module(video_dir)
    import shortlib as S
    S.setup_fonts()

    only = None
    if args.units:
        only = {int(x) for x in args.units.split(",")}

    import matplotlib.pyplot as plt
    from PIL import Image

    made = []
    for i, u in enumerate(mod.UNITS):
        if only is not None and i not in only:
            continue
        d_est = estimate_duration(u)
        painters = [(mod.SCENES[u.scene], "")]
        cov = mod.SCENES.get(f"{u.scene}__cover")
        if u.cover and cov:
            painters.append((cov, "_cover"))
        for painter, suffix in painters:
            for t in ts:
                # **--t はユニットの実時間(推定尺)に対する進行度**(2026-08-29
                # 批評6周目)。旧実装は anim 窓(約1秒)しか見ておらず、
                # 「ナレーション後半の静止」が下見で検収できなかった。
                # painter へ渡す t は本番と同じく anim 窓の進行度(1.0で飽和)
                anim = max(0.05, min(u.anim, d_est) or d_est)
                head = 0.07 if not suffix else 0.0
                t_unit = head + (d_est - head) * t
                t_anim = min(1.0, max(0.0, (t_unit - head) / anim))
                if suffix:
                    t_anim = t          # カバーは従来どおり素の t で検収
                fig = S.new_canvas(t_unit)
                S.SUB_TIME = (t_unit, d_est)   # painter が第2の拍を読む
                painter(fig, t_anim)
                if not suffix:
                    delay = getattr(u, "sub_delay", 0.0)
                    S.SUB_TIME = (t_unit - delay, max(0.3, d_est - delay))
                    S.draw_subtitle(fig, u.subtitle,
                                    pop=(1.06 if t <= ts[0] else 1.0))
                f = outdir / f"{i:02d}_{u.scene}{suffix}_t{t:.2f}.png"
                S.save_frame(fig, f)
                plt.close(fig)
                if args.scale and args.scale != S.W:
                    im = Image.open(f)
                    im = im.resize((args.scale, int(args.scale * S.H / S.W)),
                                   Image.LANCZOS)
                    im.save(f)
                made.append(f)
    print(f"{len(made)} frames -> {outdir}")


if __name__ == "__main__":
    main()
