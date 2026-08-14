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
BADGE = "2026年度・どちらも40年働いた場合"

KOKUMIN_M = 70_608
HOSHU_HIREI = 96_063
MODEL_KAISHAIN = 166_671
HOKENRYO = 17_920
assert KOKUMIN_M * 12 == 847_296, "verify.pyと不一致"
assert KOKUMIN_M + HOSHU_HIREI == MODEL_KAISHAIN, "verify.pyと不一致"
assert HOKENRYO * 12 == 215_040, "verify.pyと不一致"


def scene_kokan(fig, t):
    """固有シーン: 制度の骨格「払う期間 → もらう期間」の交換を1枚で見せる。"""
    a1 = sc.clamp01(t * 2.0)
    a2 = sc.clamp01(t * 2.0 - 0.8)
    fig.text(0.5, 0.90, "国民年金は、全員が入る", ha="center", color=INK_2, fontsize=34)
    fig.patches.append(FancyBboxPatch((0.10, 0.66), 0.80, 0.11, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=MUTED_BAR,
                                      edgecolor="none", alpha=a1))
    fig.text(0.5, 0.715, "20歳から60歳まで  払う", ha="center", va="center", color=INK,
             fontsize=34, alpha=a1)
    fig.text(0.5, 0.615, "↓", ha="center", va="center", color=INK_2, fontsize=44, alpha=a2)
    fig.patches.append(FancyBboxPatch((0.10, 0.50), 0.80, 0.11, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=GOLD,
                                      edgecolor="none", alpha=a2))
    fig.text(0.5, 0.555, "65歳から一生  もらう", ha="center", va="center", color=INK,
             fontsize=34, alpha=a2,
             path_effects=stroke_fx(INK, outline=outline_for(34), fatten=1.5))
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_2kai(fig, t):
    """固有シーン: 会社員=国民年金(土台)+厚生年金(上)の積み上げ。土台を先に描く。

    立ち絵(x<0.342, y0.245-0.465)と重ならないよう、テキストはすべて y>0.48 に置く。
    """
    a1 = sc.clamp01(t * 2.0)
    a2 = sc.clamp01(t * 2.0 - 0.9)
    fig.text(0.5, 0.905, "だから、こう積み上がる", ha="center", color=INK_2, fontsize=34)
    fig.text(0.66, 0.375, "あなたの給料からも、\n引かれてる?", ha="center", color=EMPH,
             fontsize=29, linespacing=1.4, alpha=sc.clamp01(t * 1.6 - 1.0))
    if a2 > 0:
        fig.patches.append(FancyBboxPatch((0.14, 0.665), 0.72, 0.115, boxstyle="round,pad=0.008",
                                          transform=fig.transFigure, facecolor=MUTED_BAR,
                                          edgecolor="none", alpha=a2))
        fig.text(0.5, 0.7225, "厚生年金  会社員だけ", ha="center", va="center", color=INK,
                 fontsize=34, alpha=a2)
    fig.patches.append(FancyBboxPatch((0.14, 0.535), 0.72, 0.115, boxstyle="round,pad=0.008",
                                      transform=fig.transFigure, facecolor=GOLD,
                                      edgecolor="none", alpha=a1))
    fig.text(0.5, 0.5925, "国民年金  月7万608円", ha="center", va="center", color=INK,
             fontsize=34, alpha=a1,
             path_effects=stroke_fx(INK, outline=outline_for(34), fatten=1.5))
    fig.text(0.5, 0.49, "土台は、自営業と同じ国民年金", ha="center", color=INK_2,
             fontsize=27, alpha=a2)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


def scene_sa(fig, t):
    """固有シーン: 比較は同じ物差し(モデル年金)同士。差=そのまま厚生年金の分になる。

    立ち絵と重ならないよう、テキストはすべて y>0.48 に置く。
    """
    a1 = sc.clamp01(t * 2.2)
    a2 = sc.clamp01(t * 2.2 - 0.7)
    a3 = sc.clamp01(t * 2.2 - 1.4)
    fig.text(0.5, 0.905, "同じ条件で、くらべると", ha="center", color=INK_2, fontsize=34)
    fig.text(0.27, 0.775, "国民年金だけ", ha="center", color=INK_2, fontsize=28, alpha=a1)
    fig.text(0.27, 0.705, "月7万608円", ha="center", color=INK, fontsize=36, alpha=a1)
    fig.text(0.73, 0.775, "会社員の場合", ha="center", color=INK_2, fontsize=28, alpha=a2)
    fig.text(0.73, 0.705, "月16万6671円", ha="center", color=INK, fontsize=36, alpha=a2)
    fig.text(0.73, 0.65, "7万608円 + 9万6063円", ha="center", color=INK_2,
             fontsize=23, alpha=a2)
    fig.text(0.5, 0.565, "差 = 厚生年金の分", ha="center", color=EMPH, fontsize=46, alpha=a3,
             path_effects=stroke_fx(EMPH, outline=outline_for(46), fatten=2.5))
    fig.text(0.5, 0.49, "(どちらも40年働いた場合・厚労省の試算)",
             ha="center", color=INK_2, fontsize=26, alpha=a3)
    draw_badge(fig, BADGE)
    draw_footer_brand(fig, BRAND)


