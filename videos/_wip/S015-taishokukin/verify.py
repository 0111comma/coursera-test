#!/usr/bin/env python3
"""S015: 退職所得控除の検証。出典: 国税庁タックスアンサーNo.1420(plan.md参照)。"""


def kojo(years: int) -> int:
    """退職所得控除(万円)。20年まで40万/年、超過分は70万/年。最低80万。"""
    if years <= 20:
        return max(80, 40 * years)
    return 800 + 70 * (years - 20)


def kazei_taisho(taishokukin_man: int, years: int) -> int:
    """課税対象となる退職所得(万円)。控除後の1/2(端数は簡略化)。"""
    return max(0, taishokukin_man - kojo(years)) // 2


def main():
    assert kojo(20) == 800
    assert kojo(30) == 1_500
    assert kojo(38) == 2_060          # 勤続38年 → 2,060万円
    assert kojo(38) > 2_000           # 2000万円 < 控除 → 課税ゼロ
    assert kazei_taisho(2_000, 38) == 0
    assert kazei_taisho(2_500, 38) == 220  # 超えても(2500-2060)÷2=220万にだけ課税
    print("S015 verify: ALL OK")
    print(f"  控除: 勤続20年={kojo(20)}万 / 30年={kojo(30):,}万 / 38年={kojo(38):,}万")
    print(f"  退職金2000万・勤続38年 → 課税対象{kazei_taisho(2_000, 38)}万円(税0円)")
    print(f"  退職金2500万・勤続38年 → 課税対象{kazei_taisho(2_500, 38)}万円")


if __name__ == "__main__":
    main()
