#!/usr/bin/env python3
"""S021 の数値検証。動画内の数字はすべてここで再計算する。

問い: 「老後2000万円」は、毎月いくら積み立てたら届くのか。
前提(すべて仮定):
  35歳から定年までの30年(360ヶ月)で2000万円をつくる
  預金は年0.4%(2026年8月のメガバンクの水準)、運用は年5%と仮定
  毎月末に積み立てる。年5%は仮定で、増える保証はない(戦略§6)
"""
GOAL = 20_000_000
MONTHS = 360
YOKIN, UNYO = 0.004, 0.05


def monthly(annual: float) -> float:
    r = annual / 12
    return GOAL / (((1 + r) ** MONTHS - 1) / r)


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S021 数値検証(2000万円 / 30年)")
    a, b = monthly(YOKIN), monthly(UNYO)
    print(f"  預金 年0.4%: 月 {a:,.0f}円")
    print(f"  運用 年5%  : 月 {b:,.0f}円")

    eq("預金だけのとき(百円丸め)", round(a / 100) * 100, 52_300)
    eq("年5%と仮定したとき(百円丸め)", round(b / 100) * 100, 24_000)
    eq("毎月の差", 52_300 - 24_000, 28_300)

    eq("30年で出す額(預金・万円)", round(a * MONTHS / 10_000), 1_883)
    eq("30年で出す額(運用・万円)", round(b * MONTHS / 10_000), 865)
    eq("出す額の差(万円)", round(a * MONTHS / 10_000) - round(b * MONTHS / 10_000), 1_018)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
