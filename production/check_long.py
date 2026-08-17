#!/usr/bin/env python3
"""長尺(横型)専用の機械ゲート(ループ71 フェーズ11)。

なぜ必要か:
  L001 を「ゴミ」と判定されたとき、**ショート用の9ゲートは全部通っていた。**
  1ユニットずつの品質は基準内なのに、通して見ると成立していない。
  ユニット単位のゲートは9つあるのに、
  **「30秒時点で何が出ているか」「章の出口に答えがあるか」を測るものが1つも無かった。**

  フェーズ2〜10で測る道具を `timeline_long.py` に足してきたが、
  あれは**目で見る道具**で、通らなくても走ってしまう。だから落ちるゲートにする。

  そして **フェーズ1の反省**を効かせる: 自分で作ったゲートのせいで
  L002 は尺のために89ユニット足された。だから
  **「量を増やせば通るゲート」は WARN に落とし、
    「量を増やしても通らないゲート」だけを不合格にする。**

  例: 「図が6割以上」は飾りの図を足せば通ってしまう → WARN。
      「数字を図なしで言わない」「図なしが25秒続かない」は
      量では通せず、置き方を直さないと通らない → 不合格。

レンダリング前に走ること:
  音声があればそこから秒を読み、無ければ字数から推定する。
  **2時間焼いてから落ちるのでは意味がない。**

使い方:
    python3 production/check_long.py                    # videos/L0* 全部
    python3 production/check_long.py videos/L001-...    # 1本だけ
"""
import importlib.util
import re
import sys
import wave
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parent
sys.path.insert(0, str(PRODUCTION))

FIGURE_KINDS = {"barsN", "compare2", "band", "curve", "timeline", "table", "checklist"}
NUM = re.compile(r"[0-9][0-9,\.]*\s*(?:円|%|歳|年|万円|万|割)")
HANTEI = re.compile(r"(得|損|差|払う|払わ|かかる|かから|引ける|引けない|安く|高く|戻る|減る)")
QUESTION = re.compile(r"(のか|のだろうか|だろうか|ますか|でしょうか)[。?？]?$")
ROADMAP = re.compile(r"([0-9０-９一二三四五六七八九]+\s*つの章|[0-9０-９]+\s*章で|"
                     r"これから[^。]*確かめ)")
MENSEKI = re.compile(r"(時点の(制度|内容|金利)|制度は.*変わる|確かめてほしい|"
                     r"以上|終わり|ありがとう|参考まで)")
NEXT = re.compile(r"(次の動画|別の動画|概要欄|この続き|もう1本|関連|"
                  r"[SL]0?\d{2,3}|ショート(で|も))")

# 長尺の1文字あたりの秒。ショートの 0.152 は SPEED_SCALE 1.3 のときの実測値で、
# 長尺は 1.15 に下げた(05-tempo.md)ので 1.3/1.15 倍する
SEC_PER_CHAR_LONG = 0.152 * (1.3 / 1.15)


