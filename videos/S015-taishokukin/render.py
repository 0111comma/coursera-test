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
    # 立ち絵(y0.245-0.465)を避け、結びの一文まで含めて y>0.48 に収める
    base, hmax = 0.525, 0.215
    h1 = hmax * a1
    h2 = hmax * (2_000 / 2_060) * a2
    fig.patches.append(Rectangle((0.16, base), 0.28, h1, transform=fig.transFigure,
                                 facecolor=GOLD, edgecolor="none"))
    fig.patches.append(Rectangle((0.56, base), 0.28, h2, transform=fig.transFigure,
                                 facecolor=MUTED_BAR, edgecolor="none"))
    fig.text(0.30, base + hmax + 0.028, "枠 2,060万", ha="center", color=INK, fontsize=30, alpha=a1,
             path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.5))
    fig.text(0.70, base + hmax * (2_000 / 2_060) + 0.028, "退職金 2,000万", ha="center",
             color=INK_2, fontsize=28, alpha=a2)
    if a2 >= 1:
        fig.text(0.5, 0.49, "枠の中 → 所得税0円", ha="center", color=EMPH, fontsize=32)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_zero": sc.hero("0円", "退職金2000万円にかかる所得税", BADGE, BRAND, size=128, sub_fs=30),
    "hero_zero__cover": sc.cover("その退職金、税金はいくら?", "税金0円", "そのカラクリは?",
                                 "勤続38年の例・国税庁", BRAND, main_size=118),
    "quiz": sc.quiz("クイズ", "2000万円もらって", "なぜ税金0円?", "(勤続38年の場合)", BADGE, BRAND),
    "kotae": sc.reveal("非課税の枠", "退職金には、税金のかからない枠", "名前は「退職所得控除」", BADGE, BRAND, size=92),
    "waku": scene_waku,
    "shikumi": sc.card("枠の育ち方", "20年までは年40万", "(21年目からは、年70万ずつ増える)", BADGE, BRAND,
                       main_size=50,
                     ask="あなたの勤続だと、枠はいくら?"),
    "koeru": sc.card("枠を超えても", "超えた分の半分に課税", "(2500万円なら、220万円にだけ税金)", BADGE, BRAND,
                     main_size=48),
    "ideco": sc.card("ただし注意", "iDeCoを近い時期に受け取ると", "(この枠が減ることがある。10年ルール)", BADGE, BRAND,
                     main_size=40),
    "jigyaku": sc.card("ここだけの話", "ボクはまだ勤続2年目", "(枠が育つのは、これからなのだ)", BADGE, BRAND,
                       main_size=46),
    "chips": sc.chips("この枠、知ってた?", ["知ってた", "初めて知った", "親に教える", "退職金がない"], BADGE, BRAND),
    "loop_back": sc.hero("0円", "退職金2000万円にかかる所得税", BADGE, BRAND, size=128, sub_fs=30),
}

# 全ビートを But/Therefore で繋ぐ(D10・ループ㊶)。check_flow.py で断絶0件を確認すること。
UNITS = [
    Unit("hero_zero", "【0円】。退職金2000万円にかかる税金。", anim=1.2, cover=True,
         se="pop", face="surprised", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("quiz", "2000万円もらって、なんで0円だと思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kotae", "答えは、退職金の【非課税の枠】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("waku", "その枠、勤続38年なら【2060万円】。", anim=1.6, speed=1.1, intonation=1.15),
    Unit("shikumi", "この枠は20年まで年40万、あとは年70万。",
         narration="この枠は20年まで毎年40万、あとは毎年70万。", anim=1.2, speed=1.15),
    Unit("koeru", "その枠を超えても、課税は超えた分の【半分】。", anim=1.2, se="don", speed=1.1,
         intonation=1.15),
    Unit("ideco", "ただしiDeCoを近くで受け取ると、枠が減る。",
         narration="ただしイデコを近くで受け取ると、枠が減る。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("jigyaku", "ちなみにボクは、まだ勤続2年目なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
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
