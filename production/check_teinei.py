#!/usr/bin/env python3
"""「端折っていないか」の機械チェック(ループ51)。

ユーザー指摘(3回目):
  「また端折りすぎてる。相手が本当に初心者だと仮定してもっと丁寧に」
  「同じこと言ってるので学習して欲しい」

なぜ再発したかの診断:
  1. 尺の**下限がなかった**。上限55秒に対して作っていたのは40〜42秒で、
     15秒ぶんの説明を捨てても機械は何も言わなかった
  2. 「1ユニットに新しい数字をいくつ出したか」を数えていなかった。
     「株価1500円わる利益100円」のように、初出の数字を2つ同時に投げていた
  3. 専門用語(債券・指数・権利落ち・PER…)を、意味を言う前に使っていた

判定:
  0. 話題が不明  : 1文目に「何の話か」を示す語がない(ループ52)
     ユーザー指摘:「ショート動画で流れてくるこの動画にたどり着いた人が、
     まずそもそも投資の話なのかすら分からない」
     S022の反省で作った「フックは名詞なしで分かる矛盾にする」を文章のまま持っていたら、
     話題語ごと消すところまでやってしまった。矛盾で引くのは正しいが、
     **話題語(株・投資・NISA…)は必ず1文目に残す**
  1. 尺が短い    : 推定尺が MIN_SEC 未満。上限まで使って説明を足すこと
  2. 詰め込み    : 1ユニットに初出の数値が2つ以上
  3. 用語が裸    : 専門用語が字幕に出るのに、どこにも「言い換え」がない
  4. 説明が後    : 用語を使ってから2文以上あとで言い換えている(WARN)

使い方:
    python3 production/check_teinei.py                 # 全動画
    python3 production/check_teinei.py videos/S011-... # 1本だけ
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

MIN_SEC = 46.0        # これ未満なら、上限(55.5秒)まで説明を足す余地がある
MAX_NEW_NUM = 1       # 1ユニットに出してよい「初出の数値」の数

# 初心者が意味を知らない前提の語。字幕に出すなら、必ずどこかで言い換える
JARGON = [
    "債券", "利回り", "表面利率", "額面", "満期", "発行体", "元本",
    "指数", "レバレッジ", "インデックス", "投資信託", "投信", "基準価額",
    "権利落ち", "権利確定", "配当", "源泉徴収", "課税",
    "為替", "為替ヘッジ", "円安", "円高",
    "信用取引", "空売り", "貸株料", "追証", "約定", "単元",
    "PER", "1株あたり", "複利", "分配金", "含み益", "評価額",
]
# 1文目に必ず入れる「何の話か」を示す語。フィードを流し見ている人が
# 「これは自分に関係あるお金の話だ」と判定できる語であること
TOPIC = [
    # 投資・お金の器
    "株", "投資", "投信", "投資信託", "NISA", "iDeCo", "債券", "年金", "貯金", "預金",
    "金利", "為替", "円安", "円高", "配当", "保険", "税金", "住民税", "所得税",
    "手取り", "年収", "給料", "ボーナス", "ローン", "積立", "利息", "老後", "資産",
    # 生活で実際に払う・もらうもの(S020 宝くじ / S021 学費 はここで拾う)
    "宝くじ", "学費", "教育費", "子ども", "退職金", "家賃", "医療費", "ふるさと納税",
    "スマホ", "電気代", "車",
]
# 「言い換えた」と認める書き方。用語と同じ字幕にこれがあれば定義したとみなす
GLOSS = ("とは", "という", "のこと", "意味", "つまり", "呼ばれる", "呼ぶ", "＝", "=")

# 「1万5000円」を1つの数として数える(桁の区切りで割ると、詰め込み判定が誤爆する)
NUM = re.compile(r"(?:[0-9０-９][0-9０-９.,]*\s*[億万千百]?\s*)+(?:%|倍|割|円|年|歳|日|ドル)?")


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"t_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def plain(u):
    return u.subtitle.replace("【", "").replace("】", "")


def check_video(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return []
    units = getattr(_load(render_py), "UNITS", [])
    if not units:
        return []
    subs = [plain(u) for u in units]
    issues = []

    # 0. 1文目に話題語がない = 何の動画か分からないまま流される
    if not any(w in subs[0] for w in TOPIC):
        issues.append(("#1", "話題が不明",
                       f"1文目「{subs[0]}」に、何の話か示す語がない。"
                       f"株・投資・NISA など、流し見の人が自分ごとと判定できる語を入れる"))

    # 1. 尺が短い(端折りの一番の温床)
    chars = sum(len(s) for s in subs)
    est = chars * 0.191 + len(units) * 0.15
    if est < MIN_SEC:
        issues.append(("(動画全体)", "尺が短い",
                       f"推定{est:.0f}秒。上限55秒まで{55 - est:.0f}秒ぶん、"
                       f"説明を足す余地がある(端折っていないか)"))

    # 2. 詰め込み(1ユニットに初出の数値が2つ以上)
    def key(tok):
        """「100円」と「100」は同じ数として扱う(単位違いで初出判定が誤爆する)。"""
        return re.sub(r"(%|倍|割|円|年|歳|日|ドル)$", "", tok.replace(" ", "").replace(",", ""))

    seen_nums = set()
    for i, s in enumerate(subs):
        nums = {m.group().replace(" ", "") for m in NUM.finditer(s)}
        fresh = sorted(n for n in nums if key(n) not in seen_nums)
        seen_nums |= {key(n) for n in nums}
        if i == 0:
            continue      # 1文目は「0円。退職金2000万円にかかる税金。」型が正しい(S015)
        if len(fresh) > MAX_NEW_NUM:
            issues.append((f"#{i + 1}", "詰め込み",
                           f"初出の数値が{len(fresh)}個: {'、'.join(fresh)}"
                           f" — 「{s[:20]}」。1文につき新しい数字は1つまで"))

    # 3. 用語が裸(言い換えがない)
    joined = "".join(subs)
    for term in JARGON:
        if term not in joined:
            continue
        explained = any(term in s and any(g in s for g in GLOSS) for s in subs)
        if not explained:
            first = next(i for i, s in enumerate(subs) if term in s)
            issues.append((f"#{first + 1}", "用語が裸",
                           f"「{term}」を説明せずに使っている。"
                           f"「〜とは」「〜のこと」で一度言い換えること"))
        else:
            first = next(i for i, s in enumerate(subs) if term in s)
            gloss_at = next(i for i, s in enumerate(subs)
                            if term in s and any(g in s for g in GLOSS))
            if gloss_at > first + 1:   # 名前を出した次の文で言い換えるのは正しい順序
                issues.append((f"#{first + 1}", "説明が後(WARN)",
                               f"「{term}」を#{first + 1}で使い、#{gloss_at + 1}で説明している。"
                               f"使う前に言い換える"))
    return sorted(set(issues))


def main():
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
            for where, kind, detail in issues:
                print(f"       {where:6} [{kind}] {detail}")
        else:
            print(f"[OK] {vdir.name}")
    print()
    if fails:
        print(f"結果: {total}件(うち不合格{fails}件)。"
              f"相手は本当の初心者。数字の出どころと用語の意味を必ず言うこと。")
        sys.exit(1)
    print("結果: 不合格なし" + (f"(WARN {total}件)" if total else ""))


if __name__ == "__main__":
    main()
