#!/usr/bin/env python3
"""図が「図」になっているかの機械チェック(ループ㊺)。

ユーザー指摘:「めちゃくちゃ図がわかりづらい。何を伝えたいのかわからない」

根拠は docs/research/figure-forms.md:
- Larkin & Simon (1987): 図が効くのは情報が位置で索引されるから。
  位置・長さ・向き・面積が意味を持たない図は、箱に入った文章にすぎない
- Mayer 冗長性(d=0.87): 図の中の文がナレーションと同義だと学習を妨げる
- Mayer 合図(d=0.46): 強調は本質1点に絞る

判定(シーンごと):
  1. 図形ゼロ    : 図形が0個でテキストが3つ以上 → 箇条書きをしているだけ
  2. 文章        : 15字以上の文字列が2つ以上 → 図ではなく文章を並べている
  3. 冗長        : 図の中の文字列が、そのユニットの字幕と6割以上重なる
  4. 強調過多    : 強調色の要素が3つ以上(WARN)

動画レベル:
  5. 図が足りない : 図のあるユニットが4割未満
  6. 数字が無言   : 図に出ている数値が、どの字幕にも出てこない(ループ㊾)
     ユーザー指摘:「買った金額と売った金額をちゃんと言わないとよくわからんよ」
     図に100万・80万と書いてあっても、声が「その値段で売る」としか言わなければ、
     見ている人は何と何の差額なのか分からない。音だけでも follow できることが条件

使い方:
    python3 production/check_figure.py                 # 全動画
    python3 production/check_figure.py videos/S022-... # 1本だけ
"""
import importlib.util
import re
import sys
import warnings
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

import matplotlib
matplotlib.use("Agg")
import shortlib as S  # noqa: E402

LONG_TEXT = 15        # これ以上の長さの文字列は「文」とみなす
MAX_LONG = 1          # 「文」は1つまで(見出し用)
MIN_SHAPES = 1        # 図形が0個なら図ではない
FIGURE_COVERAGE = 0.40  # 図のあるユニットが全体に占める最低割合
REDUNDANT_RATIO = 0.6

# 「数字が無言」判定は、文字列ではなく**値**で比べる。
# 図が「70,608円」、声が「7万608円」なら同じ値なので合格にしたい。
# 逆に、図にしかない金額は、書式が違うだけでは言い訳にならない。
NUM_RE = re.compile(
    r"(\d[\d,]*)\s*億\s*(\d[\d,]*)?\s*万?\s*(\d[\d,]*)?"   # ○億○万○
    r"|(\d[\d,]*)\s*万\s*(\d[\d,]*)?"                          # ○万○
    r"|(\d[\d,]*(?:\.\d+)?)\s*(%|倍|割)"                        # 割合
    r"|(\d[\d,]*)\s*(円|年|歳)")                                  # 素の数字+単位


def money_values(text: str) -> set:
    """文章から、声に出すべき数値を取り出す。単位のない目盛り数字と西暦は無視する。"""
    out = set()
    for m in NUM_RE.finditer(text.replace("，", ",").replace("、", "")):
        g = m.groups()
        if g[0]:                                   # ○億○万○
            v = int(g[0].replace(",", "")) * 10**8
            v += int(g[1].replace(",", "")) * 10**4 if g[1] else 0
            v += int(g[2].replace(",", "")) if g[2] else 0
            out.add(v)
        elif g[3]:                                 # ○万○
            v = int(g[3].replace(",", "")) * 10**4
            v += int(g[4].replace(",", "")) if g[4] else 0
            out.add(v)
        elif g[5]:                                 # 割合
            out.add(f"{float(g[5].replace(',', '')):g}{g[6]}")
        elif g[7]:                                 # 素の数字+単位
            v = int(g[7].replace(",", ""))
            if g[8] == "年" and 1900 <= v <= 2100:
                continue                           # 出典の西暦・時点表記は声に出さなくてよい
            out.add(v if g[8] == "円" else f"{v}{g[8]}")
    return out

