#!/usr/bin/env python3
"""S017: 宝くじの1億円は税金ゼロ。株の1億円は2割(およそ2000万円)引かれる。

企画書は plan.md。基準作 S011 の8行を埋めてから作った。

P-0(persona.md): ショートは選ばれない。興味ゼロの人に押し込まれる。
入口は「宝くじ」= 買ったことがなくても知っている物。NISAで始めない(F5)。
NISAは**答えとして中で出す**。

図の型(figure-forms.md):
- 主役は「同じ1億円なのに、片方だけ削られる」 → 固有シーン hako()。
  左に宝くじの1億円、右に株の1億円を同じ縮尺で並べ、右の上だけを灰色にする。
  NISAの段で、その灰色が消える。削られる/削られないが面積で分かる
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
BADGE = "1億円のもうけ・税20.315%で計算"

TOTAL = 10000        # 1億円(万円単位)
TAX = 2000           # 20.315% を画面表示に合わせて丸めた額(厳密な額は verify.py)
NET = TOTAL - TAX
assert TAX == 2000 and NET == 8000, "verify.pyの丸め表示と不一致"


def hako(stock=False, tax=False, nisa=False, note=""):
    """固有シーン: 同じ1億円を、宝くじと株で並べる。

    左=宝くじの当せん金1億円(まるごと金色)。
    右=株のもうけ1億円。tax にすると上の税金ぶん(およそ2000万円)が灰色になり、
    nisa にするとその灰色が消えてまた1億円に戻る。
    同じ縮尺なので、削られた面積がそのまま税金の額になる。
    """
    Y0 = 0.560
    HMAX = 0.200

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "同じ1億円のもうけ", ha="center", color=INK_2, fontsize=34)
        fig.add_artist(sc.plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                     color=MUTED, linewidth=1.5, alpha=0.5))
        a = sc.clamp01(t * 1.8)
        # 左: 宝くじ(まるごと残る)
        fig.patches.append(Rectangle((0.17, Y0), 0.24, HMAX, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        fig.text(0.29, Y0 + HMAX + 0.032, "1億円", ha="center", va="center", color=INK,
                 fontsize=32, path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        fig.text(0.29, Y0 - 0.032, "宝くじ", ha="center", va="center",
                 color=INK_2, fontsize=27)
        # 右: 株のもうけ。税金の分だけ上が灰色になる(NISAなら戻る)
        if stock:
            cut = (tax and not nisa)
            h_net = HMAX * (NET if cut else TOTAL) / TOTAL
            fig.patches.append(Rectangle((0.59, Y0), 0.24, h_net, transform=fig.transFigure,
                                         facecolor=GOLD, edgecolor="none", alpha=0.95))
            if cut:
                fig.patches.append(Rectangle((0.59, Y0 + h_net), 0.24,
                                             HMAX * TAX / TOTAL * a, transform=fig.transFigure,
                                             facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
            fig.text(0.71, Y0 + HMAX + 0.032, "1億円", ha="center", va="center", color=INK,
                     fontsize=32, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
            fig.text(0.71, Y0 - 0.032, "株のもうけ", ha="center", va="center",
                     color=INK_2, fontsize=27)
        if note:
            fig.text(0.5, 0.487, note, ha="center", va="center", color=EMPH,
                     fontsize=34, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("その当せん金", "税金はかからない", BADGE, BRAND, size=92, sub_fs=42),
    "nazo__cover": sc.cover("宝くじ1億円、税金はいくら?", "0円",
                            "株の1億円だと2割とられる", "はじめての人向け", BRAND, main_size=190),
    "horitsu": sc.card("なぜゼロなのか", "法律で決まっている", "(当せん金付証票法 第13条)",
                       BADGE, BRAND, main_size=54, head_fs=34),
    "marugoto": hako(),
    "toi": sc.quiz("では、こちらは", "株で1億円", "もうけたら?", "", BADGE, BRAND),
    "zeiritsu": hako(stock=True, note="20.315%"),
    "bunkatsu": hako(stock=True, tax=True, note="税金 2000万円"),
    "nokori": hako(stock=True, tax=True, note="手取り8000万円"),
    "hikaku": hako(stock=True, tax=True),
    "dake": sc.card("大金だけの話?", "そうではない", "(もうけが小さくても同じ率)",
                    BADGE, BRAND, main_size=62, head_fs=34,
                    ask="あなたなら、どっちで受け取る?"),
    "juman": sc.card("身近な額で見ると", "10万円のもうけ", "(たとえば持っていた株を売った時)",
                     BADGE, BRAND, main_size=58, head_fs=34),
    "zei2": sc.card("その時の税金は", "2万315円", "(もうけの20.315%)",
                    BADGE, BRAND, main_size=72, head_fs=34),
    "furi": sc.card("ところが", "税金がゼロの箱", "(同じもうけでも、置く場所で変わる)",
                    BADGE, BRAND, main_size=62, head_fs=34),
    "nisa": sc.card("その箱の名前", "NISA", "(証券会社などで作る口座の種類)",
                    BADGE, BRAND, main_size=110, head_fs=34),
    "nisa2": hako(stock=True, tax=True, nisa=True, note="この中なら引かれない"),
    "jougen": sc.card("ただし条件がある", "入れる額に上限", "(いくらでも入れられるわけではない)",
                      BADGE, BRAND, main_size=58, head_fs=34),
    "waku": sc.bars2("NISAに入れられる額",
                     ("一生で", 1800, "1800万円"),
                     ("毎年", 360, "360万円"),
                     BADGE, BRAND, ymax=1950),
    "waku2": sc.bars2("NISAに入れられる額",
                      ("一生で", 1800, "1800万円"),
                      ("毎年", 360, "360万円"),
                      BADGE, BRAND, ymax=1950),
    "shime": sc.hero("同じもうけでも", "置く場所でちがう", BADGE, BRAND, size=88, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行は plan.md 参照:
#   入口=宝くじ(買ったことがなくても知っている。NISAでは始めない=F5)
#   予想「1億円当たったら半分は税金でしょ」→ 結論「宝くじはゼロ。でも株は2割」
#   オチ=実害(およそ2000万円/身近な額でも2万315円)+ 行動(NISAという箱がある)
UNITS = [
    Unit("nazo", "宝くじで1億円当たっても、税金はゼロなのだ。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("horitsu", "まず、これは法律で決まっている。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("marugoto", "だから1億円は、まるごと手元に残るのだ。", anim=1.4, speed=1.15),
    Unit("toi", "では、株で1億円もうけたら?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("zeiritsu", "この場合は20.315%が、税金で引かれる。", anim=1.4, speed=1.15),
    Unit("bunkatsu", "つまりおよそ2000万円が、税金になる。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("nokori", "すると手元に残るのは、およそ8000万円。", anim=1.6, speed=1.15),
    Unit("hikaku", "つまり同じ1億円なのに、ここまでちがう。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("dake", "これは、1億円だけの話ではないのだ。", anim=1.4, speed=1.15),
    Unit("juman", "たとえば、10万円もうけたとする。", anim=1.4, speed=1.15),
    Unit("zei2", "その税金は、2万315円になるのだ。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("furi", "でも、税金がゼロになる箱がある。", anim=1.4, face="happy",
         speed=1.15, intonation=1.2),
    Unit("nisa", "それがNISAと呼ばれる、口座の種類。", anim=1.4, speed=1.15),
    Unit("nisa2", "そのNISAの中なら、税金がゼロになる。", anim=1.6, face="happy",
         speed=1.15),
    Unit("jougen", "ただし、入れられる額に上限がある。", anim=1.4, speed=1.15),
    Unit("waku", "その上限は、一生で1800万円まで。", anim=1.4, speed=1.15),
    Unit("waku2", "そして毎年、入れられるのは360万円まで。", anim=1.4, speed=1.15),
    Unit("shime", "同じもうけでも、置く場所で2割ちがう。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S017.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
