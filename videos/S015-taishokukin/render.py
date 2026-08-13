#!/usr/bin/env python3
"""S015: 退職金2000万円でも税金0円(T1クイズ型)。数値はverify.pyとassert照合。"""
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
BADGE = "勤続38年の例・2026年8月時点の制度"


def kojo(years):
    if years <= 20:
        return max(80, 40 * years)
    return 800 + 70 * (years - 20)


assert kojo(20) == 800 and kojo(30) == 1_500 and kojo(38) == 2_060, "verify.pyと不一致"
assert max(0, 2_000 - kojo(38)) // 2 == 0, "verify.pyと不一致"
assert max(0, 2_500 - kojo(38)) // 2 == 220, "verify.pyと不一致"


def scene_waku(fig, t):
    """固有シーン: 非課税枠2,060万 vs 退職金2,000万の棒比較。"""
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.90, "非課税の枠 と 退職金", ha="center", color=INK_2, fontsize=34)
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.5)
    hmax = 0.30
    h1 = hmax * a1
    h2 = hmax * (2_000 / 2_060) * a2
    fig.patches.append(Rectangle((0.16, 0.40), 0.28, h1, transform=fig.transFigure,
                                 facecolor=GOLD, edgecolor="none"))
    fig.patches.append(Rectangle((0.56, 0.40), 0.28, h2, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.30, 0.40 + hmax + 0.03, "枠 2,060万", ha="center", color=INK, fontsize=30, alpha=a1,
             path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.5))
    fig.text(0.70, 0.40 + hmax * (2_000 / 2_060) + 0.03, "退職金 2,000万", ha="center",
             color=INK_2, fontsize=28, alpha=a2)
    if a2 >= 1:
        fig.text(0.5, 0.335, "枠の中 → 所得税0円", ha="center", color=EMPH, fontsize=32)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_zero": sc.hero("0円", "退職金2000万円にかかる所得税", BADGE, BRAND, size=128, sub_fs=30),
    "hero_zero__cover": sc.cover("退職金2000万円", "税金0円", "そのカラクリは?",
                                 "勤続38年の例・国税庁", BRAND, main_size=118),
    "quiz": sc.quiz("クイズ", "2000万円もらって", "なぜ税金0円?", "(勤続38年の場合)", BADGE, BRAND),
    "kotae": sc.reveal("非課税の枠", "勤続38年なら2,060万円まで", "名前は「退職所得控除」", BADGE, BRAND, size=92),
    "waku": scene_waku,
    "shikumi": sc.card("枠の育ち方", "年40万 → 年70万", "(20年までは40万/年、超えたら70万/年)", BADGE, BRAND,
                       main_size=50),
    "koeru": sc.card("枠を超えても", "超えた分の半分だけ", "(2500万なら220万にだけ課税)", BADGE, BRAND,
                     main_size=48),
    "ideco": sc.card("ただし注意", "iDeCoと近い受け取り", "(10年ルールで枠が減ることあり)", BADGE, BRAND,
                     main_size=48),
    "jigyaku": sc.card("ここだけの話", "ボクはまだ勤続2年目", "(枠が育つのは、これからなのだ)", BADGE, BRAND,
                       main_size=46),
    "hayami": sc.hayami("非課税の枠(退職所得控除)", [
        ("勤続20年", "800万円"),
        ("勤続30年", "1,500万円"),
        ("勤続38年", "2,060万円"),
    ], "枠を超えた分も1/2にだけ課税", BADGE, BRAND, focal=2),
    "chips": sc.chips("この枠、知ってた?", ["知ってた", "初めて知った", "親に教える", "退職金がない"], BADGE, BRAND),
    "loop_back": sc.hero("0円", "退職金2000万円にかかる所得税", BADGE, BRAND, size=128, sub_fs=30),
}

UNITS = [
    Unit("hero_zero", "【0円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_zero", "退職金2000万円に、かかる所得税。", anim=0.0, speed=1.2),
    Unit("quiz", "2000万円もらって、なんで0円だと思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "退職金には、【非課税の枠】があるのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("waku", "勤続38年なら、枠は【2060万円】なのだ。", anim=1.6, speed=1.1, intonation=1.15),
    Unit("shikumi", "勤続20年まで年40万、そのあと年70万育つ。",
         narration="勤続20年まで毎年40万、そのあと毎年70万育つ。", anim=1.2, speed=1.15),
    Unit("koeru", "枠を超えても、超えた分の【半分】だけ課税。", anim=1.2, se="don", speed=1.1,
         intonation=1.15),
    Unit("ideco", "ただしiDeCoと近い受け取りは、注意なのだ。",
         narration="ただしイデコと近い受け取りは、注意なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("jigyaku", "ちなみにボクは、まだ勤続2年目なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("hayami", "勤続年数べつの枠は、【早見表】なのだ。", anim=0.8, se="pop", speed=1.2),
    Unit("chips", "あなたはこの枠、知ってた?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして2000万円の税金が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S015.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
