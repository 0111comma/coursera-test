#!/usr/bin/env python3
"""S014: 銀行に100万円を1年置いてつく利息より、ATM手数料のほうが多い。

企画書は plan.md。基準作 S011 の8行を埋めてから作った。

P-0(persona.md): ショートは選ばれない。興味ゼロの人に押し込まれる。
入口は「銀行」= 口座を持っていない人がいない物。専門語では始めない(F5)。

図の型(figure-forms.md):
- 主役は「もらえる額」と「払う額」の高さくらべ → 固有シーン zandaka()。
  左の棒は1年の利息4000円。上の灰色が税金、下の金色が手取り。
  手取りの高さに水平線を1本引いておき、右にATM手数料の棒を立てると、
  その線を越える形になる。「越えた」ことが線と棒の位置だけで分かる
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
BADGE = "100万円・1年・年0.4%で計算"

GROSS, TAX, NET = 4000, 813, 3187      # 利息・税金・手取り(円)
FEE_YEAR = 3960                        # 330円 × 12回
assert NET + TAX == GROSS and FEE_YEAR > NET, "verify.pyと不一致"


def zandaka(split=False, fee=False, note=""):
    """固有シーン: 1年の利息と、1年のATM手数料を同じ縮尺で並べる。

    左=利息4000円。split で上の灰色(税金813円)と下の金色(手取り3187円)に分かれる。
    手取りの高さに水平線を引くので、右のATM手数料の棒が線を越えるかどうかが形で分かる。
    fee が False のあいだ右の棒は出さない(図を一度に完成させない・G4)。
    """
    Y0 = 0.560
    HMAX = 0.200
    VMAX = GROSS

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "1年でもらう額と、1年で払う額", ha="center",
                 color=INK_2, fontsize=34)
        fig.add_artist(sc.plt.Line2D([0.10, 0.90], [Y0, Y0], transform=fig.transFigure,
                                     color=MUTED, linewidth=1.5, alpha=0.5))
        a = sc.clamp01(t * 1.8)
        h_net = HMAX * (NET if split else GROSS) / VMAX
        fig.patches.append(Rectangle((0.17, Y0), 0.24, h_net, transform=fig.transFigure,
                                     facecolor=GOLD, edgecolor="none", alpha=0.95))
        if split:
            fig.patches.append(Rectangle((0.17, Y0 + h_net), 0.24, HMAX * TAX / VMAX * a,
                                         transform=fig.transFigure, facecolor=MUTED_BAR,
                                         edgecolor="none", alpha=0.95))
            # 手取りの高さに1本引いておく。右の棒がここを越えるかどうかが結論
            fig.add_artist(sc.plt.Line2D([0.14, 0.86], [Y0 + h_net, Y0 + h_net],
                                         transform=fig.transFigure, color=MUTED,
                                         linewidth=1.2, alpha=0.45))
        fig.text(0.29, Y0 + HMAX * GROSS / VMAX + 0.032, f"{GROSS}円",
                 ha="center", va="center", color=INK, fontsize=32,
                 path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
        fig.text(0.29, Y0 - 0.032, "1年の利息", ha="center", va="center",
                 color=INK_2, fontsize=27)
        if fee:
            h_fee = HMAX * FEE_YEAR / VMAX * a
            fig.patches.append(Rectangle((0.59, Y0), 0.24, h_fee, transform=fig.transFigure,
                                         facecolor=EMPH, edgecolor="none", alpha=0.95))
            fig.text(0.71, Y0 + HMAX * FEE_YEAR / VMAX + 0.032, f"{FEE_YEAR}円",
                     ha="center", va="center", color=INK, fontsize=32, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(32), fatten=1.8))
            fig.text(0.71, Y0 - 0.032, "1年のATM手数料", ha="center", va="center",
                     color=INK_2, fontsize=27)
        if note:
            fig.text(0.5, 0.487, note, ha="center", va="center", color=EMPH,
                     fontsize=34, alpha=sc.clamp01(t * 2 - 0.4),
                     path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


def herasu(step=0):
    """固有シーン: 手数料の減らし方を、上から順に点灯させるチェックリスト。

    ユーザー指摘(ループ61):「減らすのを止めるって具体的にどうすれば良いのか
    案を出してあげると良いかもね」。締めが行動に変わらないと、見た人は何もできない。
    3つを並べて置き、言った順に色を変える。止めて見れば持ち帰れる形にする(D16)。
    """
    ROWS = ["平日の昼に下ろす", "下ろすのは月1回", "無料の回数を調べる"]
    Y0, DY = 0.760, 0.078

    def painter(fig, t):
        from matplotlib.patches import Rectangle
        fig.text(0.5, 0.905, "手数料の減らし方", ha="center", color=INK_2, fontsize=34)
        for i, row in enumerate(ROWS):
            y = Y0 - i * DY
            on = i < step
            a = sc.clamp01(t * 2.4 - i * 0.2) if on else 0.5
            fig.patches.append(Rectangle((0.155, y - 0.020), 0.040, 0.040,
                                         transform=fig.transFigure,
                                         facecolor=EMPH if on else MUTED_BAR,
                                         edgecolor="none", alpha=0.95 * a + 0.05))
            fig.text(0.225, y, row, ha="left", va="center",
                     color=INK if on else MUTED, fontsize=34, alpha=a,
                     path_effects=stroke_fx(INK, outline=outline_for(34), fatten=1.8)
                     if on else None)
        draw_badge(fig, BADGE)
        draw_footer_brand(fig, BRAND)
    return painter


SCENES = {
    "nazo": sc.hero("その預金の利息", "手数料に負ける", BADGE, BRAND, size=88, sub_fs=42),
    "nazo__cover": sc.cover("100万円、1年でいくら増える?", "3187円",
                            "ATM手数料のほうが多い", "はじめての人向け", BRAND, main_size=150),
    "kinri": sc.card("いまの普通預金は", "年0.4%", "(2026年8月・大手3行)",
                     BADGE, BRAND, main_size=84, head_fs=34),
    "mukashi": sc.card("この水準は", "34年ぶり", "(長いあいだ、ほぼゼロが続いていた)",
                       BADGE, BRAND, main_size=80, head_fs=34),
    "risoku": zandaka(),
    "zei": zandaka(),   # 4000円の棒を出したまま「ここから引かれる」と言う
    "ritsu": sc.card("その税金の率は", "20.315%", "(所得税と住民税の合計)",
                     BADGE, BRAND, main_size=76, head_fs=34),
    "hikare": zandaka(split=True, note="税金で813円"),
    "nokori": zandaka(split=True, note="残るのは3187円"),
    "toi": sc.quiz("ここで比べたいもの", "同じ1年で払う", "ATMの手数料", "", BADGE, BRAND),
    "atm": sc.card("コンビニで下ろすと", "1回330円", "(大手行の時間外の水準)",
                   BADGE, BRAND, main_size=80, head_fs=34,
                   ask="あなたの口座、無料は月何回?"),
    "itsu": sc.card("いつ取られるか", "夜と土日", "(平日の昼だけ安い銀行が多い)",
                    BADGE, BRAND, main_size=80, head_fs=34),
    "tsuki": sc.stack("月に1回だけ使うと", 12, "四角ひとつが1回ぶん", "年に12回",
                      BADGE, BRAND, cols=6),
    "nenkan": zandaka(split=True, fee=True),
    "hikaku": zandaka(split=True, fee=True, note="手数料のほうが多い"),
    "erabenai": sc.card("金利について", "自分では選べない", "(決めるのは銀行と日銀)",
                        BADGE, BRAND, main_size=56, head_fs=34),
    "herasu0": herasu(0),
    "herasu1": herasu(1),
    "herasu2": herasu(2),
    "herasu3": herasu(3),
    "shime": sc.hero("増やす前に", "減らすのを止める", BADGE, BRAND, size=88, sub_fs=44),
}

# ネタ選定ゲート(F1/F3/F4/F5) — 基準作S011の8行は plan.md 参照:
#   入口=銀行(口座を持っていない人がいない。専門語ではない)
#   予想「金利が34年ぶりに上がったなら、置いておけば増える」
#   → 結論「1年の利息3187円より、月1回のATM手数料3960円のほうが多い」
#   オチ=実害(773円のマイナス)+ 見方の変更(金利は選べないが手数料は選べる)
UNITS = [
    Unit("nazo", "銀行に100万円。1年の利息は3187円。", anim=1.0, cover=True,
         se="pop", face="normal", speed=1.05, intonation=1.25),
    Unit("kinri", "その銀行の金利は、年0.4%。", anim=1.2, face="happy",
         speed=1.15, intonation=1.2),
    Unit("mukashi", "これは34年ぶりの高さなのだ。", anim=1.2, face="surprised",
         speed=1.15, intonation=1.2),
    Unit("risoku", "でも100万円だと、1年で4000円。", anim=1.4, speed=1.15),
    Unit("zei", "しかも、そこから税金が引かれる。", anim=1.4, speed=1.15),
    Unit("ritsu", "その税金は、20.315%。", anim=1.4, speed=1.15),
    Unit("hikare", "つまり813円は、税金で消える。", anim=1.4, face="troubled",
         speed=1.15),
    Unit("nokori", "するとその残りが、3187円なのだ。", anim=1.6, speed=1.15),
    # ATMは「エイティーエム」と読まれるので、読み上げだけカナにする(ループ61)
    Unit("toi", "では、ATMの手数料を見てみるのだ。", anim=1.4, face="troubled",
         speed=1.1, intonation=1.2, pause_scale=1.3,
         narration="では、エーティーエムの手数料を見てみるのだ。"),
    Unit("atm", "その手数料は、コンビニで330円。", anim=1.4, speed=1.15),
    Unit("itsu", "これは平日の夜や、土日の場合。", anim=1.4, speed=1.15),
    Unit("tsuki", "その330円を、月1回使うとする。", anim=1.4, speed=1.15),
    Unit("nenkan", "すると1年で、3960円になる。", anim=1.6, face="surprised",
         se="impact", se_at=0.34, speed=1.1, intonation=1.2),
    Unit("hikaku", "その3960円は、利息3187円より多い。", anim=1.6, face="surprised",
         puchun=True, se="don", speed=1.1, intonation=1.2),
    Unit("erabenai", "しかもその金利は、自分では選べない。", anim=1.4, face="troubled",
         speed=1.15),
    # ユーザー指摘(ループ61):「減らすのを止める」だけでは何をすればいいか分からない。
    # 具体案を3つ、チェックリストとして上から点灯させる
    Unit("herasu0", "でもその手数料は、3つの方法で減らせる。", anim=1.4, face="happy",
         speed=1.15, intonation=1.2),
    Unit("herasu1", "まず、下ろすのは平日の昼にする。", anim=1.4, speed=1.15),
    Unit("herasu2", "そして下ろす回数を、月1回にまとめる。", anim=1.4, speed=1.15),
    Unit("herasu3", "さらに口座の、無料回数を調べる。", anim=1.4, speed=1.15),
    Unit("shime", "増やす前に、減らすのを止めるのだ。", anim=1.0, pad=0.15, face="smug",
         speed=1.1, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S014.mp4")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
