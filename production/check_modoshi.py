#!/usr/bin/env python3
"""直した文が、あとの周で元に戻っていないかを見るゲート(2026-09-07)。

日本語パネル4周目の指摘:

> 3周目に「対応済み(コミット)」で閉じた直しのうち7件が、4周目の台本で
> 元の形に戻っている。ストックの「対応済み」を人手で守るのをやめ、
> **書き直し後の台本に対して前周の指摘が残っているかを機械で照合する**。

原因は、直したあとの尺詰めで元の言い回しに戻したこと。ログとストックは
「直した」と言っているのに出荷物は直っていない、という状態がいちばん危ない
(次の周で同じ指摘をもう一度買うことになる)。

判定はひとつだけ、**言い訳の余地がない形**にしてある:

    ストックで「対応済み」になっている行の**直す前の文**が、
    いまの render.py の字幕にそのまま残っていたら落とす。

「直し」の文と突き合わせない理由: 実際の出荷では尺やほかのゲートの都合で
提案どおりの文にならないことが多く、照合すると誤検出ばかりになる。
直す前の文の**再出現**なら、それは巻き戻し以外にありえない。

使い方:
    python3 production/check_modoshi.py                    # 全動画
    python3 production/check_modoshi.py videos/Z001-...    # 1本だけ
"""
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent

# ストックごとの「直す前」の欄の位置(| で割ったときの添え字)。
# nihongo-stock: '' ID 日付 動画 カット 型 審査員 重さ **直す前** 直し 状態 ''
# shiteki-stock: '' ID 日付 動画 審査員 重さ 指摘 **根拠** 直し 状態 ''
STOCKS = {
    ROOT / "docs/research/nihongo-stock.md": 8,
    ROOT / "docs/research/shiteki-stock.md": 7,
}

MIN_LEN = 12          # これより短い断片は偶然一致するので見ない
DONE_RE = re.compile(r"対応済み")
ROW_RE = re.compile(r"^\|\s*([A-Z]\d{3})-[^|]*\|")


NEAR_RATIO = 0.62      # 文字bigramの類似度。これ以上なら「疑い」として出す(落とさない)


def _bigrams(t: str) -> set:
    t = re.sub(r"[、。「」『』?!  ]", "", t)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def _similar(a: str, b: str) -> float:
    """文字bigramの Jaccard 類似度。0〜1。"""
    x, y = _bigrams(a), _bigrams(b)
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)


def _sentences(cell: str) -> list[str]:
    """「直す前」の欄から、台本の文だけを取り出す。

    欄は「…」でくくってあることも、地のまま書いてあることもある。
    どちらも拾うが、説明の地の文を拾わないよう、句点か疑問符で終わる
    ものだけにする。
    """
    cell = cell.strip()
    out = [m.group(1).strip()
           for m in re.finditer(r"「([^「」]{%d,}?)」" % MIN_LEN, cell)]
    if not out and len(cell) >= MIN_LEN:
        out = [cell]
    return [s for s in out if s.endswith(("。", "?", "?"))]


def rows_for(video_id: str):
    """その動画の「対応済み」の行から (ID, 直す前の文, ストック名) を集める。"""
    found = []
    for stock, col in STOCKS.items():
        if not stock.exists():
            continue
        for line in stock.read_text(encoding="utf-8").splitlines():
            m = ROW_RE.match(line)
            if not m or m.group(1) != video_id:
                continue
            cells = line.split("|")
            if len(cells) <= col + 2 or not DONE_RE.search(cells[-2]):
                continue
            for s in _sentences(cells[col]):
                found.append((cells[1].strip(), s, stock.name))
    return found


def main(video_dir: Path) -> int:
    render = video_dir / "render.py"
    if not render.exists():
        return 0
    src = render.read_text(encoding="utf-8")
    # **字幕そのものと一致したときだけ落とす。**部分一致だと語の再利用を
    # 巻き戻しと呼んでしまう(「上司の機嫌」は何度出てもよい)
    subtitles = set(re.findall(r'Unit\("[^"]+", "([^"]*)"', src))

    hits, near, seen = [], [], set()
    for tid, before, stock in rows_for(video_dir.name.split("-")[0]):
        if before in seen:
            continue
        seen.add(before)
        if before in subtitles:
            hits.append((tid, before, stock))
            continue
        # **言い回しを変えた巻き戻し**(2026-09-07 批評パネル)。
        # 「自分で変えられることだけを見た」は、一度落とした
        # 「変えられることだけ見てた」と字面が違うので上の完全一致では止まらない。
        # 文字bigramの類似度で「疑い」を出す。**落とさない**のは、
        # 同じ話題を扱う以上どうしても似た文が出るため(誤検出でゲートを
        # 止めると、次から人が理由なく免除を足す入口になる)。
        # 疑いは日本語パネル/批評パネルへの入力として使う
        for sub in subtitles:
            if _similar(before, sub) >= NEAR_RATIO:
                near.append((tid, before, sub, stock))
                break

    for tid, before, sub, stock in near:
        print(f"  [疑い] {video_dir.name} {tid} ({stock}) — 言い回しを変えた巻き戻しかもしれない")
        print(f"         直す前: 「{before}」")
        print(f"         いまの字幕: 「{sub}」")

    if not hits:
        print(f"[OK] {video_dir.name}" + (f" — 疑い{len(near)}件(落とさない)" if near else ""))
        return 0
    print(f"[NG] {video_dir.name} — 直したはずの文が戻っている {len(hits)}件")
    for tid, before, stock in hits:
        print(f"       {tid}  ({stock})")
        print(f"              「{before}」")
    return len(hits)


if __name__ == "__main__":
    targets = ([Path(a) for a in sys.argv[1:]]
               if len(sys.argv) > 1
               else sorted(p for p in (ROOT / "videos").iterdir()
                           if p.is_dir() and not p.name.startswith("_")))
    n = sum(main(t) for t in targets)
    print()
    if n:
        print("結果: {}件の巻き戻し。**ストックの「対応済み」を「未対応」に戻すか、"
              "台本を直すか、どちらかをすること。**".format(n))
    else:
        print("結果: 巻き戻しなし")
    sys.exit(0)
