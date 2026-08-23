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
