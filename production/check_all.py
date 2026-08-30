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

# 縦横で共通のゲート。
# **zentei は先頭に置く。**「説明していない数字を画面に出さない」は
# 2026-08-23 にユーザーが「第一優先で絶対今後落としてほしくない」と言ったゲート。
# 台本の直しよりも前に、企画(前提と根拠)が立っているかを見る。
# tempo は縦型だけ見る(check_tempo が横型を自分で除外する)。
# 「1カット1.6〜1.8秒」は競合の実測から出した基準なのに、**書いてあるだけで
# 機械が見ていなかった**ので守られていなかった(S032が3.65秒。2026-08-24)。
#
# kotoba / design は、批評パネル2回分の指摘を規則にした新しいゲート
# (2026-08-30。docs/research/kotoba-rules.md と design-rules.md)。
# パネル(サブエージェント8人×複数ラウンド)を毎本回すのは費用が見合わないので、
# **パネルが見つけた欠陥のうち機械で見られるものは機械に見させる**。
# 既存の公開済み動画は gate_exempt.txt で丸ごと外してある(触らない方針)。
COMMON = ["zentei", "toi", "hold", "tempo", "teinei", "flow", "figure", "overlap",
          "ikko", "yomi", "ryakugo", "goi", "bunsho", "yougo", "yokkyu",
          "kotoba", "design", "video"]
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
