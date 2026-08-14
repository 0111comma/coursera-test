#!/usr/bin/env python3
"""文脈の断絶チェック(ループ㊶)。

ユーザー指摘:「全体の話の繋がりが見えない。文脈が2回途切れてて、
もう何の話してるか分からなくなる」。

1文ずつは明確でも、文と文が繋がっていないと視聴者は迷子になる。
プレイブックのD10「全ビートがBut/Thereforeで繋がる」は文章で書いてあるだけで
検査されていなかったため、機械チェックにする。

判定: ユニットNは、次のどちらかを必ず満たすこと。
  (a) 冒頭が接続語(でも/だから/では/つまり/まず/ただし/しかも/じゃあ …)
  (b) 直前のユニットに出た内容語(2文字以上の漢字語・カタカナ語・数値)を受けている

どちらも無い = 前の文と何の関係もない文がいきなり始まる = 文脈の断絶。

末尾のCTA・ループユニットは意図的な転換なので除外する。

使い方:
    python3 production/check_flow.py                    # 全動画
    python3 production/check_flow.py videos/S010-...    # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

# 文頭に置かれたら「前を受けている」とみなす接続語
CONNECTIVES = (
    "でも", "だから", "では", "じゃあ", "つまり", "まず", "ただし", "しかも", "さらに",
    "そして", "その", "これ", "この", "それ", "ちなみに", "実は", "なのに", "しかし",
    "一方", "逆に", "そこで", "だが", "けど", "ところが", "答えは", "そのうち",
)

# 内容語として数えない汎用語(これだけ一致しても「繋がっている」とは言えない)
STOPWORDS = {
    "こと", "もの", "とき", "ため", "場合", "自分", "本当", "今回", "あなた", "ボク",
    "以上", "以下", "以内", "程度", "感じ", "話", "額", "分", "円", "月", "年", "日",
}

TAIL_EXEMPT = 2   # 末尾N個(CTA・ループバック)は判定しない


def content_words(text: str) -> set:
    """漢字語・カタカナ語・英字語・数値を内容語として拾う。"""
    words = set()
    words |= set(re.findall(r"[一-龥]{2,}", text))          # 漢字2字以上
    words |= set(re.findall(r"[ァ-ヴー]{2,}", text))         # カタカナ
    words |= set(re.findall(r"[A-Za-z]{2,}", text))          # 英字
    words |= set(re.findall(r"[0-9０-９]+(?:万|億|%|円)?", text))  # 数値
    return {w for w in words if w not in STOPWORDS}


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"f_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    lines = [u.subtitle.replace("【", "").replace("】", "") for u in units]
    breaks = []
    last = len(lines) - TAIL_EXEMPT
    for i in range(1, last):
        cur, prev = lines[i], lines[i - 1]
        if cur.startswith(CONNECTIVES):
            continue
        shared = content_words(cur) & content_words(prev)
        if shared:
            continue
        breaks.append((i + 1, prev, cur))
    return breaks


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())

    total = 0
    for vdir in targets:
        breaks = check_video(vdir)
        if breaks:
            total += len(breaks)
            print(f"[NG] {vdir.name} — 文脈の断絶 {len(breaks)}件")
            for n, prev, cur in breaks:
                print(f"       #{n}  前: {prev}")
                print(f"            今: {cur}   ← 接続語も共通語もない")
        else:
            print(f"[OK] {vdir.name}")

    print()
    if total:
        print(f"結果: {total}件の断絶。接続語を置くか、前の文に出た語を受けること。")
        sys.exit(1)
    print("結果: 断絶なし")


if __name__ == "__main__":
    main()