SCENES = {
    "hero_count": sc.hero_count(70608, "月{:,}円", BADGE, BRAND, size=96,
                                lead="老後にもらえる年金は?"),
    "hero_count__cover": sc.cover("その老後、月7万円で足りる?", "月7万608円", "老後にもらえる年金の額",
                                  "2026年度の満額・40年納めた場合", BRAND, main_size=100),
    # 背骨の宣言。ここから先の全ビートが「働き方でどう変わるか」の説明になる
    "hatarakikata": sc.card("でも、ここが大事", "額は、働き方で変わる", "(同じ65歳でも、2倍以上ちがう)", BADGE, BRAND,
                            main_size=48),
    "kokan": scene_kokan,
    "haraikiru": sc.card("その保険料を40年ぶん払うと", "月7万608円", "(65歳から、一生もらえる)", BADGE, BRAND,
                         main_size=54, head_fs=32),
    "jieigyo": sc.card("自営業・フリーランスは", "この保険料を、自分で払う", "(毎月17,920円の納付書が届く)", BADGE, BRAND,
                       main_size=42),
    "kaishain": sc.card("では、会社員は?", "保険料は、給料から引かれる", "(納付書は届かない。天引きだから)", BADGE, BRAND,
                        main_size=42),
    "kousei": scene_2kai,
    "heikin": sc.reveal("月9万6063円", "国民年金の上に乗る、厚生年金の分", "平均的な収入で40年働いた場合", BADGE, BRAND,
                        size=96),
    "sa": scene_sa,
    "ikkai": sc.card("ただし、乗るのは", "会社員だった期間の分だけ", "(自営業でいる間は、増えない)", BADGE, BRAND,
                     main_size=40),
    "teikibin": sc.card("じゃあ、自分はいくら?", "ねんきん定期便", "(毎年、誕生月に届くあのハガキ)", BADGE, BRAND,
                        main_size=52),
    "chips": sc.chips("あなたは今、どれ?",
                      ["今、会社員", "今、自営業", "会社員だった", "わからない"], BADGE, BRAND, q_fs=44),
    "loop_back": sc.hero("月7万608円", "65歳から毎月もらう、国民年金だけの額", BADGE, BRAND,
                         size=96, sub_fs=29),
}

# 全ビートを But/Therefore で繋ぐ(D10・ループ㊶)。
# 各行の頭の接続語か、直前の行に出た語を必ず受けること。文脈を切らない。
UNITS = [
    Unit("hero_count", "月【7万608円】。老後にもらえる年金の額。", anim=1.2, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.2, pitch=0.0),
    # But: 数字は1つではない、と宣言して背骨を立てる
    Unit("hatarakikata", "でも年金の額は、働き方で大きく変わるのだ。", anim=1.2, face="troubled",
         speed=1.15, intonation=1.2),
    # Therefore: まず全員に共通する部分から
    Unit("kokan", "まず20歳から60歳まで、全員が【国民年金】。", anim=1.6, speed=1.1),
    Unit("haraikiru", "その保険料を40年払うと、月7万608円。", anim=1.2, speed=1.15),
    # 「払う」の話を受けて、払い方の違いへ(自営業=見える / 会社員=見えない)
    Unit("jieigyo", "この保険料、自営業は毎月1万7920円。", anim=1.2, speed=1.15),
    Unit("kaishain", "では会社員は?保険料は給料から引かれる。", anim=1.2, face="troubled",
         speed=1.15, intonation=1.2, pause_scale=1.2),
    # Therefore: そのまとめて払った保険料が、2階建てを生む
    Unit("kousei", "だから国民年金に、【厚生年金】が乗るのだ。", anim=1.6,
         speed=1.1, intonation=1.15),
    Unit("heikin", "厚生年金は平均的な収入で、月【9万6063円】。", anim=1.4, face="surprised",
         puchun=True, se="impact", se_at=0.34,
         speed=1.1, intonation=1.2, pitch=-0.05, pause_scale=1.3),
    Unit("sa", "これを7万608円に足すと、合計16万6671円。", anim=1.6, se="don", speed=1.15),
    Unit("ikkai", "ただし乗るのは、会社員だった期間の分だけ。", anim=1.2, face="happy",
         speed=1.1, intonation=1.15),
    Unit("teikibin", "じゃあ自分は?【ねんきん定期便】で分かるのだ。", anim=1.2, speed=1.15),
    Unit("chips", "あなたは今、会社員?自営業?", anim=1.4, pad=0.15, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loop_back", "国民年金だけなら、40年払って月7万608円。", anim=0.8, pad=0.1, face="smug",
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S010.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
