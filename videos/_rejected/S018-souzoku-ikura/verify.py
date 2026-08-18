#!/usr/bin/env python3
"""S018 の数値検証: 申告しなかった場合の上乗せ。"""
HONRAI = 1_000_000        # 本来の税額(仮定)

# 無申告加算税: 50万円までは15%、50万〜300万は20%、300万超は30%
def mushinkoku(zei):
    a = min(zei, 500_000) * 0.15
    b = max(0, min(zei, 3_000_000) - 500_000) * 0.20
    c = max(0, zei - 3_000_000) * 0.30
    return int(a + b + c)

m = mushinkoku(HONRAI)
assert m == 175_000, m          # 50万×15% + 50万×20% = 7.5万 + 10万

# 重加算税(悪質と判断された場合): 最大40%
JU_RITSU = 0.40
ju = int(HONRAI * JU_RITSU)
assert ju == 400_000, ju
assert HONRAI + ju == 1_400_000

# 相続税の基礎控除(法定相続人3人の場合)
def kiso(n):
    return 30_000_000 + 6_000_000 * n
assert kiso(1) == 36_000_000
assert kiso(3) == 48_000_000

print(f"  本来の税額 {HONRAI:,}円 のとき")
print(f"    無申告加算税(15/20/30%の段階) = {m:,}円")
print(f"    重加算税(最大{JU_RITSU:.0%})            = {ju:,}円")
print(f"    → 合計 {HONRAI + ju:,}円(差 {ju:,}円)")
print(f"  ※ 延滞税は別")
print(f"  基礎控除: 法定相続人1人 {kiso(1):,}円 / 3人 {kiso(3):,}円")
print("S018 verify: ALL OK")
