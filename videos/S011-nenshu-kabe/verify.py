#!/usr/bin/env python3
"""S011: 年収の壁(2026年分)の検証。出典: 国税庁+令和8年度税制改正大綱(plan.md参照)。"""

KISO = 1_040_000          # 基礎控除(令和8年分。恒久62万+特例42万。年収約665万円以下)
KYUYO = 740_000           # 給与所得控除の最低保障(令和8年分。恒久69万+特例5万)
WALL_2026 = 1_780_000     # 所得税の非課税ライン
WALL_2025 = 1_230_000     # 2025年分(123万)
WALL_OLD = 1_030_000      # 旧・103万
JUMINZEI = 1_100_000      # 住民税の壁(2026年度・単身)


def main():
    assert KISO + KYUYO == WALL_2026, KISO + KYUYO
    assert WALL_2026 - WALL_OLD == 750_000            # 103万から75万円上がった
    assert WALL_2026 - WALL_2025 == 550_000
    print("S011 verify: ALL OK")
    print(f"  2026年分の非課税ライン: {WALL_2026:,}円 (104万+74万)")
    print(f"  103万との差: +{WALL_2026 - WALL_OLD:,}円")


if __name__ == "__main__":
    main()
