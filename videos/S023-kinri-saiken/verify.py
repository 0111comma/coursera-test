#!/usr/bin/env python3
"""S023: 金利と債券価格が逆に動くことの検証。

例: 額面100万円・年利1%(毎年1万円)・残り10年の債券。
    市場金利(利回り)が1%→3%に上がったとき、この債券はいくらで売れるか。

価格 = 毎年の利息と満期の額面を、市場金利で割り引いた現在価値の合計。
出典: 財務省「国債について」/日本証券業協会「債券の基礎知識」(plan.md参照)
"""

GAKUMEN = 1_000_000     # 額面
COUPON = 0.01           # 表面利率(この債券が毎年払う利息の率)
NENSU = 10              # 残りの年数


def kakaku(riMawari: float) -> float:
    """市場金利が riMawari のときの、この債券の理論価格。"""
    rishi = GAKUMEN * COUPON
    genzai = sum(rishi / (1 + riMawari) ** t for t in range(1, NENSU + 1))
    return genzai + GAKUMEN / (1 + riMawari) ** NENSU


def main():
    rishi = GAKUMEN * COUPON
    assert rishi == 10_000                        # この債券の利息は毎年1万円

    # 市場金利が表面利率と同じなら、価格は額面ちょうど
    assert round(kakaku(0.01)) == GAKUMEN

    # 金利が3%に上がると値下がりする
    p3 = kakaku(0.03)
    assert round(p3) == 829_396, round(p3)
    assert round(p3 / 10_000) == 83               # 動画表記「約83万円」
    nesage = GAKUMEN - p3
    assert round(nesage / 10_000) == 17           # 値下がり 約17万円
    assert p3 < GAKUMEN                           # 金利↑ → 価格↓

    # 逆に金利が下がると値上がりする(方向の確認)
    assert kakaku(0.005) > GAKUMEN

    # 直感の説明: 新しい債券との利息差は毎年2万円、10年で20万円
    shin_rishi = GAKUMEN * 0.03
    assert shin_rishi == 30_000
    assert (shin_rishi - rishi) * NENSU == 200_000
    # 実際の値下がり(17万円)は、その差を現在価値に割り引いた分だけ小さい
    assert nesage < (shin_rishi - rishi) * NENSU

    # 満期まで持てば額面は戻る(発行体が約束を果たす限り)
    assert GAKUMEN == 1_000_000

    print("S023 verify: ALL OK")
    print(f"  額面{GAKUMEN:,}円・年利{COUPON:.0%}(毎年{rishi:,}円)・残り{NENSU}年")
    print(f"  市場金利1% → 価格 {kakaku(0.01):,.0f}円")
    print(f"  市場金利3% → 価格 {p3:,.0f}円(約{nesage:,.0f}円の値下がり)")
    print(f"  新しい債券の利息 {shin_rishi:,.0f}円 との差は毎年{shin_rishi-rishi:,.0f}円")


if __name__ == "__main__":
    main()
