MONTHLY_MAN = 3
MONTHS = 12
ANNUAL_MAN = MONTHLY_MAN * MONTHS
TSUMITATE_MAN = 120
GROWTH_MAN = 240
assert ANNUAL_MAN == 36 and ANNUAL_MAN <= TSUMITATE_MAN

if __name__ == "__main__":
    print({k:v for k,v in globals().copy().items() if k.isupper()})
