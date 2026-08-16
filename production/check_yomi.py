#!/usr/bin/env python3
"""読み間違いの機械チェック(ループ61)。

ユーザー指摘:「S17はNISAをえぬあいえすえーと読んでるけど。にーさでしょ?
              こんな初歩的なミスなんで治せなかった?」

なぜ直っていなかったかの診断(言い訳なしの事実):
  **同じ問題は S002 で既に見つけて直していた。** そこにはこう書いてある:
      narration="でもニーサなら、税金ゼロ。",  # エヌアイエスエー読み回避(kana照合済み)
  つまり「NISAはニーサと書き直す」という知識は、去年の自分がコードのコメントとして
  リポジトリに残していた。**コメントに書いただけで、チェックにしなかった。**
  だから S017 を新しく書いたとき、その知識は一緒に運ばれてこなかった。
  ユーザーに何度も言われている「文章で書いたルールは守られない」が、そのまま起きた。

何を検査するか:
  VOICEVOX の /audio_query は、実際に読み上げる**カナ**を返す。
  レンダリングと同じ文字列を投げて、返ってきたカナを見れば読み間違いは機械で分かる。

  1. 誤読    : 要注意語が台本にあるのに、カナが正しい読みになっていない
  2. 未登録  : 半角アルファベットが2文字以上続くのに、下の表に無い
               (新しい略語が出るたび「読みをどうするか」を必ず決めさせる)

使い方:
    python3 production/check_yomi.py                 # 全動画
    python3 production/check_yomi.py videos/S017-... # 1本だけ
VOICEVOX が起動していること(bash production/setup_voicevox.sh)。
"""
import importlib.util
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

VOICEVOX_URL = "http://127.0.0.1:50021"
SPEAKER = 3

# 台本に出たら、カナがこう読まれていなければならない語。
# 「誤読の実例」は、そう読まれてしまった記録(再発したらすぐ分かるように残す)。
YOMI = {
    # 語        : (正しい読みのカナ, 誤読の実例)
    "NISA":      ("ニーサ", "エヌアイエスエー"),      # S002で発見 → S017で再発(ループ61)
    "iDeCo":     ("イデコ", "アイデコ"),
    "ATM":       ("エーティーエム", ""),
    "PER":       ("ピーイーアール", ""),
    "S&P":       ("エスアンドピー", ""),
    "ETF":       ("イーティーエフ", ""),
    "GDP":       ("ジーディーピー", ""),
    "IPO":       ("アイピーオー", ""),
}
# 半角アルファベットの連なり。ここに出た語は必ず YOMI に登録されていること
ALPHA_RUN = re.compile(r"[A-Za-z][A-Za-z&.]+")


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"y_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def kana_of(text: str) -> str:
    """VOICEVOX が実際に読むカナを取る(レンダリングと同じ文字列を投げる)。"""
    url = f"{VOICEVOX_URL}/audio_query?speaker={SPEAKER}&text={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("kana", "")


# VOICEVOX の kana は長音「ー」を母音で書く(ニーサ → ニイサ / エーティーエム → エエティイエム)。
# 照合する側も同じ書き方に直さないと、正しく読めているのに不合格になる。
VOWEL_OF = {}
for _row, _v in (("アカサタナハマヤラワガザダバパャァ", "ア"),
                 ("イキシチニヒミリギジヂビピィ", "イ"),
                 ("ウクスツヌフムユルグズヅブプュゥヴ", "ウ"),
                 ("エケセテネヘメレゲゼデベペェ", "エ"),
                 ("オコソトノホモヨロヲゴゾドボポョォ", "オ")):
    for _c in _row:
        VOWEL_OF[_c] = _v


def expand_choon(kana: str) -> str:
    """「ー」を直前のカナの母音に開く(VOICEVOXのkana表記に合わせる)。"""
    out = []
    for ch in kana:
        out.append(VOWEL_OF.get(out[-1], "") if ch == "ー" and out else ch)
    return "".join(out)


def plain(kana: str) -> str:
    """アクセント記号と区切りを外して、語の照合だけができる形にする。"""
    s = kana.replace("'", "").replace("/", "").replace("、", "").replace("_", "")
    return expand_choon(s)


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    issues = []
    for i, u in enumerate(units, 1):
        src = u.subtitle.replace("【", "").replace("】", "")   # 画面に出る文
        spoken = u.tts_text()                                  # 実際に読ませる文
        kana = plain(kana_of(spoken))
        for word, (want, seen_before) in YOMI.items():
            if word not in src and word not in spoken:
                continue
            if expand_choon(want) in kana:
                continue
            hint = f"(過去に「{seen_before}」と読まれた)" if seen_before else ""
            issues.append((f"#{i}", "誤読",
                           f"「{word}」を「{want}」と読んでいない{hint}。"
                           f"実際のカナ「{kana}」。"
                           f"Unit(narration=...) でカナ書きに置き換えること"))
        # 表に無い略語は、読みを決めないまま通さない
        for run in ALPHA_RUN.findall(spoken):
            if run not in YOMI and run.upper() not in YOMI:
                issues.append((f"#{i}", "未登録の略語",
                               f"「{run}」の読みが check_yomi.py の YOMI に無い。"
                               f"実際のカナ「{kana}」を確かめて、表に足すこと"))
    return issues


def main():
    try:
        urllib.request.urlopen(f"{VOICEVOX_URL}/version", timeout=5).read()
    except Exception:
        print("VOICEVOX が起動していない。bash production/setup_voicevox.sh を先に実行すること")
        sys.exit(2)
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
        print(f"結果: {total}件の読み間違い。字幕は元の表記のまま、"
              f"Unit(narration=...) で読み上げ用の文だけカナにすること。")
        sys.exit(1)
    print("結果: 読み間違いなし")


if __name__ == "__main__":
    main()
