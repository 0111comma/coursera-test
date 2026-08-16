#!/usr/bin/env python3
"""S013: 3000万円の家を買うと、実際に払うのは3571万円。数値は verify.py と照合。

企画書は plan.md。基準作 S011 の8行を埋めてから作った。

P-0(persona.md): ショートは選ばれない。興味ゼロの人に押し込まれる。
入口は「家」= 買う予定がなくても値段を知っている物。専門語では始めない(F5)。

図の型(figure-forms.md):
- 主役は「借りた額」と「その上に乗る利息」の比 → 固有シーン kaeshi()。
  下に借りた3000万円、その上に利息を積む。金利ごとに同じ縮尺の棒を2本並べ、
  積み上がりの差そのものを見せる(利息は借りた額に「乗る」ものだから積み上げ)
- 毎月の返済額は金額の大小なので、共通の底からの棒2本(bars2)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (  # noqa: E402
    Unit, render_video, require_voicevox, stroke_fx, outline_for,
    draw_badge, draw_footer_brand, INK, INK_2, MUTED, MUTED_BAR, EMPH,
)
import scenes_common as sc  # noqa: E402

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"
BADGE = "3000万円・35年・元利均等で計算"

BASE = 3000        # 借りた額(万円)
INT_VAR = 571      # 年1.025%のときの利息(万円)
INT_FIX = 1948     # 年3.140%のときの利息(万円)
assert BASE + INT_VAR == 3571 and BASE + INT_FIX == 4948, "verify.pyと不一致"
assert INT_FIX - INT_VAR == 1377


def kaeshi(ia=None, ib=None, note="", note_color=EMPH):
    """固有シーン: 借りた3000万円の上に、利息を積む。

    下の灰色=借りたお金(どちらの金利でも同じ3000万円)。
    上の金色=利息。左が年1.025%、右が年3.14%。
    同じ縮尺なので、棒の高さの差がそのまま「金利で変わる額」になる。
    ia/ib が None のあいだは、その棒はまだ出さない(図を一度に完成させない・G4)。
    """
    Y0 = 0.560
    HMAX = 0.200
    VMAX = BASE + INT_FIX      # 図に出る最大額。両方の棒を同じ縮尺で描く

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "借りた3000万円と、上に乗る利息", ha="center",
                 color=INK_2, fontsize=34)
        fig.add_artist(sc.plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                     color=MUTED, linewidth=1.5, alpha=0.5))
        h_base = HMAX * BASE / VMAX
        a = sc.clamp01(t * 1.8)

        def bar(x, interest, foot, show):
            """1本ぶん。下=借りた額、上=利息(伸びる)。"""
            if not show:
                return
            fig.patches.append(Rectangle((x, Y0), 0.24, h_base, transform=fig.transFigure,
                                         facecolor=MUTED_BAR, edgecolor="none", alpha=0.95))
            top = Y0 + h_base
            if interest is not None:
                h_int = HMAX * interest / VMAX * a
                fig.patches.append(Rectangle((x, top), 0.24, h_int,
                                             transform=fig.transFigure, facecolor=EMPH,
                                             edgecolor="none", alpha=0.95))
                top += h_int
            total = BASE + (interest or 0)
            fig.text(x + 0.12, top + 0.032, f"{total}万円", ha="center", va="center",
                     color=INK, fontsize=32,
                     path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
            fig.text(x + 0.12, Y0 - 0.032, foot, ha="center", va="center",
                     color=INK_2, fontsize=27)

        bar(0.17, ia, "年1.025%", True)
        bar(0.59, ib, "年3.14%", ib is not None)
        if note:
            fig.text(0.5, 0.487, note, ha="center", va="center", color=note_color,
                     fontsize=34, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(note_color, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("その家の値段", "払う額とは違う", BADGE, BRAND, size=88, sub_fs=42),
    "nazo__cover": sc.cover("3000万円の家、いくら払う?", "3571万円",
                            "差額は銀行にいく", "はじめての人向け", BRAND, main_size=132),
    "kariru": sc.card("家を買うときの話", "お金を借りる", "(全額を現金で払う人は少ない)",
                      BADGE, BRAND, main_size=62, head_fs=34),
    "loan": sc.card("その借金の名前", "住宅ローン", "(家を買うために借りるお金)",
                    BADGE, BRAND, main_size=72, head_fs=34),
    "gaku": sc.card("この動画で使う条件", "3000万円", "(35年・元利均等・ボーナス払いなし)",
                    BADGE, BRAND, main_size=54, head_fs=34),
    "risoku": sc.card("借りると何が起きるか", "利息がつく", "(借りた額より多く返すことになる)",
                      BADGE, BRAND, main_size=68, head_fs=34),
    "toha": sc.card("その利息とは", "借りるお礼", "(貸してくれた側に払うお金)",
                    BADGE, BRAND, main_size=68, head_fs=34),
    "wariai": sc.card("その割合の呼び名", "金利", "(年に何%かで表す)",
                      BADGE, BRAND, main_size=88, head_fs=34),
    "kinri1": sc.card("いまの金利のひとつ", "年1.025%", "(2026年8月・大手行の変動金利)",
                      BADGE, BRAND, main_size=76, head_fs=34,
                      ask="あなたなら、いくら借りる?"),
    "getsu1": sc.card("毎月はらう額は", "8万5036円", "(3000万円・35年・年1.025%)",
                      BADGE, BRAND, main_size=66, head_fs=34),
    "kaisu": sc.stack("何回はらうのか", 35, "四角ひとつで12回はらう", "35年で420回",
                      BADGE, BRAND, cols=7),
    "goukei1": kaeshi(ia=INT_VAR),
    "risoku1": kaeshi(ia=INT_VAR, note="利息 571万円"),
    "ginko": kaeshi(ia=INT_VAR, note="571万円は銀行へ"),
    "toi": sc.quiz("金利は1つではない", "変わらない金利だと", "いくらになる?", "", BADGE, BRAND),
    "kinri2": sc.card("35年ずっと同じなら", "年3.14%", "(2026年7月・フラット35の最頻金利)",
                      BADGE, BRAND, main_size=76, head_fs=34),
    "getsu2": sc.bars2("毎月はらう額のちがい",
                       ("年1.025%", 8.5036, "8万5036円"),
                       ("年3.14%", 11.7812, "11万7812円"),
                       BADGE, BRAND, ymax=13),
    "goukei2": kaeshi(ia=INT_VAR, ib=INT_FIX),
    "risoku2": kaeshi(ia=INT_VAR, ib=INT_FIX, note="利息 1948万円"),
    "sa": kaeshi(ia=INT_VAR, ib=INT_FIX, note="差は1377万円"),
    "shime": sc.hero("値札は3000万円", "払うのは3571万円", BADGE, BRAND,
                     size=84, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行は plan.md 参照:
#   入口=家(専門語ではない。買う予定がなくても値段を知っている)
#   予想「3000万円の家なら3000万円払う」→ 結論「3571万円。金利が違うと1377万円変わる」
#   オチ=実害(571万円が銀行のもうけ)+ 見方の変更(家の値段は金利でも決まる)
UNITS = [
    Unit("nazo", "3000万円の家。でも払うのは3571万円。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("kariru", "まず、家を買う人はお金を借りる。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("loan", "その借金が、住宅ローンなのだ。", anim=1.2, speed=1.15),
    Unit("gaku", "その3000万円を、35年で借りる。", anim=1.4, speed=1.15),
    Unit("risoku", "すると借りたお金に、利息がつくのだ。", anim=1.4, speed=1.15),
    Unit("toha", "利息とは、借りるお礼のお金のこと。", anim=1.4, speed=1.15),
    Unit("wariai", "その割合が、金利なのだ。", anim=1.2, speed=1.15),
    Unit("kinri1", "その金利は、いま年1.025%ほど。", anim=1.4, speed=1.15),
    Unit("getsu1", "すると毎月、8万5036円をはらう。", anim=1.4, speed=1.15),
    Unit("kaisu", "これを35年、420回くり返すのだ。", anim=1.6, speed=1.15),
    Unit("goukei1", "その合計が、最初の3571万円。", anim=1.4, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("risoku1", "つまり利息が、571万円なのだ。", anim=1.4, speed=1.15),
    Unit("ginko", "その571万円は、銀行のもうけになる。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("toi", "でも、変わらない金利もあるのだ。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("kinri2", "その金利だと、いま年3.14%。", anim=1.4, speed=1.15),
    Unit("getsu2", "その場合、毎月11万7812円。", anim=1.4, speed=1.15),
    Unit("goukei2", "するとその合計は、4948万円。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("risoku2", "つまり利息が、1948万円なのだ。", anim=1.4, speed=1.15),
    Unit("sa", "同じ家なのに、その差は1377万円。", anim=1.6, face="surprised",
         speed=1.1, intonation=1.2),
    Unit("shime", "家の値段は、金利でも決まるのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S013.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
