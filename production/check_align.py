#!/usr/bin/env python3
"""字幕とシーンのズレを見つける機械チェック(ループ59)。

なぜ作ったか(3回やった同じミス):
  S014・S016・S012 で、UNITS が参照するシーンが1つずれていた。
  たとえば S012 では、字幕が「つまり年に、36万6千円が引かれる」と言っている裏で、
  図は 59万円 の棒を出していた。1本ぶん全部を目で照合しないと気づけない。
  ユーザーに指摘されて直したあと「次はこの照合もチェック化する」と約束したのがこれ。

これは**合否を出すゲートではなく、照合表を必ず読ませるための道具**である。
不合格にするのは「シーンがない」だけ。理由:

  ズレを機械が断定できるか試したが、できなかった。
  「字幕の値が自分のシーンになく、隣のシーンにある」を不合格にすると、
  ユーザー合格判定の S011 が落ちる:
    #13 字幕「つまり75歳で、払った分に届く」/ 図は棒が並んだ瞬間(75歳は次のカードで出す)
  これは正しい作りで、事故と形が同じ。S021 の
    #5 字幕「その差、1548万円」/ 図は838万円と2387万円(差そのものは描かない)
  も同様。**人の合否と一致しない機械判定は入れない**(ループ51の教訓)。

  3回の事故はどれも、ユニット順に「字幕/シーン/図に出ている数値」を
  並べて読めば一目で分かった。だからこのツールの仕事は判定ではなく、
  その表を毎回必ず出すことにする。

出力:
  - 全ユニットの 字幕 / シーン名 / 図に出ている数値 の表
  - 字幕の値が図に無い箇所に ← 印(意図どおりか、目で確かめる)
  - Unit が存在しないシーン名を指していたら不合格(これは常にバグ)

判定から外すもの:
  - バッジ(条件の注記)とフッター(ブランド)。全シーンに出るので照合の役に立たない
  - シーンに数値が1つも無い場合(hero・quiz など、絵で語らないシーン)
  - 早見表(1シーンに TABLE_NUMS 個以上の数値)。読み上げる図ではない

使い方:
    python3 production/check_align.py                 # 全動画
    python3 production/check_align.py videos/S013-... # 1本だけ
"""
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import shortlib as S  # noqa: E402
# 日本語フォントを入れてから描く。ここは文字の中身しか見ないので結果は変わらないが、
# 入れ忘れると豆腐(□)で描かれ、あとで幅や位置を見る判定を足したときに静かに狂う
S.setup_fonts()
from check_figure import (  # noqa: E402
    BADGE_ANCHOR, FOOTER_ANCHOR, TABLE_NUMS, money_values, _load,
)


def scene_values(painter):
    """シーンを1枚描いて、そこに出ている数値を集める(バッジ・フッターは除く)。"""
    fig = S.new_canvas()
    painter(fig, 1.0)
    fig.canvas.draw()
    vals = set()
    for art in fig.texts:
        x, y = art.get_position()
        if abs(x - BADGE_ANCHOR[0]) < 1e-6 and abs(y - BADGE_ANCHOR[1]) < 1e-6:
            continue
        if abs(x - FOOTER_ANCHOR[0]) < 1e-6 and abs(y - FOOTER_ANCHOR[1]) < 1e-6:
            continue
        vals |= money_values(art.get_text().replace("\n", ""))
    S.plt.close(fig)
    return vals


def fmt(v):
    """図の数値を、字幕と見比べやすい形にして表示する。"""
    if isinstance(v, int):
        return f"{v / 10_000:g}万円" if v >= 10_000 else f"{v:,}円"
    return str(v)


def table(vdir: Path):
    """1本ぶんの照合表を返す。(行のリスト, 未描画の数を数えた件数, 欠落シーン名)"""
    render_py = vdir / "render.py"
    if not render_py.exists():
        return [], 0, []
    mod = _load(render_py)
    scenes = getattr(mod, "SCENES", {})
    units = getattr(mod, "UNITS", [])
    rows, marks, missing = [], 0, []
    cache = {}
    for i, u in enumerate(units, 1):
        if u.scene not in scenes:
            missing.append(u.scene)
            rows.append((i, u.scene, u.subtitle, "(シーンがない)", "!!"))
            continue
        if u.scene not in cache:
            cache[u.scene] = scene_values(scenes[u.scene])
        shown = cache[u.scene]
        said = money_values(u.subtitle.replace("【", "").replace("】", ""))
        note = " ".join(fmt(v) for v in sorted(shown, key=str)) or "—"
        if len(shown) >= TABLE_NUMS:
            note = f"(早見表 {len(shown)}値)"
            mark = ""
        elif said and shown and not (said & shown):
            mark = "←"
            marks += 1
        else:
            mark = ""
        rows.append((i, u.scene, u.subtitle, note, mark))
    return rows, marks, missing


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    fails = 0
    for vdir in targets:
        rows, marks, missing = table(vdir)
        if not rows:
            continue
        print(f"── {vdir.name} ──")
        for i, scene, sub, shown, mark in rows:
            print(f"  {i:>3} {scene:<10} {sub:<24} | {shown} {mark}")
        if missing:
            fails += len(missing)
            print(f"  [NG] SCENES にないシーン名: {'、'.join(missing)}")
        elif marks:
            print(f"  [要確認] 字幕の値が図に無い箇所が{marks}件(← 印)。"
                  f"意図どおりか目で確かめること")
        print()
    if fails:
        print("結果: 存在しないシーンを参照している。render.py を直すこと。")
        sys.exit(1)
    print("結果: シーン名はすべて実在。← 印は目で確認する(合否は出さない)")


if __name__ == "__main__":
    main()
