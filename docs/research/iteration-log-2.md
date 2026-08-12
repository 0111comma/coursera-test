# 検証ループ記録 第2〜30ループ(全要素の見直し)

2026-08-12実施。第1ループ(プロット、[iteration-log.md](iteration-log.md))に続き、
「すべての要素を自分で勝手に決めない」方針で、残り29要素を「調査→基準化→検証→改善」した。

| L | 要素 | 調査結論 → 検証結果と改善 |
|---|---|---|
| 2 | カラーパレット | コントラスト最優先・金融は青=信頼/金=お金のアクセント・黒×金=プレミアム・70/20/10。黒背景+青+黄アクセントは合格。**運用益の橙は色連想がズレて不合格→金色(#c98500)に変更**(青+金のCVD/コントラスト検証PASS) |
| 3 | フォント | テロップの定番は源ノ角ゴシック(=Noto Sans CJK JP)の太ウェイト。**IPAゴシック+疑似太字は不合格→Noto Sans CJK JP Black/Boldへ全面切替** |
| 4 | 話者・声 | ずんだもんは解説系の定番で合格。話速1.2は妥当域(1.2〜1.3)。**強調ユニットの抑揚ノブがなく→intonationScale対応を追加** |
| 5 | BGM | 音量は本編100:BGM15(10〜30)が定石→実効約15%で合格。lo-fi曲調も目的整合 |
| 6 | 効果音 | 用途は切替/強調/操作の3種・表示の頭に同期・入れすぎ禁止。**SEゼロで不合格→合成SE(pop/don)を強調4箇所に追加** |
| 7 | 冒頭フレーム | フィードでは静止した最初のフレーム+タイトルが見える。**カウント途中の中途半端な数字が先頭で不合格→完成形カバーフレーム(0.07秒)を先頭に挿入** |
| 8 | フィード表示・サムネ | UIオーバーレイを避け中央70%に配置。**thumbnail.pngの自動書き出しを追加**(モバイルのサムネ設定用) |
| 9 | イージング | 自動アニメ=easeInOut/反応=easeOutが定石。**全部easeOutで部分不合格→グラフ成長系をeaseInOutへ** |
| 10 | テロップの出し方 | ずんだもん/ゆっくり系の定番は文単位の全文置き換え(カラオケ式は歌系)→合格。表示瞬間のポップ(スケール収束)を追加 |
| 11 | 縦型レイアウト | スマホ視線は上→下。見出し/図/字幕の階層は合格 |
| 12 | グラフの見せ方 | 段階的リビール+注釈が定石(1度に1データ点)→実装済みで合格 |
| 13 | ペーシング | 画面変化を切らさないのが維持率の定石。**長ユニットで3秒超の静止があり不合格→全ユニットのアニメ時間を延長し常時構築の動きに** |
| 14 | キャラ利用規約 | ずんだもんはYouTube収益化OK・クレジット必須(公式ガイドライン)→概要欄記載済みで合格 |
| 15 | パワーワード | 常識揺さぶり+【】囲み+検証型(〜してみた)が高性能。**タイトルを「月1万円の積立は意味ない?【20年分計算してみた】」に改稿** |
| 16 | 概要欄・タグSEO | タイトル冒頭30字が検索に効く・説明欄空白はNG・#shorts必須。**#shortsを追加**、他は合格 |
| 17 | 投稿時間 | 日本は平日17〜20時(ピーク20-23時)・土日10〜12時→運用ルール新設(戦略に記録) |
| 18 | ループ再生の継ぎ目 | 「最後の文が最初に繋がる」物語ループが定石→質問→(リプレイ)答えの構造で合格 |
| 19 | ラウドネス | YouTube基準は-14LUFS(小さくても持ち上げられない)。**-16設定は不合格→-14に修正** |
| 20 | 字幕サイズ | フルHDで画面高6〜8%相当・スマホは大きめ鉄則。**40pt(2.9%)は小さく不合格→52pt+12字折り返しに拡大** |
| 21 | 出典の見せ方 | 画面+概要欄の二段構えが理想→概要欄・仮定バッジ合格、早見表に計算方式キャプション追加 |
| 22 | バズ実例の共通項 | テキストオーバーレイ+58%・意外性×有用性・ビフォーアフター→v3は全て実装済みで合格 |
| 23 | 視聴者層データ | Shorts毎日視聴は10代7割/20代6割/30代4割→ターゲット(20-35)整合・語彙は平易維持で合格 |
| 24 | ブランディング | 短く・覚えやすく・テーマ即分かるオリジナル組合せ→「数字で見るお金の教科書」合格 |
| 25 | A/Bテスト運用 | 公式「テストと比較」でサムネ3案・1要素ずつ・CTRより維持率優先→運用ルール化 |
| 26 | 品質チェック自動化 | チェックリスト標準化が品質のばらつきを防ぐ→**production/check_video.py を実装**(尺・音量・解像度・禁止語・クレジット等14項目) |
| 27 | ミュート視聴 | モバイルの75%(ミレニアル85%)が無音視聴→全シーン見出し+図+全文テロップで音なし完結、合格 |
| 28 | カバーフレーム情報量 | ミュート可読は3〜6語→「411万円」+「月1万円×20年」の2要素で合格 |
| 29 | 総合再検証 | 全改善を反映して再レンダリング→自動チェック**14項目ALL PASS**(50.9秒/-16.1dB/1080x1920/thumbnail出力) |
| 30 | 文書化・統合 | 本ログ・フォーマット規則・戦略運用節・スキルを更新(このコミット) |

## 主な出典(ループ順)

- 配色: [ショート動画デザインのコツ](https://toshikazu-creator.com/2025/05/06/short-video-design-color-font/), [Color Psychology for Financial Services](https://bethanyworks.com/color-psychology-financial-services-brands/), [YouTube Thumbnail Color Psychology](https://www.growthos.in/blog/youtube-thumbnail-color-psychology)
- フォント: [動画に適したフォントを研究する](https://okami-no.hatenablog.com/entry/2024/06/02/114353), [テロップに使えるフォント一覧](https://varietytelop.com/2023/11/08/font/)
- 話者・調声: [VOICEVOXキャラクター一覧と声質比較](https://ai-yomiage.com/blog/voicevox-2026-knzC8V)
- BGM音量: [ショート動画向け!BGM・効果音の音量設定](https://kotatsu.info/2021-09-13-short-bgm-se-volume/)
- SE: [効果音の入れ方: タイミングと音量の基本](https://tadaoto.com/blog/how-to-add-sound-effects-to-video/)
- 冒頭フレーム/サムネ: [YouTube Shorts Thumbnail Strategy 2026](https://miraflow.ai/blog/youtube-shorts-thumbnail-strategy-2026), [vidIQ: Shorts Custom Thumbnails](https://vidiq.com/blog/post/youtube-shorts-custom-thumbnails/)
- イージング: [イージングの使い分けレシピ](https://feb19.jp/blog/20161201_animation), [ICS Media: CSSイージングのお手本](https://ics.media/en/entry/18730/)
- テロップ技法: [カラオケテロップの作り方](https://varietytelop.com/2025/05/21/karaoke/)
- 視線誘導: [レイアウトにおける視線の誘導(DDC)](https://www.ddc.co.jp/dtp/archives/20181105/100000.html)
- グラフアニメ: [Flourish: Animated charts](https://flourish.studio/blog/animated-charts/)
- ペーシング: [プロが教えるショート動画編集のコツ](https://www.ab-net.co.jp/abilivepromotion/news/247/)
- キャラ規約: [ずんずんPJ キャラクター利用のガイドライン](https://zunko.jp/guideline.html), [VOICEVOX全キャラの収益化可否](https://minbdevice.com/voicevox-license/)
- パワーワード: [キラーキーワード24選](https://tcd-theme.com/2020/12/24hit-keywords.html)
- タグSEO: [Shortsタグ最適化](https://blog.jarea.jp/movie/youtube/shorts-tag-optimization), [ショートのハッシュタグ(マーケドリブン)](https://pamxy.co.jp/marke-driven/sns-marketing/youtube/youtube-short-hashtag/)
- 投稿時間: [YouTubeショート投稿時間と頻度の正解](https://0120.co.jp/blog/video-16/)
- ループ編集: [How to Create a Looping Video for Shorts](https://www.mariosomedia.com/blog/seamlessloop)
- ラウドネス: [YouTuberのためのラウドネスノーマライゼーション](https://lowpass.studio/loudness-normalization/)
- 字幕サイズ: [見やすいテロップの入れ方(omniweb)](https://omniweb.jp/m25/), [テロップの最適なサイズ](https://video-knowledge.com/character_size_time_timing/)
- 出典表示: [出典の種類と正しい表記方法](https://media.tategatadouga-labo.com/p143/)
- バズ実例: [ショート動画マーケティング完全ガイド(Ownly)](https://www.ownly.jp/sslab/short-form-content-marketing)
- 視聴者層: [LINEリサーチ: ショート動画利用実態](https://prtimes.jp/main/html/rd/p/000000415.000129774.html), [ADK 縦型ショート動画調査](https://www.adkms.jp/wp/wp-content/uploads/2024/03/20240327_NewsRelease_%E7%B8%A6%E5%9E%8B%E3%82%B7%E3%83%A7%E3%83%BC%E3%83%88%E5%8B%95%E7%94%BB%E8%AA%BF%E6%9F%BB.pdf)
- チャンネル名: [チャンネル名の決め方(Lumii)](https://lumii.co.jp/blog/youtube-channel-name/)
- ABテスト: [サムネイルA/Bテスト機能(フルスピード)](https://growthseed.jp/experts/sns/youtube-thumbnail-ab-test/)
- チェックリスト: [動画投稿チェックリスト(DTM)](https://www.dt-media.jp/column/youtube-checklist)
- ミュート視聴: [無音視聴時代の動画字幕](https://debono.co.jp/media/doga-jimaku-telop-ai/), [サイレントでも伝わる動画広告](https://video-academy.jp/blog/know/knowledge/6418/)
