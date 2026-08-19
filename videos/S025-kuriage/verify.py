#!/usr/bin/env python3
"""S025 の数値検証。動画内の数字はすべてここで再計算する。

問い: 住宅ローンを100万円繰り上げ返済すると、利息はいくら減るのか。
前提(すべて仮定):
  3000万円 / 35年 / 年1.0% / 元利均等返済
  10年目に100万円を繰り上げ返済する(期間短縮型。毎月の返済額は変えない)
  金利は仮定であり、実際の条件は借入先で変わる
"""
GANKIN, ANN, N = 30_000_000, 0.01, 420
R = ANN / 12
KURIAGE = 1_000_000


def monthly() -> float:
    return GANKIN * R * (1 + R) ** N / ((1 + R) ** N - 1)


def balance_after(months: int) -> float:
    pay, b = monthly(), GANKIN
    for _ in range(months):
        b = b * (1 + R) - pay
    return b


def rest_interest(bal: float) -> float:
    pay, b, total = monthly(), bal, 0.0
    while b > 1:
        i = b * R
        b = b + i - pay
        total += i
        if b < 0:
            break
    return total


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S025 数値検証(3000万円 / 35年 / 年1.0%と仮定)")
    eq("毎月の返済額", round(monthly()), 84_686)

    b10 = balance_after(120)
    eq("10年後の残高(万円)", round(b10 / 10_000), 2_247)

    a, b = rest_interest(b10), rest_interest(b10 - KURIAGE)
    eq("そのままの残り利息", round(a), 2_935_058)
    eq("100万円を繰り上げた後の残り利息", round(b), 2_658_679)
    eq("減る利息", round(a - b), 276_378)

    # 同じ100万円を、20年目に繰り上げた場合
    b20 = balance_after(240)
    c, d = rest_interest(b20), rest_interest(b20 - KURIAGE)
    eq("20年目にやった場合の減る利息", round(c - d), 155_644)
    eq("早いほうが多く減る額", round((a - b) - (c - d)), 120_734)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
