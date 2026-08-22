#!/usr/bin/env python3
"""figure2.md の測定を再現するスクリプト(A5 第2ラウンド)。

    python3 docs/research/elements/figure2_measure.py

出すもの:
  1. 7型を t=1.0 で描いたときの、全テキストの「実際に描かれた pt」「実測bbox」「実alpha」
  2. 要素数を増やしたときの破綻点(棒の重なり・箱からのはみ出し・字幕帯への侵入)
  3. L001 / L002 の全シーンに当てた3判定(意図しない薄さ / 箱はみ出し / 注記が字幕帯)
"""
import importlib.util
import itertools
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "production"))
warnings.filterwarnings("ignore")

import matplotlib                                    # noqa: E402
matplotlib.use("Agg")
import shortlib as S                                 # noqa: E402
S.use_landscape()
S.setup_fonts()
import scenes_long as sl                             # noqa: E402

W, H = 1920, 1080
BAND_TOP = (S.SUBTITLE_Y + S.SUB_LINE_H * 0.80) * H   # 字幕帯の上端 = 222px
BADGE_A, BRAND_A = (0.972, 0.940), (0.5, 0.036)


def _chrome(a):
    x, y = a.get_position()
    return ((abs(x - BADGE_A[0]) < 1e-6 and abs(y - BADGE_A[1]) < 1e-6)
            or (abs(x - BRAND_A[0]) < 1e-6 and abs(y - BRAND_A[1]) < 1e-6))


def probe(painter, t=1.0):
    """painter を描いて、テキストの実測値と図形の bbox を返す。"""
    fig = S.new_canvas()
    painter(fig, t)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts, boxes = [], []
    for a in fig.texts:
        s = a.get_text().replace("\n", "")
        if not s.strip() or _chrome(a):
            continue
        bb = a.get_window_extent(renderer=r)
        texts.append(dict(text=s, pt=round(float(a.get_fontsize()), 2),
                          alpha=a.get_alpha(), x0=bb.x0, y0=bb.y0,
                          w=bb.width, h=bb.height, color=str(a.get_color())))
    for p in fig.patches:
        try:
            bb = p.get_window_extent()
            boxes.append((bb.x0, bb.y0, bb.width, bb.height))
        except Exception:
            pass
    S.plt.close(fig)
    return texts, boxes


def judge(texts, boxes):
    """figure2.md で提案している3判定。checklist の意図的な減光は呼び出し側で除く。"""
    out = []
    for t in texts:
        if t["alpha"] is not None and t["alpha"] < 0.98:
            out.append(("薄い", f"「{t['text'][:14]}」alpha={t['alpha']:.2f}"))
        if t["y0"] < BAND_TOP:
            out.append(("注記が字幕帯", f"「{t['text'][:16]}」下端{t['y0']:.0f}px < {BAND_TOP:.0f}px"))
        for bx, by, bw, bh in boxes:
            cx, cy = t["x0"] + t["w"] / 2, t["y0"] + t["h"] / 2
            if bx < cx < bx + bw and by < cy < by + bh and t["w"] > bw + 2 and bw > 50:
                out.append(("箱はみ出し", f"「{t['text']}」{t['w']:.0f}px > 箱{bw:.0f}px"))
    for a, b in itertools.combinations(texts, 2):
        ox = min(a["x0"] + a["w"], b["x0"] + b["w"]) - max(a["x0"], b["x0"])
        oy = min(a["y0"] + a["h"], b["y0"] + b["h"]) - max(a["y0"], b["y0"])
        if ox > 2 and oy > 2:
            out.append(("重なり", f"「{a['text'][:10]}」×「{b['text'][:10]}」{ox:.0f}x{oy:.0f}px"))
    return out


