#!/usr/bin/env python3
"""カットの速さ — **ショートの速度感に合っているか**(2026-08-24)。

ユーザー指摘:
  「今までのショート動画の速度感に合ってないので、
    すぐスワイプしてしまう可能性がすごい高い」

これは感覚ではなく**実測で足りていなかった**。
S032 の render.py の3行目には、私自身がこう書いていた:

    1カット1.6〜1.8秒。

出典は docs/research/competitor-shorts-teardown-2026-08-23.md:

    | 動画1 | 2.96% | 約34カット |
    | 動画2 | 2.72% | 約37カット |
    60秒なら **1カット1.6〜1.8秒**。

ところが実際に作った S032 は:

    40.1秒 / 11カット = **3.65秒/カット**(目標の半分以下)

**基準を書いておきながら、機械で見ていなかったから守られなかった。**
だからここで見る。

判定:
  1. 平均カット長が MAX_CUT_SEC を超えたら不合格
  2. 1カットが LONG_CUT_SEC 以上そのままなら不合格(その1枚で飽きる)
  3. 「同じ場面が続くユニット」は1カットと数える。
     字幕が変わっても**絵が変わらなければ視聴者にはカットではない**

尺は音声があれば実測、無ければ字数から推定する(焼く前に落とすため)。

免除: production/gate_exempt.txt に `動画ID:tempo:0  # 理由`
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAX_CUT_SEC = 2.4     # 平均。競合1.6〜1.8に対し、余裕を見てここを上限にする
LONG_CUT_SEC = 4.5    # 1カットの上限。これ以上そのままの絵は出さない
CHARS_PER_SEC = 7.4   # 字数→秒の推定(SPEED_SCALE 1.3 のときの実測値)


def load_exempt(gate: str) -> set[str]:
    f = ROOT / "production" / "gate_exempt.txt"
    out = set()
    if not f.exists():
        return out
    for ln in f.read_text().splitlines():
        body, _, reason = ln.partition("#")
        parts = body.strip().split(":")
        if len(parts) == 3 and parts[1] == gate and reason.strip():
            out.add(parts[0])
    return out


def units_of(src: str) -> list[tuple[str, str]]:
    return re.findall(r'Unit\(\s*"([^"]+)",\s*"([^"]+)"', src)


def real_duration(vdir: Path) -> float | None:
    mp4 = next(iter(sorted((vdir / "output").glob("*.mp4"))), None)
    if mp4 is None:
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(mp4)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def check_video(vdir: Path):
    rp = vdir / "render.py"
    if not rp.exists():
        return []
    src = rp.read_text()
    if "use_landscape" in src:
        return []            # 長尺は check_long が別の基準で見る
    units = units_of(src)
    if not units:
        return []

    # 絵が変わる回数。同じ場面が続くユニットは1カット
    cuts, prev = [], None
    for scene, sub in units:
        if scene != prev:
            cuts.append([sub])
        else:
            cuts[-1].append(sub)
        prev = scene

    total = real_duration(vdir)
    estimated = total is None
    if estimated:
        total = sum(len(s.replace("【", "").replace("】", ""))
                    for _, s in units) / CHARS_PER_SEC

    issues = []
    avg = total / len(cuts)
    if avg > MAX_CUT_SEC:
        need = int(total / MAX_CUT_SEC + 0.999)
        issues.append(("(全体)", "カットが遅い",
                       f"{total:.1f}秒 / {len(cuts)}カット = "
                       f"**1カット{avg:.2f}秒**。上限{MAX_CUT_SEC}秒。"
                       f"競合は1.6〜1.8秒。**あと{need - len(cuts)}カット要る**"
                       f"{'(尺は字数からの推定)' if estimated else ''}"))

    # 1カットが長すぎないか(その場面のユニットの尺を合算)
    per_char = total / max(1, sum(len(s.replace("【", "").replace("】", ""))
                                  for _, s in units))
    for i, subs in enumerate(cuts, 1):
        sec = sum(len(s.replace("【", "").replace("】", "")) for s in subs) * per_char
        if sec >= LONG_CUT_SEC:
            issues.append((f"カット{i}", "同じ絵が長い",
                           f"約{sec:.1f}秒そのまま。{LONG_CUT_SEC}秒以上は動かすか割ること: "
                           f"「{subs[0][:20]}」"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    ex = load_exempt("tempo")
    total = 0
    for vdir in targets:
        if vdir.name.split("-")[0] in ex:
            print(f"[--] {vdir.name} — 免除")
            continue
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:8} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。**ショートは1カット1.6〜1.8秒。**")
        print("      絵が変わらない時間が続くと、内容が正しくてもスワイプされる。")
        sys.exit(1)
    print("結果: カットの速さは基準内")


if __name__ == "__main__":
    main()
