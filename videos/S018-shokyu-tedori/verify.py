#!/usr/bin/env python3
"""S018 の数値検証。動画内の数字はすべてここで再計算する。

問い: 月給が1万円上がると、手取りはいくら増えるのか。
前提(2026年度・確認日 2026-08-18):
  40歳未満・東京・協会けんぽ・年収500万円台の会社員
  健康保険 9.85% の半分 = 4.925%
  子ども・子育て支援金 0.23% の半分 = 0.115%
  厚生年金 18.3% の半分 = 9.15%
  雇用保険(労働者負担) 0.5%
  → 本人が払う社会保険料は合計 14.69%
  所得税 10% + 復興特別所得税 2.1%分 = 10.21%
  住民税 10%
社会保険料は先に引かれ、**その残りに**税がかかる。
"""
AGARI = 10_000
SHAHO_RATE = 0.04925 + 0.00115 + 0.0915 + 0.005      # = 0.1469
SHOTOKU_RATE = 0.10 * 1.021                          # 復興特別所得税ぶんを上乗せ
JUMIN_RATE = 0.10


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S018 数値検証(月給1万円アップ / 40歳未満・東京・年収500万円台)")
    eq("社会保険料の合計率(%表示の100倍)", round(SHAHO_RATE * 10000), 1469)

    shaho = round(AGARI * SHAHO_RATE)
    eq("引かれる社会保険料", shaho, 1_469)

    kazei = AGARI - shaho
    eq("税がかかる額", kazei, 8_531)

    shotoku = round(kazei * SHOTOKU_RATE)
    jumin = round(kazei * JUMIN_RATE)
    eq("所得税", shotoku, 871)
    eq("住民税", jumin, 853)

    tedori = AGARI - shaho - shotoku - jumin
    eq("手取りの増え", tedori, 6_807)
    eq("消える額", AGARI - tedori, 3_193)

    # 年に直すと
    eq("年の手取り増(ボーナスを除く12ヶ月)", tedori * 12, 81_684)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
