#!/usr/bin/env python3
"""S018: 積立スタート年齢の差の検証。月1万円・65歳まで・年5%(仮定)・月複利。

計算方式: 毎月末に1万円を積み立て、残高に月利(5%÷12)が付く想定。
年5%はあくまで仮定であり、将来の運用成果を保証・予測するものではない。
"""

R = 0.05 / 12
TSUMITATE = 10_000


def fv(months: int) -> float:
    bal = 0.0
    for _ in range(months):
        bal = bal * (1 + R) + TSUMITATE
    return bal


def main():
    a = fv(480)   # 25歳→65歳(40年)
    b = fv(360)   # 35歳→65歳(30年)
    c = fv(240)   # 45歳→65歳(20年)
    a_man, b_man, c_man = (round(x / 10_000) for x in (a, b, c))
    assert a_man == 1_526, a_man
    assert b_man == 832, b_man
    assert c_man == 411, c_man
    assert a_man - b_man == 694          # 最終差 約694万円
    assert 480 * TSUMITATE - 360 * TSUMITATE == 1_200_000  # 元本差は120万円だけ
    assert round(a / (480 * TSUMITATE), 2) == 3.18
    assert round(b / (360 * TSUMITATE), 2) == 2.31
    print("S018 verify: ALL OK")
    print(f"  25歳スタート: 約{a_man:,}万円(元本480万)")
    print(f"  35歳スタート: 約{b_man:,}万円(元本360万)")
    print(f"  45歳スタート: 約{c_man:,}万円(元本240万)")
    print(f"  差 約{a_man - b_man}万円(払った差は120万円)")


if __name__ == "__main__":
    main()
