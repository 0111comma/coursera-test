#!/usr/bin/env python3
"""S034「大手のままか、同じ回線のオンライン専用プランか」の数値検証。

P-M(35歳・男性・会社員)向け。欲求B(大きな選択を間違えたくない)。

**2026-08-30 に数値を全面更新した。**旧版は MM総研 2025年1月調査(平均4,356円 /
大手5,025円)で1年半古く、そのまま台本にすると「時点表記のある古い数字」になっていた。

| 前提 | 値 | 出どころ | 確度 |
|---|---|---|---|
| スマホ代の平均 | 4,198円/月 | MM総研 2026年7月調査 | B |
| MNO4ブランド(大手) | 4,853円/月 | 同上 | B |
| サブブランド | 3,296円/月 | 同上 | B |
| MVNO | 1,979円/月 | 同上 | B |
| ahamo | 2,970円/月 | ahamo公式(30GB + 5分かけ放題) | **A** |
| ahamo かけ放題オプション | 1,100円/月 | ahamo公式 | **A** |

**確度Bなのは、この環境から一次資料を開けないため。**
egress proxy が m2ri.jp・itmedia・k-tai.watch をいずれも遮断する。
数値は複数の独立した報道(ケータイWatch / ITmedia / マイナビ / Web担)の
検索スニペットが一致することで確認した(2026-08-30 確認)。
ahamo の料金だけは公式LPのスニペットで直接確認できたので確度A。

**投稿前にユーザーの環境で料金を再確認すること。**

この動画は**差額を30年積む計算をしない**(S033と同型の反復になるため)。
出すのは「月の差」と「1年の差」まで。判定は「今の使用ギガを見る」で閉じる。
"""

# ---- スマホ代の月額(MM総研 2026年7月調査。端末代の分割は含まない)
AVERAGE = 4_198        # 利用者全体の平均
MAJOR = 4_853          # MNO4ブランド(ドコモ・au・ソフトバンク・楽天)
SUB_BRAND = 3_296      # サブブランド(UQ・ワイモバイル等)
MVNO = 1_979           # MVNO(いわゆる格安SIM)

# ---- 大手のオンライン専用プラン(ahamo公式。30GB + 5分かけ放題)
ONLINE = 2_970
ONLINE_KAKEHODAI = 1_100   # 24時間かけ放題にする場合の追加額

DIFF = MAJOR - ONLINE                   # 大手の平均 − オンライン専用
YEAR = DIFF * 12                        # 1年ぶんの差

# かけ放題を付けても差が残るか(「安いのは条件を削っているからだ」への答え)
DIFF_WITH_KAKEHODAI = MAJOR - (ONLINE + ONLINE_KAKEHODAI)
YEAR_WITH_KAKEHODAI = DIFF_WITH_KAKEHODAI * 12

# サブブランドとの比較(第3の選択肢。概要欄用)
DIFF_SUB = MAJOR - SUB_BRAND

if __name__ == "__main__":
    print("スマホ代の月額(MM総研 2026年7月調査。端末代の分割を除く):")
    for n, v in (("利用者全体の平均", AVERAGE), ("MNO4ブランド(大手)", MAJOR),
                 ("サブブランド", SUB_BRAND), ("MVNO", MVNO)):
        print(f"  {n:26} {v:>6,}円")
    print(f"  {'ahamo(30GB+5分かけ放題)':26} {ONLINE:>6,}円   ← ahamo公式")

    print(f"\n大手 {MAJOR:,} − オンライン専用 {ONLINE:,} = **{DIFF:,}円/月**")
    assert DIFF == 1_883, DIFF
    print(f"1年ぶん: {DIFF:,} × 12 = **{YEAR:,}円**")
    assert YEAR == 22_596, YEAR

    print(f"\n24時間かけ放題({ONLINE_KAKEHODAI:,}円)を足しても:")
    print(f"  {MAJOR:,} − ({ONLINE:,} + {ONLINE_KAKEHODAI:,}) = "
          f"**{DIFF_WITH_KAKEHODAI:,}円/月** / 1年 {YEAR_WITH_KAKEHODAI:,}円")
    assert DIFF_WITH_KAKEHODAI == 783, DIFF_WITH_KAKEHODAI
    assert YEAR_WITH_KAKEHODAI == 9_396, YEAR_WITH_KAKEHODAI

    print(f"\n(参考)大手 − サブブランド = {DIFF_SUB:,}円/月")
    assert DIFF_SUB == 1_557, DIFF_SUB

    # 台本で**声に出す**値。丸めない(S032の「82歳」の再発防止)
    print(f"\n台本で言う値: 大手{MAJOR:,}円 / オンライン専用{ONLINE:,}円 / "
          f"差{DIFF:,}円 / 1年{YEAR:,}円 / かけ放題込みでも{DIFF_WITH_KAKEHODAI}円 ✓")
