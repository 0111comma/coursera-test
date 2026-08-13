#!/usr/bin/env python3
"""S012: 10万円のリボ払い、本当の値段(T6ビフォーアフター型)。数値はverify.pyとassert照合。"""
import sys
from pathlib import Path

from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "年率15%・月5千円・元利定額の試算"


def simulate(principal, annual_rate, monthly_pay):
    balance, months, total_interest, balances = principal, 0, 0, []
    while balance > 0:
        months += 1
        interest = round(balance * annual_rate / 12)
        total_interest += interest
        pay = min(monthly_pay, balance + interest)
        balance = balance + interest - pay
        balances.append(balance)
    return months, total_interest, balances


MONTHS, FEE, BALANCES = simulate(100_000, 0.15, 5_000)
assert (MONTHS, FEE) == (24, 15_794), "verify.pyと不一致"
assert 100_000 + FEE == 115_794 and BALANCES[11] == 51_774, "verify.pyと不一致"
M2, FEE2, _ = simulate(200_000, 0.15, 5_000)
assert (M2, FEE2) == (56, 78_997), "verify.pyと不一致"


def scene_zandaka(fig, t):
    """固有シーン: 残高の推移バー(24ヶ月)。1年後でも半分強残ることを見せる。"""
    fig.text(0.5, 0.90, "残高はこう減る(月5千円)", ha="center", color=INK_2, fontsize=32)
    x0, x1, y0, hmax = 0.12, 0.88, 0.42, 0.34
    w = (x1 - x0) / 24
    n_show = int(sc.clamp01(t * 1.6) * 24 + 0.999)
    for i in range(min(n_show, 24)):
        h = hmax * (BALANCES[i] / 100_000)
        color = GOLD if i == 11 else MUTED_BAR
        fig.patches.append(Rectangle((x0 + i * w, y0), w * 0.72, max(h, 0.004),
                                     transform=fig.transFigure, facecolor=color,
                                     edgecolor="none"))
    if n_show >= 12:
        fig.text(x0 + 11.5 * w, y0 + hmax * 0.62, "1年後\nまだ5.2万円", ha="center",
                 color=INK, fontsize=26,
                 path_effects=stroke_fx(INK, outline=outline_for(26), fatten=1.5))
    fig.text(x0, y0 - 0.045, "1ヶ月目", ha="left", color=INK_2, fontsize=22)
    fig.text(x1, y0 - 0.045, "24ヶ月目", ha="right", color=INK_2, fontsize=22)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(115_794, "{:,}円", BADGE, BRAND, size=96),
    "hero_count__cover": sc.cover("10万円の買い物", "11万5794円", "リボ払いの本当の値段",
                                  "年率15%・月5千円の試算", BRAND, main_size=96),
    "hero_full": sc.hero("11万5794円", "10万円をリボ払いした場合の総額(試算)", BADGE, BRAND,
                         size=92, sub_fs=29),
    "joken": sc.card("10万円の買い物を", "月5千円のリボ払い", "(年率15%・元利定額で試算)", BADGE, BRAND,
                     main_size=50),
    "quiz": sc.quiz("クイズ", "払い終わるまで", "何ヶ月かかる?", "(月5千円ずつ)", BADGE, BRAND),
    "kotae": sc.reveal("2年(24ヶ月)", "手数料は15,794円", "10万円+15,794円=115,794円", BADGE, BRAND, size=88),
    "zandaka": scene_zandaka,
    "shikumi": sc.card("手数料の仕組み", "残高に年率15%", "(毎月、残高×1.25%が上乗せ)", BADGE, BRAND,
                       main_size=52),
    "ikkatsu": sc.card("ちなみに", "一括払いなら0円", "(手数料は「分けた期間」の値段)", BADGE, BRAND,
                       main_size=54),
    "niju": sc.card("20万円に増えると", "手数料 約7.9万円", "(78,997円・完済まで4年8ヶ月)", BADGE, BRAND,
                    main_size=50),
    "akiru": sc.card("ここだけの話", "2年後には飽きてそう", "(支払いだけ残るのだ)", BADGE, BRAND,
                     main_size=48),
    "hayami": sc.hayami("リボの値段は、雪だるま式", [
        ("10万円の手数料", "+15,794円"),
        ("20万円の手数料", "+78,997円"),
        ("完済まで", "2年 / 4年8ヶ月"),
        ("1年後の残高", "51,774円"),
        ("一括払いなら", "0円"),
    ], "年率15%・月5千円・元利定額の試算(2026年8月)", BADGE, BRAND, focal=0),
    "chips": sc.chips("リボ、使ったことある?", ["使ってる", "昔使ってた", "使わない", "こわくなった"], BADGE, BRAND),
    "loop_back": sc.hero("11万5794円", "10万円をリボ払いした場合の総額(試算)", BADGE, BRAND,
                         size=92, sub_fs=29),
}

UNITS = [
    Unit("hero_count", "【11万5794円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "10万円の買い物の、本当の値段。", anim=0.8, speed=1.2),
    Unit("joken", "リボ払い、月5千円コースの場合なのだ。", anim=1.2, speed=1.15),
    Unit("quiz", "では、何ヶ月かかると思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "答えは【2年】。手数料、約1万6千円。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("zandaka", "1年払っても、まだ半分残ってるのだ。", anim=1.6, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("shikumi", "利息は年率15%。残高に、毎月かかるのだ。", anim=1.2, speed=1.15),
    Unit("ikkatsu", "ちなみに一括なら、手数料【0円】なのだ。", anim=1.2, speed=1.15),
    Unit("niju", "20万円に増えると、約7万9千円なのだ。", anim=1.2, se="don", speed=1.1,
         face="surprised", intonation=1.15),
    Unit("akiru", "買った物、2年後には飽きてそうなのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("hayami", "金額べつの値段は、【早見表】なのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "あなたはリボ、使ったことある?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして本当の値段が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S012.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
