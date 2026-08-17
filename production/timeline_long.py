#!/usr/bin/env python3
"""長尺動画のタイムラインを秒単位で出す(ループ70 フェーズ2)。

なぜ必要か:
  L001 を「ゴミ」と判定されたあと原因を探したとき、
  **通しで何秒に何が起きているかを誰も見ていなかった**ことが分かった。
  ユニット単位のゲートは8つあるのに、「30秒時点で何が出ているか」を測る道具が無い。
  離脱は秒で起きるので、秒で見られるようにする。

出すもの:
  - 各ユニットの開始秒・シーンの型(図か文字か)・字幕
  - 章の開始秒
  - 冒頭30秒の判定(3段構え: 0-5s 割り込み / 5-15s 約束 / 15-30s 引っかけ)
  - 図が最初に出る秒、答えの数値が最初に出る秒

使い方:
    python3 production/timeline_long.py videos/L001-nisa-son
    python3 production/timeline_long.py videos/L001-nisa-son --all   # 全ユニット
"""
import importlib.util
import re
import sys
import wave
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# scenes_long のうち、位置や長さが意味を持つ「図」の型
FIGURE_KINDS = {"barsN", "compare2", "band", "curve", "timeline", "table", "checklist"}
NUM = re.compile(r"[0-9][0-9,\.]*\s*(?:円|%|歳|年|万円|万)")


def load(vdir: Path):
    rp = vdir / "render.py"
    spec = importlib.util.spec_from_file_location(f"t_{vdir.name}", rp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, rp.read_text()


def scene_kinds(src: str, scenes) -> dict:
    """SCENES の各キーが、どの型の関数で作られたかを render.py の字面から引く。"""
    out = {}
    for key in scenes:
        m = re.search(r'"' + re.escape(key) + r'":\s*s[cl]?\.?(\w+)', src)
        out[key] = m.group(1) if m else "?"
    return out


def durations(vdir: Path, n: int):
    """work/ に残っている音声から、各ユニットの尺を読む。"""
    wd = vdir / "output" / "work"
    out = []
    for i in range(n):
        for name in (f"seg_{i:02d}_pad.wav", f"seg_{i:02d}.wav"):
            p = wd / name
            if p.exists():
                with wave.open(str(p)) as w:
                    out.append(w.getnframes() / w.getframerate())
                break
        else:
            return None      # まだ合成していない
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    vdir = Path(args[0])
    mod, src = load(vdir)
    units = mod.UNITS
    kinds = scene_kinds(src, mod.SCENES)
    durs = durations(vdir, len(units))
    if durs is None:
        print("音声がまだありません。先に一度レンダリングを走らせてください")
        sys.exit(2)

    starts, t = [], 0.0
    for d in durs:
        starts.append(t)
        t += d
    total = t

    print(f"{vdir.name}: 総尺 {total:.1f}秒({total / 60:.2f}分) / {len(units)}ユニット\n")
    limit = len(units) if show_all else 14
    print("  秒     型            字幕")
    for i, u in enumerate(units[:limit]):
        k = kinds.get(u.scene, "?")
        mark = "図  " if k in FIGURE_KINDS else "文字"
        print(f"{starts[i]:6.1f}  {mark} {k:11} {u.subtitle}")
    if not show_all and len(units) > limit:
        print(f"  ...(残り{len(units) - limit}ユニット。--all で全部出す)")

    # 章の開始秒
    first = {}
    for i, u in enumerate(units):
        first.setdefault(u.scene, i)
    chapters = [(starts[i], k, units[i].subtitle)
                for k, i in sorted(first.items(), key=lambda kv: kv[1])
                if re.fullmatch(r"ch\d+", k)]
    if chapters:
        print("\n章の開始秒:")
        for s, k, sub in chapters:
            print(f"  {s:6.1f}s  {k}  {sub}")

    # 冒頭の判定
    fig_at = next((starts[i] for i, u in enumerate(units)
                   if kinds.get(u.scene) in FIGURE_KINDS), None)
    num_at = next((starts[i] for i, u in enumerate(units) if NUM.search(u.subtitle)), None)
    print("\n冒頭の判定(02-opening.md の3段構え):")
    print(f"  図が最初に出る秒     : {fig_at if fig_at is None else f'{fig_at:.1f}s'}"
          + ("   ← 20秒以内に1つは置く" if (fig_at or 99) > 20 else "   OK"))
    print(f"  数値が最初に出る秒   : {num_at if num_at is None else f'{num_at:.1f}s'}"
          + ("   ← 15秒以内に約束の数字を出す" if (num_at or 99) > 15 else "   OK"))
    if chapters:
        near60 = [s for s, _, _ in chapters if 45 <= s <= 75]
        print(f"  45〜75秒の章の切れ目 : {[f'{s:.1f}s' for s in near60] or 'なし  OK'}"
              + ("   ← 離脱の山と重なる。ずらす" if near60 else ""))


if __name__ == "__main__":
    main()