def load(vdir: Path):
    rp = vdir / "render.py"
    spec = importlib.util.spec_from_file_location(f"g_{vdir.name}", rp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, rp.read_text()


def scene_kinds(src, scenes):
    out = {}
    for key in scenes:
        m = re.search(r'"' + re.escape(key) + r'":\s*s[cl]?\.?(\w+)', src)
        out[key] = m.group(1) if m else "?"
    return out


def durations(vdir: Path, units, scenes, out_name):
    """音声があれば実測、無ければ字数から推定する。

    **署名が一致しないときは実測を使わない。** 台本を作り直したあとに
    古い音声から秒を読むと、まったく別の台本の秒で判定してしまう
    (フェーズ12で実際に踏んだ。93ユニットの新台本を、157ユニットの旧音声で測っていた)。
    """
    import shortlib as S
    est = [len(re.sub(r"[。、【】]", "", u.tts_text())) * SEC_PER_CHAR_LONG + u.pad
           for u in units]
    wd = vdir / "output" / "work"
    sig_file = wd / "signature.txt"
    if not sig_file.exists():
        return est, "推定"
    want = S.render_signature(units, scenes, out_name=out_name)
    if sig_file.read_text().strip() != want:
        return est, "推定(音声は古い台本のもの)"
    out = []
    for i in range(len(units)):
        p = wd / f"seg_{i:02d}_pad.wav"
        if not p.exists():
            return est, "推定"
        with wave.open(str(p)) as w:
            out.append(w.getnframes() / w.getframerate())
    return out, "実測"


def check_video(vdir: Path):
    """(不合格リスト, 注意リスト, 見出し文字列) を返す。"""
    mod, src = load(vdir)
    if "use_landscape" not in src:
        return None, None, "横型ではない(このゲートは長尺専用)"
    units, kinds = mod.UNITS, scene_kinds(src, mod.SCENES)
    m = re.search(r'render_video\([^)]*?"([^"]+\.mp4)"', src, re.S)
    durs, how = durations(vdir, units, mod.SCENES, m.group(1) if m else "")
    starts, t = [], 0.0
    for d in durs:
        starts.append(t)
        t += d
    total = t
    bad, warn = [], []

    def fail(tag, cond, msg):
        if not cond:
            bad.append((tag, msg))

    def note(tag, cond, msg):
        if not cond:
            warn.append((tag, msg))

    is_fig = [kinds.get(u.scene) in FIGURE_KINDS for u in units]
    heads = [i for i, u in enumerate(units)
             if re.fullmatch(r"ch\d+", u.scene) and (i == 0 or units[i - 1].scene != u.scene)]
    blocks = [(0, "冒頭")] + [(i, units[i].scene) for i in heads]

    # ---- 冒頭(02-opening.md)
    num_at = next((starts[i] for i, u in enumerate(units) if NUM.search(u.subtitle)), 1e9)
    fig_at = next((starts[i] for i in range(len(units)) if is_fig[i]), 1e9)
    fail("冒頭の数値", num_at <= 15, f"最初の数値が {num_at:.1f}s(15秒以内に出す)")
    fail("冒頭の図", fig_at <= 20, f"最初の図が {fig_at:.1f}s(20秒以内に置く)")
    near60 = [starts[i] for i in heads if 45 <= starts[i] <= 75]
    fail("離脱の山の切れ目", not near60,
         f"45〜75秒に章の切れ目 {[f'{s:.1f}s' for s in near60]}(ずらす)")

    # ---- 構成(03-structure.md)
    fail("章の数", len(heads) <= 5, f"{len(heads)}章(9分なら4〜5)")
    for j, (i, name) in enumerate(blocks):
        e = blocks[j + 1][0] if j + 1 < len(blocks) else len(units)
        span = (starts[e] if e < len(units) else total) - starts[i]
        n_fig = sum(1 for k in range(i, e) if is_fig[k])
        if name != "冒頭":
            fail(f"{name}の尺", 60 <= span <= 150, f"{span:.1f}s(100〜130sが目安。60未満/150超は不合格)")
        note(f"{name}の図", n_fig / max(1, e - i) >= 0.40,
             f"図 {n_fig / max(1, e - i):.0%}(4割以上にする)")
    drop = re.compile(r"[。、では第0-9１-９章]")
    for i in heads:
        a = set(drop.sub("", units[i - 1].subtitle))
        b = set(drop.sub("", units[i].subtitle))
        ov = len(a & b) / max(1, len(b))
        fail(f"{units[i].scene}の継ぎ目", ov < 0.50,
             f"前章の出口と章札の重なり {ov:.0%}(章札は問いを繰り返さない)")

    # ---- リズム(04-rhythm.md)
    stops = [i for i, u in enumerate(units) if u.pad >= 0.5]
    fail("止め", len(stops) >= 3,
         f"pad≥0.5s が {len(stops)}箇所(章の出口の判定の直前に置く。3箇所以上)")

    # ---- 話速(05-tempo.md)
    chars = sum(len(re.sub(r"[。、【】]", "", u.tts_text())) for u in units)
    cpm = chars / total * 60
    fail("話速", 290 <= cpm <= 360, f"{cpm:.0f}字/分(標準300〜350。速めは400〜)")

    # ---- 画面(06-screen.md)
    num_i = [i for i, u in enumerate(units) if NUM.search(u.subtitle)]
    naked = [i for i in num_i if not is_fig[i]]
    if num_i:
        fail("数字が図の上にない", len(naked) / len(num_i) <= 0.10,
             f"{len(naked)}/{len(num_i)}本({len(naked) / len(num_i):.0%}) "
             f"{[f'#{i}' for i in naked[:6]]}")
    figless, cur = [], []
    for i in range(len(units)):
        if is_fig[i]:
            if cur:
                figless.append(cur)
            cur = []
        else:
            cur.append(i)
    if cur:
        figless.append(cur)
    worst = max((sum(durs[i] for i in r), r) for r in figless) if figless else (0, [])
    fail("図なしの連続", worst[0] <= 25,
         f"{worst[0]:.1f}秒(#{worst[1][0]}〜#{worst[1][-1]})が図なし(25秒以下にする)")
    note("図の割合", sum(is_fig) / len(units) >= 0.60,
         f"図 {sum(is_fig) / len(units):.0%}(6割以上。※飾りの図を足して通さない)")

    # ---- 進行感(07-progress.md)
    for j, (i, name) in enumerate(blocks):
        e = blocks[j + 1][0] if j + 1 < len(blocks) else len(units)
        tail = units[max(i, e - 2):e]
        ok = any((NUM.search(u.subtitle) or HANTEI.search(u.subtitle))
                 and not QUESTION.search(u.subtitle) for u in tail)
        fail(f"{name}の出口の判定", ok,
             f"#{e - 1}「{units[e - 1].subtitle}」が判定になっていない(問いは判定ではない)")
    road = next((starts[i] for i, u in enumerate(units) if ROADMAP.search(u.subtitle)), 1e9)
    fail("全体量の予告", road <= 60, f"「何章あるか」が {road:.1f}s(冒頭60秒までに言う)")

    # ---- 立ち絵(09-character.md)
    on_fig = sum(1 for i in range(len(units)) if is_fig[i] and units[i].chara != "none")
    if sum(is_fig):
        fail("図の上の立ち絵", on_fig / sum(is_fig) <= 0.50,
             f"{on_fig}/{sum(is_fig)}本({on_fig / sum(is_fig):.0%})に立ち絵。"
             f"図が主役の回は chara=\"none\"")
    faces = {}
    for u in units:
        faces[u.face] = faces.get(u.face, 0) + 1
    main, n_main = max(faces.items(), key=lambda kv: kv[1])
    note("表情の偏り", n_main / len(units) <= 0.80,
         f"{main} が {n_main}/{len(units)}({n_main / len(units):.0%})。判定で変える")

    # ---- 締め(10-ending.md)
    tail_i = [i for i in range(len(units)) if starts[i] >= total - 20]
    dis = [i for i in tail_i if MENSEKI.search(units[i].subtitle)]
    nxt = [i for i in tail_i if NEXT.search(units[i].subtitle)]
    fail("終了画面の枠", not dis,
         f"最後の20秒に免責・退出の言葉 {[f'#{i}' for i in dis]}(前に移して1文にする)")
    fail("次に見るものの名指し", bool(nxt),
         "最後の20秒に次の動画の名前が無い(名前と、見ると何が分かるかを言う)")

    head = (f"{total:.1f}秒({total / 60:.2f}分) / {len(units)}ユニット / "
            f"{cpm:.0f}字/分 / 章{len(heads)} / 尺は{how}")
    return bad, warn, head


def main():
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "videos").glob("L0*") if (p / "render.py").exists())
    if not targets:
        print("長尺の動画がありません")
        return
    total_bad = 0
    for vdir in targets:
        bad, warn, head = check_video(vdir)
        if bad is None:
            print(f"[SKIP] {vdir.name} — {head}")
            continue
        print(f"\n=== {vdir.name} — {head} ===")
        for tag, msg in warn:
            print(f"  [WARN] {tag} — {msg}")
        for tag, msg in bad:
            print(f"  [NG]   {tag} — {msg}")
        total_bad += len(bad)
        if not bad:
            print("  ALL PASS")
    print()
    if total_bad:
        print(f"結果: 不合格 {total_bad}件。WARNは落とさない")
        sys.exit(1)
    print("結果: ALL PASS")


if __name__ == "__main__":
    main()
