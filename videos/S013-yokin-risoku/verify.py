#!/usr/bin/env python3
"""S013: 預金利息の検証。出典: メガバンク公表金利(2026-08時点)ほか(plan.md参照)。"""

GENKIN = 1_000_000
FUTSU = 0.0040    # 普通預金 年0.40%(メガバンク・2026-08-03〜)
TEIKI = 0.0050    # 定期預金1年 年0.50%
KYU = 0.00001     # 旧・普通預金 年0.001%(2016〜2024年ごろ)
ATM_FEE = 220     # コンビニATM手数料の下限帯


def main():
    risoku = int(GENKIN * FUTSU)
    assert risoku == 4_000, risoku
    kyu_risoku = int(GENKIN * KYU)
    assert kyu_risoku == 10, kyu_risoku
    assert risoku // kyu_risoku == 400          # 400倍
    teiki_risoku = int(GENKIN * TEIKI)
    assert teiki_risoku == 5_000, teiki_risoku

    # 源泉税 20.315%(国税15.315%+地方税5%、それぞれ円未満切捨て)
    kokuzei = int(risoku * 0.15315)
    chihou = int(risoku * 0.05)
    tedori = risoku - kokuzei - chihou
    assert (kokuzei, chihou, tedori) == (612, 200, 3_188), (kokuzei, chihou, tedori)

    # 旧金利時代: ATM手数料1回(220円)は利息何年分か
    assert ATM_FEE // kyu_risoku == 22          # 22年分

    print("S013 verify: ALL OK")
    print(f"  普通預金0.40%: 利息{risoku:,}円(税引後{tedori:,}円)")
    print(f"  定期1年0.50%: 利息{teiki_risoku:,}円")
    print(f"  旧0.001%: 利息{kyu_risoku}円 → 400倍 / ATM1回={ATM_FEE//kyu_risoku}年分")


if __name__ == "__main__":
    main()
