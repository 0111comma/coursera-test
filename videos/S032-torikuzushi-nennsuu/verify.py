#!/usr/bin/env python3
"""S032「1000万円を月5万ずつ取り崩すと何年もつか」の数値検証。

前提はすべて仮定であることを台本で明示する。
制度の数値ではなく算数なので、制度改正で腐らない。
"""
PRINCIPAL = 10_000_000     # 取り崩す元手
DRAW = 50_000              # 毎月の取り崩し額
START_AGE = 65


def months_until_empty(principal: int, draw: int, annual_rate: float,
                       cap_months: int = 1200) -> int:
    """毎月末に draw を引き、残りを年利 annual_rate で運用したときに尽きる月数。"""
    bal, m = float(principal), 0
    while bal > 0 and m < cap_months:
        bal = bal * (1 + annual_rate / 12) - draw
        m += 1
    return m


CASES = [(0.00, "運用しない"), (0.03, "年3%で運用"), (0.05, "年5%で運用")]
RESULT = {}
for r, label in CASES:
    m = months_until_empty(PRINCIPAL, DRAW, r)
    RESULT[r] = (m, m / 12, START_AGE + m / 12)

if __name__ == "__main__":
    print(f"元手 {PRINCIPAL:,}円 / 毎月 {DRAW:,}円 取り崩し / {START_AGE}歳から")
    for r, label in CASES:
        m, y, age = RESULT[r]
        print(f"  {label:10s}: {m:4d}か月 = {y:5.1f}年  → {age:.0f}歳で尽きる")
    # 台本で使う値の確認
    assert months_until_empty(PRINCIPAL, DRAW, 0.00) == 200
    print(f"\n検算: 1000万 ÷ 5万 = {PRINCIPAL//DRAW}か月 = {PRINCIPAL//DRAW/12:.1f}年 ✓")
    # 「何歳まで持たせたいか」から逆算した取り崩し額
    print("\n95歳(30年)まで持たせるなら、毎月いくらまでか:")
    for r, label in CASES:
        lo, hi = 1000, 200_000
        for _ in range(60):
            mid = (lo + hi) / 2
            if months_until_empty(PRINCIPAL, int(mid), r) >= 360: lo = mid
            else: hi = mid
        print(f"  {label:10s}: 毎月 {int(lo//1000*1000):,}円まで")
