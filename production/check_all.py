#!/usr/bin/env python3
"""全ゲートをまとめて走らせる(ループ71)。

ゲートが10本を超え、**走らせ忘れたゲートがそのまま不具合になった**。
S017・S018 は check_figure が不合格のまま納品されていた
(ゲートを1本ずつ手で叩いていて、この2本だけ叩き忘れていた)。
だから1コマンドにする。忘れる余地を消すほうが早い。

使い方:
    python3 production/check_all.py videos/S016-nisa-waku
    python3 production/check_all.py                 # 全動画
"""
import subprocess
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent

# 縦横で共通のゲート
COMMON = ["toi", "teinei", "flow", "figure", "overlap", "ikko", "yomi",
          "ryakugo", "goi", "bunsho", "yokkyu", "video"]
LONG_ONLY = ["long"]                       # 横型だけ


def is_long(vdir: Path) -> bool:
    return vdir.name.startswith("L")


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    bad = 0
    for vdir in targets:
        gates = COMMON + (LONG_ONLY if is_long(vdir) else [])
        print(f"=== {vdir.name}")
        for g in gates:
            r = subprocess.run([sys.executable, str(PRODUCTION / f"check_{g}.py"), str(vdir)],
                               capture_output=True, text=True)
            last = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
            tail = last[-1] if last else ""
            mark = "OK " if r.returncode == 0 else "NG "
            if r.returncode != 0:
                bad += 1
                print(f"  {mark}{g}")
                for ln in last[:-1]:
                    print(f"        {ln}")
            else:
                print(f"  {mark}{g:8} {tail}")
    print()
    if bad:
        print(f"結果: {bad}本のゲートが不合格。焼く前に直すこと。")
        sys.exit(1)
    print("結果: 全ゲート合格")


if __name__ == "__main__":
    main()
