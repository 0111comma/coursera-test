#!/usr/bin/env python3
"""S016 の数値検証。動画内の数字はすべてここで再計算する。

制度(2026年8月時点・確認日 2026-08-18):
  つみたて投資枠  年120万円
  成長投資枠      年240万円
  合計            年360万円
  一生ぶんの上限  1800万円(うち成長投資枠は1200万円まで)
"""
TSUMITATE_YEAR = 1_200_000
SEICHO_YEAR = 2_400_000
SHOGAI = 18_000_000
SEICHO_SHOGAI = 12_000_000


def main():
    ok = True

    def eq(name, got, want):
        nonlocal ok
        hit = got == want
        ok &= hit
        print(f"  [{'OK' if hit else 'NG'}] {name}: {got:,} (期待 {want:,})")

    print("S016 数値検証")
    # 1. つみたて投資枠の月あたり = 分かれ目の数字
    eq("つみたて投資枠の月あたり", TSUMITATE_YEAR // 12, 100_000)
    # 2. 成長投資枠の月あたり
    eq("成長投資枠の月あたり", SEICHO_YEAR // 12, 200_000)
    # 3. 2つ合わせた年と月
    eq("合わせた年の上限", TSUMITATE_YEAR + SEICHO_YEAR, 3_600_000)
    eq("合わせた月の上限", (TSUMITATE_YEAR + SEICHO_YEAR) // 12, 300_000)
    # 4. 成長投資枠だけでは埋まらない残り
    eq("成長投資枠で埋まらない残り", SHOGAI - SEICHO_SHOGAI, 6_000_000)
    # 5. 最短で埋まる年数(合わせて使った場合)
    eq("最短の年数", SHOGAI // (TSUMITATE_YEAR + SEICHO_YEAR), 5)
    # 6. つみたて投資枠だけの年数
    eq("つみたて投資枠だけの年数", SHOGAI // TSUMITATE_YEAR, 15)

    print("結果:", "全一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
