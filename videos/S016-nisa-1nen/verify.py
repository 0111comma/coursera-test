#!/usr/bin/env python3
"""S016 の数値検証。動画内の数字はすべてここで再計算する。

問い: 積立を1年おくらせると、20年後にいくら違うのか。
前提(すべて仮定):
  毎月3万円 / 年5% / 20年つづける場合と、1年おくらせて19年にする場合を、
  **同じ日にそろえて**比べる。
  年5%はあくまで仮定で、増える保証はない(戦略§6)。
"""
TSUKI = 30_000
RATE = 0.05
R = RATE / 12
ZEI = 0.20315          # 課税口座の税率(所得税15% + 復興0.315% + 住民税5%)


def fv(months: int) -> float:
    """毎月末に積み立てたときの、月数後の合計。"""
    return TSUKI * (((1 + R) ** months - 1) / R)


def man(x: float) -> int:
    """万円に丸める(動画で言う単位)。"""
    return round(x / 10_000)


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S016 数値検証(毎月3万円 / 年5%と仮定)")
    a, b = fv(240), fv(228)
    print(f"  20年つづけた場合: {a:,.0f}円")
    print(f"  19年にした場合  : {b:,.0f}円")

    eq("20年後の合計(万円)", man(a), 1233)
    eq("1年おくらせた場合(万円)", man(b), 1138)
    eq("差(万円)", man(a) - man(b), 95)

    # 出したお金そのものの差は、1年ぶんの積立額だけ
    eq("出したお金の差(万円)", man(TSUKI * 12), 36)
    eq("増えるはずだった分(万円)", (man(a) - man(b)) - man(TSUKI * 12), 59)

    # 課税口座なら、この差のうち「増えた分」に税がかかる
    zei = (a - b - TSUKI * 12) * ZEI
    print(f"  課税口座なら差から引かれる税: {zei:,.0f}円")
    eq("課税口座で引かれる税(万円)", man(zei), 12)

    # 毎月1万円の人は、そのまま3分の1
    eq("月1万円の場合の差(万円)", round((man(a) - man(b)) / 3), 32)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
