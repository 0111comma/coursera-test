#!/usr/bin/env python3
"""S011 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

額面100万円・表面利率1%(毎年1万円)・残存10年の債券を、
市場の利回りが2%になった時点で評価する。
"""
FACE = 1_000_000        # 額面
COUPON_RATE = 0.01      # 表面利率
YEARS = 10              # 残存年数
MARKET_YIELD = 0.02     # 市場の利回り


def price(face, coupon_rate, years, yld):
    """将来の利息と元本を、市場の利回りで割り引いた現在価値。"""
    c = face * coupon_rate
    return sum(c / (1 + yld) ** t for t in range(1, years + 1)) + face / (1 + yld) ** years


def main():
    coupon = FACE * COUPON_RATE
    new_coupon = FACE * MARKET_YIELD
    p = price(FACE, COUPON_RATE, YEARS, MARKET_YIELD)
    loss = FACE - p

    assert coupon == 10_000, coupon
    assert new_coupon == 20_000, new_coupon
    assert round(p) == 910_174, round(p)
    assert round(p / 10_000) == 91, "画面表示の91万円と不一致"
    assert round(loss / 10_000) == 9, "画面表示の9万円と不一致"
    # 金利が変わらなければ価格は額面のまま(逆方向の確認)
    assert round(price(FACE, COUPON_RATE, YEARS, COUPON_RATE)) == FACE

    print("S011 verify: ALL OK")
    print(f"  毎年の利息: {coupon:,.0f}円(表面利率{COUPON_RATE:.0%})")
    print(f"  金利2%の新しい債券の利息: {new_coupon:,.0f}円")
    print(f"  利回り2%で評価した価格: {p:,.0f}円 → 画面は約{p/10_000:.0f}万円")
    print(f"  途中で売ると出る損: {loss:,.0f}円 → 画面は約{loss/10_000:.0f}万円")
    print(f"  満期まで持てば額面{FACE:,.0f}円(発行体が破綻しない場合)")


if __name__ == "__main__":
    main()
