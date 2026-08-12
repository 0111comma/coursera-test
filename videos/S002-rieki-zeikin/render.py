#!/usr/bin/env python3
"""S002: 積立の利益にかかる税金(20.315%)とNISA。shortlibでレンダリングする。

数値はverify.pyと同一の計算式から再計算し、assertで照合してから描画する。
バッジ(打消し表示): #1〜8「利益は仮定・元本保証なし」/#9〜17「2026年8月時点の税制・制度」。
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "production"))
from shortlib import (
    Unit, render_video, require_voicevox, ease_out, ease_in_out, ease_out_back,
    stroke_fx, outline_for, style_axes, draw_badge, draw_footer_brand, draw_glow_text,
    SURFACE, INK, INK_2, MUTED, MUTED_BAR, GRID, BASELINE, SERIES_1, EMPH, GOLD,
)

OUTDIR = Path(__file__).resolve().parent / "output"
BRAND = "数字で見るお金の教科書"

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---- 数値(verify.pyと同一計算) ----
RATE = 0.05
MONTHLY = 10_000

def fv(months: int) -> float:
    r = RATE / 12
    return MONTHLY * ((1 + r) ** months - 1) / r

TAX_RATE = 0.15 + 0.15 * 0.021 + 0.05          # 20.315%
GAIN = 1_710_000                                # 利益(宣言値。厳密値1,710,337も表示は同じ)
PRINCIPAL_MAN = 240
GAIN_MAN = 171
TAX171 = GAIN * TAX_RATE                        # 347,386.5円
NET171 = GAIN - TAX171                          # 1,362,613.5円
TAX_MAN = TAX171 / 10_000                       # 34.74万
NET_MAN = NET171 / 10_000                       # 136.26万
GAIN30 = fv(360) - 3_600_000                    # 4,722,586円
TAX30 = GAIN30 * TAX_RATE                       # 959,393円

assert round(TAX_RATE, 5) == 0.20315
assert round(TAX171 / 1000) == 347 and round(NET_MAN) == 136
assert round((fv(240) - 2_400_000) / 1000) == 1710  # 厳密値1,710,337 ≒ 宣言値171万円
assert round(GAIN30 / 10_000) == 472 and round(TAX30 / 10_000) == 96, "verify.pyと不一致"

TABLE_GAINS = [50, 100, 171, 300, 500]          # 万円
TABLE_TAX = [round(g * 10_000 * TAX_RATE / 1000) / 10 for g in TABLE_GAINS]
assert TABLE_TAX == [10.2, 20.3, 34.7, 60.9, 101.6]


# ---- シーン(painter(fig, t)) ----

def _hero2(fig, main: str, sub: str | None = None, sub_alpha=1.0, size=110):
    draw_glow_text(fig, 0.5, 0.62, main, size)
    if sub:
        fig.text(0.5, 0.52, sub, ha="center", va="center",
                 color=INK_2, fontsize=38, alpha=clamp01(sub_alpha))
    draw_footer_brand(fig, BRAND)


def scene_hero_count(fig, t):
    # 深掘り④: 突発出現(スケールパンチ)+円単位カウントアップ→「34万7千円」
    appear = ease_out_back(clamp01(t * 3.4))
    scale = 0.25 + 0.75 * appear
    v = int(round(TAX171) * ease_out(clamp01(t * 1.15)))
    txt = f"{v // 10_000}万{(v % 10_000) // 1000}千円" if v >= 10_000 else f"{v // 1000}千円"
    draw_glow_text(fig, 0.5, 0.62, txt, 110 * max(scale, 0.05))
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_hero_count__cover(fig, t):
    # サムネ専用構図(⑨)。上=文脈/中央=メイン4字/下=対比。タイトルとは役割分担(⑯)
    fig.text(0.5, 0.795, "税金で消える額", ha="center", va="center", color=INK_2,
             fontsize=46, path_effects=stroke_fx(INK_2, outline=outline_for(46), fatten=1.5))
    draw_glow_text(fig, 0.5, 0.615, "約35万円", 132)
    fig.text(0.5, 0.435, "NISAなら 0円", ha="center", va="center", color=INK,
             fontsize=44, path_effects=stroke_fx(INK, outline=outline_for(44), fatten=2))
    fig.text(0.5, 0.88, "利益は年5%と仮定の計算", ha="center", va="center", color=MUTED, fontsize=24)
    draw_footer_brand(fig, BRAND)


def scene_hero_full(fig, t):
    _hero2(fig, "34万7千円", "積立の利益から引かれる税金", sub_alpha=clamp01(t))
    draw_badge(fig, "利益は仮定・元本保証なし")


# ---- 元本+利益の積み上げバー(#3〜8) ----

def _stack_axes(fig):
    ax = fig.add_axes([0.16, 0.42, 0.68, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(0, 470)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["left"].set_visible(False)
    return ax


def _seg(ax, y0, h, color, alpha=1.0):
    ax.bar([0], [h], bottom=[y0], width=0.85, color=color, alpha=alpha)


def _seg_label(ax, y, text, color=INK, fs=30, alpha=1.0, x=0.55):
    ax.text(x, y, text, ha="left", va="center", color=color, fontsize=fs, alpha=alpha)


def scene_stack_base(fig, t):
    ax = _stack_axes(fig)
    e = ease_in_out(clamp01(t))
    _seg(ax, 0, PRINCIPAL_MAN * e, MUTED_BAR)
    if t > 0.35:
        _seg_label(ax, PRINCIPAL_MAN * e / 2, f"元本 {round(PRINCIPAL_MAN * e)}万円", INK_2)
    fig.text(0.5, 0.90, "月1万円 × 20年", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_stack_gain(fig, t):
    ax = _stack_axes(fig)
    _seg(ax, 0, PRINCIPAL_MAN, MUTED_BAR)
    _seg_label(ax, PRINCIPAL_MAN / 2, "元本 240万円", INK_2)
    e = ease_in_out(clamp01(t))
    g = GAIN_MAN * e
    _seg(ax, PRINCIPAL_MAN, g, GOLD)
    if t > 0.25:
        _seg_label(ax, PRINCIPAL_MAN + g / 2, f"利益 {round(g)}万円", EMPH, fs=32)
    fig.text(0.5, 0.90, "年5%と仮定した場合", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def _stack_full(ax, tax_alpha=0.0, tax_label=None, net_label=None, dim_gain=False):
    _seg(ax, 0, PRINCIPAL_MAN, MUTED_BAR)
    _seg_label(ax, PRINCIPAL_MAN / 2, "元本 240万円", MUTED)
    net = GAIN_MAN - TAX_MAN
    _seg(ax, PRINCIPAL_MAN, GAIN_MAN, GOLD, alpha=0.45 if dim_gain else 1.0)
    if tax_alpha > 0:  # 利益の上部=税の帯
        _seg(ax, PRINCIPAL_MAN + net, TAX_MAN, BASELINE, alpha=tax_alpha)
        if tax_label:
            _seg_label(ax, PRINCIPAL_MAN + net + TAX_MAN / 2, tax_label, EMPH, fs=28)
    if net_label:
        _seg_label(ax, PRINCIPAL_MAN + net / 2, net_label, INK, fs=28)


def scene_stack_tax(fig, t):
    ax = _stack_axes(fig)
    a = clamp01(t * 1.6)
    _stack_full(ax, tax_alpha=a, tax_label="税 約20%" if t > 0.4 else None)
    if t <= 0.4:
        _seg_label(ax, PRINCIPAL_MAN + GAIN_MAN / 2, "利益 171万円", EMPH, fs=32)
    fig.text(0.5, 0.90, "利益には税金がかかる", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_quiz(fig, t):
    fig.text(0.5, 0.90, "クイズ", ha="center", color=INK_2, fontsize=34)
    fig.text(0.5, 0.68, "171万円 × 約20%", ha="center", va="center", color=INK, fontsize=46,
             path_effects=stroke_fx(INK, outline=outline_for(46), fatten=2))
    a = clamp01(t * 2 - 0.4)
    draw_glow_text(fig, 0.5, 0.52, "?", 110 * max(ease_out_back(a), 0.05))
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_answer(fig, t):
    ax = _stack_axes(fig)
    _stack_full(ax, tax_alpha=1.0, tax_label=f"税 -34万7千円" if t > 0.2 else None)
    fig.text(0.5, 0.90, "正解", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_tedori(fig, t):
    ax = _stack_axes(fig)
    _stack_full(ax, tax_alpha=1.0, tax_label="税 -34万7千円",
                net_label="手取り 136万円" if t > 0.3 else None)  # 右端見切れ防止で短縮
    fig.text(0.5, 0.90, "手取りはこうなる", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_breakdown(fig, t):
    # 20.315%の内訳を行形式で(0.315%は比例バーだと見えないため)
    rows = [("所得税", "15%", 15 / 20.315), ("住民税", "5%", 5 / 20.315),
            ("復興特別所得税", "0.315%", 0.03)]
    fig.text(0.5, 0.90, "20.315%の内訳", ha="center", color=INK_2, fontsize=34)
    for i, (name, val, w) in enumerate(rows):
        a = clamp01(t * 3 - i * 0.55)
        y = 0.70 - i * 0.085
        fig.text(0.40, y, name, ha="right", va="center", color=INK_2, fontsize=30, alpha=a)
        fig.add_artist(FancyBboxPatch(
            (0.44, y - 0.016), max(0.36 * w * ease_out(a), 0.012), 0.032,
            boxstyle="round,pad=0.004", transform=fig.transFigure,
            facecolor=GOLD, edgecolor="none", alpha=a))
        fig.text(0.84, y, val, ha="right", va="center", color=INK, fontsize=30, alpha=a)
    a2 = clamp01(t * 2 - 1.1)
    fig.text(0.5, 0.42, "合計 20.315%", ha="center", va="center", color=EMPH, fontsize=44,
             alpha=a2, path_effects=stroke_fx(EMPH, outline=outline_for(44), fatten=2))
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


# ---- 課税口座 vs NISA(#10〜11) ----

def _nisa_axes(fig):
    ax = fig.add_axes([0.14, 0.42, 0.72, 0.42])
    style_axes(ax)
    ax.grid(False)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 200)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["課税口座", "NISA"])
    ax.tick_params(axis="x", labelsize=30, colors=INK_2)
    return ax


def _nisa_bars(ax, t_nisa=1.0, dim_left=False, label_left=True, nisa_label=True):
    net = GAIN_MAN - TAX_MAN
    la = 0.45 if dim_left else 1.0
    ax.bar([0], [net], width=0.5, color=GOLD, alpha=la)
    ax.bar([0], [TAX_MAN], bottom=[net], width=0.5, color=BASELINE, alpha=la)
    if label_left:
        ax.text(0, net + TAX_MAN + 8, "税 -34万7千円", ha="center", color=INK_2, fontsize=26, alpha=la)
    e = ease_in_out(clamp01(t_nisa))
    h = GAIN_MAN * e
    ax.bar([1], [h], width=0.5, color=GOLD)
    if nisa_label and t_nisa > 0.2:
        ax.text(1, h + 8, f"{round(h)}万円", ha="center", color=INK, fontsize=30)


def scene_nisa_zero(fig, t):
    ax = _nisa_axes(fig)
    _nisa_bars(ax, t_nisa=t)
    fig.text(0.5, 0.90, "同じ利益171万円でも", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


def scene_marugoto(fig, t):
    ax = _nisa_axes(fig)
    _nisa_bars(ax, t_nisa=1.0, dim_left=True, nisa_label=False)
    a = clamp01(t * 2)
    # y=GAIN+6: バッジ(下端y=0.810)の下に収める(+26だと重なって隠れる)
    ax.text(1, GAIN_MAN + 6, "まるごと 171万円", ha="center", color=EMPH, fontsize=28, alpha=a)
    fig.text(0.5, 0.90, "同じ利益171万円でも", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


def scene_chishiki(fig, t):
    fig.text(0.5, 0.90, "手取りの差を生むのは?", ha="center", color=INK_2, fontsize=34)
    fig.text(0.34, 0.68, "運用の腕", ha="center", color=INK, fontsize=48,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=2))
    fig.text(0.72, 0.68, "×", ha="center", va="center", color=MUTED, fontsize=64)
    a = clamp01(t * 2 - 0.6)
    fig.text(0.34, 0.53, "制度の知識", ha="center", color=EMPH, fontsize=52, alpha=a,
             path_effects=stroke_fx(EMPH, outline=outline_for(52), fatten=2))
    fig.text(0.72, 0.53, "◯", ha="center", va="center", color=EMPH, fontsize=64, alpha=a)
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


def scene_if472(fig, t):
    fig.text(0.5, 0.90, "もし30年つづけたら?", ha="center", color=INK_2, fontsize=34)
    draw_glow_text(fig, 0.5, 0.62, f"利益 {round(GAIN30 / 10_000 * ease_out(clamp01(t)))}万円", 84)
    fig.text(0.5, 0.50, "(元本360万円・年5%と仮定)", ha="center", va="center",
             color=MUTED, fontsize=26, alpha=clamp01(t * 2 - 0.8))
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_tax96(fig, t):
    _hero2(fig, "-96万円", None, size=104)
    a = clamp01(t * 2 - 0.5)
    fig.text(0.5, 0.50, "NISAなら 0円", ha="center", va="center", color=EMPH, fontsize=40,
             alpha=a, path_effects=stroke_fx(EMPH, outline=outline_for(40), fatten=2))
    fig.text(0.5, 0.90, "472万円にかかる税金", ha="center", color=INK_2, fontsize=34)
    draw_badge(fig, "2026年8月時点の税制・制度")


def scene_waku(fig, t):
    _hero2(fig, "1800万円", "1人あたりの非課税枠(生涯)", sub_alpha=clamp01(t * 2 - 0.4), size=100)
    draw_badge(fig, "2026年8月時点の税制・制度")


def scene_hayami(fig, t):
    fig.text(0.5, 0.88, "利益にかかる税金 早見表", ha="center", color=INK, fontsize=38,
             path_effects=stroke_fx(INK, outline=outline_for(38), fatten=2))
    fig.patches.append(FancyBboxPatch(
        (0.095, 0.40), 0.73, 0.38, boxstyle="round,pad=0.012",
        transform=fig.transFigure, fill=False, edgecolor=INK_2,
        linewidth=2.5, linestyle=(0, (6, 5)),
    ))
    fig.text(0.115, 0.795, "スクショ用", ha="left", color=EMPH, fontsize=24, alpha=clamp01(t))
    fig.text(0.52, 0.735, "課税なら", ha="center", color=MUTED, fontsize=28)
    fig.text(0.76, 0.735, "NISAなら", ha="center", color=MUTED, fontsize=28)
    for i, (g, tax) in enumerate(zip(TABLE_GAINS, TABLE_TAX)):
        y = 0.675 - i * 0.055
        fig.text(0.24, y, f"利益{g}万", ha="center", color=MUTED, fontsize=26)
        fig.text(0.52, y, f"-{tax}万", ha="center", color=INK, fontsize=30)
        fig.text(0.76, y, "0円", ha="center", color=INK, fontsize=30)
    fig.text(0.46, 0.425, "税率20.315%で計算(2026年8月時点)", ha="center", color=MUTED, fontsize=24)
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


def scene_chips(fig, t):
    fig.text(0.5, 0.76, "NISA、もう使ってる?", ha="center", color=INK, fontsize=52,
             path_effects=stroke_fx(INK, outline=outline_for(52), fatten=3))
    chips = ["使ってる", "課税口座のみ", "これから", "初めて知った"]
    for i, c in enumerate(chips):
        a = clamp01(t * 3.2 - i * 0.7)
        if a <= 0:
            continue
        x = 0.29 + (i % 2) * 0.42
        y = 0.66 - (i // 2) * 0.10
        fig.text(x, y, c, ha="center", va="center", color=INK, fontsize=34, alpha=a,
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=SURFACE,
                           edgecolor=EMPH, linewidth=2.5, alpha=a))
    fig.text(0.5, 0.40, "▼ コメントで教えて ▼", ha="center", va="center",
             color=MUTED, fontsize=30, alpha=clamp01(t * 2 - 1.0))
    draw_badge(fig, "2026年8月時点の税制・制度")
    draw_footer_brand(fig, BRAND)


def scene_kei(fig, t):
    # H1/H3: 96万の直後の過剰リアクション(関連ユーモア: 金額の翻訳を兼ねる)
    fig.text(0.5, 0.90, "96万円の大きさ", ha="center", color=INK_2, fontsize=34)
    a = clamp01(t * 2)
    fig.text(0.5, 0.62, "軽自動車ほぼ1台", ha="center", va="center", color=INK,
             fontsize=48 * max(ease_out_back(a), 0.05), alpha=a,
             path_effects=stroke_fx(INK, outline=outline_for(48), fatten=2))
    fig.text(0.5, 0.51, "が税金で消える計算", ha="center", va="center",
             color=EMPH, fontsize=34, alpha=clamp01(t * 2 - 0.8),
             path_effects=stroke_fx(EMPH, outline=outline_for(34), fatten=2))
    draw_badge(fig, "利益は仮定・元本保証なし")
    draw_footer_brand(fig, BRAND)


def scene_loop_back(fig, t):
    # E5/E6: 冒頭と同構図の34万7千円でループ(→「34万7千円。」)
    _hero2(fig, "34万7千円", "積立の利益から引かれる税金", sub_alpha=clamp01(t * 2))
    draw_badge(fig, "利益は仮定・元本保証なし")


SCENES = {
    "hero_count": scene_hero_count,
    "hero_count__cover": scene_hero_count__cover,
    "hero_full": scene_hero_full,
    "stack_base": scene_stack_base,
    "stack_gain": scene_stack_gain,
    "stack_tax": scene_stack_tax,
    "quiz": scene_quiz,
    "answer": scene_answer,
    "tedori": scene_tedori,
    "breakdown": scene_breakdown,
    "nisa_zero": scene_nisa_zero,
    "marugoto": scene_marugoto,
    "chishiki": scene_chishiki,
    "if472": scene_if472,
    "tax96": scene_tax96,
    "waku": scene_waku,
    "hayami": scene_hayami,
    "kei": scene_kei,
    "chips": scene_chips,
    "loop_back": scene_loop_back,
}

# Given-New: 各文は動画内で導入済みの語+新情報1つ(タイトル・S001視聴に依存しない)
UNITS = [
    Unit("hero_count", "【34万7千円】。", anim=1.2, cover=True, se="pop",
         speed=1.05, intonation=1.2, pitch=0.0),
    Unit("hero_full", "積立の利益から、引かれる税金。", anim=0.8, speed=1.2),
    Unit("stack_base", "月1万円を20年、積み立てたとする。", anim=1.8, speed=1.15),
    Unit("stack_gain", "年5%仮定なら、利益は【171万円】。", anim=2.0, speed=1.15, intonation=1.15),
    Unit("stack_tax", "でも利益には、【約20%】の税金がかかる。", anim=1.8,
         speed=1.15, intonation=1.15, pitch=-0.04),
    Unit("quiz", "171万の20%…【いくら】だと思う?", anim=1.4,
         speed=1.15, intonation=1.25),
    Unit("answer", "答えは、【34万7千円】なのだ。", anim=1.2,
         puchun=True, se="impact", se_at=0.34,
         speed=1.12, intonation=1.2, pitch=-0.06, pause_scale=1.25),
    Unit("tedori", "手取りは、【136万円】。", anim=1.4,
         speed=1.15, intonation=1.1, pitch=-0.06),
    Unit("breakdown", "正確には、【20.315%】。", anim=2.0, speed=1.15, intonation=1.1),
    Unit("nisa_zero", "でも【NISA】なら、税金ゼロ。", anim=1.8,
         narration="でもニーサなら、税金ゼロ。",  # エヌアイエスエー読み回避(kana照合済み)
         speed=1.15, intonation=1.25, pitch=0.0),
    Unit("marugoto", "同じ利益が、まるごと【手取り】に。", anim=1.2, speed=1.15, intonation=1.2),
    # E2: エスカレーション(30年ケースの方が損失が大きい)をピークの前へ移動
    Unit("if472", "30年で、利益【472万円】なら?", anim=1.4, speed=1.2, intonation=1.25),
    Unit("tax96", "税金は、【約96万円】なのだ。", anim=1.2, se="don",
         speed=1.12, intonation=1.2, pitch=-0.04, pause_scale=1.2),
    # H1/H3: 衝撃数字の直後に過剰リアクション(金額の翻訳=関連ユーモア)
    Unit("kei", "軽自動車ほぼ1台が、消えるのだ。", anim=1.2,
         speed=1.1, intonation=1.3, pitch=0.02),
    # ピーク(感情の頂点)を尾でなくここに(E1: 尺の70〜85%)
    Unit("chishiki", "腕の差じゃなく、【知識の差】なのだ。", anim=1.2, pad=0.25,
         speed=1.1, intonation=1.2, pitch=-0.04),
    Unit("hayami", "【早見表】で、税額を見るのだ。", anim=0.8, se="pop", speed=1.2),
    # E7: 質問はループ点の手前+N1(あなた)
    Unit("chips", "あなたはもう、【NISA】使ってる?", anim=1.4, pad=0.15,
         narration="あなたはもう、ニーサ使ってる?",
         speed=1.15, intonation=1.2),
    # E5/E6: ナラティブループ(→冒頭「34万7千円。」)
    Unit("loop_back", "知らないままだと、この税金なのだ。", anim=0.8, pad=0.1,
         speed=1.15, intonation=1.15, pitch=-0.03),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, "S002.mp4")
    print(f"engine: {result['engine']}")
    print(f"total: {result['total_sec']:.1f}s")
    print(f"mp4: {result['mp4']}")
