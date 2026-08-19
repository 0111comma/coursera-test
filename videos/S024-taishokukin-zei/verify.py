#!/usr/bin/env python3
"""S024 の数値検証。動画内の数字はすべてここで再計算する。

問い: 退職金2000万円に、税金はいくらかかるのか。
前提(2026年8月時点・確認日 2026-08-19):
  退職所得控除 = 勤続20年以下 40万円 × 年数 / 20年超 800万円 + 70万円 ×(年数-20)
  課税される退職所得 = (退職金 - 控除)× 1/2
  所得税は分離課税(復興特別所得税2.1%を上乗せ)、住民税10%
"""
TAISHOKU = 20_000_000


def kojo(years: int) -> int:
    return 400_000 * years if years <= 20 else 8_000_000 + 700_000 * (years - 20)


def zei(years: int):
    kazei = max(0, TAISHOKU - kojo(years)) // 2
    if kazei <= 1_950_000:
        sh = kazei * 0.05
    elif kazei <= 3_300_000:
        sh = kazei * 0.10 - 97_500
    elif kazei <= 6_950_000:
        sh = kazei * 0.20 - 427_500
    else:
        sh = kazei * 0.23 - 636_000
    return kazei, round(sh * 1.021), round(kazei * 0.10)


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S024 数値検証(退職金2000万円)")
    eq("勤続30年の控除", kojo(30), 15_000_000)
    k30, s30, j30 = zei(30)
    eq("勤続30年の課税される額", k30, 2_500_000)
    eq("勤続30年の所得税", s30, 155_702)
    eq("勤続30年の住民税", j30, 250_000)
    eq("勤続30年の税の合計", s30 + j30, 405_702)
    eq("勤続30年の手取り", TAISHOKU - (s30 + j30), 19_594_298)

    eq("勤続20年の控除", kojo(20), 8_000_000)
    k20, s20, j20 = zei(20)
    eq("勤続20年の課税される額", k20, 6_000_000)
    eq("勤続20年の税の合計", s20 + j20, 1_388_722)

    eq("10年の差", (s20 + j20) - (s30 + j30), 983_020)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
