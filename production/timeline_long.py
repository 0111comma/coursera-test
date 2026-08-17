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

    # 章の区切り(章札のシーンが最初に出たユニット)
    heads = [i for i, u in enumerate(units)
             if re.fullmatch(r"ch\d+", u.scene) and (i == 0 or units[i - 1].scene != u.scene)]
    blocks = [(0, "冒頭")] + [(i, units[i].scene) for i in heads]
    chapters = [(starts[i], units[i].scene, units[i].subtitle) for i in heads]

    if blocks[1:]:
        print("\n章ブロックの尺と図の割合(03-structure.md):")
        for j, (i, name) in enumerate(blocks):
            e = blocks[j + 1][0] if j + 1 < len(blocks) else len(units)
            end = starts[e] if e < len(units) else total
            seg = units[i:e]
            figs = sum(1 for u in seg if kinds.get(u.scene) in FIGURE_KINDS)
            note = ""
            if end - starts[i] > 150:
                note = "  ← 長い。話題が2つ以上入っていないか"
            elif end - starts[i] < 60:
                note = "  ← 短い。章の切れ目にするほどの塊か"
            if figs / len(seg) < 0.40:
                note += "  ← 図が4割未満"
            print(f"  {name:6} {starts[i]:6.1f}s → {end:6.1f}s  尺 {end - starts[i]:5.1f}s"
                  f"  {len(seg):3}ユニット  図 {figs / len(seg):3.0%}{note}")
        print(f"  章の数(冒頭を除く): {len(chapters)}"
              + ("   ← 9分なら4〜5。多いと切れ目でのリセットが増える"
                 if len(chapters) > 5 else "   OK"))

        # 継ぎ目: 前章の出口と章札が同じ問いを2回言っていないか
        print("\n章の継ぎ目(前章の出口 × 章札の重なり):")
        waste = 0.0
        for i in heads:
            if i == 0:
                continue
            drop = re.compile(r"[。、では第0-9１-９章]")
            a = set(drop.sub("", units[i - 1].subtitle))
            b = set(drop.sub("", units[i].subtitle))
            ov = len(a & b) / max(1, len(b))
            d = durs[i - 1] + durs[i]
            bad = ov >= 0.50
            if bad:
                waste += d
            print(f"  {units[i].scene:6} 重なり {ov:3.0%}  2ユニット {d:4.1f}s"
                  + ("   ← 同じ問いを2回言っている" if bad else ""))
            print(f"         出口: {units[i - 1].subtitle}")
            print(f"         章札: {units[i].subtitle}")
        if waste:
            print(f"  重複した継ぎ目の合計: {waste:.1f}s"
                  f"({waste / total:.0%})   ← 章札は問いを繰り返さず、答えの予告を言う")

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
