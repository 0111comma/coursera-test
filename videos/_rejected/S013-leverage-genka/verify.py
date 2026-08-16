#!/usr/bin/env python3
"""S013 の数値検証。動画内の数字はすべてここで再計算して一致を確認する。

「日々の値動きの2倍」を目指す商品は、指数が上下してから元の水準に戻ると、
元の水準に戻らない(逓減)。その差を実際に計算する。
"""
START = 100.0
DAY1 = -0.10          # 1日目: 指数が10%下がる
LEV = 2               # 日々の値動きの2倍


def track(moves, lev):
    """日ごとに lev 倍のリターンをかけ合わせる(毎日リセットされる商品の動き)。"""
    v = START
    for m in moves:
        v *= (1 + m * lev)
    return v


def main():
    # 2日目は、指数がちょうど元の100に戻る上げ幅
    idx_after_day1 = START * (1 + DAY1)
    day2 = START / idx_after_day1 - 1

    idx = track([DAY1, day2], 1)
    lev2 = track([DAY1, day2], LEV)

    assert round(idx_after_day1) == 90, idx_after_day1
    assert round(day2 * 1000) / 10 == 11.1, round(day2 * 100, 1)
    assert round(idx, 6) == 100.0, idx
    assert round(lev2, 1) == 97.8, lev2
    # 先に上げて後で下げた場合も、やはり元には戻らない(減り幅は同じではない)
    up_first = track([0.10, 1 / 1.10 - 1], LEV)
    assert up_first < START, up_first
    assert round(up_first, 1) == 98.2, up_first

    print("S013 verify: ALL OK")
    print(f"  1日目: 指数 {START:.0f} → {idx_after_day1:.0f}({DAY1:+.0%})"
          f" / 2倍型 {START:.0f} → {START * (1 + DAY1 * LEV):.0f}({DAY1 * LEV:+.0%})")
    print(f"  2日目: 指数が元に戻る上げ幅は {day2:+.1%}")
    print(f"       指数 {idx:.1f} / 2倍型 {lev2:.1f}")
    print(f"  指数は元どおりでも、2倍型は {START - lev2:.1f} 減っている(約{(START - lev2) / START:.1%})")
    print(f"  先に上げて後で下げた場合も元に戻らない: {up_first:.1f}")


if __name__ == "__main__":
    main()
