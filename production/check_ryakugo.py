#!/usr/bin/env python3
"""専門語を途中から略していないかの機械チェック(ループ65)。

ユーザー指摘:
  「S13、変動と固定はみたいな表現してるけど…変動金利と固定金利でしょ?
    なんでずっと省略してるの…? 何回言ったらこれ直るの?」

なぜ再発したかの診断(言い訳なしの事実):
  ループ60で**同じ指摘**を受けている(「変わらない金利もある、から何の話か分からない」)。
  そのとき「専門語は避けるのではなく、名前で呼んで、その場で意味を言う」を
  **プレイブック W7 として文章で書いた**。だが**機械チェックにしなかった**。
  そしてループ64(プロット改善)で尺を詰めたとき、
  「変動金利」→「変動」、「固定金利」→「固定」と2文字ずつ削って辻褄を合わせた。
  W8(尺のために助詞と動詞を削らない)と同じ穴を、語のレベルで開けていた。

  文章で書いたルールは守られない。だからチェックにする。

判定:
  **render.py のどこか(画面の文字を含む)に正式名が出ている**なら、
  ナレーションでその語を**頭だけ**にして使ってはいけない(「変動は」「変動が」…)。

  最初は「台本に正式名が出たら」を条件にしていたが、それでは S013 を素通りさせた。
  S013 は**ナレーションで一度も「変動金利」と言っていない**(画面のグラフの凡例にだけ
  「変動金利」と書いてある)。略しているのではなく最初から略語しか喋っていない、
  という一番悪い形だったので、条件を「画面に出ていれば」に広げた。

使い方:
    python3 production/check_ryakugo.py                 # 全動画
    python3 production/check_ryakugo.py videos/S013-... # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# (正式名, 略しがちな頭) — 台本に正式名が出たら、頭だけの単独使用を禁じる。
# 「変動する」のような動詞の一部と区別するため、頭の直後に来てよい文字も持たせる。
PAIRS = [
    ("変動金利", "変動"),
    ("固定金利", "固定"),
    ("国民年金", "国民"),
    ("厚生年金", "厚生"),
    ("住民税", "住民"),
    ("所得税", "所得"),
    ("普通預金", "普通"),
    ("投資信託", "投信"),
    ("損益通算", "損益"),
    ("高額療養費", "高額"),
    ("退職所得控除", "退職控除"),
]
# 頭の直後がこれらなら、略語として単独で使われている(助詞・句読点・文末)
PARTICLES = "はがをにでもとやのなら、。?!でしょよねか"


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"r_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    subs = [u.subtitle.replace("【", "").replace("】", "") for u in units]
    source = render_py.read_text()      # 画面に出る文字も含めて探す
    issues = []
    for full, head in PAIRS:
        if full not in source:
            continue                    # その語を扱っていない動画は対象外
        tail = full[len(head):]         # 「変動金利」なら「金利」
        for i, s in enumerate(subs, 1):
            for m in re.finditer(re.escape(head), s):
                after = s[m.end():]
                if after.startswith(tail):
                    continue            # 正式名として使われている
                if not after or after[0] in PARTICLES:
                    issues.append((f"#{i}", "専門語を略している",
                                   f"「{full}」と言っているのに「{head}」だけで使っている: "
                                   f"「{s}」。尺が足りないならビートを削ること(W8)"))
                    break
    return sorted(set(issues))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:5} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。一度フルネームで呼んだ語は、最後までフルネームで呼ぶこと。")
        sys.exit(1)
    print("結果: 略語なし")


if __name__ == "__main__":
    main()
