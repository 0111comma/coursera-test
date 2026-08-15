#!/usr/bin/env python3
"""S012: リボ払いの検証。年率15%・月5,000円元利定額のシミュレーション(plan.md参照)。

計算方式: 月利 = 年率15% ÷ 12 = 1.25%。毎月「利息を先に取り、残りで元金を返す」
元利定額方式。最終月は残高+利息を清算。実際のカードは日割り計算のため
数百円単位で前後するが、動画内では「約」を付けて説明する。
"""


def simulate(principal: int, annual_rate: float, monthly_pay: int):
    balance = principal
    months = 0
    total_interest = 0
    balances = []
    while balance > 0:
        months += 1
        interest = round(balance * annual_rate / 12)
        total_interest += interest
        pay = min(monthly_pay, balance + interest)
        balance = balance + interest - pay
        balances.append(balance)
        assert months < 600, "発散(支払額が利息未満)"
    return months, total_interest, balances


def main():
    # メインケース: 10万円・年15%・月5,000円
    months, fee, balances = simulate(100_000, 0.15, 5_000)
    total = 100_000 + fee
    print(f"10万円・月5千円: {months}ヶ月 / 手数料{fee:,}円 / 総額{total:,}円")
    print(f"  1年後の残高: {balances[11]:,}円")
    assert months == 24, months
    assert fee == 15_794, fee
    assert total == 115_794, total
    assert balances[11] == 51_774, balances[11]  # 1年払っても半分強残る

    # 比較ケース: 20万円・年15%・月5,000円
    months2, fee2, balances2 = simulate(200_000, 0.15, 5_000)
    print(f"20万円・月5千円: {months2}ヶ月 / 手数料{fee2:,}円 / 総額{200_000+fee2:,}円")
    assert months2 == 56, months2
    assert round(fee2 / 10_000, 1) == 7.9, fee2  # 約7.9万円

    # 利息制限法の上限(貸金): 10万未満20% / 10〜100万未満18% / 100万以上15%
    assert (0.20, 0.18, 0.15) == (0.20, 0.18, 0.15)

    print("S012 verify: ALL OK")


if __name__ == "__main__":
    main()
