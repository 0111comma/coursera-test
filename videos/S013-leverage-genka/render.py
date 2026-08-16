#!/usr/bin/env python3
"""S013: 2倍の商品は、元の水準に戻っても減っている。数値は verify.py と照合。

図の型(figure-forms.md):
- 主役は「指数は戻ったのに、2倍型は戻らない」という2本の線の離れ方。
  → 同じ軸に2本の折れ線(lines2)。横位置=日、縦位置=水準。右端に直接ラベル
- 各日の値動きは棒2本(-10% と -20%)。長さで倍率が見える
- 最後の差は棒2本 + 差の帯

図に出した数字は必ず字幕でも言う(S010でのユーザー指摘)。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "100から始めた場合の例"

# verify.py と同じ計算(2日分。1日目 -10%、2日目は指数がちょうど100に戻る上げ幅)
DAY2 = 100 / 90 - 1
IDX = [100.0, 90.0, 100.0]
LEV = [100.0, 100 * (1 - 0.20), 100 * 0.80 * (1 + DAY2 * 2)]
assert round(DAY2 * 100, 1) == 11.1 and round(LEV[-1], 1) == 97.8, "verify.pyと不一致"


def scene_maiban(fig, t):
    """固有シーン: 「毎日リセットされる」を位置で見せる。

    2倍型が約束しているのは1日ぶんの値動きだけ。翌日はまた新しい残高から2倍になる。
    横位置=日、箱の高さ=その日の始まりの残高。減った残高から2倍しても戻らない。
    """
    from matplotlib.patches import Rectangle
    fig.text(0.5, 0.905, "2倍が約束しているのは、1日ぶん", ha="center",
             color=INK_2, fontsize=34)
    days = [("1日目のはじめ", 100, MUTED_BAR), ("2日目のはじめ", 80, EMPH)]
    for i, (name, val, color) in enumerate(days):
        a = sc.clamp01(t * 2.4 - i * 0.8)
        if a <= 0:
            continue
        x = 0.30 + i * 0.36
        h = 0.20 * (val / 100) * a
        fig.patches.append(Rectangle((x - 0.13, 0.560), 0.26, h, transform=fig.transFigure,
                                     facecolor=color, edgecolor="none", alpha=0.95))
        fig.text(x, 0.560 + h + 0.030, f"{val:.0f}", ha="center", va="center", color=INK,
                 fontsize=36, alpha=a,
                 path_effects=stroke_fx(INK, outline=outline_for(36), fatten=2))
        fig.text(x, 0.525, name, ha="center", va="center", color=INK_2, fontsize=26, alpha=a)
    fig.add_artist(__import__("matplotlib.pyplot", fromlist=["x"]).Line2D(
        [0.10, 0.90], [0.560, 0.560], transform=fig.transFigure,
        color=MUTED, linewidth=1.5, alpha=0.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "nazo": sc.hero("元に戻ったのに", "減っている", BADGE, BRAND, size=88, sub_fs=46),
    "nazo__cover": sc.cover("元に戻ったのに、なぜ減る?", "2倍の商品",
                            "毎日リセットされるから", "はじめての人向け", BRAND, main_size=118),
    "shisu": sc.card("まず言葉の説明", "株全体の平均", "(日経平均やS&P500のこと)", BADGE, BRAND,
                     main_size=58, head_fs=34),
    "shohin": sc.card("こういう商品がある", "平均の2倍だけ動く",
                      "(レバレッジ型と呼ばれる)", BADGE, BRAND,
                      main_size=52, head_fs=34),
    "kau": sc.card("買ってみる", "100だけ買う", "(単位は円でも万円でも同じ)",
                   BADGE, BRAND, main_size=56, head_fs=34),
    "yakusoku": sc.card("ただし約束は", "その日1日ぶんだけ", "(毎日、はかり直す)",
                        BADGE, BRAND, main_size=52, head_fs=34),
    "nijuu": sc.bars2("1日目の値動き",
                      ("平均", 10, "10%下がる"),
                      ("2倍の商品", 20, "20%下がる"),
                      BADGE, BRAND),
    "day1": sc.bars2("1日目の値動き",
                     ("平均", 10, "10%下がる"),
                     ("2倍の商品", 20, "20%下がる"),
                     BADGE, BRAND),
    "nokori": scene_maiban,
    "day2": sc.card("2日目に平均は元へ", "戻るには何%必要?", "(90から100に戻す上げ幅)",
                    BADGE, BRAND, main_size=46, head_fs=34,
                    ask="あなたなら、何日持つ?"),
    "juuichi": sc.card("答えは", "11.1%上がる", "(90 × 1.111 = 100)",
                       BADGE, BRAND, main_size=58, head_fs=34),
    "kekka": sc.lines2("2日たった後の水準",
                       [("平均", IDX, INK), ("2倍の商品", LEV, EMPH)],
                       BADGE, BRAND, ymin=78, ymax=102,
                       xlabels=["はじめ", "1日目", "2日目"]),
    "sa": sc.bars2("2日目が終わった時点",
                   ("平均", 100, "100"),
                   ("2倍の商品", 97.8, "97.8"),
                   BADGE, BRAND, gap="差 2.2", ymax=105),
    "riyu": scene_maiban,
    "muki": sc.card("順番を変えても", "やはり元には戻らない", "(先に上げても、98.2)",
                    BADGE, BRAND, main_size=46, head_fs=32),
    "joken": sc.card("逆の場合", "大きく増える", "(目減りするのは、上下する時)",
                     BADGE, BRAND, main_size=48, head_fs=34),
    "shime": sc.hero("上下をくり返すほど", "2倍の商品は目減りするのだ", BADGE, BRAND,
                     size=74, sub_fs=34),
}

# ネタ選定ゲート(F1): 予想「2倍の商品なら、指数が戻れば自分も戻るのでは?」
#   → 結論「毎日リセットされるので、上下をくり返すと元の水準に戻らない」
# ループ51(端折り禁止): 1文につき新しい数字は1つまで。専門用語は使う前に言い換える。
UNITS = [
    Unit("nazo", "元の値段に戻ったのに、減っている商品。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("shisu", "まず【指数】とは、株全体の平均のこと。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("shohin", "その平均の2倍だけ動く商品があるのだ。", anim=1.4, speed=1.15),
    Unit("kau", "その商品を、100だけ買ったとする。", anim=1.4, speed=1.15),
    Unit("yakusoku", "ただし約束は、その日1日ぶんだけ。", anim=1.4, speed=1.15),
    Unit("day1", "たとえば平均が10%下がったとする。", anim=1.4, speed=1.15),
    Unit("nijuu", "その商品は2倍なので、20%下がるのだ。", anim=1.4, speed=1.15),
    Unit("nokori", "つまり手元は、80まで減るのだ。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("day2", "では次の日、平均が元に戻るとする。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("juuichi", "そのとき必要な上げ幅は、【11.1%】。", anim=1.4, speed=1.15),
    Unit("kekka", "でも80から増やすので、追いつかない。", anim=1.6, face="troubled",
         speed=1.15),
    Unit("sa", "その結果は【97.8】。平均は100なのに。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34, speed=1.1, intonation=1.2, pitch=-0.05),
    Unit("riyu", "その差2.2は、80から増やしたからだ。", anim=1.2, speed=1.15),
    Unit("joken", "逆に上げ続ける時は、大きく増える。", anim=1.2, face="happy",
         speed=1.15),
    Unit("shime", "上下をくり返すほど、この目減りは積もる。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S013.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
