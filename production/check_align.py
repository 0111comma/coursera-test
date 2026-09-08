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
    CHROME_GID, BADGE_ANCHOR, FOOTER_ANCHOR, TABLE_NUMS, money_values, _load,
)


def scene_values(painter):
    """シーンを1枚描いて、そこに出ている数値を集める(バッジ・フッターは除く)。"""
    fig = S.new_canvas()
    painter(fig, 1.0)
    fig.canvas.draw()
    vals = set()
    for art in fig.texts:
        if art.get_gid() == CHROME_GID:
            continue              # テーマの帯・バッジ
        x, y = art.get_position()
        if abs(x - BADGE_ANCHOR[0]) < 1e-6 and abs(y - BADGE_ANCHOR[1]) < 1e-6:
            continue
        if abs(x - FOOTER_ANCHOR[0]) < 1e-6 and abs(y - FOOTER_ANCHOR[1]) < 1e-6:
            continue
        vals |= money_values(art.get_text().replace("\n", ""))
    S.plt.close(fig)
    return vals


def bars_label_offsets(painter):
    """棒グラフの「棒の中心・値ラベルのink中心・カテゴリ名のink中心」のずれ(px)。

    2026-08-30 consistency/high: 棒の値ラベルが棒の中心から**右に**ずれていた。
    実測(棒/ラベルの各ink中心): 11 左棒 356 / ラベル 401(+45px=棒幅220pxの20%)、
    13 左 356/389(+33)・右 723/766(+43)、18 左 356/371(+15)・右 723/744(+21)。
    全て同方向にずれ、量だけばらついた。原因は big_number の
    「中央揃えの基準は数字部分の中心」という規則が、対象物の上に載せる
    ラベルにもそのまま適用され、単位のサイドベアリングぶんブロック全体が
    右へ押し出されていたこと(単独ヒーロー数字には正しい規則だが、
    棒のラベルには誤り)。いまは align_on="block" を渡している。

    返り値: [(棒の中心px, 値ラベルのink中心px, カテゴリ名のink中心px), ...]
    """
    import numpy as np
    fig = S.new_canvas(1.0)
    painter(fig, 1.0)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    # 棒(PathPatch)の中心
    bars = []
    for art in fig.artists:
        if type(art).__name__ != "PathPatch":
            continue
        e = art.get_window_extent(renderer=r)
        if e.width < 40 or e.height < 40:
            continue
        bars.append(((e.x0 + e.x1) / 2, e.y0, e.y1))
    texts = []
    for art in fig.texts:
        if str(art.get_gid() or "").startswith(CHROME_GID):
            continue
        e = art.get_window_extent(renderer=r)
        texts.append(((e.x0 + e.x1) / 2, (e.y0 + e.y1) / 2, e.x0, e.x1, art))
    S.plt.close(fig)
    out = []
    for cx, y0, y1 in sorted(bars):
        near = [t for t in texts if abs(t[0] - cx) < 180]
        above = [t for t in near if t[1] > y1]
        below = [t for t in near if t[1] < y0]
        if not above or not below:
            continue
        # 同じ行にある文字を1つのラベルとしてまとめる
        def ink_center(group):
            g0 = min(t[2] for t in group)
            g1 = max(t[3] for t in group)
            return (g0 + g1) / 2
        lab_y = min(t[1] for t in above)
        lab = [t for t in above if abs(t[1] - lab_y) < 40]
        cat_y = max(t[1] for t in below)
        cat = [t for t in below if abs(t[1] - cat_y) < 40]
        out.append((cx, ink_center(lab), ink_center(cat)))
    return out


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
        # A1: 棒の中心と、その上の値ラベル・下のカテゴリ名の ink 中心が揃っているか
        try:
            mod = _load(vdir / "render.py")
            scenes = getattr(mod, "SCENES", {})
            src = (vdir / "render.py").read_text()
            import re as _re
            bar_keys = [m.group(1) for m in
                        _re.finditer(r'"([A-Za-z0-9_]+)"\s*:\s*s[a-z]\.bars\(', src)]
            for k in bar_keys:
                for cx, lx, tx in bars_label_offsets(scenes[k]):
                    if abs(lx - cx) > 3.0 or abs(tx - cx) > 3.0:
                        fails += 1
                        print(f"  [NG] A1 {k}: 棒の中心 {cx:.0f}px に対し "
                              f"値ラベル {lx:.0f}px({lx - cx:+.0f}) / "
                              f"カテゴリ名 {tx:.0f}px({tx - cx:+.0f})。"
                              f"±3px 以内に揃えること")
        except Exception as e:      # noqa: BLE001
            print(f"  [--] A1 判定は走らなかった: {e}")
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
