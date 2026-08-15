#!/usr/bin/env python3
"""S019: 児童手当の総額検証。出典: こども家庭庁(2024年10月拡充後の制度・plan.md参照)。

支給期間は誕生月の翌月〜18歳の年度末(高校生年代まで)。月数は誕生月で変わり、
3月生まれが最少(0歳〜3歳未満36ヶ月+3歳〜18歳年度末180ヶ月=216ヶ月)、
4月生まれが最多(227ヶ月)。ここでは分かりやすさ優先で「3歳まで36ヶ月」と概数化。
"""

SANSAI_MIMAN = 15_000   # 3歳未満(第1子・第2子) 月額
SANSAI_IJO = 10_000     # 3歳〜高校生年代(第1子・第2子) 月額
DAISANSHI = 30_000      # 第3子以降 月額(年齢によらず)


def main():
    m1 = SANSAI_MIMAN * 36
    assert m1 == 540_000, m1                 # 3歳まで 54万円
    m2 = SANSAI_IJO * 180
    assert m2 == 1_800_000, m2               # 3歳〜18歳年度末(3月生まれ) 180万円
    total_march = m1 + m2
    assert total_march == 2_340_000          # 3月生まれ 総額234万円(最少)
    total_april = m1 + SANSAI_IJO * 191
    assert total_april == 2_450_000          # 4月生まれ 総額245万円(最多)
    assert total_april - total_march == 110_000  # 誕生月の差 11万円
    d3 = DAISANSHI * 216
    assert d3 == 6_480_000                   # 第3子(3月生まれ) 総額648万円
    print("S019 verify: ALL OK")
    print(f"  3歳まで: {m1:,}円 / 3歳〜18歳年度末: {m2:,}円")
    print(f"  総額: 3月生まれ{total_march:,}円 〜 4月生まれ{total_april:,}円(差{total_april-total_march:,}円)")
    print(f"  第3子以降: {d3:,}円")


if __name__ == "__main__":
    main()
