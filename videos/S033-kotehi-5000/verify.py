#!/usr/bin/env python3
"""S033「毎月5000円の固定費を1つ止めると、65歳でいくらになるか」の数値検証。

**この動画には、外から持ってくる数値が1つも無い。**(2026-08-24)
理由: この実行環境からは官公庁のサイト(.go.jp)が全部ブロックされていて、
一次資料を開いて確かめられない。確かめられない数字を画面に出さない、という
CLAUDE.md の最優先ゲートに従い、前提はすべて**明示した仮定**にした。

| 前提 | 値 | 根拠 |
|---|---|---|
| 止める固定費 | 月5000円 | **仮定。**視聴者が自分の額に置き換える前提の例 |
| 期間 | 35歳→65歳の30年 | **仮定。**この動画の対象(P-M: 35歳の会社員) |
| 利回り | 年5% | **仮定。**元本保証ではない。減る年もある |

利回りは仮定なので、**0%(ただ貯める)の場合も必ず並べて出す。**
「増える前提」だけを見せない(戦略§6-2)。
"""
MONTHLY = 5_000        # 止める固定費(仮定)
START_AGE = 35         # P-M の年齢
END_AGE = 65
MONTHS = (END_AGE - START_AGE) * 12


def future_value(monthly: int, months: int, annual_rate: float) -> float:
    """毎月末に monthly を積み、残りを年利 annual_rate で運用したときの残高。"""
    bal = 0.0
    for _ in range(months):
        bal = bal * (1 + annual_rate / 12) + monthly
    return bal


CASES = [(0.00, "ただ貯める"), (0.03, "年3%で運用"), (0.05, "年5%で運用")]
RESULT = {r: future_value(MONTHLY, MONTHS, r) for r, _ in CASES}

PRINCIPAL = MONTHLY * MONTHS          # 出したお金の合計
FV5 = RESULT[0.05]                    # 年5%(仮定)のとき
GAIN5 = FV5 - PRINCIPAL               # 増えた分
DAILY = MONTHLY / 30                  # 1日あたりに直すといくらか

if __name__ == "__main__":
    print(f"毎月 {MONTHLY:,}円 を {START_AGE}歳から{END_AGE}歳まで({MONTHS}か月)")
    print(f"  1日あたり  : {DAILY:.0f}円")
    print(f"  出したお金 : {PRINCIPAL:,}円")
    for r, label in CASES:
        print(f"  {label:10s}: {RESULT[r]:,.0f}円")

    assert PRINCIPAL == 1_800_000, PRINCIPAL
    print(f"\n検算: {MONTHLY:,} × {MONTHS} = {PRINCIPAL:,}円 ✓")
    print(f"      {END_AGE - START_AGE}年 × 12 = {MONTHS}か月 ✓")

    # 台本で**声に出す**丸めた値。嘘になっていないかをここで確かめる
    ROUND_PRINCIPAL = 180             # 「180万円」
    ROUND_FV5 = round(FV5 / 10_000)   # 「416万円」
    ROUND_GAIN = ROUND_FV5 - ROUND_PRINCIPAL
    assert abs(PRINCIPAL / 10_000 - ROUND_PRINCIPAL) < 0.5
    assert abs(FV5 / 10_000 - ROUND_FV5) < 0.5
    print(f"\n台本で言う値: 出したお金 {ROUND_PRINCIPAL}万円 / "
          f"年5%なら {ROUND_FV5}万円 / 増えた分 {ROUND_GAIN}万円 ✓")
    print(f"      ただ貯めるだけでも {RESULT[0.00]/10_000:.0f}万円")

    # 「1日167円」の実感。視聴者が自分の生活に置き換えるための数
    print(f"\n1日 {DAILY:.0f}円 = {MONTHLY:,}円/月。"
          f"この額を止めるだけで、30年後に {ROUND_FV5}万円(年5%と仮定した場合)")
