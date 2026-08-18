#!/usr/bin/env python3
"""S016 の数値検証: NISAの枠は翌年に、簿価ぶんだけ戻る。"""
SHOGAI = 18_000_000      # 生涯投資枠
NENKAN = 3_600_000       # 年間投資枠

BOKA = 1_000_000         # 買った値段(簿価)
URINE = 1_500_000        # 売った値段

rieki = URINE - BOKA
assert rieki == 500_000, rieki

# 翌年に戻るのは簿価ぶん。売値ではない
modoru = BOKA
assert modoru == 1_000_000
kieru = URINE - modoru
assert kieru == 500_000, kieru

# 値下がりして売った場合は、簿価まるごと戻る(売値より多く戻る)
URINE_SON = 800_000
modoru_son = BOKA
assert modoru_son > URINE_SON
assert modoru_son - URINE_SON == 200_000

# 生涯投資枠に対する割合
assert SHOGAI // BOKA == 18
assert NENKAN // BOKA == 3

print(f"  生涯投資枠 {SHOGAI:,}円 / 年間投資枠 {NENKAN:,}円")
print(f"  {BOKA:,}円で買って {URINE:,}円で売る → 利益 {rieki:,}円(非課税)")
print(f"  翌年に戻る枠 = 買った値段の {modoru:,}円")
print(f"  売った値段との差 {kieru:,}円ぶんは、枠として戻らない")
print(f"  逆に {URINE_SON:,}円に値下がりして売ると、戻るのは {modoru_son:,}円("
      f"売値より {modoru_son - URINE_SON:,}円多い)")
print("S016 verify: ALL OK")
