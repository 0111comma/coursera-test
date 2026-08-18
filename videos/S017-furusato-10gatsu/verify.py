#!/usr/bin/env python3
"""S017 の数値検証: ふるさと納税の基準が変わる日と、残り日数。"""
from datetime import date

SEKO = date(2026, 10, 1)      # 地場産品基準の厳格化
KOUKAI = date(2026, 8, 26)    # 公開予定日

nokori = (SEKO - KOUKAI).days
assert nokori == 36, nokori
# 「9月30日まで」が現行ルールの最終日
saigo = date(2026, 9, 30)
assert (SEKO - saigo).days == 1

# 変わらないルール(この動画で「変わらない」と言う数字)
CHOTATSU = 0.30    # 返礼品の調達費は寄付額の3割以下
KEIHI = 0.50       # 募集経費の総額は5割以下
assert CHOTATSU == 0.3 and KEIHI == 0.5

print(f"  施行日 {SEKO} / 現行ルールの最終日 {saigo}")
print(f"  公開日 {KOUKAI} の時点で、残り {nokori}日")
print(f"  変わらないもの: 調達費 {CHOTATSU:.0%}以下 / 募集経費 {KEIHI:.0%}以下")
print("S017 verify: ALL OK")
