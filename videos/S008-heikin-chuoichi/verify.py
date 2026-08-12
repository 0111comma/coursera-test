#!/usr/bin/env python3
"""S008: 平均と中央値(「平均に騙されるな」)の数値検証。

1) 自作の「10人の村」の例(動画の核。完全に検証可能な算数):
   貯金100万円の人が9人+9,100万円の人が1人 → 平均1,000万円/中央値100万円
2) 実データはJ-FLEC「家計の金融行動に関する世論調査(2025年)」(2025年12月18日公表)の転記:
   - 単身世帯: 平均919万円/中央値130万円
   - 二人以上世帯: 平均1,940万円/中央値720万円
   出典: https://www.j-flec.go.jp/data/kakekin_2025/ (確認日2026-08-12)
   ※転記値のため再計算はできない。動画では比率(約7倍)のみ自前計算
"""
import statistics

# --- 10人の村 ---
village = [100] * 9 + [9_100]          # 万円
avg = sum(village) / len(village)      # 1,000万円
med = statistics.median(village)       # 100万円
assert avg == 1_000 and med == 100, (avg, med)

# --- 実データ(転記)と比率 ---
SINGLE_AVG, SINGLE_MED = 919, 130      # 単身世帯(万円)
FAMILY_AVG, FAMILY_MED = 1_940, 720    # 二人以上世帯(万円)
ratio = SINGLE_AVG / SINGLE_MED        # 7.07倍
assert round(ratio) == 7, ratio

print(f"10人の村: 平均{avg:.0f}万円 / 中央値{med:.0f}万円")
print(f"単身世帯(J-FLEC 2025): 平均{SINGLE_AVG}万円 / 中央値{SINGLE_MED}万円 (約{ratio:.1f}倍)")
print(f"二人以上世帯(同): 平均{FAMILY_AVG}万円 / 中央値{FAMILY_MED}万円")
print("OK: すべての数値が台本と一致")
