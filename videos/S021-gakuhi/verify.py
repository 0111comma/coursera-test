#!/usr/bin/env python3
"""S021: 学費の検証。出典: 文科省 子供の学習費調査(令和5年度)・国立大学の標準額(plan.md参照)。"""

ZENKORITSU = 5_960_000    # 幼稚園〜高校まで全て公立(15年間)の学習費総額(約596万・調査の概数)
ZENSHIRITSU = 19_760_000  # 同・全て私立(約1,976万)
KOKURITSU_NYU = 282_000   # 国立大 入学料(標準額)
KOKURITSU_JUGYO = 535_800  # 国立大 授業料(標準額・年)
SHIDAI_BUNKEI = 4_110_000  # 私立大文系4年間の納付金の目安(約411万)


def main():
    kokudai = KOKURITSU_NYU + KOKURITSU_JUGYO * 4
    assert kokudai == 2_425_200, kokudai        # 国立大4年 約242万円
    saian = ZENKORITSU + kokudai
    assert saian == 8_385_200, saian            # 最安コース 約838万円
    assert round(saian / 10_000) == 839 or round(saian / 100_000) == 84  # 表記は約838万
    chukan = ZENKORITSU + SHIDAI_BUNKEI
    assert chukan == 10_070_000                 # 全公立+私大文系 約1,007万円
    saidai = ZENSHIRITSU + SHIDAI_BUNKEI
    assert saidai == 23_870_000                 # 全私立+私大文系 約2,387万円
    assert round(saidai / saian, 1) == 2.8      # 最安との差 約2.8倍
    # S019接続: 児童手当234万円は最安コースの約28%
    assert round(2_340_000 / saian * 100) == 28
    print("S021 verify: ALL OK")
    print(f"  最安(全公立+国立大): {saian:,}円")
    print(f"  全公立+私大文系: {chukan:,}円")
    print(f"  全私立: {saidai:,}円(最安の約{saidai/saian:.1f}倍)")
    print(f"  児童手当234万でまかなえる割合: 約{2_340_000/saian:.0%}")


if __name__ == "__main__":
    main()
