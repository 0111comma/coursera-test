#!/usr/bin/env python3
"""読み間違いの機械チェック(ループ71で作り直し)。

ユーザー指摘:
  「相続税の動画、マジゴミだと思う。何の話してるかわかんないし、**読み間違いもあるし**」

実際に S018 で「相続人」を **ソオゾクジン** と読んでいた(正しくは そうぞくにん)。
前の版のこのファイルは**手で書いた誤読しやすい語の一覧**で、
「相続人」が入っていなかったので [OK] を返していた。**登録し忘れは黙って通っていた。**

作り直した判定:
  1. VOICEVOX に実際に読ませ、その読み(カナ)をもらう
  2. 同じ文を形態素解析(janome)して、辞書の読みを並べる
  3. **語ごとに突き合わせ**、辞書の読みが音声の中に見つからない語を落とす

数字・記号・辞書に読みの無い語は突き合わせから外し、その先で位置を取り直す。
長音の書き方のゆれ(ソオ/ソウ、ゼエ/ゼイ)は畳んでから比べる。

正しいのに落ちる組み合わせは production/yomi_ok.txt に「語:読み」で足す。
**一覧に無い語は落ちる**向きにしてあるので、登録し忘れは黙って通らない。

VOICEVOX が起動していないと走らない(bash production/setup_voicevox.sh)。

使い方:
    python3 production/check_yomi.py                    # 全動画
    python3 production/check_yomi.py videos/S018-...    # 1本だけ
"""
import importlib.util
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

OK_FILE = PRODUCTION / "yomi_ok.txt"
ENDPOINT = "http://127.0.0.1:50021"
SPEAKER = 3
WINDOW = 14          # 何モーラ先まで探しにいくか(数字や未知語を飛ばすため)

try:
    from janome.tokenizer import Tokenizer
except ImportError:
    print("[NG] janome が入っていません。`pip install janome` を実行してください。",
          file=sys.stderr)
    sys.exit(2)

_T = Tokenizer()

# オ段・エ段の長音の書き方のゆれを畳む(VOICEVOXは「ソオ」、辞書は「ソウ」)。
# **文字列を for で回すと1文字ずつになる**。「チョ」が「チ」と「ョ」に割れて
# 「ミチオ」を「ミチウ」に変えてしまい、助詞の「を」が行方不明になった。並びで持つ。
_O_ROW = ["オ", "コ", "ソ", "ト", "ノ", "ホ", "モ", "ヨ", "ロ", "ゴ", "ゾ", "ド", "ボ", "ポ",
          "キョ", "ショ", "チョ", "ニョ", "ヒョ", "ミョ", "リョ", "ギョ", "ジョ", "ビョ", "ピョ"]
_E_ROW = ["エ", "ケ", "セ", "テ", "ネ", "ヘ", "メ", "レ", "ゲ", "ゼ", "デ", "ベ", "ペ"]



_VOWEL = {}
for _row, _v in [("アカサタナハマヤラワガザダバパャァヮ", "ア"),
                 ("イキシチニヒミリギジヂビピィ", "イ"),
                 ("ウクスツヌフムユルグズヅブプュゥヴ", "ウ"),
                 ("エケセテネヘメレゲゼデベペェ", "エ"),
                 ("オコソトノホモヨロゴゾドボポョォ", "オ")]:
    for _ch in _row:
        _VOWEL[_ch] = _v


def _expand_choon(k: str) -> str:
    """「ー」を直前の音の母音に開く(ボーナス→ボオナス)。

    VOICEVOX の kana は長音を母音の文字で書く。辞書側の「ー」を消すだけだと
    ボナス vs ボオナスで、音声が正しくても不一致になる。"""
    out = []
    for ch in k:
        if ch == "ー" and out:
            out.append(_VOWEL.get(out[-1], ""))
        else:
            out.append(ch)
    return "".join(out)


def loose(k: str) -> str:
    """記号と表記ゆれだけを落とす。**長音の畳み込みはここでやらない。**

    音声の側で畳むと語をまたいで壊れる。「ダト|オモッテ」の「トオ」を
    長音と見て「ダトウモッテ」にしてしまい、「思っ」が行方不明になった。
    長音のゆれは、**辞書側の1語だけ**を variants() で開いて吸収する。
    """
    k = re.sub(r"[’'_/、。?!\s]", "", k)
    k = _expand_choon(k)
    return k.replace("ヴ", "ブ").replace("ヅ", "ズ").replace("ヂ", "ジ")


