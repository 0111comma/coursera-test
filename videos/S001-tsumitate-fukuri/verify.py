# S001「411万円」動画内のすべての数値を検証するスクリプト
# 実行: python3 verify.py
#
# 前提(すべて仮定であり、将来の運用成果を保証するものではない):
MONTHLY = 10_000      # 毎月の積立額(円)
YEARS = 20            # 積立期間(年)
ANNUAL_RATE = 0.05    # 想定年利(仮定)。月次複利(年利/12を毎月適用)で計算

months = YEARS * 12
r = ANNUAL_RATE / 12

# 毎月末に MONTHLY を積み立て、月次複利で運用した場合の将来価値
# FV = P * ((1+r)^n - 1) / r
fv = MONTHLY * ((1 + r) ** months - 1) / r
principal = MONTHLY * months
gain = fv - principal

print(f"積立総額(元本)      : {principal:,.0f} 円")
print(f"20年後の評価額(FV)  : {fv:,.0f} 円")
print(f"運用益              : {gain:,.0f} 円")
print(f"評価額(万円丸め)    : 約{round(fv / 10_000)}万円")
print(f"元本(万円)          : {principal / 10_000:.0f}万円")
print(f"運用益(万円丸め)    : 約{round(gain / 10_000)}万円")

# 動画内の比較用: 利息ゼロ(銀行に置いただけ)との差
print(f"利息ゼロとの差      : 約{round(gain / 10_000)}万円")

# 参考: 年利3%(仮定)の場合(「利回りは仮定」を示す比較パターン)
r3 = 0.03 / 12
fv3 = MONTHLY * ((1 + r3) ** months - 1) / r3
print(f"[参考] 年利3%仮定    : 約{round(fv3 / 10_000)}万円")

# 参考: 月3万円の場合(ピークの数字。将来価値は積立額に比例する)
fv_3man = 30_000 * ((1 + r) ** months - 1) / r
print(f"[参考] 月3万円・年利5%仮定: 約{round(fv_3man / 10_000)}万円")

# フリ(視聴者の素朴な予測): 「20年で411万なら10年でちょうど半分」の値
# → 実際の10年目(155万)との差が「複利は直線ではない」のオチになる
half_linear = fv / 2
fv10 = MONTHLY * ((1 + r) ** 120 - 1) / r
print(f"直線予想の10年目(411万の半分): {half_linear / 10_000:.1f}万円")
print(f"実際の10年目               : 約{round(fv10 / 10_000)}万円")
print(f"後半10年の増加分            : 約{round((fv - fv10) / 10_000)}万円")

# 人間スケール換算: 月1万円は1日いくらか
print(f"月1万円の1日あたり          : 約{MONTHLY / 30:.0f}円")