def main():
    print("=== 1. 7型の実測(t=1.0)===")
    B, BR = "2026年8月時点", "数字で見るお金の教科書"
    G, M = S.GOLD, S.MUTED_BAR
    cases = {
        "F-hero": sl.hero("株で20万円の損", "※ 仮定の例です", B, BR),
        "F-card": sl.card("利益にかかる税率", "20.315%", "※ 申告分離課税", B, BR),
        "F-compare2": sl.compare2("見出し", ("左", [("益20万", 20, G), ("損20万", 20, M)], "税 0円"),
                                  ("右", [("益20万", 20, G), ("損20万", 20, M)], "税 40,630円"),
                                  B, BR, note_l="※ 相殺できる", note_r="※ できない"),
        "F-barsN": sl.barsN("見出し", [("所得税", 15, "15%"), ("住民税", 5, "5%"),
                                     ("復興特別所得税", 0.315, "0.315%")], B, BR, ymax=17),
        "F-band": sl.band("見出し", "利益 20万円", 0.79685, "手元 15万9370円",
                          "税 40,630円", B, BR, show_rest=True),
        "F-timeline": sl.timeline("見出し", [(f"{i+1}年目", "利益 10万円", "引ける", i == 4)
                                           for i in range(5)], B, BR, note="※ 注記"),
        "F-table": sl.table("見出し", ["その年", "課税口座", "NISA", "差"],
                            [("利益だけ", "税あり", "税0円", "0円"),
                             ("損だけ", "繰越可", "消える", "0円"),
                             ("両方", "相殺できる", "できない", "40,630円")], B, BR, highlight=2),
    }
    for name, p in cases.items():
        ts, _ = probe(p)
        print(f"-- {name}")
        for t in ts:
            al = "" if t["alpha"] is None else f" alpha={t['alpha']:.2f}"
            print(f"   {t['pt']:>6}pt 幅{t['w']:>6.0f}px 高{t['h']:>5.1f}px "
                  f"字幕比{t['pt']/S.SUB_FS:4.2f} {t['color']:<9}{al} {t['text'][:22]}")

    print("\n=== 2. 要素数を増やしたときの破綻点 ===")
    for n in range(2, 9):
        ts, bx = probe(sl.timeline("見出し", [(f"{i+1}年目", "利益 10万円", "引ける", False)
                                            for i in range(n)], B, BR))
        k = [x for x in judge(ts, bx) if x[0] != "注記が字幕帯"]
        print(f" timeline n={n}: {len(k)}件 {k[:2]}")
    for n in range(2, 11):
        ts, bx = probe(sl.barsN("見出し", [(f"項目{i+1}の名前", 10 + i, f"{40630+i:,}円")
                                         for i in range(n)], B, BR))
        print(f" barsN N={n}: {len(judge(ts, bx))}件")
    for m in range(1, 6):
        it = [(f"益{20+i}万", 20 + i, G) for i in range(m)]
        ts, bx = probe(sl.compare2("見出し", ("左", it, "計"), ("右", it, "計"), B, BR))
        print(f" compare2 m={m}: {len([x for x in judge(ts,bx) if x[0]!='注記が字幕帯'])}件")
    for r in (3, 5, 6, 7, 8):
        ts, bx = probe(sl.table("見出し", ["年", "額"],
                                [(f"{i+1}行目", "40,630円") for i in range(r)], B, BR))
        print(f" table rows={r}: {len(judge(ts, bx))}件")

    print("\n=== 3. L001 / L002 の全シーンに当てる ===")
    for vid in ("L001-nisa-son", "L002-kinri-wakaremichi"):
        rp = ROOT / "videos" / vid / "render.py"
        if not rp.exists():
            continue
        spec = importlib.util.spec_from_file_location("v_" + vid, rp)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        used = {}
        for u in mod.UNITS:
            used[u.scene] = used.get(u.scene, 0) + 1
        tot = {}
        for key, p in mod.SCENES.items():
            if key.endswith("__cover"):
                continue        # カバーは立ち絵が無く全幅を使う。判定から外す
            if {"items", "lit"} <= set(p.__code__.co_freevars):
                continue        # checklist の減光は意図的
            for kind, detail in judge(*probe(p)):
                tot[kind] = tot.get(kind, 0) + 1
                print(f"  [{kind}] {vid[:4]} {key}(x{used.get(key,0)}): {detail}")
        print(f"  → {vid}: {tot}")

    print("\n=== 4. 要素が『薄い』のではなく『描かれない』点(反証側の追加測定)===")
    #   stagger が大きいと clamp01 が 0 になり、`if a <= 0: continue` で
    #   その要素はフレームに1度も現れない。薄さより先にこちらが効く。
    def n_drawn(painter, suffix):
        ts, _ = probe(painter)
        return len([t for t in ts if t["text"].endswith(suffix)])
    for n in range(4, 9):
        got = n_drawn(sl.timeline("見出し", [(f"{i+1}年目", "利益", "引ける", False)
                                           for i in range(n)], B, BR), "年目")
        print(f" timeline n={n}: 描かれた箱 {got}/{n}" + ("  ← 消えている" if got < n else ""))
    for r in range(6, 10):
        got = n_drawn(sl.table("見出し", ["年", "額"],
                               [(f"{i+1}行目", "40,630円") for i in range(r)], B, BR), "行目")
        print(f" table rows={r}: 描かれた行 {got}/{r}" + ("  ← 消えている" if got < r else ""))
    for n in (9, 10, 11):
        got = n_drawn(sl.barsN("見出し", [(f"項{i+1}", 10 + i, f"{i}%") for i in range(n)],
                               B, BR), "%")
        print(f" barsN N={n}: 描かれた値ラベル {got}/{n}" + ("  ← 消えている" if got < n else ""))


if __name__ == "__main__":
    main()
