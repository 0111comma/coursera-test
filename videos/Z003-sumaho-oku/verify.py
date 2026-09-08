#!/usr/bin/env python3
"""動画に出る数の検算(check_video が全動画に要求する)。

この回に**計算らしい計算は無い**。出るのは年と年齢と動作の個数だけで、
どれも plan.md §10 の前提表に根拠と出典がある。
ここでやるのは、**表の年から引き算で作った数だけ**の再計算。
"""
IMA = 2026                    # 動画の時点(plan.md §10 の確認日)
SHOHAN = 1670                 # 『パンセ』初版(ポール・ロワイヤル版)
PASCAL_UMARE, PASCAL_SHIBO = 1623, 1662
VOLTAIRE_HANRON = 1734        # 『哲学書簡』フランス語版

sa = IMA - SHOHAN
print(f"初版{SHOHAN}年 → いま({IMA}年)まで {sa}年 → 動画では概数で「350年」と言う")
assert 340 <= sa <= 360, "概数「350年」から離れすぎ"
print(f"パスカルの没年齢: {PASCAL_SHIBO - PASCAL_UMARE}歳(動画で言うのは39歳)")
assert PASCAL_SHIBO - PASCAL_UMARE == 39
print(f"反論({VOLTAIRE_HANRON}年)は初版の {VOLTAIRE_HANRON - SHOHAN}年あと"
      f"(**「まっさきに」とは言わない**根拠)")
print("動作の個数: 1件(今夜、棚に置くスマホ。plan.md §10)")
print("OK: 動画で声に出す数は、すべて前提表か上の引き算から出ている")