_RENDAKU = str.maketrans("カキクケコサシスセソタチツテトハヒフヘホ",
                         "ガギグゲゴザジズゼゾダヂヅデドバビブベボ")


def variants(reading: str):
    """辞書の読み1語を、VOICEVOXの書き方のゆれまで開く(ソウゾク→ソオゾク)。"""
    out = {reading}
    if reading == "ウ":
        out.add("オ")          # 「だろ|う」の う は、音では オ(ダロオ)
    if reading == "ナニ":
        out.add("ナン")        # 何% や 何歳 の 何 は ナン
    if reading and reading[0] in "カキクケコサシスセソタチツテトハヒフヘホ":
        out.add(reading[0].translate(_RENDAKU) + reading[1:])  # 連濁: リボ払い=バライ
    for a in _O_ROW:
        if a + "ウ" in reading:
            out |= {v.replace(a + "ウ", a + "オ") for v in list(out)}
    for a in _E_ROW:
        if a + "イ" in reading:
            out |= {v.replace(a + "イ", a + "エ") for v in list(out)}
    return out


def voicevox_kana(text: str) -> str:
    url = f"{ENDPOINT}/audio_query?text={urllib.parse.quote(text)}&speaker={SPEAKER}"
    with urllib.request.urlopen(urllib.request.Request(url, method="POST"), timeout=30) as r:
        return json.load(r)["kana"]


def load_ok():
    if not OK_FILE.exists():
        return set()
    out = set()
    for ln in OK_FILE.read_text().splitlines():
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        if ":" in ln:
            w, y = ln.split(":", 1)
            out.add((w.strip(), loose(y.strip())))
        else:
            out.add((ln, None))          # 語だけ = その語の読みは確認済み
    return out


def expected_tokens(text: str):
    """(表層, 期待する読み) の並び。読みが分からない語は読み None。"""
    out = []
    for t in _T.tokenize(text):
        surf, pos = t.surface, t.part_of_speech.split(",")[0]
        sub = t.part_of_speech.split(",")[1]
        rd = t.reading
        if pos in ("助詞", "接続詞") and surf.endswith("は"):
            rd = loose(rd)[:-1] + "ワ"      # は・では・とは・には … 助詞のハはワ
        elif pos == "助詞" and surf == "を":
            rd = "オ"
        elif pos == "助詞" and surf == "へ":
            rd = "エ"
        sub2 = t.part_of_speech.split(",")[2]
        # 数詞(万・千)と助数詞(円・月・歳)も飛ばす。「3千」は連濁でサンゼン、
        # 「12月」はガツで、辞書のセン・ツキと突き合わせると音声が正しくても落ちる。
        # 飛ばした並びは check_line が数字ごと VOICEVOX に単体で聞いて照合する
        if (rd == "*" or re.search(r"[0-9０-９]", surf) or pos == "記号"
                or sub == "数" or sub2 == "助数詞"):
            out.append((surf, None))
        else:
            out.append((surf, loose(rd)))
    return out


def compounds(text: str):
    """辞書に1語として載っていない複合名詞を返す(ループ71)。

    「相続人」は IPADIC に無く、「相続」+「人」に割れる。
    そして IPADIC はここの「人」を **ジン** と読む。VOICEVOX も同じ辞書系なので
    **辞書と音声が同じように間違える**。語ごとの突き合わせでは一致してしまい、
    ソオゾクジンがそのまま通った。

    だから「辞書が1語として知らない複合語」は、読みが保証されていないものとして
    ぜんぶ出す。正しく読めていることを耳で確かめたら yomi_ok.txt に足す。
    """
    toks = [(t.surface, t.part_of_speech.split(",")[0], t.part_of_speech.split(",")[1])
            for t in _T.tokenize(text)]
    runs, cur = [], []
    for surf, pos, sub in toks:
        if pos == "名詞" and sub not in ("数", "代名詞", "非自立"):
            cur.append(surf)
        else:
            if len(cur) >= 2:
                runs.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        runs.append("".join(cur))
    out = []
    for r in runs:
        if len(r) < 3 or not re.search(r"[一-龥]", r):
            continue
        if not re.fullmatch(r"[一-龥ヶァ-ヴーA-Za-z々]+", r):
            continue                      # ひらがなが混じる並びは複合語ではない
        if len(list(_T.tokenize(r))) == 1:
            continue                      # 辞書に1語としてある
        out.append(r)
    return out


