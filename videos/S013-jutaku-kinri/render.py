#!/usr/bin/env python3
"""S013: 変動と固定、どっちが得だったのか。数値は verify.py と照合。

企画書は plan.md。ユーザー指摘(ループ62):
  「結局人が気にしたいのって、どっちが得して、どっちが損でっていう話じゃん」
仕組みと差額で終わらせず、**過去の事実 → いま起きていること → 分岐点** まで出す。

P-0(persona.md): ショートは選ばれない。入口は「家」= 誰でも値段を知っている物(F5)。

図の型(figure-forms.md):
- 主役は「借りた額の上に、利息が乗る」比 → 固有シーン kaeshi()。
  下に借りた3000万円、その上に利息を積む。2つの金利を同じ縮尺で並べる
- どっちを選んでいるか → 数えられるブロック(4個のうち3個)
- 金利の水準の推移 → 共通の底からの棒2本(昔8.5% と いま1.025%)
- 分岐点 → kaeshi() の変動側を伸ばして固定と同じ高さにする
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

# 「変動」と「固定」の動き方のちがいを見せるためだけの模式線(ループ60)。
# 将来の金利を予想する図ではないので、縦軸には目盛りを置かず、値も画面に出さない。
# 上下に振れるか/一直線かという**形**だけが情報。
# 変動の線は固定の線を何度も横切らせる。理由は2つ:
#   1. 固定の線に重なって隠れないようにするため(重ねると「変動だけの図」に見える)
#   2. 変動が固定より高くなることも低くなることもある、と形で示すため。
#      どちらかの側に寄せると「変動のほうが得」という主張になってしまう(戦略§6)
# 色は EMPH(金) と INK(オフホワイト)。GOLD と EMPH では同系色で線が見分けられなかった。
HENDO = [1.0, 1.5, 1.1, 2.1, 2.9, 2.3, 3.1, 1.8, 2.7, 1.4, 2.4]
KOTEI = [2.2] * len(HENDO)
XLAB = ["借りた時"] + [""] * (len(HENDO) - 2) + ["35年後"]


def kaeshi(ia=None, ib=None, note="", foot_a="変動 1.025%"):
    """固有シーン: 借りた3000万円の上に、利息を積む。

    下の灰色=借りたお金(どちらの金利でも同じ3000万円)。上の金色=利息。
    左が変動、右が固定。同じ縮尺なので、棒の高さの差がそのまま金額の差になる。
    ia/ib が None のあいだは、その棒はまだ出さない(図を一度に完成させない・G4)。
    foot_a は左の棒の足元。分岐点の場面では「5年後に3.83%」に差し替える。
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

        bar(0.17, ia, foot_a, True)
        bar(0.59, ib, "固定 3.14%", ib is not None)
        if note:
            fig.text(0.5, 0.487, note, ha="center", va="center", color=EMPH,
                     fontsize=34, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("変動金利か、固定金利か", "1377万円の差", BADGE, BRAND, size=92, sub_fs=44),
    "nazo__cover": sc.cover("変動金利と固定金利、どっちが得?", "1377万円",
                            "同じ家なのに、この差", "はじめての人向け", BRAND, main_size=150),
    "shurui": sc.card("住宅ローンの金利", "2つの種類", "(途中で変わるか、変わらないか)",
                      BADGE, BRAND, main_size=72, head_fs=34),
    "hendo": sc.lines2("金利の動き方(イメージ)",
                       [("変動金利", HENDO, EMPH)],
                       BADGE, BRAND, ymin=0.7, ymax=3.4, xlabels=XLAB),
    "kotei": sc.lines2("金利の動き方(イメージ)",
                       [("変動金利", HENDO, EMPH), ("固定金利", KOTEI, INK)],
                       BADGE, BRAND, ymin=0.7, ymax=3.4, xlabels=XLAB),
    "kinri1": sc.card("いまの変動金利は", "年1.025%", "(2026年8月・大手行の水準)",
                      BADGE, BRAND, main_size=76, head_fs=34,
                      ask="あなたなら、どっちを選ぶ?"),
    "yasui": kaeshi(ia=INT_VAR, ib=INT_FIX, note="差はここ"),
    "agaru": sc.card("ただし変動金利は", "途中で上がる", "(そこが固定とのちがい)",
                     BADGE, BRAND, main_size=62, head_fs=34),
    "kinri2": sc.card("いまの固定金利は", "年3.14%", "(2026年7月・フラット35の最頻金利)",
                      BADGE, BRAND, main_size=76, head_fs=34),
    "kariru": sc.card("借りかたの条件", "35年で返す", "(元利均等・ボーナス払いなし)",
                      BADGE, BRAND, main_size=54, head_fs=34),
    "goukei1": kaeshi(ia=INT_VAR),
    "goukei2": kaeshi(ia=INT_VAR, ib=INT_FIX),
    "sa": kaeshi(ia=INT_VAR, ib=INT_FIX, note="差は1377万円"),
    # 「どこまで上がれば逆転するか」だけを1本の鎖で追う(ループ64)
    "toi": sc.quiz("では、あなたの場合", "変動が1%上がると", "毎月いくら?", "", BADGE, BRAND),
    "maitsuki": sc.bars2("毎月はらう額",
                         ("いまの変動金利", 8.5036, "いまの額"),
                         ("1%上がると", 9.9764, "ふえた額"),
                         BADGE, BRAND, gap="+1万4728円", ymax=11),
    "gyakuten": sc.quiz("ここが知りたい所", "どこまで上がれば", "逆転する?", "", BADGE, BRAND),
    "gonen": sc.stack("まず考える時点", 5, "四角5つで5年ぶん", "借りてから5年",
                      BADGE, BRAND, cols=5),
    "bunki": kaeshi(ia=INT_VAR, ib=INT_FIX, foot_a="5年後に3.83%"),
    "narabu": kaeshi(ia=INT_FIX, ib=INT_FIX, foot_a="5年後に3.83%"),
    "narabu2": kaeshi(ia=INT_FIX, ib=INT_FIX, foot_a="5年後に3.83%",
                      note="ここで固定と同じ"),
    "wakare": sc.card("逆転する金利", "年3.83%", "(5年後に上がって、そのまま続いた場合)",
                      BADGE, BRAND, main_size=80, head_fs=34),
    "shime": sc.hero("変動金利は今の安さ", "固定金利は先の安心", BADGE, BRAND, size=88, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行は plan.md 参照:
#   入口=家(専門語ではない。買う予定がなくても値段を知っている)
#   予想「どっちでも似たようなものでしょ」→ 結論「1377万円ちがう。過去は変動が正解だったが、
#        2024年から上がりはじめた。5年後に3.83%まで上がれば固定と並ぶ」
#   オチ=実害(1%で毎月1万4728円)+ 見方の変更(変動は今の安さ、固定は先の安心を買っている)
UNITS = [
    # 専門語は最後まで略さずフルネームで呼ぶ(ループ65のユーザー指摘・W7)。
    # 尺は「変動と固定」に縮めて捻出しない。足りないならビートを削る(W8)
    Unit("nazo", "3000万円の家。金利で1377万円ちがう。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("shurui", "住宅ローンの金利は、変動金利と固定金利。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("kotei", "変動金利は変わり、固定金利は変わらない。", anim=1.6, speed=1.15),
    Unit("kinri1", "その変動金利は、いま年1.025%。", anim=1.4, speed=1.15),
    Unit("kinri2", "一方の固定金利は、年3.14%。", anim=1.4, speed=1.15),
    Unit("kariru", "これで3000万円を、35年借りるとする。", anim=1.4, speed=1.15),
    Unit("goukei1", "すると変動金利なら、3571万円。", anim=1.4, speed=1.15),
    Unit("goukei2", "一方の固定金利は、4948万円。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("sa", "その差が、さっきの1377万円。", anim=1.4, face="surprised",
         speed=1.1, intonation=1.2),
    Unit("yasui", "つまりここまでは、変動金利が安い。", anim=1.4, speed=1.15),
    Unit("agaru", "でも変動金利は、途中で上がるのだ。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("toi", "その変動金利が1%上がると?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("maitsuki", "すると毎月、1万4728円ふえる。", anim=1.4, face="surprised",
         speed=1.15),
    Unit("gyakuten", "では、どこまで上がれば逆転する?", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3),
    Unit("gonen", "まず5年後を、考えてみるのだ。", anim=1.4, speed=1.15),
    Unit("bunki", "そこで3.83%まで上がったら?", anim=1.4, speed=1.15),
    Unit("narabu2", "その総額が、固定金利と同じ4948万円に。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("wakare", "だから3.83%が、分かれ目なのだ。", anim=1.4, face="smug",
         speed=1.15),
    Unit("shime", "変動金利は今の安さ、固定金利は先の安心。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S013.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
