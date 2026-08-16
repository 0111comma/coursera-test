#!/usr/bin/env python3
"""S011 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

NISA口座の損失は、他の口座の利益と相殺(損益通算)できない。
同じ損をしても、その損がNISAで出たかどうかで、払う税金が変わる。
"""
PROFIT = 500_000     # 普通の口座(特定口座)で出た利益
LOSS = 500_000       # 同じ年に出た損失
TAX = 0.20315        # 上場株式等の利益にかかる税(所得税15.315%+住民税5%)


def tax_on(amount):
    return amount * TAX


def main():
    # 1. どちらも普通の口座 → 損と利益を足し引きできる(損益通算)
    both_normal = max(PROFIT - LOSS, 0)
    tax_normal = tax_on(both_normal)

    # 2. 損のほうがNISA → NISAの損は税の計算に入らない
    tax_nisa = tax_on(PROFIT)

    assert round(tax_on(PROFIT)) == 101_575, round(tax_on(PROFIT))
    assert round(tax_on(PROFIT) / 10_000) == 10, "画面表示の約10万円と不一致"
    assert both_normal == 0 and tax_normal == 0
    assert round(tax_nisa - tax_normal) == 101_575

    print("S011 verify: ALL OK")
    print(f"  普通の口座の利益: {PROFIT:,}円 / 同じ年の損: {LOSS:,}円")
    print(f"  どちらも普通の口座: 差し引き{both_normal:,}円 → 税金 {tax_normal:,.0f}円")
    print(f"  損がNISAの場合   : 利益{PROFIT:,}円にそのまま課税 → 税金 {tax_nisa:,.0f}円")
    print(f"  差: {tax_nisa - tax_normal:,.0f}円(画面は約{ (tax_nisa - tax_normal)/10_000:.0f}万円)")
    print(f"  税率 {TAX:.3%}(所得税15.315% + 住民税5%)")


if __name__ == "__main__":
    main()