def check_line(text: str, ok):
    kana = loose(voicevox_kana(text))
    pos = 0
    bad = []
    pending = []
    for surf, want in expected_tokens(text):
        if not want:
            pending.append(surf)          # 数字・記号・未知語。まとめて後で位置を進める
            continue
        if (surf, want) in ok or (surf, None) in ok:
            continue
        # 直前に数字や未知語を飛ばしていたら、その読みを VOICEVOX に単体で聞き、
        # 本文の読みの中で探して位置をそこまで進める。窓を開けるだけだと
        # 「20.21%に」の助詞ニが数字の読みの中のニに食いつき、後続がずれる
        limit = pos + WINDOW
        if pending:
            joined = "".join(pending)
            g = loose(voicevox_kana(joined)) if loose(joined) != "" else ""
            i = kana.find(g, pos) if g else -1
            # 飛ばした並びの読みは今の位置のすぐ先にあるはず。遠くの一致は
            # 別の語の一部(「2」のニが後ろの助詞ニに食いつく)なので採らない
            if i != -1 and i - pos > 4:
                i = -1
            if i != -1:
                pos = i + len(g)
                limit = pos + WINDOW
                pending = []
            else:
                # 数字は後ろの助数詞で読みが変わる(2つめ=フタツメ、単体の2=ニ)。
                # 今の語まで含めて聞き直し、見つかればその語ごと照合済みにする。
                # 数字を含まない飛ばし(読点だけ等)でやると逆に壊すので、数字の時だけ
                j = -1
                if re.search(r"[0-9０-９]", joined):
                    g2 = loose(voicevox_kana(joined + surf))
                    j = kana.find(g2, pos) if g2 else -1
                pending = []
                if j != -1:
                    pos = j + len(g2)
                    continue
                limit = len(kana)         # それでも読みが違う数字は窓を全開に
        hit = -1
        for v in variants(want):
            i = kana.find(v, pos)
            if i != -1 and i <= limit and (hit == -1 or i < hit):
                hit, want_hit = i, v
        if hit == -1:
            near = kana[pos:pos + len(want) + 4]
            bad.append((surf, want, near))
            # ズレの連鎖を止める。窓の外でも見つかればそこまで位置を進める
            for v in variants(want):
                j = kana.find(v, pos)
                if j != -1:
                    pos = j + len(v)
                    break
        else:
            pos = hit + len(want_hit)
    return bad


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"v_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_video(vdir: Path, ok):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    issues = []
    seen = set()
    for i, u in enumerate(units, 1):
        # 照合するのは実際に読み上げるテキスト(narration上書きとREADING表を通した後)。
        # 字幕の生テキストで照合すると、上書きで直してある NISA や 令和 が誤検出になる
        text = u.tts_text()
        for surf, want, near in check_line(text, ok):
            issues.append((f"#{i}", "読み間違いの疑い",
                           f"「{surf}」を {want} と読むはずが、音声は「{near}」。"
                           f"正しければ production/yomi_ok.txt に「{surf}:{near}」を足すこと"))
        for c in compounds(text):
            if c in seen or any(w == c for w, _ in ok):
                continue
            seen.add(c)
            kana = loose(voicevox_kana(c))
            issues.append((f"#{i}", "読みが未確認の複合語",
                           f"「{c}」は辞書に1語として無い。音声は「{kana}」。"
                           f"合っていれば production/yomi_ok.txt に「{c}:{kana}」を足すこと"))
    return issues


def main():
    try:
        urllib.request.urlopen(f"{ENDPOINT}/version", timeout=5).read()
    except Exception:
        print("[NG] VOICEVOX が起動していません。"
              "`bash production/setup_voicevox.sh` を実行してください。", file=sys.stderr)
        sys.exit(2)
    ok = load_ok()
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        issues = check_video(vdir, ok)
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {len(issues)}件")
            for where, kind, detail in issues:
                print(f"       {where:5} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if total:
        print(f"結果: {total}件。読みが違う語は、かなで書くか言い換えること。")
        sys.exit(1)
    print("結果: 読み間違いなし")


if __name__ == "__main__":
    main()
