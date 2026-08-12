# 伸びるショート動画の型(リサーチ→制作ルール)

調査日: 2026-08-12。複数ソースで一致した知見のみをルール化した。
各ルールは `production/shortlib.py` と `templates/script-short.md` に実装されている。

## 数字で分かっていること

- **離脱の50〜60%は最初の3秒**で起きる。ショートの勝負は冒頭1〜2秒
- 1カット1〜3秒のテンポに再編集して**再生数2.5倍**になった実例
- Shortsの平均視聴時間は45秒→58秒に伸びており、**情報密度の高い長め(40〜60秒)**が評価される傾向
- 冒頭の維持率が強い動画は、総インプレッションで3〜5倍の差がつく(YouTube Creator Insiderデータの引用)

## 制作ルール(R1〜R12)

### 冒頭(0〜2秒)

- **R1 ミュート可読**: 冒頭フレームだけで「何の動画か」が音なしで分かる。画面中央に3〜6語の大テキスト(本チャンネルでは「数字」)。挨拶・自己紹介・前置きは禁止
- **R2 初手から動く**: 静止画で始めない。数字のカウントアップ等、最初の1秒に動きを入れて親指を止める
- **R3 第一声で言い切る**: ナレーションの最初の文はフックの数字・結論。「今日は〜について」は禁止

### テンポ(2秒ルール)

- **R4 画面変化は1〜3秒ごと**: 同じ画面を3秒以上見せない。グラフは一気に見せず「積み上がる・伸びる・増える」動きで段階的に見せる
- **R5 1ユニット=1文**: ナレーションは短文に割り、1文ごとに画面(または画面内の状態)を変える。無駄な間はカットし話速は速め(1.15〜1.25)
- **R6 音声とテロップの完全同期**: 字幕は読み上げている文そのもの。音と字幕がズレるとストレスで離脱される

### テロップ(縦型の定番)

- **R7 太ゴシック+縁取り+影**: 縁取りは文字サイズの5〜10%。スマホで潰れない太さ・高コントラスト
- **R8 キーワードだけ強調色**: フルテロップでも重要語(数字)だけ黄色。黄色文字+黒縁は強調の定番
- **R9 セーフエリア**: 右端(ボタン列)・最下部(タイトルUI)に重要情報を置かない

### 構成

- **R10 1動画1メッセージ**: 詰め込まない。SDS(要点→詳細→要点)で、詳細は「種明かし」として展開
- **R11 ループとコメント誘発**: 最後は冒頭に概念的につながる終わり方(リワッチで冒頭が意味を持つ)+視聴者への質問でコメントを誘発。「チャンネル登録してね」より質問のほうが効く
- **R12 タイトルは結末を見せない**: 疑問形・続きが気になる形。「〜がこちら」「いくらになる?」

### 音声・BGM

- **R13 解説ショートのAI音声はVOICEVOXが標準**: ずんだもんは「解説動画で聞かない日がない」レベルに受容されており、親しみやすさ(「〜なのだ」口調)が難しい内容の間口を広げる。本チャンネルは**ずんだもん(ノーマル)**を既定にする(クレジット「VOICEVOX:ずんだもん」必須)
- **R14 BGMは小さく敷く**: 無音は単調。ナレーションを邪魔しない音量(-18〜20dB)で敷き、テンポ感を作る

## 本チャンネルの型への落とし込み(ショート)

```
0-1秒   数字カウントアップ(R1,R2,R3)     「411万円。」
1-8秒   種明かし開始。1文ごとに画面変化    元本→運用益が積み上がる棒グラフ
8-20秒  仕組み(複利)を動くグラフで        線が伸びる→注釈がポンと出る
20-30秒 別パターン比較(仮定の明示)        棒が1本ずつ出る
30-40秒 ループ+質問                     「月3万なら1233万。あなたは月いくら?」
```

- 尺の目安: **35〜50秒**(密度優先。伸ばすための水増し禁止)
- コンプライアンス表示(「年利◯%と仮定」バッジ等)は全編維持(戦略§6と両立させる)

## 出典

一致度の高い順に主要ソースを記載(いずれも2025〜2026年の記事)。

- 冒頭2秒・離脱データ・ミュート可読: [The First 3 Seconds: Hook Structures That Stop Scroll on Shorts](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026), [YouTube Shorts Retention Rate (2026): What Works](https://www.shortimize.com/blog/youtube-shorts-retention-rate), [YouTubeショートの伸ばし方(Xcuu)](https://xcuu.jp/column/youtube-shortstips/)
- 視聴維持率・冒頭で決まる: [【2026年最新】YouTubeショートが伸びない原因と対策(ムビスケ)](https://www.muvisuke.com/column/547/), [YouTube ショート成長ガイド (2026)](https://youseo.app/ja/youtube-shorts-growth-guide)
- ループ・リワッチ・callback: [The YouTube Shorts Retention Curve Playbook (2026)](https://aibrify.com/blog/youtube-shorts-retention-curve-playbook), [Best YouTube Shorts Hooks and Formats in 2026](https://www.conbersa.ai/learn/best-youtube-shorts-hooks)
- ジェットカット・1カット1〜3秒・2.5倍実例・倍速: [ジェットカットを使いこなす(Leading communication)](https://www.le-commu.co.jp/news/news-2575/), [テンポのよい動画で視聴維持率をあげよう(動画の窓口)](https://dougano-madoguchi.com/?p=2917), [ショート動画編集の完全攻略(solezore)](https://solezore.co.jp/blog/short-video-edit/)
- テロップ設計(縁取り5〜10%・黄色強調・太ゴシック): [テロップ・字幕デザインの教科書(freedoor)](https://freedoor.co.jp/blog/video-telop-design-guide/), [縦型動画のテロップ設計(ZVA)](https://zva.co.jp/knowledge/vertical-caption-design.html), [動画テロップの作法](https://0120.co.jp/blog/video-125/)
- 長め高密度Shortsの傾向(平均視聴時間45→58秒): [ショート動画トレンド2026](https://0120.co.jp/blog/video-43/)
- 1動画1メッセージ・タイトル・継続検証: [YouTubeショート再生回数の伸ばし方(VIDWEB)](https://vidweb.co.jp/column/8103/), [YouTube公式ヘルプ: ショートの検索と見つけやすさのヒント](https://support.google.com/youtube/answer/11914225?hl=ja)
- ずんだもん/VOICEVOXの受容: [AIずんだもん完全入門(findAI)](https://ai.appmatch.jp/843-2/), [VOICEVOX徹底解説](https://ai-yomiage.com/blog/voicevoxai-QqRGUs)
- 金融系で伸びる要素(図解・平易・信頼性): [金融業界YouTubeチャンネル成功事例(key-movie)](https://key-movie.forfreelance.co.jp/blog/youtube/finance/), [お金の勉強に役立つYouTubeチャンネル15選](https://aibashiro.jp/contents/studying-money-youtube/)

※ 一部記事はこの作業環境のネットワークポリシーで本文取得がブロックされたため、検索結果の要約ベース。複数ソースで一致した項目のみ採用した。
