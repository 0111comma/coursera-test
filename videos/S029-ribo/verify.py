#!/usr/bin/env python3
"""S029 の数値検証。動画内の数字はすべてここで再計算する。

問い: 10万円の買い物をリボ払いにすると、総額いくらになるのか。
前提(2026年8月時点・確認日 2026-08-19):
  手数料率は年15% = 月1.25%(多くのカードのリボがこの水準)
  毎月5000円の元利定額(5000円の中に手数料が入っている)
"""
GAKU = 100_000
RATE = 0.15 / 12
PAY = 5_000


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S029 数値検証(10万円 / 年15% / 月5000円)")
    # 1ヶ月目の内訳
    first_i = round(GAKU * RATE)
    eq("月の率(%の100倍)", round(RATE * 10000), 125)
    eq("1ヶ月目の手数料", first_i, 1_250)
    eq("1ヶ月目に減る元金", PAY - first_i, 3_750)

    # 完済までを回す
    bal, months, total_i = GAKU, 0, 0.0
    while bal > 0:
        i = bal * RATE
        total_i += i
        pay = min(PAY, bal + i)
        bal = bal + i - pay
        months += 1
    eq("完済までの月数", months, 24)
    eq("手数料の合計", round(total_i), 15_795)
    eq("払う総額", GAKU + round(total_i), 115_795)

    # 一括なら手数料0円(1回払いは手数料がかからない)
    eq("一括払いとの差", round(total_i), 15_795)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
