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

LONG_TEXT = 15        # これ以上の長さの文字列は「文」とみなす(縦型1080px幅の基準)
LONG_TEXT_WIDE = 26   # 横型1920pxでの同じ基準。**画面幅に対する割合を揃える**
#   縦型の15字は横幅のほぼ全部を占めるので「文を貼っている」ことの目安になるが、
#   横型で15字は幅の4割しかなく、注記として普通に読める大きさである。
#   この閾値は**解像度に依存する**ので、形式に合わせて換算する
#   (字幕の折り返しを12字→26字にしたのと同じ比率)。
#   一方で「冗長」(Mayer)は認知の話なので、解像度では変えない。
MAX_LONG = 1          # 「文」は1つまで(見出し用)
MIN_SHAPES = 1        # 図形が0個なら図ではない
FIGURE_COVERAGE = 0.40  # 図のあるユニットが全体に占める最低割合
REDUNDANT_RATIO = 0.6
TABLE_NUMS = 6        # これ以上の数値を持つシーンは早見表とみなす

# 「数字が無言」判定は、文字列ではなく**値**で比べる。
# 図が「70,608円」、声が「7万608円」なら同じ値なので合格にしたい。
# 逆に、図にしかない金額は、書式が違うだけでは言い訳にならない。
# 数値の連なり(1億2千万・7万608円・3千2百円 など)と、その後ろの単位
NUM_RUN = re.compile(r"(?:\d[\d,]*(?:\.\d+)?\s*[億万千百]?\s*)+(?:%|倍|割|円|年|歳)?")
NUM_PART = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*([億万千百])?")
UNIT = re.compile(r"(%|倍|割|年|歳)\s*$")
MULT = {"億": 10**8, "万": 10**4, "千": 10**3, "百": 10**2}


def money_values(text: str) -> set:
    """文章から、声に出すべき数値を取り出す。

    図が「70,608円」で声が「7万608円」なら同じ値なので合格にしたい。
    そのため文字列ではなく**値**に正規化して比べる。
    単位も桁もない裸の数字(軸の目盛り)と、出典の西暦は判定から外す。
    """
    out = set()
    for m in NUM_RUN.finditer(text.replace("，", ",").replace("、", "").replace(",", "")):
        run = m.group()
        total, has_keta = 0.0, False
        for num, keta in NUM_PART.findall(run):
            if not num:
                continue
            total += float(num) * MULT.get(keta, 1)
            has_keta = has_keta or bool(keta)
        u = UNIT.search(run)
        unit = u.group(1) if u else ("円" if run.rstrip().endswith("円") else "")
        if unit in ("年", "歳") and not has_keta:
            if unit == "年" and 1500 <= total <= 2100:
                continue                      # 出典の西暦・時点表記は声に出さなくてよい
            out.add(f"{total:g}{unit}")
        elif unit in ("%", "倍", "割"):
            out.add(f"{total:g}{unit}")
        elif unit == "円" or has_keta:
            out.add(int(total))
        # 単位も桁もない裸の数字は、軸の目盛りとみなして無視する
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


_NUMBERISH = set("0123456789,.%円年万千億ヶか月日 　+-=×÷")


def _is_number_label(t: str) -> bool:
    """「差は 40,630円」のような、数値の見出しかどうか。

    数値部分が半分以上を占めるなら、それは文ではなく**数字の掲示**である。
    規則6(図の数値は声でも言うこと)が、この重なりをわざと作っている。
    """
    return sum(1 for c in t if c in _NUMBERISH) / max(1, len(t)) >= 0.5


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
        # fig.add_artist で足した線・矢印は fig.lines ではなく fig.artists に入る
        n_shapes += len([a for a in fig.artists
                         if type(a).__name__ in ("Line2D", "Polygon", "Rectangle")
                         or type(a).__name__.startswith("FancyArrow")])

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
        scene_values = set()
        for t in body:
            scene_values |= money_values(t)
        # 早見表(一覧表)は、読み上げるためではなく止めて見るための図。
        # 1シーンに数値が TABLE_NUMS 個以上あるなら一覧表とみなし、無言判定から外す
        if len(scene_values) < TABLE_NUMS:
            fig_numbers |= scene_values

        # 1. 図の有無を数える(個別には落とさない。カードは図でなくてよい)
        if n_shapes >= MIN_SHAPES:
            n_with_figure[0] += 1

        # 2. 文章を並べている
        long_text = LONG_TEXT_WIDE if S.W == 1920 else LONG_TEXT
        longs = [t for t in body if len(t) >= long_text]
        if len(longs) > MAX_LONG:
            issues.append((u.scene, "文章",
                           f"{long_text}字以上の文字列が{len(longs)}個: 「{longs[0][:18]}」ほか"))

        # 3. 冗長(図の文字が字幕と重なる)
        for t in body:
            if _is_number_label(t):
                continue      # 数値ラベルの重なりは規則6が要求しているもの
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
