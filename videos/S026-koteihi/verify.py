#!/usr/bin/env python3
"""S026 の数値検証。動画内の数字はすべてここで再計算する。

問い: 毎月の固定費を3000円下げると、20年でいくらになるのか。
前提(すべて仮定):
  下げた3000円をそのまま毎月積み立てる / 20年 / 年5%と仮定
  年5%は仮定であり、増える保証はない(戦略§6)
"""
TSUKI = 3_000
RATE = 0.05
MONTHS = 240


def fv(months: int) -> float:
    r = RATE / 12
    return TSUKI * (((1 + r) ** months - 1) / r)


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S026 数値検証(月3000円 / 20年 / 年5%と仮定)")
    eq("1年ぶん", TSUKI * 12, 36_000)
    eq("20年ためるだけ", TSUKI * MONTHS, 720_000)
    eq("年5%で増やした場合", round(fv(MONTHS)), 1_233_101)
    eq("増えた分", round(fv(MONTHS)) - TSUKI * MONTHS, 513_101)

    # 手取りを3000円増やすのと比べる(手取りは額面の約68%。S018で計算した)
    eq("同じ効果を給料で得るなら(額面の月あたり)", round(TSUKI / 0.68), 4_412)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
