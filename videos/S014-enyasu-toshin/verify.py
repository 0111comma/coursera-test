#!/usr/bin/env python3
"""S014 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

為替ヘッジなしの外国株投信は「現地の値段 × 為替」で円の値段が決まる。
現地が1円も動かなくても、為替だけで円建ての評価額は動く。
"""
SHARES_USD = 100.0     # 現地の値段(ドル)
RATE0 = 150.0          # 買ったときの為替
RATE_YASU = 170.0      # 円安になった場合
RATE_TAKA = 130.0      # 円高になった場合


def yen(usd, rate):
    return usd * rate


def main():
    base = yen(SHARES_USD, RATE0)
    yasu = yen(SHARES_USD, RATE_YASU)
    taka = yen(SHARES_USD, RATE_TAKA)

    assert base == 15_000, base
    assert yasu == 17_000, yasu
    assert taka == 13_000, taka
    assert round((yasu / base - 1) * 1000) / 10 == 13.3, (yasu / base - 1)
    assert round((taka / base - 1) * 1000) / 10 == -13.3, (taka / base - 1)
    # 現地が10%下がっても、為替が同じだけ円安なら円建てはほぼ変わらない
    both = yen(SHARES_USD * 0.90, RATE0 / 0.90)
    assert round(both) == 15_000, both

    print("S014 verify: ALL OK")
    print(f"  買ったとき: {SHARES_USD:.0f}ドル × {RATE0:.0f}円 = {base:,.0f}円")
    print(f"  円安({RATE_YASU:.0f}円): {yasu:,.0f}円 → {(yasu / base - 1):+.1%}(現地は0%)")
    print(f"  円高({RATE_TAKA:.0f}円): {taka:,.0f}円 → {(taka / base - 1):+.1%}(現地は0%)")
    print(f"  現地が10%下がっても、同じだけ円安なら円建ては {both:,.0f}円 で変わらない")


if __name__ == "__main__":
    main()
