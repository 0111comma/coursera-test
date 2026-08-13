#!/usr/bin/env python3
"""S014: 手数料の検証。出典: 大手銀行の公表手数料(2026-08時点・plan.md参照)。"""

CONBINI_ATM = 220     # コンビニATM(日中)の代表値
CONBINI_ATM_YORU = 330  # コンビニATM(時間外)
JIKANGAI = 110        # 自行ATMの時間外手数料の代表値
FURIKOMI_MADO = 990   # 他行宛て振込(窓口)の最大帯
FURIKOMI_APP = 110    # 他行宛て振込(ネット・アプリ)の下限帯
FUTSU_KINRI = 0.0040  # 普通預金 年0.40%(S013と共通)


def main():
    year = CONBINI_ATM * 52
    assert year == 11_440, year                    # 週1利用で年11,440円
    assert FURIKOMI_MADO - FURIKOMI_APP == 880     # 窓口とアプリの差
    # 年11,440円は「いくらの預金の利息(税引前)」に相当するか
    genpon = int(year / FUTSU_KINRI)
    assert genpon == 2_860_000, genpon             # 預金286万円分の利息
    assert int(2_860_000 * FUTSU_KINRI) == year
    print("S014 verify: ALL OK")
    print(f"  コンビニATM週1: 年{year:,}円(= 預金{genpon:,}円の年利息と同額)")
    print(f"  振込: 窓口{FURIKOMI_MADO}円 vs アプリ{FURIKOMI_APP}円(差{FURIKOMI_MADO-FURIKOMI_APP}円)")


if __name__ == "__main__":
    main()
