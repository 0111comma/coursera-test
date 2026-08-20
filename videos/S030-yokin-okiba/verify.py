#!/usr/bin/env python3
"""S030 の数値検証。動画内の数字はすべてここで再計算する。

問い: 100万円の置き場所を変えると、利息は年いくら変わるのか。
前提(2026年8月時点の水準・確認日 2026-08-19):
  普通預金 年0.4%(メガバンクの水準)
  1年定期  年0.5%(メガバンクの水準)/ 年1.3%(高いネット銀行の水準)
  利息には 20.315% の税がかかる
"""
GAKU = 1_000_000
FUTSU, TEIKI_MEGA, TEIKI_NET = 0.004, 0.005, 0.013
ZEI = 0.20315


def ato(riritsu: float) -> int:
    return round(GAKU * riritsu * (1 - ZEI))


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S030 数値検証(100万円 / 2026年8月の水準)")
    eq("普通預金の利息(税引き前)", round(GAKU * FUTSU), 4_000)
    eq("普通預金の利息(税引き後)", ato(FUTSU), 3_187)
    eq("メガバンク定期(税引き後)", ato(TEIKI_MEGA), 3_984)
    eq("高い定期(税引き後)", ato(TEIKI_NET), 10_359)

    eq("普通→メガ定期の差", ato(TEIKI_MEGA) - ato(FUTSU), 797)
    eq("普通→高い定期の差", ato(TEIKI_NET) - ato(FUTSU), 7_172)
    eq("10年ぶん(単利で置いた場合)", (ato(TEIKI_NET) - ato(FUTSU)) * 10, 71_720)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
