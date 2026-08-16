#!/usr/bin/env python3
"""「1本の鎖になっているか」の機械チェック(ループ64 / プロット改善プログラム フェーズ2)。

ユーザー指摘:「金利の話のやつ、もっと意味わかんなくなってる、プロットが」

診断(docs/research/plot-loop-2026-08/01-research.md):
  物語理解の研究では、出来事の重要さを予測するのは
    (1) 直接の因果的つながりの数
    (2) 冒頭から結末までの因果の鎖の上に載っているか
  の2つ。人は提示された順ではなく**因果の順**に思い出す。
  だから鎖に載っていない事実は落ちるだけでなく、
  **鎖を探して失敗するあいだ次の文が入らない。**

  自チャンネルの実測でも、合否を分けたのは数値の個数ではなく**鎖の本数**だった。
    S011(合格): 種になる数字2つ、全部1本の鎖
    S013(却下): 3つの鎖 + 3つの単発

判定の作り方:
  字幕に出てくる数値を出現順に並べ、**前に出た数値から四則演算で導けるか**を試す。
  導けたら、その数値と元の数値を同じグループにまとめる(union-find)。
  最後に残ったグループの数が「鎖の本数」。

  導出に使ってよい補助定数は 12(ヶ月)・100(%)・2・10 だけ。
  許容誤差は1.5%(画面表示は万円単位に丸めるため)。

判定:
  1. 鎖が多すぎる : 独立したグループが MAX_CHAINS を超える → **不合格**
  2. 宙に浮いた数字: どのグループにも入らない単独の数値 → **参考表示のみ**

較正の結果(02-calibration.md):
  鎖の本数は合否をきれいに分けた(合格作は1〜2本、S013だけ4本)。
  一方 **単発の個数は使えなかった**。ユーザー合格判定の S015(住民税)が5個出る。
  理由は画面表示の丸め。17万円(実際は176,700円)から 1万4700円 を導こうとすると
  170000÷12=14166 で3.8%ずれ、許容誤差を超えて「繋がっていない」と判定される。
  許容誤差を5%まで緩めると今度は S013 の鎖まで繋がってしまい、逆に見逃す。
  **丸めの影響を受ける指標は閾値にしない。** 単発は目で見るための情報として出すだけにした。

使い方:
    python3 production/check_ikko.py                 # 全動画
    python3 production/check_ikko.py videos/S013-... # 1本だけ
    python3 production/check_ikko.py --detail videos/S013-...   # 鎖の中身を表示
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

MAX_CHAINS = 2        # 独立した鎖はここまで(02-calibration.md で較正)
# 単発(宙に浮いた数字)は表示するだけで不合格にしない。丸めで誤爆するため(較正結果)
TOL = 0.015           # 導出の許容誤差(画面は万円単位に丸めるため)
HELPERS = (12, 100, 2, 10)   # ヶ月・パーセント・倍・桁。これ以外の定数は使わない

MULT = {"億": 10**8, "万": 10**4, "千": 10**3, "百": 10**2}
NUM_RUN = re.compile(r"(?:[0-9０-９][0-9０-９.,]*\s*[億万千百]?\s*)+"
                     r"(?:%|％|倍|割|円|年|歳|日|回|人)?")
NUM_PART = re.compile(r"([0-9０-９][0-9０-９.,]*)\s*([億万千百])?")


def to_value(run: str):
    """「1万7920円」→ 17920 のように、表記から値を取り出す。"""
    run = run.translate(str.maketrans("０１２３４５６７８９", "0123456789")).replace(",", "")
    total, has_keta = 0.0, False
    for num, keta in NUM_PART.findall(run):
        if not num:
            continue
        try:
            total += float(num) * MULT.get(keta, 1)
        except ValueError:
            return None
        has_keta = has_keta or bool(keta)
    if total == 0:
        return None
    # 西暦は計算の材料ではない(2026年・1991年など)
    if 1500 <= total <= 2100 and not has_keta and ("年" in run):
        return None
    return total


class Union:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def join(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def derives(target, a, b):
    """a と b から target が作れるか(四則+パーセント)。"""
    for v in (a + b, a - b, b - a, a * b, a * b / 100, a * b / 10_000):
        if v > 0 and abs(v - target) <= TOL * target:
            return True
    for x, y in ((a, b), (b, a)):
        if y and (x / y) > 0 and abs(x / y - target) <= TOL * target:
            return True
    return False


def chains_of(values):
    """出現順の数値列から、鎖(連結成分)を作る。

    「前に出た数値2つ(または1つ+補助定数)から導けるか」を順に試す。
    導けたら同じ鎖にまとめる。
    """
    u = Union()
    seen = []          # (値, 通し番号)
    for i, v in enumerate(values):
        u.find(i)
        pool = seen + [(h, None) for h in HELPERS]
        linked = False
        for ai, (a, ia) in enumerate(pool):
            for b, ib in pool[ai + 1:]:
                if derives(v, a, b):
                    for j in (ia, ib):
                        if j is not None:
                            u.join(i, j)
                            linked = True
                    if linked:
                        break
            if linked:
                break
        seen.append((v, i))
    groups = {}
    for i in range(len(values)):
        groups.setdefault(u.find(i), []).append(i)
    return groups


def _load(render_py: Path):
    spec = importlib.util.spec_from_file_location(f"k_{render_py.parent.name}", render_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def analyse(vdir: Path):
    render_py = vdir / "render.py"
    if not render_py.exists():
        return None
    units = getattr(_load(render_py), "UNITS", [])
    labels, values, seen_keys = [], [], set()
    for u in units:
        s = u.subtitle.replace("【", "").replace("】", "")
        for m in NUM_RUN.finditer(s):
            run = m.group().strip()
            v = to_value(run)
            if v is None:
                continue
            key = round(v, 4)
            if key in seen_keys:
                continue           # 同じ値の再登場は新しい情報ではない
            seen_keys.add(key)
            values.append(v)
            labels.append(run)
    groups = chains_of(values)
    sized = sorted(groups.values(), key=len, reverse=True)
    chains = [g for g in sized if len(g) >= 2]
    orphans = [g[0] for g in sized if len(g) == 1]
    return {"labels": labels, "chains": chains, "orphans": orphans}


def check_video(vdir: Path):
    r = analyse(vdir)
    if r is None:
        return []
    issues = []
    if len(r["chains"]) > MAX_CHAINS:
        issues.append(("鎖が多すぎる",
                       f"独立した鎖が{len(r['chains'])}本(上限{MAX_CHAINS})。"
                       f"1本の動画は1つの問いを1本の計算で解くこと"))
    return issues


def main():
    detail = "--detail" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    targets = [Path(a) for a in args] or sorted(
        p for p in (ROOT / "videos").iterdir() if (p / "render.py").exists())
    total = 0
    for vdir in targets:
        r = analyse(vdir)
        if r is None:
            continue
        issues = check_video(vdir)
        head = f"鎖{len(r['chains'])}本 / 宙に浮いた数字{len(r['orphans'])}個"
        if issues:
            total += len(issues)
            print(f"[NG] {vdir.name} — {head}")
            for kind, detail_msg in issues:
                print(f"       [{kind}] {detail_msg}")
            names = "、".join(r["labels"][i] for i in r["orphans"])
            if names:
                print(f"       (参考)どの計算にも繋がらない数値: {names}")
        else:
            print(f"[OK] {vdir.name} — {head}")
        if detail:
            for n, g in enumerate(r["chains"], 1):
                print(f"       鎖{n}: {' → '.join(r['labels'][i] for i in g)}")
            if r["orphans"]:
                print(f"       単発: {'、'.join(r['labels'][i] for i in r['orphans'])}")
    print()
    if total:
        print(f"結果: {total}件。足すときは同じ量を引く。引けないなら2本に割ること。")
        sys.exit(1)
    print("結果: 鎖は1本にまとまっている")


if __name__ == "__main__":
    main()
