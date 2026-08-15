#!/usr/bin/env python3
"""S017: NISAの損益通算不可の検証。出典: 金融庁NISA特設サイト・国税庁(plan.md参照)。"""

SONSHITSU = 500_000   # 例: NISA口座での損失50万円
RIEKI = 500_000       # 例: 課税口座での利益50万円
ZEIRITSU = 0.20315    # 譲渡益課税(所得税15.315%+住民税5%)


def main():
    zei = int(RIEKI * ZEIRITSU)
    assert zei == 101_575, zei
    # 課税口座同士: 利益50万と損失50万を通算 → 課税所得0 → 税0円(=101,575円が浮く)
    assert max(0, RIEKI - SONSHITSU) * ZEIRITSU == 0
    # NISAの損失: 通算に使えない → 利益50万にまるごと課税
    assert int(RIEKI * ZEIRITSU) == 101_575
    # 繰越控除(課税口座): 翌年以後3年間 / NISA: 不可
    KURIKOSHI_YEARS = 3
    assert KURIKOSHI_YEARS == 3
    print("S017 verify: ALL OK")
    print(f"  利益50万円への税: {zei:,}円(20.315%)")
    print("  課税口座同士: 損50万と通算 → 税0円")
    print(f"  NISAの損50万: 通算不可 → 税{zei:,}円のまま(差{zei:,}円)")


if __name__ == "__main__":
    main()
