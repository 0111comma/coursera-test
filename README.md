# お金・金融リテラシー YouTubeチャンネル 企画リポジトリ

Claude Codeで教育系YouTube動画を「企画→制作→投稿」まで回すプロジェクトの、**企画フェーズ**を管理するリポジトリ。

## 中身

| パス | 内容 |
|---|---|
| `docs/research/theme-candidates.md` | テーマ選定の市場調査・候補評価マトリクス |
| `docs/strategy.md` | チャンネル戦略(コンセプト・差別化・フォーマット・コンプライアンス・KPI) |
| `ideas/backlog.md` | ネタのストック(ステータス管理付き) |
| `templates/` | 企画書・台本のテンプレート |
| `production/` | 制作パイプライン(描画/TTS/ffmpeg結合、VOICEVOXセットアップ) |
| `videos/<ID>-<slug>/` | 動画1本ごとの企画書・台本・検証スクリプト・完成mp4 |
| `.claude/skills/` | 企画〜制作ワークフロー用のClaude Codeスキル |

## ワークフロー

Claude Codeでこのリポジトリを開き、スラッシュコマンドで回す:

1. `/ideate` — 戦略に沿ったネタ出し → `ideas/backlog.md` に追加
2. `/plan-video` — ネタ1つを企画書に(制度の事実確認+数値の計算検証込み)
3. `/write-script` — 企画書から台本に(コンプライアンスのセルフチェック込み)
4. `/produce-video` — 台本からmp4をレンダリング(1080×1920、VOICEVOX音声+字幕+グラフ)
5. mp4(`videos/<ID>/output/<ID>.mp4`)をローカルからYouTubeに投稿

詳細は `CLAUDE.md` を参照。
