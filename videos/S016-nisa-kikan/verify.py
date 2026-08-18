#!/usr/bin/env python3
"""S016 の数値検証: NISAの金融機関変更の期限。

金額の計算は無い動画なので、検証するのは**日付の勘定**。
2026年に変更したい場合の受付期間と、残り日数を確かめる。
"""
from datetime import date

# 受付は「変更したい年の前年10月1日」から「その年の9月30日」まで
KAITEN = date(2025, 10, 1)
SHIME = date(2026, 9, 30)
assert (SHIME - KAITEN).days == 364, (SHIME - KAITEN).days

# 動画の公開時点(2026年8月末)から締切までの残り
KOUKAI = date(2026, 8, 26)
nokori = (SHIME - KOUKAI).days
assert nokori == 35, nokori

# 1月に1度でも買うと、その年は変更できない → 次に変えられるのは翌年
# 1月に買った人が次に手続きできる年
assert SHIME.year + 1 == 2027

print(f"  受付期間: {KAITEN} 〜 {SHIME}({(SHIME - KAITEN).days}日間)")
print(f"  公開日 {KOUKAI} の時点で、締切まで残り {nokori}日")
print(f"  その年に1度でも買うと変更不可 → 次に変えられるのは {SHIME.year + 1}年ぶん")
print("S016 verify: ALL OK")
