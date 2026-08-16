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
    "すると", "たとえば", "例えば", "やがて", "もし", "なので", "そこ", "こう",
)


# ─────────────────────────────────────────────────────────────
# ループ54: 接続語の有無だけでは「繋がっている」ことにならない。
# S013は15文中13文が接続語で始まっていたので全部素通りし、
# ユーザーに「文脈なさすぎる」と再指摘された。
# 表面の目印ではなく、**指す先があるか**を見る。
# ─────────────────────────────────────────────────────────────
DEF_RE = re.compile(r"([一-龥ァ-ヴーA-Za-z0-9]{2,})とは")
SUBJ_RE = re.compile(r"([一-龥ァ-ヴー]{2,})(?:は|が)")
DEMONSTRATIVE = ("その", "この", "あの", "これ", "それ", "あれ")
GENERIC = {"場合", "とき", "こと", "もの", "ほう", "ため", "あと", "自分", "今回",
           "普通", "実際", "本当", "最後", "最初", "全部", "一部", "以上", "以下"}
# 誰でも指す先が分かる日常語は、前振りなしで主語にしてよい(persona.md P-0)。
# この規則が捕まえたいのは「約束は」「手元は」のように**指す先が不明な語**であって、
# 「平均寿命は」のように単体で意味が決まる語ではない
WELL_KNOWN = {"男性", "女性", "日本人", "日本", "平均寿命", "会社員", "家族", "政府",
              "会社", "銀行", "給料", "税金", "年金", "保険料", "手取り", "年収",
              "物価", "値段", "株価", "利息", "家賃", "学費", "宝くじ", "貯金"}


def referent_issues(subs, tail_exempt=2):
    """指す先のない語を洗い出す。

    1. 定義文「XとはY」の X が、直前の文に出ていない
       → 「なぜ急にその言葉の説明が始まるのか」が分からない
    2. 文の主語 X(「Xは」「Xが」)が新出で、指示語も付いていない
       → 主語が宙に浮く(「ただし約束は」= 何の約束?)
    """
    out = []
    for i, cur in enumerate(subs):
        if i >= len(subs) - tail_exempt:
            continue          # 末尾はCTAと冒頭への戻り。新しい主語が出てよい
        if cur.rstrip().endswith(("?", "?")):
            continue          # 問いかけは、新しい話題を持ち出してよい
        prev = " ".join(subs[max(0, i - 3):i])   # 直前3文まで遡って探す
        for m in DEF_RE.finditer(cur):
            term = m.group(1)
            if i > 0 and term not in prev:
                out.append((i + 1, "前振りのない定義",
                            f"「{term}とは」と説明を始めているが、"
                            f"直前の文に「{term}」が出ていない: 「{cur[:20]}」"))
        m = SUBJ_RE.search(cur)
        if not m:
            continue
        subj = m.group(1)
        head = cur[:m.start()]
        if subj in GENERIC or subj in WELL_KNOWN or subj in prev:
            continue
        if any(d in head for d in DEMONSTRATIVE):
            continue        # 「その残りの605万円は」型。指す先は前文にある
        if head.endswith("に"):
            continue        # 「株価に上限はない」型。主題は直前の名詞のほう
        if head and (head[-1].isdigit() or head[-1] in "万億千百0123456789０-９"):
            continue        # 「605万円は」型。数字の一部を名詞と誤認しない
        if "は" in head or "、" in head[-3:]:
            continue        # すでに主題がある文の従属節。文の主語ではない
        if f"{subj}とは" in cur:
            continue
        if i > 0:
            out.append((i + 1, "前振りのない主語",
                        f"「{subj}」が初めて出るのに主語になっている: 「{cur[:20]}」"))
    return out

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
        breaks.append((i + 1, prev, cur, "接続語も共通語もない"))
    # 接続語があっても「指す先」がなければ繋がっていない(ループ54)
    for n, kind, detail in referent_issues(lines, TAIL_EXEMPT):
        breaks.append((n, lines[n - 2] if n >= 2 else "", lines[n - 1], f"{kind}: {detail}"))
    return sorted(breaks)


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())

    total = 0
    for vdir in targets:
        breaks = check_video(vdir)
        if breaks:
            total += len(breaks)
            print(f"[NG] {vdir.name} — 文脈の断絶 {len(breaks)}件")
            for n, prev, cur, why in breaks:
                print(f"       #{n}  前: {prev}")
                print(f"            今: {cur}")
                print(f"            → {why}")
        else:
            print(f"[OK] {vdir.name}")

    print()
    if total:
        print(f"結果: {total}件の断絶。接続語を置くか、前の文に出た語を受けること。")
        sys.exit(1)
    print("結果: 断絶なし")


if __name__ == "__main__":
    main()
