#!/usr/bin/env python3
"""S009: 高額療養費制度の数値検証。

動画・企画書・render.pyで使うすべての数値をここで再計算し、assertで確認する。
制度値の出典: 厚労省の高額療養費制度資料(2026年8月改定)。plan.mdの出典欄参照。
"""

MEDICAL = 1_000_000  # 医療費総額の例


def cap_c_new(medical: int) -> int:
    """区分ウ(年収約370〜770万円)の自己負担限度額。2026年8月〜。"""
    return int(85_800 + (medical - 286_000) * 0.01)


def cap_c_old(medical: int) -> int:
    """区分ウの旧限度額。〜2026年7月。"""
    return int(80_100 + (medical - 267_000) * 0.01)


def main() -> None:
    sanwari = int(MEDICAL * 0.3)
    assert sanwari == 300_000, sanwari

    new = cap_c_new(MEDICAL)
    old = cap_c_old(MEDICAL)
    assert new == 92_940, new
    assert old == 87_430, old
    assert new - old == 5_510, new - old

    # 定額部分の引き上げ幅(区分ウ): 85,800 − 80,100 = +5,700
    assert 85_800 - 80_100 == 5_700

    # 窓口で3割払った場合の払い戻し
    payback = sanwari - new
    assert payback == 207_060, payback

    # フックの丸め: 92,940円 → 約9.3万円
    assert round(new / 10_000, 1) == 9.3

    # 年収別の基準額(2026年8月〜・70歳未満)。旧額+引き上げ幅=新額の内部整合を確認
    brackets = {
        "ア(約1160万〜)": (252_600, 17_700, 270_300),
        "イ(約770〜1160万)": (167_400, 11_700, 179_100),
        "ウ(約370〜770万)": (80_100, 5_700, 85_800),
        "エ(〜約370万)": (57_600, 3_900, 61_500),
        "オ(住民税非課税)": (35_400, 1_500, 36_900),
    }
    for name, (old_base, up, new_base) in brackets.items():
        assert old_base + up == new_base, name

    print("S009 verify: ALL OK")
    print(f"  医療費{MEDICAL:,}円の3割: {sanwari:,}円")
    print(f"  自己負担上限(区分ウ・2026年8月〜): {new:,}円")
    print(f"  同(〜2026年7月): {old:,}円 (差 +{new - old:,}円)")
    print(f"  払い戻し(3割窓口払い時): {payback:,}円")


if __name__ == "__main__":
    main()
