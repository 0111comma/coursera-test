#!/usr/bin/env python3
"""S016 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

PER = 株価 ÷ 1株あたりの利益。「その会社の利益の何年分の値段か」を表す。
"""
PRICE = 1_500.0     # 株価
EPS = 100.0         # 1株あたりの年間利益
PRICE_B = 3_000.0   # 別の会社の株価(同じ利益)


def per(price, eps):
    return price / eps


def main():
    a = per(PRICE, EPS)
    b = per(PRICE_B, EPS)

    assert a == 15.0, a
    assert b == 30.0, b
    # 利益が2倍に増えれば、株価が同じでもPERは半分になる
    assert per(PRICE, EPS * 2) == 7.5, per(PRICE, EPS * 2)
    # PER15倍を回収するのに必要な利益の合計は、ちょうど株価
    assert EPS * a == PRICE, EPS * a

    print("S016 verify: ALL OK")
    print(f"  株価{PRICE:,.0f}円 ÷ 1株利益{EPS:,.0f}円 = PER {a:.0f}倍(利益{a:.0f}年分)")
    print(f"  同じ利益で株価{PRICE_B:,.0f}円なら = PER {b:.0f}倍(利益{b:.0f}年分)")
    print(f"  利益が2倍の{EPS * 2:,.0f}円に増えると、株価{PRICE:,.0f}円のままでもPERは{per(PRICE, EPS * 2)}倍")
    print(f"  {EPS:,.0f}円 × {a:.0f}年 = {EPS * a:,.0f}円 = 株価")


if __name__ == "__main__":
    main()
