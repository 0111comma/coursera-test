#!/usr/bin/env python3
"""S017 の数値検証。動画内の数字はすべてここで再計算する。

前提(2026年8月時点・確認日 2026-08-18):
  ふるさと納税は、上限までの寄付なら 自己負担2000円を除いて税金から引かれる。
  上限を超えた分は**引かれない**(そのまま自腹)。
  返礼品は寄付額の3割まで(総務省の3割基準)。

ここでは「上限の内で1万円ふやす」と「上限を超えて1万円出す」を比べる。
自己負担2000円は年に1回ぶんの固定額なので、**増やした1万円の側**には乗らない。
"""
KIFU = 10_000
HENREI_RATE = 0.3


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S017 数値検証")
    henrei = int(KIFU * HENREI_RATE)
    eq("返礼品の目安(寄付1万円の3割)", henrei, 3_000)

    # 上限の内: 1万円は税金からそのまま引かれる → 手出しは増えない
    uchi_tedashi = KIFU - KIFU              # 控除1万円
    eq("上限の内 手出し", uchi_tedashi, 0)
    eq("上限の内 差し引き", henrei - uchi_tedashi, 3_000)

    # 上限の外: 1万円は引かれない → まるまる手出し
    soto_tedashi = KIFU - 0                 # 控除0円
    eq("上限の外 手出し", soto_tedashi, 10_000)
    eq("上限の外 差し引き", henrei - soto_tedashi, -7_000)

    # 内と外の差
    eq("内と外の差", (henrei - uchi_tedashi) - (henrei - soto_tedashi), 10_000)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
