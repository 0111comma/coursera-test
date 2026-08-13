#!/usr/bin/env python3
"""S010: 国民年金だけなら月いくら(T3比較型)。数値はverify.pyと同一・assert照合。"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_out_back,
    stroke_fx, outline_for, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, EMPH, GOLD,
)
import scenes_common as sc

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "2026年度の年金額・平均は実績統計"

KOKUMIN_M = 70_608
MODEL_HUFU = 237_279
HEIKIN = 147_000
assert KOKUMIN_M * 12 == 847_296 and 96_063 + KOKUMIN_M * 2 == MODEL_HUFU, "verify.pyと不一致"
assert HEIKIN - KOKUMIN_M == 76_392, "verify.pyと不一致"
assert 17_920 * 12 == 215_040, "verify.pyと不一致"  # 保険料(2026年度)月額×12


def scene_nikai(fig, t):
    """固有シーン: 年金の2階建て構造。"""
    a1 = sc.clamp01(t * 1.8)
    a2 = sc.clamp01(t * 1.8 - 0.6)
    fig.text(0.5, 0.90, "会社員の年金は2階建て", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.845, "あなたは、どっちの階に住む?", ha="center", color=EMPH, fontsize=32,
             alpha=sc.clamp01(t * 1.6 - 0.6))
    fig.patches.append(FancyBboxPatch((0.22, 0.46), 0.56, 0.10, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=MUTED_BAR,
                                      edgecolor="none", alpha=a1))
    fig.text(0.5, 0.51, "1階: 国民年金(全員)", ha="center", va="center", color=INK,
             fontsize=30, alpha=a1)
    fig.patches.append(FancyBboxPatch((0.22, 0.58), 0.56, 0.10, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=GOLD,
                                      edgecolor="none", alpha=a2))
    fig.text(0.5, 0.63, "2階: 厚生年金(会社員)", ha="center", va="center", color=INK,
             fontsize=30, alpha=a2,
             path_effects=stroke_fx(INK, outline=outline_for(30), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(70608, "{:,}円", BADGE, BRAND, size=104,
                                lead="その老後、月7万円で足りる?"),
    "hero_count__cover": sc.cover("その老後、月7万円で足りる?", "月7万608円", "国民年金だけの現実",
                                  "2026年度の満額・厚労省", BRAND, main_size=104),
    "hero_full": sc.hero("月7万608円", "国民年金(満額)の1ヶ月分", BADGE, BRAND, size=100),
    "genjitsu": sc.card("毎月の保険料", "17,920円 × 40年", "(2026年度の保険料。未納があると減る)", BADGE, BRAND, main_size=48),
    "seikatsu": sc.card("この額で暮らすと", "家賃を払うと、残り数万円", "(年間でも847,296円。ここから食費・光熱費)",
                        BADGE, BRAND, main_size=44),
    "quiz": sc.quiz("クイズ", "会社員がもらう年金は", "平均でいくら?", "(厚生年金+国民年金)", BADGE, BRAND),
    "kaisha": sc.reveal("月14万7千円", "厚生年金をもらう人の平均", "厚労省の実績統計(基礎年金込み)", BADGE, BRAND, size=92),
    "sa": sc.card("同じ65歳でも", "差は月7万6千円", "(147,000 − 70,608 = 76,392円)", BADGE, BRAND, main_size=52),
    "nikai": scene_nikai,
    "ikkai": sc.card("フリーランス・自営業は", "1階だけ", "(国民年金のみ。2階は自分で作る)", BADGE, BRAND, main_size=56),
    "edamame": sc.card("ここだけの話", "毎日、塩ゆで枝豆をかじる老後", "(それだけは避けたいのだ…)", BADGE, BRAND, main_size=40),
    "huufu": sc.hero("月23万7279円", "夫婦2人のモデル(会社員+専業)", BADGE, BRAND, size=88),
    "teikibin": sc.card("自分の見込み額は", "ねんきん定期便", "(毎年誕生月に届くハガキ)", BADGE, BRAND, main_size=52),
    "chips": sc.chips("あなたは何階建て?", ["1階だけ", "2階建て", "iDeCoで3階", "わからない"], BADGE, BRAND),
    "loop_back": sc.hero("月7万608円", "国民年金(満額)の1ヶ月分", BADGE, BRAND, size=100),
}

UNITS = [
    Unit("hero_count", "【7万608円】。", anim=1.2, cover=True, se="pop", face="surprised",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "65歳からもらう、国民年金の満額。", anim=0.8, speed=1.2),
    Unit("genjitsu", "保険料は月1万8千円。40年でこの額なのだ。", anim=1.2, speed=1.1,
         face="troubled", intonation=1.15, pitch=-0.04),
    Unit("seikatsu", "家賃を払ったら、残りは数万円なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.2, pitch=-0.04),
    Unit("quiz", "では会社員の年金は、いくらだと思う?", anim=1.4, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.3),
    Unit("kaisha", "平均で、月【14万7千円】なのだ。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("sa", "同じ65歳で、差は月7万6千円なのだ。", anim=1.2, speed=1.15),
    Unit("nikai", "会社員の年金は、【2階建て】だからなのだ。", anim=1.6, speed=1.1, intonation=1.15),
    Unit("ikkai", "フリーランスは、1階だけなのだ。", anim=1.2, face="troubled", speed=1.15),
    Unit("edamame", "毎日枝豆をかじる老後は、無理なのだ。", anim=1.2, face="troubled",
         speed=1.1, intonation=1.3, pitch=0.02),
    Unit("huufu", "夫婦のモデルなら、月23万7279円。", anim=1.0, se="don", speed=1.15),
    Unit("teikibin", "自分の見込みは、【ねんきん定期便】で見る。", anim=1.2, speed=1.15),
    Unit("chips", "あなたの年金は、何階建て?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "そして1階だけの満額が、これなのだ。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S010.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