# 常に出る要素(バッジ・ブランド)は判定から除く
BADGE_ANCHOR = (0.90, 0.83)
FOOTER_ANCHOR = (0.5, 0.045)


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"g_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _overlap_ratio(a: str, b: str) -> float:
    """2つの文字列の文字集合の重なり(短い方を分母に)。"""
    sa = set(a) - set("。、()()【】 　")
    sb = set(b) - set("。、()()【】 　")
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / min(len(sa), len(sb))


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    mod = _load(render_py)
    scenes = getattr(mod, "SCENES", {})
    units = getattr(mod, "UNITS", [])
    issues = []
    n_with_figure = [0]
    fig_numbers = set()
    spoken = money_values("".join(u.subtitle for u in units).replace("【", "").replace("】", ""))

    for u in units:
        painter = scenes.get(u.scene)
        if painter is None:
            continue
        fig = S.new_canvas()
        painter(fig, 1.0)
        fig.canvas.draw()

        # 図形の数(バッジのbboxは fig.texts 側なので patches には出ない)
        n_shapes = len(fig.patches) + len(fig.lines)
        for ax in fig.axes:
            pos = ax.get_position()
            if pos.width > 0.9 and pos.height > 0.9:
                continue          # new_canvas の全面背景
            n_shapes += len(ax.lines) + len(ax.patches) + len(ax.collections)
        n_shapes += len([a for a in fig.artists if type(a).__name__.startswith("FancyArrow")])

        texts = []
        for art in fig.texts:
            x, y = art.get_position()
            if abs(x - BADGE_ANCHOR[0]) < 1e-6 and abs(y - BADGE_ANCHOR[1]) < 1e-6:
                continue
            if abs(x - FOOTER_ANCHOR[0]) < 1e-6 and abs(y - FOOTER_ANCHOR[1]) < 1e-6:
                continue
            t = art.get_text().replace("\n", "")
            if t.strip():
                texts.append((t, art.get_color()))
        S.plt.close(fig)

        body = [t for t, _ in texts]
        subtitle = u.subtitle.replace("【", "").replace("】", "")
        for t in body:
            fig_numbers |= money_values(t)

        # 1. 図の有無を数える(個別には落とさない。カードは図でなくてよい)
        if n_shapes >= MIN_SHAPES:
            n_with_figure[0] += 1

        # 2. 文章を並べている
        longs = [t for t in body if len(t) >= LONG_TEXT]
        if len(longs) > MAX_LONG:
            issues.append((u.scene, "文章",
                           f"{LONG_TEXT}字以上の文字列が{len(longs)}個: 「{longs[0][:18]}」ほか"))

        # 3. 冗長(図の文字が字幕と重なる)
        for t in body:
            if len(t) >= 10 and _overlap_ratio(t, subtitle) >= REDUNDANT_RATIO:
                issues.append((u.scene, "冗長",
                               f"字幕とほぼ同義: 図「{t[:18]}」/ 字幕「{subtitle[:18]}」"))
                break

        # 4. 強調過多(WARN)
        n_emph = sum(1 for _, c in texts if str(c).lower() == S.EMPH.lower())
        if n_emph >= 3:
            issues.append((u.scene, "強調過多(WARN)", f"強調色の文字が{n_emph}個。合図は1点に絞る"))

    # 動画レベル: 図のあるユニットが4割未満なら、文字だけの動画になっている
    if units:
        ratio = n_with_figure[0] / len(units)
        if ratio < FIGURE_COVERAGE:
            issues.append(("(動画全体)", "図が足りない",
                           f"図のあるユニットが{n_with_figure[0]}/{len(units)}"
                           f"({ratio:.0%})。文字カードだけで説明している"))
    # 図に出した数字は、必ず声でも言う(音だけで追えること)
    mute = sorted((n for n in fig_numbers - spoken), key=str)
    if mute:
        issues.append(("(動画全体)", "数字が無言",
                       f"図にあるが字幕にない数値: {'、'.join(str(n) for n in mute[:6])}"
                       f"。何と何の数字なのか、声でも言うこと"))

    # 同じシーンの同じ指摘は1件にまとめる
    return sorted(set(issues))


def main():
    warnings.filterwarnings("ignore")
    S.setup_fonts()
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())

    total = fails = 0
    for vdir in targets:
        issues = check_video(vdir)
        hard = [i for i in issues if "WARN" not in i[1]]
        if issues:
            total += len(issues)
            fails += len(hard)
            print(f"[{'NG' if hard else 'WARN'}] {vdir.name} — {len(issues)}件")
            for scene, kind, detail in issues:
                print(f"       {scene:12} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")

    print()
    if fails:
        print(f"結果: {total}件(うち不合格{fails}件)。docs/research/figure-forms.md の判定表で図の型を選び直すこと。")
        sys.exit(1)
    print(f"結果: 不合格なし" + (f"(WARN {total}件)" if total else ""))


if __name__ == "__main__":
    main()
