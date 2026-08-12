# お金・金融リテラシー YouTubeチャンネル 企画リポジトリ

Claude Codeで教育系YouTube動画を「企画→制作→投稿」まで回すプロジェクトの、**企画フェーズ**を管理するリポジトリ。

## 中身

| パス | 内容 |
|---|---|
| `docs/research/theme-candidates.md` | テーマ選定の市場調査・候補評価マトリクス |
| `docs/strategy.md` | チャンネル戦略(コンセプト・差別化・フォーマット・コンプライアンス・KPI) |
| `ideas/backlog.md` | ネタのストック(ステータス管理付き) |
| `templates/` | 企画書・台本のテンプレート |
| `videos/<ID>-<slug>/` | 動画1本ごとの企画書・台本・数値検証スクリプト |
| `.claude/skills/` | 企画ワークフロー用のClaude Codeスキル |

## ワークフロー

Claude Codeでこのリポジトリを開き、スラッシュコマンドで回す:

1. `/ideate` — 戦略に沿ったネタ出し → `ideas/backlog.md` に追加
2. `/plan-video` — ネタ1つを企画書に(制度の事実確認+数値の計算検証込み)
3. `/write-script` — 企画書から台本に(コンプライアンスのセルフチェック込み)
4. 台本(`videos/<ID>/script.md`)を制作パイプラインに渡す

詳細は `CLAUDE.md` を参照。
