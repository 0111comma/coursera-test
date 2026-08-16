#!/usr/bin/env python3
"""S011: 金利が上がると、債券が下がる。企画書は plan.md、数値は verify.py と照合。

図の型(figure-forms.md):
- 「利息の比較」は棒2本。長さ=毎年もらえる利息。数字を大きく書くだけにしない
- 「値段の調整」も棒2本+差の帯。100万 → 91万、差9万が長さで見える
- 「満期まで持つ」は折れ線。横位置=時間、縦位置=値段。91万から100万へ戻る形

ユーザー指摘(S010)への対応: 図に出した金額は、必ず字幕でも言う。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, EMPH, GOLD,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "100万円・10年の債券の例"

# verify.py と同じ計算を再現して照合する(数値の二重確認)
FACE, CRATE, YEARS, YLD = 1_000_000, 0.01, 10, 0.02
PRICE = sum(FACE * CRATE / (1 + YLD) ** t for t in range(1, YEARS + 1)) + FACE / (1 + YLD) ** YEARS
assert round(PRICE) == 910_174, "verify.pyと不一致"
assert round(PRICE / 10_000) == 91 and round((FACE - PRICE) / 10_000) == 9

def kashi(n_rows=3):
    """固有シーン: 債券の経路図(figure-forms.md「物やお金が動く → 経路図」)。

    n_rows で矢印を1本ずつ足していく。初心者向けなので、
    「貸す → 利息 → 返ってくる」を1回の説明で全部見せない(ループ51)。
    意味を担うのは矢印の向き。右向き=貸したお金、左向き=戻ってくるお金。
    """
    ROWS = [(0.690, +1, "100万円を貸す", GOLD),
            (0.605, -1, "毎年1万円の利息", EMPH),
            (0.520, -1, "10年後に100万円", GOLD)]

    def painter(fig, t):
        from matplotlib.patches import FancyArrow
        fig.text(0.5, 0.905, "債券のしくみ", ha="center", color=INK_2, fontsize=34)
        for x, name in ((0.20, "あなた"), (0.80, "国や会社")):
            fig.text(x, 0.762, name, ha="center", va="center", color=INK, fontsize=32,
                     path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        for i, (y, direction, label, color) in enumerate(ROWS[:n_rows]):
            a = 1.0 if i < n_rows - 1 else sc.clamp01(t * 2.4)
            if a <= 0:
                continue
            x0, dx = (0.28, 0.44) if direction > 0 else (0.72, -0.44)
            fig.add_artist(FancyArrow(x0, y, dx * a, 0, width=0.006, head_width=0.026,
                                      head_length=0.022, transform=fig.transFigure,
                                      facecolor=color, edgecolor="none",
                                      length_includes_head=True, alpha=a))
            fig.text(0.50, y + 0.030, label, ha="center", va="center", color=color,
                     fontsize=27, alpha=a)
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("金利が上がって", "損した人がいる", BADGE, BRAND, size=88, sub_fs=44),
    "nazo__cover": sc.cover("金利が上がると、なぜ債券は下がる?", "債券", "利息は変わらないのに",
                            "はじめての人向け", BRAND, main_size=132),
    "namae": sc.card("持っていたのは", "債券", "(さいけん、と読む)",
                     BADGE, BRAND, main_size=68, head_fs=34),
    "teigi": kashi(1),
    "kasu": kashi(1),
    "risoku": kashi(2),
    "kaeru": kashi(3),
    "kinri": sc.card("ここで世の中の", "金利が上がった", "(お金を借りる側が払う分が増えた)",
                     BADGE, BRAND, main_size=54, head_fs=34),
    "shin": sc.bars2("同じ100万円で、もらえる利息",
                     ("前からある債券", 1, "毎年1万円"),
                     ("新しく出た債券", 2, "毎年2万円"),
                     BADGE, BRAND, gap="差 1万円"),
    "toi": sc.quiz("では、どうなるか", "毎年1万円のほう", "100万円で買う?", "", BADGE, BRAND),
    "sageru": sc.card("利息は途中で増やせない", "値段を下げる", "(そうしないと、誰も買わない)",
                      BADGE, BRAND, main_size=58, head_fs=34,
                      ask="あなたの投信にも入ってる?"),
    "nedan": sc.bars2("その債券に、いま付く値段",
                      ("金利が上がる前", 100, "100万円"),
                      ("上がった後", 91, "91万円"),
                      BADGE, BRAND, gap="差 9万円", ymax=105),
    "son": sc.card("いま売ると", "9万円の損", "(持っている人の評価額が減る)",
                   BADGE, BRAND, main_size=62, head_fs=34),
    "manki": sc.lines2("最後まで持った場合",
                       [("持ち続ける", [100, 91, 94, 97, 100], INK)],
                       BADGE, BRAND, ymin=88, ymax=102,
                       xlabels=["買った日", "", "", "", "返る日"]),
    "dare": sc.card("だから損になるのは", "途中で売った人だけ", "(発行体が破綻しない場合)",
                    BADGE, BRAND, main_size=48, head_fs=34),
    "shime": sc.hero("金利が上がると", "債券は下がる。もう分かるのだ", BADGE, BRAND,
                     size=84, sub_fs=34),
}

# ネタ選定ゲート(F1): 予想「金利が上がったら、もらえる利息が増えるだけでは?」
#   → 結論「利息は固定なので、値段のほうが下がって帳尻を合わせる」
# ループ51(端折り禁止): 1文につき新しい数字は1つまで。専門用語は使う前に言い換える。
UNITS = [
    Unit("nazo", "金利が上がって、損した人がいるのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("namae", "その人が持っていたのは、【債券】。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("teigi", "債券とは、お金を貸すことなのだ。", anim=1.4, speed=1.15),
    Unit("kasu", "その債券を、国に100万円ぶん買うのだ。", anim=1.4, speed=1.15),
    Unit("risoku", "すると毎年、1万円の利息がもらえる。", anim=1.4, face="happy",
         speed=1.15),
    Unit("kaeru", "そして10年たつと、お金は返ってくる。", anim=1.4, speed=1.15),
    Unit("kinri", "その後、世の中の金利が上がった。", anim=1.2, speed=1.15),
    Unit("shin", "すると新しい債券は、毎年2万円になる。", anim=1.4, speed=1.15),
    Unit("toi", "では毎年1万円のほう、誰が買うのだ?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("sageru", "だから値段を下げないと、買い手がつかない。", anim=1.2, speed=1.15),
    Unit("nedan", "その値段が、【91万円】まで下がるのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34, speed=1.1, intonation=1.2, pitch=-0.05),
    Unit("son", "つまり今売ると、9万円の損になる。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("manki", "でも返す日まで持てば、100万円は戻る。", anim=1.6, face="happy",
         speed=1.1, intonation=1.2),
    Unit("dare", "損になるのは、途中で売った人だけなのだ。", anim=1.2, speed=1.15),
    Unit("shime", "ニュースの金利上昇が、これで分かる。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S011.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
