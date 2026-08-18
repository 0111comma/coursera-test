#!/usr/bin/env python3
"""S022 の数値検証。動画内の数字はすべてここで再計算する。

問い: 2026年4月から新しく引かれ始めたお金は、年にいくらか。
前提(2026年度・確認日 2026-08-18):
  子ども・子育て支援金。会社員(被用者保険)の率は 0.23%。
  労使折半なので本人負担は 0.115%。
  計算は実際の給料ではなく、標準報酬月額と標準賞与額にかかる。
  ここでは 標準報酬月額36万円 / 賞与は年100万円 で計算する。
"""
HYOJUN = 360_000
SHOYO = 1_000_000
RATE_ALL = 0.0023
RATE_HONNIN = RATE_ALL / 2      # 労使折半


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S022 数値検証(標準報酬月額36万円・賞与年100万円)")
    eq("本人の率(%の10000倍)", round(RATE_HONNIN * 1_000_000), 1_150)

    tsuki = round(HYOJUN * RATE_HONNIN)
    eq("毎月引かれる額", tsuki, 414)
    eq("12ヶ月ぶん", tsuki * 12, 4_968)

    shoyo = round(SHOYO * RATE_HONNIN)
    eq("賞与から引かれる額", shoyo, 1_150)
    eq("1年の合計", tsuki * 12 + shoyo, 6_118)

    # 会社も同じ額を出しているので、制度全体では2倍
    eq("会社のぶんも足すと", (tsuki * 12 + shoyo) * 2, 12_236)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
