#!/usr/bin/env python3
"""冒頭の問いの機械チェック(ループ71)。

ユーザー指摘:
  「最初の5秒、10秒で見るかどうか、実は最初の1、2秒で決まるんだよね。
    そこでこの動画は何なのか、どの欲望に対して訴求してるのかを、
    ちゃんと質問として言語化してあげて、それを訴求する時間を作れよ。1、2秒。」

  「年金って何歳まで生きたら元が取れるの? それ計算した人は少ないけど、
    そもそも**損したくない**っていう訴求ポイントに対して、
    これ見たいって思わせることができるのが強み」

  「ふるさと納税のやつ、これゴミだよ。制度を紹介するとか、変わったルールを
    解説するのは別に俺らじゃなくていいわけ」

つまり **1ユニット目は、欲求を問いの形にして口に出す**。
状況の説明から入らない。制度の名前から入らない。

判定(すべて不合格):
  1. 1ユニット目が疑問形で終わる(? / か。 / のか。 / だろうか。)
  2. 1ユニット目が20字以内 — **WARNのみ**(2026-08-23に不合格から降格)。
     字数で縛ると意味が壊れる。見るのは字数ではなく読み上げの秒数
  3. その問いに**損得の語**が入っている(いくら・何歳・損・戻る・取られる…)。
     「〜とは何か」のような制度の問いは、損得の語が無いので落ちる
  4. plan.md に「## 最初の一言(問い)」があり、1ユニット目と一致する
  5. カバー(*__cover)の1行目も問いになっている(画面と音で同じ問いを出す)

使い方:
    python3 production/check_toi.py                  # 全動画
    python3 production/check_toi.py videos/S017-...  # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

MAX_CHARS = 20
QUESTION = re.compile(r"(\?|か。|か$|のか。|だろうか。|ますか。|ますか$)")
# 損得の語 — この動画が「誰の財布の話か」を1文目で名乗るための語
SONTOKU = [
    "いくら", "何歳", "何年", "何ヶ月", "何回", "どこまで", "いつまで", "何割",
    "損", "得", "戻", "取られ", "引かれ", "払", "もらえ", "減", "増え", "かかる",
    "自腹", "上限", "元が取れ", "足り", "間に合", "越え", "超え",
]


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"t_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def plan_toi(vdir: Path):
    plan = vdir / "plan.md"
    if not plan.exists():
        return None
    m = re.search(r"##\s*[0-9.]*\s*最初の一言.*?\n+(.+?)\n", plan.read_text())
    return m.group(1).strip().strip("*「」") if m else None


def cover_first_line(mod):
    """カバーの1行目(cover() の top 引数)を render.py の字面から拾う。"""
    src = Path(mod.__file__).read_text()
    m = re.search(r'sc\.cover\(\s*"([^"]+)"', src) or re.search(r'sl\.cover\(\s*"([^"]+)"', src)
    return m.group(1) if m else None


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    mod = _load(render_py)
    units = getattr(mod, "UNITS", [])
    if not units:
        return []
    first = units[0].subtitle.replace("【", "").replace("】", "")
    issues = []

    if not QUESTION.search(first):
        issues.append(("#1", "問いで始まっていない",
                       f"「{first}」。1ユニット目は欲求を問いの形で言うこと。"
                       f"状況の説明や制度の名前から入らない"))
    # **不合格にしない**(2026-08-23)。ユーザー指示:
    #   「文字制限かけて何言ってるかよくわからない文章になるなら
    #     文字制限かけない方がいい」
    # MAX_CHARS=20 は根拠の書かれていない裸の定数だった。
    # 実測があるのは**「冒頭3秒」**のほう(competitor-shorts-2026-08-23.md 確度B)で、
    # 字数ではない。読み上げの実測は render 前に check_video が別途出す。
    # 長さより**分かることが先**なので、ここは注意書きにとどめる。
    if len(first) > MAX_CHARS:
        issues.append(("#1", "問いが長い(WARN)",
                       f"{len(first)}字。{MAX_CHARS}字以内(約1〜2秒)にすること: 「{first}」"))
    if not any(w in first for w in SONTOKU):
        issues.append(("#1", "損得の語がない",
                       f"「{first}」に、いくら・何歳・損・戻る などの語がない。"
                       f"制度の問いではなく、視聴者の財布の問いにすること"))

    toi = plan_toi(vdir)
    if toi is None:
        issues.append(("plan.md", "最初の一言がない",
                       "plan.md に「## 最初の一言(問い)」を書き、"
                       "1ユニット目と同じ文を置くこと"))
    elif toi != first:
        issues.append(("plan.md", "最初の一言が台本と違う",
                       f"企画書「{toi}」/ 台本「{first}」"))

    cov = cover_first_line(mod)
    if cov and not QUESTION.search(cov):
        issues.append(("cover", "カバーが問いになっていない",
                       f"「{cov}」。画面と音で同じ問いを出すこと"))
    return issues


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            # WARN は数えない(2026-08-23)。ユーザー指示
            #   「文字制限かけて何言ってるかよくわからない文章になるなら
            #     文字制限かけない方がいい」
            # 降格したのにここで数えていたので、結局落ちていた。
            ng = [i for i in issues if "WARN" not in i[1]]
            total += len(ng)
            print(f"[{'NG' if ng else 'WARN'}] {vdir.name} — {len(issues)}件"
                  f"{'' if len(ng) == len(issues) else f'(うち不合格{len(ng)}件)'}")
            for where, kind, detail in issues:
                print(f"       {where:8} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。1〜2秒で、どの欲求の話かを問いにして言うこと。")
        sys.exit(1)
    print("結果: 冒頭の問いは基準内")


if __name__ == "__main__":
    main()
