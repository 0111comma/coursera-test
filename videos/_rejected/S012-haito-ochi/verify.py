#!/usr/bin/env python3
"""S012 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

株価3000円・1株あたり配当30円の例(すべて仮の数字)。
"""
PRICE = 3000        # 権利付最終日の株価
DIVIDEND = 30       # 1株あたりの配当
TAX = 0.20315       # 上場株式等の配当にかかる源泉徴収(所得税15.315%+住民税5%)


def main():
    ex_price = PRICE - DIVIDEND                 # 権利落ち日の理論上の株価
    net = DIVIDEND * (1 - TAX)                  # 配当の手取り
    total = ex_price + net                      # 受け取った直後の合計
    diff = PRICE - total

    assert ex_price == 2970, ex_price
    assert round(net, 1) == 23.9, net
    assert round(total, 1) == 2993.9, total
    assert round(diff) == 6, diff
    # NISA口座(非課税)なら合計は元の株価と同じ
    assert round(ex_price + DIVIDEND) == PRICE

    print("S012 verify: ALL OK")
    print(f"  権利付最終日の株価: {PRICE:,}円 / 配当: {DIVIDEND}円")
    print(f"  権利落ち日の理論上の株価: {ex_price:,}円")
    print(f"  配当の手取り: {net:.2f}円 → 画面は{net:.1f}円(税{TAX:.3%})")
    print(f"  受け取った直後の合計: {total:.2f}円 → 画面は{total:.1f}円")
    print(f"  もとの株価との差: 約{diff:.0f}円 少ない")
    print(f"  NISA口座(非課税)なら: {ex_price + DIVIDEND:,}円 で変わらない")


if __name__ == "__main__":
    main()
