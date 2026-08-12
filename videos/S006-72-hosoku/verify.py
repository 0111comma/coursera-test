#!/usr/bin/env python3
"""S006: 「72の法則」(資産が2倍になる年数 ≈ 72÷年利%)の検証。

- 法則値: 72 ÷ 年利(%)
- 厳密値: ln2 ÷ ln(1+年利) (年複利)
- 動画で使う範囲(年1〜8%)での相対誤差が小さいことをassertする
- インフレへの適用: 物価が年2%上昇 → 約36年でお金の実質価値が半分
"""
import math

RATES = [1, 2, 3, 4, 5, 6, 7, 8]
rule = {r: 72 / r for r in RATES}
exact = {r: math.log(2) / math.log(1 + r / 100) for r in RATES}

for r in RATES:
    err = abs(rule[r] - exact[r]) / exact[r]
    assert err < 0.04, (r, rule[r], exact[r], err)   # 全レンジで誤差4%未満

# 台本の数字
assert round(rule[5], 1) == 14.4 and round(exact[5], 1) == 14.2   # 年5% → 約14年
assert rule[1] == 72                                               # 年1% → 72年
assert rule[3] == 24 and round(rule[7], 1) == 10.3                 # 24年 / 約10年
assert rule[2] == 36                                               # 物価2% → 36年で価値半分

print("年利 | 72の法則 | 厳密値 | 誤差")
for r in RATES:
    print(f"{r}% | {rule[r]:.1f}年 | {exact[r]:.2f}年 | {abs(rule[r]-exact[r])/exact[r]:.1%}")
print("インフレ2% → 72÷2 = 36年で実質価値が半分")
print("OK: すべての数値が台本と一致")
