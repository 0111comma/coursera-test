#!/usr/bin/env python3
"""S013: 銀行の利息、3年で400倍(T4タイムライン型)。数値はverify.pyとassert照合。"""
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
BADGE = "大手銀行の普通預金・2026年8月時点"

assert int(1_000_000 * 0.0040) == 4_000, "verify.pyと不一致"
assert int(1_000_000 * 0.00001) == 10 and 4_000 // 10 == 400, "verify.pyと不一致"
assert 4_000 - int(4_000 * 0.15315) - int(4_000 * 0.05) == 3_188, "verify.pyと不一致"


def scene_kinri(fig, t):
    """固有シーン: 金利のタイムライン 0.001%→利上げ→0.40%。"""
    fig.text(0.5, 0.90, "普通預金の金利はこう動いた", ha="center", color=INK_2, fontsize=32)
    steps = [("〜2024年", "0.001%", MUTED_BAR), ("2024年〜", "利上げ開始", MUTED_BAR),
             ("2026年8月", "0.40%", GOLD)]
    for i, (yr, v, c) in enumerate(steps):
        a = sc.clamp01(t * 2.4 - i * 0.55)
        if a <= 0:
            continue
        y = 0.70 - i * 0.105
        fig.text(0.27, y, yr, ha="center", color=INK_2, fontsize=29, alpha=a)
        fig.text(0.64, y, v, ha="center", color=INK, alpha=a,
                 fontsize=40 if i == 2 else 32,
                 path_effects=stroke_fx(INK, outline=outline_for(40), fatten=2) if i == 2 else None)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(4_000, "{:,}円", BADGE, BRAND, size=118,
                                lead="その100万円、1年でいくら?"),
    "hero_count__cover": sc.cover("あなたの100万円、1年でいくら?", "4,000円", "実は3年で400倍になった",
                                  "金利0.40%・2026年8月", BRAND),
    "hero_full": sc.hero("4,000円", "100万円を1年預けたときの利息", BADGE, BRAND, size=112, sub_fs=30),
    "sukuna": sc.card("正直…", "「少なっ」と思った?", "(その感覚、もう古いかも)", BADGE, BRAND,
                      main_color=MUTED_BAR, main_size=48),
    "mukashi": sc.card("数年前まで", "たった10円", "(金利0.001%の時代・100万円で)", BADGE, BRAND,
                       main_size=56),
    "bai400": sc.reveal("400倍", "10円 → 4,000円(この3年で)", "1,000,000円 × 0.40% = 4,000円", BADGE, BRAND,
                        size=118),
    "kinri": scene_kinri,
    "teiki": sc.card("定期預金(1年)なら", "年0.50%で5千円", "(1年おろさない約束にする預け方)", BADGE, BRAND,
                     main_size=50,
                     ask="あなたの預け方は、どっち?"),
    "zeikin": sc.card("ただし利息には", "税金が約2割", "(4,000円 → 手取り3,188円)", BADGE, BRAND,
                      main_size=54),
    "atm": sc.card("ここだけの話", "昔はATM1回=利息22年分", "(手数料220円 ÷ 年10円)", BADGE, BRAND,
                   main_size=40),
    "bukka": sc.card("それでも", "物価が上がると、お金の力は減る", "(金利0.4% − 物価2% = マイナス)", BADGE, BRAND,
                     main_size=42),
    "chips": sc.chips("あなたの銀行、金利見てる?", ["見てる", "見たことない", "定期にした", "10円時代を知ってる"], BADGE, BRAND),
    "loop_back": sc.hero("4,000円", "100万円を1年預けたときの利息", BADGE, BRAND, size=112, sub_fs=30),
}

# 全ビートを But/Therefore で繋ぐ(D10・ループ㊶)。check_flow.py で断絶0件を確認すること。
UNITS = [
    Unit("hero_count", "【4千円】。100万円を1年預けた利息。", anim=1.2, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.2, pitch=0.0),
    Unit("sukuna", "この4千円、「少なっ」と思った?",
         narration="この4千円、「すくなっ」と思った?", anim=1.2, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.2),
    Unit("mukashi", "でも数年前まで、たった【10円】だったのだ。", anim=1.2, speed=1.15),
    Unit("bai400", "つまり利息は、この3年で【400倍】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("kinri", "この400倍は、金利が0.4%になったから。", anim=1.8, speed=1.15),
    Unit("teiki", "その金利、定期預金なら0.5%なのだ。", anim=1.2, speed=1.15),
    Unit("zeikin", "ただし税金が2割引かれ、手取り約3千2百円。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.15, pitch=-0.04),
    Unit("atm", "しかも昔はATM1回で、利息【22年分】が消えた。", anim=1.2, se="don", speed=1.1,
         face="troubled", intonation=1.25, pitch=0.02),
    Unit("bukka", "さらに物価が2%上がるなら、お金の力は減る。", anim=1.2, speed=1.15),
    Unit("chips", "あなたの銀行の金利、見たことある?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして今の利息が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S013.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
