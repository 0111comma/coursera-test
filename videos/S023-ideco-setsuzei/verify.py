#!/usr/bin/env python3
"""S023 の数値検証。動画内の数字はすべてここで再計算する。

問い: iDeCoに月2万円入れると、税金は年にいくら減るのか。
前提(2026年8月時点・確認日 2026-08-19):
  iDeCoの掛金は全額が所得控除になる(小規模企業共済等掛金控除)
  年収500万円台の会社員を想定し、所得税10%(復興特別所得税2.1%を上乗せ)+住民税10%
  会社員(企業年金なし)の上限は月2万3千円。2026年12月分から月6万2千円に上がる
"""
TSUKI = 20_000
SHOTOKU = 0.10 * 1.021
JUMIN = 0.10
JOGEN_NOW, JOGEN_NEW = 23_000, 62_000


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S023 数値検証(月2万円 / 年収500万円台の会社員)")
    nen = TSUKI * 12
    eq("1年の掛金", nen, 240_000)
    eq("合わせた税率(%の100倍)", round((SHOTOKU + JUMIN) * 10000), 2021)

    heru = round(nen * (SHOTOKU + JUMIN))
    eq("1年で減る税金", heru, 48_504)
    eq("20年ぶん", heru * 20, 970_080)
    eq("月あたりに直すと", heru // 12, 4_042)

    # 2026年12月から上限が上がる
    eq("いまの上限", JOGEN_NOW, 23_000)
    eq("12月からの上限", JOGEN_NEW, 62_000)
    eq("上限まで入れたときの1年ぶん",
       round(JOGEN_NEW * 12 * (SHOTOKU + JUMIN)), 150_362)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
