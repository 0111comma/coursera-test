#!/usr/bin/env python3
"""S019 の数値検証。動画内の数字はすべてここで再計算する。

問い: 積立の手数料が0.1%と1.0%で、20年後にいくら違うのか。
前提(すべて仮定):
  毎月3万円 / 20年 / 増える率は年5%と仮定
  手数料は毎年の残高から引かれるので、実際に増える率は「5% − 手数料」になる
  年5%も手数料の水準も仮定で、特定の商品を指すものではない(戦略§6)
"""
TSUKI = 30_000
RATE = 0.05
YASUI, TAKAI = 0.001, 0.010     # 年0.1% と 年1.0%


def fv(annual_rate: float, months: int = 240) -> float:
    r = annual_rate / 12
    return TSUKI * (((1 + r) ** months - 1) / r)


def man(x: float) -> int:
    return round(x / 10_000)


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S019 数値検証(毎月3万円 / 20年 / 年5%と仮定)")
    a, b = fv(RATE - YASUI), fv(RATE - TAKAI)
    print(f"  手数料0.1%のとき: {a:,.0f}円")
    print(f"  手数料1.0%のとき: {b:,.0f}円")

    eq("手数料0.1%の20年後(万円)", man(a), 1219)
    eq("手数料1.0%の20年後(万円)", man(b), 1100)
    eq("差(万円)", man(a) - man(b), 119)

    # 出したお金は同じ。差はすべて手数料と、その手数料が増えなかった分
    eq("出したお金(万円)", man(TSUKI * 240), 720)
    eq("手数料の差(%の1000倍)", round((TAKAI - YASUI) * 1000), 9)

    # 1年目だけで見ると、差は小さい
    c, d = fv(RATE - YASUI, 12), fv(RATE - TAKAI, 12)
    eq("1年目の差(円)", round(c - d), 1_522)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
