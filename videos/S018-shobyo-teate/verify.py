#!/usr/bin/env python3
"""S018 の数値検証: 傷病手当金。"""
GEKKYU = 300_000          # 標準報酬月額(等級表に実在する額)
nichigaku = GEKKYU / 30
assert nichigaku == 10_000, nichigaku
# 傷病手当金の日額 = 標準報酬日額 × 2/3(1円未満切り捨て)
shikyu_hi = int(nichigaku * 2 / 3)
assert shikyu_hi == 6_666, shikyu_hi

tsuki30 = shikyu_hi * 30
assert tsuki30 == 199_980, tsuki30
# 最初の3日は待期で出ない。30日休んだ最初の月は27日ぶん
taiki = shikyu_hi * 27
assert taiki == 179_982, taiki
sa = GEKKYU - tsuki30
assert sa == 100_020, sa

print(f"  標準報酬月額 {GEKKYU:,}円 → 日額 {int(nichigaku):,}円")
print(f"  傷病手当金の日額 = {int(nichigaku):,} × 2 ÷ 3 = {shikyu_hi:,}円")
print(f"  30日ぶん = {tsuki30:,}円(月給との差 {sa:,}円)")
print(f"  最初の月は待期3日を除く27日ぶん = {taiki:,}円")
print("S018 verify: ALL OK")
