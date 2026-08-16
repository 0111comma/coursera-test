#!/usr/bin/env python3
"""S012 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

給与明細から引かれる社会保険料は、会社もほぼ同額を払っている(労使折半)。
年収400万円・東京都・40歳未満(介護保険料なし)の概算。
実際は標準報酬月額の等級表で決まるため、ここでは年収に料率を掛けた概算とする。
"""
INCOME = 4_000_000

# 2026年度の料率
KOSEI = 0.183          # 厚生年金(労使折半)
KENKO = 0.0985         # 健康保険 協会けんぽ東京都(労使折半)
KODOMO = 0.0023        # 子ども・子育て支援金(労使折半)
KOYO_ME = 0.005        # 雇用保険 本人
KOYO_CO = 0.0085       # 雇用保険 会社


def main():
    me_rate = KOSEI / 2 + KENKO / 2 + KODOMO / 2 + KOYO_ME
    co_rate = KOSEI / 2 + KENKO / 2 + KODOMO / 2 + KOYO_CO
    me = INCOME * me_rate
    co = INCOME * co_rate
    kosei_me = INCOME * KOSEI / 2

    assert round(KOSEI / 2 * 1000) / 10 == 9.2 or round(KOSEI / 2, 4) == 0.0915
    assert round(kosei_me) == 366_000, round(kosei_me)
    assert round(me / 10_000) == 59, round(me / 10_000)
    assert round(co / 10_000) == 60, round(co / 10_000)
    assert round((me + co) / 10_000) == 119, round((me + co) / 10_000)
    assert round((INCOME + co) / 10_000) == 460, round((INCOME + co) / 10_000)

    print("S012 verify: ALL OK")
    print(f"  年収 {INCOME:,}円(東京都・40歳未満・概算)")
    print(f"  本人の負担率 {me_rate:.4%} → {me:,.0f}円(画面は約{me / 10_000:.0f}万円)")
    print(f"    うち厚生年金 9.15% = {kosei_me:,.0f}円(画面は36万6千円)")
    print(f"  会社の負担率 {co_rate:.4%} → {co:,.0f}円(画面は約{co / 10_000:.0f}万円)")
    print(f"  合計 {me + co:,.0f}円(画面は約{(me + co) / 10_000:.0f}万円)")
    print(f"  会社から見た費用 {INCOME:,} + {co:,.0f} = {INCOME + co:,.0f}円"
          f"(画面は約{(INCOME + co) / 10_000:.0f}万円)")


if __name__ == "__main__":
    main()
