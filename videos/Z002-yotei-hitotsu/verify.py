#!/usr/bin/env python3
"""動画に出る数の検算(check_video が全動画に要求する)。

この回に**計算らしい計算は無い**。出るのは年と年齢と動作の個数だけで、
どれも plan.md §10 の前提表に根拠と出典がある。
ここでやるのは、**表の年から引き算で作った数だけ**の再計算。
"""
IMA = 2026                    # 動画の時点(plan.md §10 の確認日)
SEIRITSU = 49                 # 『人生の短さについて』の執筆年(西暦。通説)
MONTAIGNE_UMARE, MONTAIGNE_YAMETA = 1533, 1570   # モンテーニュ

print(f"西暦{SEIRITSU}年 → いま({IMA}年)まで {IMA - SEIRITSU}年")
print(f"モンテーニュが職を手放した年齢: {MONTAIGNE_YAMETA - MONTAIGNE_UMARE}歳"
      f"(動画で言うのは37歳)")
assert MONTAIGNE_YAMETA - MONTAIGNE_UMARE == 37
print("動作の個数: 1件(消す予定の数。plan.md §10)")
print("OK: 動画で声に出す数は、すべて前提表か上の引き算から出ている")
