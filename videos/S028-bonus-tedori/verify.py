#!/usr/bin/env python3
"""S028 の数値検証。動画内の数字はすべてここで再計算する。

問い: ボーナス50万円の手取りはいくらか。
前提(2026年度・確認日 2026-08-19):
  40歳未満・東京・協会けんぽの会社員
  社会保険料 = 健康保険4.925% + 子ども子育て支援金0.115% + 厚生年金9.15%
             + 雇用保険0.5% = 14.69%(賞与にも同じ率がかかる)
  所得税の率は前の月の給料で決まる。この例では 8.168%(扶養なし)と仮定
"""
BONUS = 500_000
SHAHO = 0.1469
ZEI = 0.08168


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S028 数値検証(ボーナス50万円 / 40歳未満・東京)")
    shaho = round(BONUS * SHAHO)
    eq("社会保険料", shaho, 73_450)

    kazei = BONUS - shaho
    eq("税がかかる額", kazei, 426_550)

    zei = round(kazei * ZEI)
    eq("所得税", zei, 34_841)

    tedori = BONUS - shaho - zei
    eq("手取り", tedori, 391_709)
    eq("消える額", BONUS - tedori, 108_291)

    # 住民税は賞与から引かれない(前年の所得に対して毎月の給料から引かれている)
    print("  注: 住民税は賞与からは引かれない(毎月の給料から引かれている)")

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
