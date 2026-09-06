#!/usr/bin/env python3
"""Z001 の数値検証。この動画に出る数は「1900年前」の1つだけ。

| 前提 | 値 | 出どころ | 確度 |
|---|---|---|---|
| 『提要』の成立 | 2世紀前半(西暦100〜130年ごろ) | エピクテトス(50頃–135頃)の講義をアリアノスがまとめたもの | B |
| いまの年 | 2026年 | 制作時点 | 確定 |

**「2000年前」と丸めない**(docs/channel-zunda/strategy.md §5.2 の実年表記)。
出典: https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0236
(Enchiridion 1。2026-09-02確認・確度B)
"""

NOW = 2026
# 2世紀前半 = 西暦100〜130年ごろ。幅があるので両端で計算する
WRITTEN_FROM, WRITTEN_TO = 100, 130

AGO_MAX = NOW - WRITTEN_FROM      # 古いほうの端
AGO_MIN = NOW - WRITTEN_TO        # 新しいほうの端


def rounded_100(n: int) -> int:
    """百年単位に丸める(動画で言う「1900年前」の作り方)。"""
    return round(n / 100) * 100


if __name__ == "__main__":
    print(f"『提要』の成立: 西暦 {WRITTEN_FROM}〜{WRITTEN_TO} 年ごろ(2世紀前半)")
    print(f"いま({NOW}年)から見ると {AGO_MIN}〜{AGO_MAX} 年前")
    print(f"百年単位に丸めると: {rounded_100(AGO_MIN)}〜{rounded_100(AGO_MAX)} 年前")
    # 動画で言うのは「1900年前」。両端を丸めても 1900 に収まること
    assert rounded_100(AGO_MIN) == 1900, rounded_100(AGO_MIN)
    assert rounded_100(AGO_MAX) == 1900, rounded_100(AGO_MAX)
    print("\n台本で言う値: 2世紀前半 / 1900年前 ✓")
