#!/usr/bin/env python3
"""S021 の数値検証。動画内の数字はすべてここで再計算する。

問い: 1000万円を20年で貯めるには、毎月いくら必要か。
前提(すべて仮定):
  預金は年0.4%、運用は年5%と仮定。どちらも毎月末に積み立てる。
  年5%は仮定であって、増える保証はない(戦略§6)。
"""
GOAL = 10_000_000
MONTHS = 240
YOKIN, UNYO = 0.004, 0.05


def monthly(annual_rate: float) -> float:
    r = annual_rate / 12
    factor = ((1 + r) ** MONTHS - 1) / r
    return GOAL / factor


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S021 数値検証(1000万円を20年で)")
    a, b = monthly(YOKIN), monthly(UNYO)
    print(f"  預金 年0.4%: 月 {a:,.0f}円")
    print(f"  運用 年5%  : 月 {b:,.0f}円")

    eq("預金だけのとき(円)", round(a / 100) * 100, 40_000)
    eq("年5%で増えたとき(円)", round(b / 100) * 100, 24_300)
    eq("月あたりの差(円)", round(a / 100) * 100 - round(b / 100) * 100, 15_700)

    # 20年で出すお金そのものの差
    eq("20年で出すお金の差(万円)", round((a - b) * MONTHS / 10_000), 377)
    # 預金だけで出す総額
    eq("預金だけで出す総額(万円)", round(a * MONTHS / 10_000), 961)
    eq("運用を混ぜて出す総額(万円)", round(b * MONTHS / 10_000), 584)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
