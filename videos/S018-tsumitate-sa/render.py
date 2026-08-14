#!/usr/bin/env python3
"""S018: 積立、25歳と35歳でいくら差がつく?(T3比較型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "月1万円・65歳まで・年5%は仮定"

R = 0.05 / 12


def fv_series(months):
    bal, xs = 0.0, []
    for _ in range(months):
        bal = bal * (1 + R) + 10_000
        xs.append(bal)
    return xs


SER_25 = fv_series(480)
SER_35 = fv_series(360)
assert round(SER_25[-1] / 10_000) == 1_526, "verify.pyと不一致"
assert round(SER_35[-1] / 10_000) == 832, "verify.pyと不一致"
assert round(fv_series(240)[-1] / 10_000) == 411, "verify.pyと不一致"


def scene_curve(fig, t):
    """固有シーン: 25歳/35歳スタートの成長曲線(65歳時点まで)。"""
    a = sc.clamp01(t * 1.4)
    ax = fig.add_axes([0.12, 0.505, 0.76, 0.305])   # 立ち絵(y0.245-0.465)を避ける
    ax.set_facecolor("none")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(MUTED)
    n = max(2, int(480 * a))
    xs25 = [25 + i / 12 for i in range(len(SER_25))][:n]
    ax.plot(xs25, [v / 10_000 for v in SER_25[:n]], color=GOLD, lw=5)
    n35 = max(0, min(len(SER_35), n - 120))
    if n35 > 1:
        xs35 = [35 + i / 12 for i in range(len(SER_35))][:n35]
        ax.plot(xs35, [v / 10_000 for v in SER_35[:n35]], color=MUTED_BAR, lw=5)
    ax.set_xlim(25, 66)
    ax.set_ylim(0, 1650)
    ax.tick_params(colors=INK_2, labelsize=17)
    ax.set_xticks([25, 35, 45, 55, 65])
    ax.set_xticklabels(["25歳", "35歳", "45歳", "55歳", "65歳"])
    ax.set_yticks([500, 1000, 1500])
    ax.set_yticklabels(["500万", "1000万", "1500万"])
    ax.grid(axis="y", color=MUTED, alpha=0.35, lw=1)
    fig.text(0.5, 0.885, "同じ月1万円でも(年5%仮定)", ha="center", color=INK_2, fontsize=32)
    if a >= 1:
        fig.text(0.74, 0.775, "25歳〜 1,526万", ha="center", color=INK, fontsize=27,
                 path_effects=stroke_fx(INK, outline=outline_for(27), fatten=1.5))
        fig.text(0.80, 0.625, "35歳〜 832万", ha="center", color=INK_2, fontsize=25)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(694, "{:,}万円", BADGE, BRAND, size=118,
                                lead="その10年、いくらの差になる?"),
    "hero_count__cover": sc.cover("その10年、いくらの差になる?", "差694万円", "払った差は120万だけ",
                                  "月1万・65歳まで・年5%仮定", BRAND, main_size=104),
    "hero_full": sc.hero("約694万円", "始める年齢が10年ちがうと生まれる差", BADGE, BRAND,
                         size=104, sub_fs=28),
    "joken": sc.card("条件", "月1万円を65歳まで", "(増え方は年5%と仮定した場合)", BADGE, BRAND,
                     main_size=52),
    "b25": sc.card("25歳スタート", "約1,526万円", "(自分で払うのは480万円)", BADGE, BRAND,
                   main_size=56),
    "b35": sc.card("35歳スタート", "約832万円", "(自分で払うのは360万円)", BADGE, BRAND,
                   main_size=56),
    "gyaku": sc.reveal("自分で払った差は120万", "なのに65歳での差は約694万円", "(月1万円 × 10年 = 120万円)", BADGE, BRAND,
                       size=74),
    "curve": scene_curve,
    "riyu": sc.card("理由", "早い10年が一番長く増える", "(先に入れたお金ほど、増える期間が長い)", BADGE, BRAND,
                    main_size=42,
                     ask="あなたは、何歳スタート?"),
    "kasetsu": sc.card("大事な注意", "年5%は仮定", "(保証はなく、元本割れの年もある)", BADGE, BRAND,
                       main_size=56),
    "jigyaku": sc.card("ここだけの話", "10年前のボクに教えたい", "(過去には戻れないのだ)", BADGE, BRAND,
                       main_size=44),
    "chips": sc.chips("あなたは何歳スタート?", ["20代で開始", "30代で開始", "40代以降", "これから"], BADGE, BRAND),
    "loop_back": sc.hero("約694万円", "始める年齢が10年ちがうと生まれる差", BADGE, BRAND,
                         size=104, sub_fs=28),
}

UNITS = [
    Unit("hero_count", "【694万円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "始めるのが10年おそいと、これだけ減るのだ。", anim=0.8, speed=1.2),
    Unit("joken", "月1万円を、65歳まで積み立てる場合。", anim=1.2, speed=1.15),
    Unit("b25", "25歳スタートは、約【1526万円】。", anim=1.2, speed=1.1, intonation=1.15),
    Unit("b35", "35歳スタートは、約【832万円】なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("gyaku", "でも自分で多く払った額は、【120万】だけ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("curve", "増え方のカーブが、これなのだ。", anim=1.8, speed=1.2),
    Unit("riyu", "早い10年分が、いちばん長く増えるのだ。", anim=1.2, speed=1.15),
    Unit("kasetsu", "ただし年5%は【仮定】。保証はないのだ。",
         narration="ただし年率5%は仮定。保証はないのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15),
    Unit("jigyaku", "10年前のボクに、教えたいのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("chips", "あなたは、何歳スタート?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして10年の値段が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S018.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
