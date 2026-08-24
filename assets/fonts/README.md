# フォント

## M PLUS Rounded 1c(丸ゴシック)

- `MPLUSRounded1c-900.ttf` — Black。テロップ・見出し・図の文字に使う
- `MPLUSRounded1c-700.ttf` — Bold(予備)

**ライセンス: SIL Open Font License 1.1**(font name table ID 14 = http://scripts.sil.org/OFL)。
Copyright 2016 The Rounded M+ Project Authors.
OFL は再配布を認めているので、このリポジトリに置いてよい。

### なぜ入れたか

2026-08-23、ユーザー指摘「まずフォントどうにかして」。
競合(@bankacademy)のテロップは**丸ゴシック**で、こちらの Noto Sans CJK は
角ばったゴシック。並べると別物に見えていた。
コンテナには丸ゴシックが1本も入っていない(`fc-list :lang=ja` は Noto と IPA だけ)。

### 取得元

`registry.npmjs.org` の `@openfonts/m-plus-rounded-1c_all`(woff)を
fontTools で ttf に戻した。github.com はこのセッションの egress ポリシーで 403。

```
npm pack @openfonts/m-plus-rounded-1c_all
tar xzf openfonts-m-plus-rounded-1c_all-*.tgz
python3 -c "
from fontTools.ttLib import TTFont
f = TTFont('package/files/m-plus-rounded-1c-all-900.woff'); f.flavor = None
f.save('MPLUSRounded1c-900.ttf')"
```

### 使い方

`fplib.use_fp_theme()` が `_setup_font()` を呼んで登録する。
**`shortlib.setup_fonts()` は触っていない**ので、既存30本の見た目は変わらない。

---

## RocknRoll One(2026-08-24 追加。字幕・図・帯の標準書体)

**ユーザーの選定**(2026-08-24)。それまでの M PLUS Rounded 1c Black について
「すごいダサい。デフォルトっぽくてダサい」との指摘を受け、6書体を実際のフレームで
比べたうえで選んだ。

| 項目 | 内容 |
|---|---|
| ファイル | `RocknRollOne.ttf`(family = `RocknRoll One`) |
| ウェイト | **400 の1つだけ**。`font.weight` に 900 や bold を指定しない |
| ライセンス | **SIL Open Font License 1.1**(`RocknRollOne-LICENSE.txt` に全文) |
| 著作権 | Copyright 2020 The RocknRoll Project Authors |
| 配布元 | Google Fonts (https://github.com/google/fonts) |
| 取得方法 | `npm pack @fontsource/rocknroll-one@5.3.0` → `files/rocknroll-one-japanese-400-normal.woff2` を fontTools で ttf 化 |
| 商用利用 | **可**(OFL 1.1。フォント単体の販売のみ禁止) |
| 確認日 | 2026-08-24 |

**このリポジトリの環境では github.com が塞がれている**ため、npm 経由で取得している。
woff2 → ttf の変換は fontTools(brotli 必須)で行う。

### 注意: `※` が入っていない

RocknRoll One には REFERENCE MARK (U+203B) が無く、そのまま描くと豆腐(□)になる。
免責バッジの「※ 運用しない場合の計算」で使っていたため、`fplib` 側で対処している。
