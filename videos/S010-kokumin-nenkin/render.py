#!/usr/bin/env python3
"""S010: 国民年金だけなら月いくら(T3比較型)。数値はverify.pyと同一・assert照合。

ループ㊴(ペルソナ監査): 金融リテラシーが低い視聴者2人に1文ずつ聞かせる検証で、
「払う/もらう」の反転・未定義語「上乗せ」・名前のない「ハガキ」・時点の欠落が判明したため全面改稿。
- 1文目で「もらえる額」と明示する(数字だけ投げない)
- 制度の骨格「20〜60歳に払う → 65歳からもらう」を、名前より先に図で見せる
- 会社員の上乗せに「厚生年金」という名前と「給料から多く払っているから」という理由を与える
- 「ねんきん定期便」は名前+「毎年、誕生月に届くハガキ」の実物描写をセットで出す
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox,
    stroke_fx, outline_for, draw_badge, draw_footer_brand,
    INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度の金額・平均は実績統計"

KOKUMIN_M = 70_608
HEIKIN = 147_000
HOKENRYO = 17_920
assert KOKUMIN_M * 12 == 847_296, "verify.pyと不一致"
assert HEIKIN - KOKUMIN_M == 76_392, "verify.pyと不一致"
assert HOKENRYO * 12 == 215_040, "verify.pyと不一致"


def scene_kokan(fig, t):
    """固有シーン: 制度の骨格「払う期間 → もらう期間」の交換を1枚で見せる。"""
    a1 = sc.clamp01(t * 2.0)
    a2 = sc.clamp01(t * 2.0 - 0.8)
    fig.text(0.5, 0.90, "国民年金のしくみ", ha="center", color=INK_2, fontsize=34)
    fig.patches.append(FancyBboxPatch((0.10, 0.62), 0.80, 0.11, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=MUTED_BAR,
                                      edgecolor="none", alpha=a1))
    fig.text(0.5, 0.675, "20歳から60歳まで  払う", ha="center", va="center", color=INK,
             fontsize=34, alpha=a1)
    fig.text(0.5, 0.575, "↓", ha="center", va="center", color=INK_2, fontsize=44, alpha=a2)
    fig.patches.append(FancyBboxPatch((0.10, 0.42), 0.80, 0.11, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=GOLD,
                                      edgecolor="none", alpha=a2))
    fig.text(0.5, 0.475, "65歳から一生  もらう", ha="center", va="center", color=INK,
             fontsize=34, alpha=a2,
             path_effects=stroke_fx(INK, outline=outline_for(34), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(70608, "月{:,}円", BADGE, BRAND, size=96,
                                lead="老後にもらえる年金は?"),
    "hero_count__cover": sc.cover("その老後、月7万円で足りる?", "月7万608円", "老後にもらえる年金の額",
                                  "2026年度・厚労省", BRAND, main_size=100),
    "itsu": sc.card("この7万608円は", "65歳から、毎月もらう", "(40年ぶん払い切った人の額)", BADGE, BRAND,
                    main_size=48),
    "kokan": scene_kokan,
    "jieigyo": sc.card("自営業・フリーランスは", "毎月17,920円を払う", "(2026年度。自分で納める)", BADGE, BRAND,
                       main_size=48),
    "quiz": sc.quiz("クイズ", "会社で働く人は", "いくらもらえる?", "(同じ65歳で比べる)", BADGE, BRAND),
    "kousei": sc.card("会社員は", "厚生年金が上に乗る", "(給料から、その分も引かれているから)", BADGE, BRAND,
                      main_size=50, ask="あなたの年金に、厚生年金は乗ってる?"),
    "heikin": sc.reveal("月14万7千円", "国民年金+厚生年金の合計(平均)", "厚労省の実績統計より", BADGE, BRAND,
                        size=92),
    "sa": sc.card("同じ65歳でも", "差は月7万6千円", "(147,000 − 70,608 = 76,392円)", BADGE, BRAND,
                  main_size=52),
    "ikkai": sc.card("自営業に厚生年金はない", "月7万608円だけ", "(この差が、老後ずっと続く)", BADGE, BRAND,
                     main_size=50),
    "teikibin": sc.card("自分がいくらか知るには", "ねんきん定期便", "(毎年、誕生月に届くハガキ)", BADGE, BRAND,
                        main_size=52),
    "chips": sc.chips("あなたの年金に、厚生年金は乗ってる?",
                      ["乗ってる", "乗ってない", "わからない", "調べてみる"], BADGE, BRAND, q_fs=40),
    "loop_back": sc.hero("月7万608円", "65歳から毎月もらう、国民年金だけの額", BADGE, BRAND,
                         size=96, sub_fs=29),
}

UNITS = [
    Unit("hero_count", "月【7万608円】。老後にもらえる年金の額。", anim=1.2, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("itsu", "40年払い切った人が、65歳から毎月もらう額。", anim=1.0, speed=1.15),
    Unit("kokan", "20歳から60歳まで払う。それが【国民年金】なのだ。", anim=1.6, speed=1.1),
    Unit("jieigyo", "自営業は毎月1万8千円、自分で払うのだ。", anim=1.2, speed=1.15),
    Unit("quiz", "では、会社で働く人はどうなのだ?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kousei", "会社員は給料から多く払い、【厚生年金】が乗るのだ。", anim=1.2,
         speed=1.1, intonation=1.15),
    Unit("heikin", "その合計が、平均で月【14万7千円】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("sa", "同じ65歳で、月7万6千円もの差なのだ。", anim=1.2, se="don", speed=1.15),
    Unit("ikkai", "自営業に厚生年金はなく、7万608円だけなのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("teikibin", "自分の額は、【ねんきん定期便】で分かるのだ。", anim=1.2, speed=1.15),
    Unit("chips", "あなたの年金に、厚生年金は乗ってる?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "乗ってないなら、月7万608円だけなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S010.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
