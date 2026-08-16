#!/usr/bin/env python3
"""S011: 年金は、何歳まで生きたら払った分を取り返せるのか。数値は verify.py と照合。

企画書は plan.md。ユーザー判定「年金の話はとても面白い」で採用されたネタ。

P-0(persona.md): ショートは選ばれない。興味ゼロの人に押し込まれる。
入口は「年金」= 全員が払っている/もらう物。専門用語では始めない(プレイブックF5)。

図の型(figure-forms.md):
- 主役は「払った山」と「もらう山」がどこで並ぶか → 固有シーン tenbin()。
  左に払った総額の棒、右に受け取った額の棒。右が伸びて左に追いつく形で見せる
- 年ごとの積み上がりは、同じ図の中で棒を伸ばす(一度に完成させない)
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
BADGE = "2026年度の金額がずっと続いた場合"

PREMIUM, YEARS_PAY, PENSION, START = 17_920, 40, 70_608, 65
PAID = PREMIUM * 12 * YEARS_PAY
PER_YEAR = PENSION * 12
BREAK_EVEN = START + PAID / PER_YEAR
assert PAID == 8_601_600 and PER_YEAR == 847_296, "verify.pyと不一致"
assert int(BREAK_EVEN) == 75 and round((81.35 - BREAK_EVEN) * PER_YEAR / 10_000) == 525


def tenbin(years_received=0, show_break=False, show_plus=False):
    """固有シーン: 払った総額と、もらった総額を並べる。

    左=40年で払った860万円(高さ固定)。右=受け取った額(年数ぶん伸びる)。
    右が左に届いた瞬間が「元が取れた」。長さが意味を持つので、同じ縮尺で並べる。
    """
    Y0 = 0.560
    VMAX = PER_YEAR * 16.35   # 図に出る最大額(平均寿命まで受け取った場合)
    HMAX = 0.185              # その最大額のときの高さ。両方の棒を同じ縮尺で描く
    got = PER_YEAR * years_received

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "払った額と、もらった額", ha="center", color=INK_2, fontsize=34)
        fig.add_artist(sc.plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                     color=MUTED, linewidth=1.5, alpha=0.5))
        # 左: 払った総額
        h_paid = HMAX * PAID / VMAX
        fig.patches.append(Rectangle((0.17, Y0), 0.24, h_paid, transform=fig.transFigure,
                                     facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
        fig.text(0.29, Y0 + h_paid + 0.032, "860万円", ha="center", va="center", color=INK,
                 fontsize=32, path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        fig.text(0.29, Y0 - 0.032, "40年で払う", ha="center", va="center",
                 color=INK_2, fontsize=26)
        # 右: もらった総額(伸びる)
        a = sc.clamp01(t * 1.8)
        h = HMAX * (got / VMAX) * a
        if got > 0:
            fig.patches.append(Rectangle((0.59, Y0), 0.24, h, transform=fig.transFigure,
                                         facecolor=EMPH, edgecolor="none", alpha=0.95))
            # 途中の合計額は字幕で言わないので、図にも出さない(数字が無言の判定)
            label = "860万円" if show_break else ""   # 金額は字幕で言う時だけ図に出す
            if label:
                fig.text(0.71, Y0 + h + 0.032, label, ha="center", va="center", color=INK,
                         fontsize=32,
                         path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        fig.text(0.71, Y0 - 0.032, "65歳からもらう", ha="center", va="center",
                 color=INK_2, fontsize=26)
        # 払った額の高さに、水平線を1本引く(どこで追いつくかが一目で分かる)
        fig.add_artist(sc.plt.Line2D([0.14, 0.86], [Y0 + h_paid, Y0 + h_paid],
                                     transform=fig.transFigure, color=MUTED,
                                     linewidth=1.2, alpha=0.45))
        if show_break:
            fig.text(0.5, 0.492, "ここで追いついた", ha="center", va="center",
                     color=EMPH, fontsize=32, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(32), fatten=2))
        if show_plus:
            fig.text(0.5, 0.492, "はみ出た分がプラス", ha="center", va="center",
                     color=EMPH, fontsize=32, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(32), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("年金は", "元が取れるのか", BADGE, BRAND, size=104, sub_fs=44),
    "nazo__cover": sc.cover("年金って、払った分は返ってくる?", "75歳",
                            "そこが分かれ目なのだ", "はじめての人向け", BRAND, main_size=160),
    "dare": sc.card("まず、だれの話か", "自分で払う人", "(会社員は給料から引かれている)",
                    BADGE, BRAND, main_size=58, head_fs=34),
    "hokenryo": sc.card("その人が毎月払う額", "月1万7920円", "(2026年度の金額)",
                        BADGE, BRAND, main_size=58, head_fs=34),
    "yonjunen": sc.stack("何年ぶん払うのか", 40, "四角ひとつが、年に払う保険料", "ぜんぶで40年",
                         BADGE, BRAND, cols=10),
    "goukei": tenbin(0),
    "toi": sc.quiz("では、もらうほう", "65歳から", "いくらもらえる?", "", BADGE, BRAND),
    "gaku": sc.card("いちばん多い人で", "月7万608円", "(40年すべて払った場合)",
                    BADGE, BRAND, main_size=58, head_fs=34),
    "nenkan": sc.bars2("払った額と、年にもらう額",
                       ("40年で払った額", 860, "860万円"),
                       ("年にもらう額", 85, "85万円"),
                       BADGE, BRAND, ymax=900),
    "warizan": tenbin(5),
    "moto": tenbin(10.15, show_break=True),
    "juumigo": sc.card("追いつくのは", "75歳", "(65歳から10年たった時点)",
                       BADGE, BRAND, main_size=96, head_fs=34,
                       ask="あなたは何歳まで生きる?"),
    "jumyo": tenbin(16.35, show_plus=True),
    "plus": sc.card("平均寿命まで生きると", "525万円のプラス", "(男性81歳の場合)",
                    BADGE, BRAND, main_size=52, head_fs=34),
    "gyaku": tenbin(5),
    "chokin": sc.card("だから年金は", "貯金ではない", "(積み立てているわけではない)",
                      BADGE, BRAND, main_size=62, head_fs=34),
    "shime": sc.hero("年金の正体は", "貯金ではなく保険", BADGE, BRAND, size=88, sub_fs=40),
}

# ネタ選定ゲート(F1/F3/F4/F5):
#   入口=年金(全員が払う・もらう物。専門語ではない)
#   予想「払った分ぐらいは返ってくるでしょ」→ 結論「75歳まで生きないと払い損」
#   オチは実害(早く亡くなれば損)と、見方の変更(年金は貯金ではなく保険)
UNITS = [
    Unit("nazo", "年金って、払った分は返ってくるのか。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("dare", "まず、自分で払う人の保険料を見る。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("hokenryo", "その保険料は、いま月1万7920円。", anim=1.4, speed=1.15),
    Unit("yonjunen", "これを40年間、払い続けるのだ。", anim=1.6, speed=1.15),
    Unit("goukei", "その40年ぶんの合計は、860万円。", anim=1.4, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("toi", "では65歳から、いくらもらえるのか。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("gaku", "その額は、多い人で月7万608円。", anim=1.4, speed=1.15),
    Unit("nenkan", "これを年に直すと、およそ85万円。", anim=1.4, speed=1.15),
    Unit("warizan", "860万円を85万円で割ると、10年。", anim=1.6, speed=1.15),
    Unit("moto", "つまり【75歳】で、払った分に届く。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("juumigo", "その75歳より長生きすると、どうなる?", anim=1.4, speed=1.15),
    Unit("jumyo", "その場合、男性の平均寿命は81歳。", anim=1.6, speed=1.15),
    Unit("plus", "そこまで生きれば、【525万円】の得。", anim=1.4, face="happy",
         speed=1.15),
    Unit("gyaku", "でも早く亡くなれば、払い損なのだ。", anim=1.2, face="troubled",
         speed=1.15),
    Unit("chokin", "だから年金は、貯金ではないのだ。", anim=1.2, speed=1.15),
    Unit("shime", "長生きしすぎた時の、保険なのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S011.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
