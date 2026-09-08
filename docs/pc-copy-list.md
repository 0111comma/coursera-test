# PCに持っていくもの / 持っていかないもの(2026-09-08)

目的は**焼く場所をPCに移すこと**。動画を作るのに要らないものは持っていかない。

## 要る(126 MB ほど)

| 場所 | 何 | 要る理由 |
|---|---|---|
| `production/` | shortlib・scenes_*・check_*・bake.sh・bake_status.sh | 焼く本体とゲート一式(12 MB) |
| `assets/fonts/` | M PLUS Rounded 1c | 字幕の書体。**入れないと見た目が変わる**(8.9 MB) |
| `assets/character*/` | ずんだもん・四国めたんの立ち絵 | 立ち絵ありの回で要る(4 MB) |
| `assets/irasuto/` | いらすとやの PNG 14枚 | **git に入っていない。手で運ぶ**(下記) |
| `videos/<ID>-<slug>/` の `plan.md` `script.md` `render.py` `verify.py` | 台本と企画書 | これが動画の中身(全部で 164 KB) |
| `templates/` `ideas/` `CLAUDE.md` `README.md` `requirements.txt` | 型・ネタ帳・規則 | 次の動画を作るのに要る(60 KB) |
| `docs/` | 戦略・調査・ルール集 | ゲートとスキルが参照する(93 MB。**うち大半は調査の画像**なので、焼くだけなら後回しでよい) |

## 要らない(4.7 GB。ここを外すのが効く)

| 場所 | 大きさ | 要らない理由 |
|---|---|---|
| `videos/_rejected/` | **2.0 GB** | ボツ動画。しかも `output/` のフレーム5185枚と音声270本が**間違ってコミットされている**(.gitignore が `_rejected/*/output/work/` しか除いていない)。焼くのに一切要らない |
| `videos/*/output/work/` | **2.6 GB** | 中間フレーム。git 管理外。焼き直せば再生成される |
| `videos/*/output/*.mp4` | 513 MB | 焼き上がった完成品。**作るのに要らない**(投稿用に手元へ置きたいものだけ個別に) |
| `uploads/` | 78 MB | 投稿済みの mp4・srt・サムネ。記録用 |

## 手順(要るものだけ取る)

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/0111comma/coursera-test.git
cd coursera-test
git sparse-checkout set production assets templates ideas docs \
  CLAUDE.md README.md requirements.txt
# 焼きたい回だけ足す(mp4 と work は含まれない)
git sparse-checkout add videos/Z001-joushi-kigen videos/Z002-yotei-hitotsu \
  videos/Z003-sumaho-oku
git checkout claude/youtube-video-1m-subscribers-qryg54
pip install -r requirements.txt
```

`--filter=blob:none` で、過去の mp4 の中身は**必要になるまで落ちてこない**。
これで 2.2 GiB の clone が 100 MB 台で済む。

## git では運べないもの(手で置く)

`assets/irasuto/*.png`(14枚・1.5 MB)は**再配布禁止なのでコミットしていない**。
別途 zip でお渡しするので、clone した `assets/irasuto/` に展開する。
無くても落ちないが、絵が自前のベクター図に差し替わって見た目が変わる。

## ついでに直したほうがよいこと

`videos/_rejected/*/output/` の 5495 ファイル(2 GB)は、コミットされている意味がない。
`.gitignore` を `videos/_rejected/` ごと除く形に直し、履歴からも落とすと clone が軽くなる
(履歴の書き換えになるので、PCへの複製が済んで、ユーザーの許可を得てから)。
