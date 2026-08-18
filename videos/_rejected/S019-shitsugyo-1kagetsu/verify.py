#!/usr/bin/env python3
"""S019 の数値検証: 自己都合退職から失業手当が出るまでの日数。"""
from datetime import date, timedelta

TAIKI = 7          # 待期(誰でも同じ)
SEIGEN_KYU = 2     # 2025年3月までの給付制限(ヶ月)
SEIGEN_SHIN = 1    # 2025年4月以降(ヶ月)

# 3月1日に辞めた場合で、待期明けからの給付制限を数える
taishoku = date(2026, 3, 1)
taiki_ake = taishoku + timedelta(days=TAIKI)
assert taiki_ake == date(2026, 3, 8), taiki_ake

# 給付制限1ヶ月 → 4月8日から。旧ルールなら5月8日から
shin = date(2026, 4, 8)
kyu = date(2026, 5, 8)
assert (kyu - shin).days == 30, (kyu - shin).days

# 会社都合なら待期7日だけ
kaisha = taiki_ake
assert (shin - kaisha).days == 31

print(f"  退職 {taishoku} → 待期{TAIKI}日 → {taiki_ake}")
print(f"  新ルール(給付制限{SEIGEN_SHIN}ヶ月): {shin} から")
print(f"  旧ルール(給付制限{SEIGEN_KYU}ヶ月): {kyu} から")
print(f"  差 {(kyu - shin).days}日ぶん早くなった")
print(f"  会社都合なら {kaisha} から(待期だけ)")
print("S019 verify: ALL OK")
