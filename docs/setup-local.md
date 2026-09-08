# 自分のPCで動かす(2026-09-08)

リポジトリは**セーブデータそのもの**で、GitHub 側が正本。コンテナは使い捨ての作業机なので、
PC 側では「移管」ではなく **clone(複製)** をする。ここの中身は何も失われないし、
両方に置いたまま push / pull で同期できる。

```bash
git clone https://github.com/0111comma/coursera-test.git
cd coursera-test
git checkout claude/youtube-video-1m-subscribers-qryg54    # 作業中のブランチ
pip install -r requirements.txt
```

**clone は 2.2 GiB ある**(完成 mp4 をコミットしているため)。
履歴が要らなければ `git clone --depth 1` で軽くなる。

## リポジトリに入っていないもの(clone しただけでは揃わない)

| もの | どうするか |
|---|---|
| VOICEVOX エンジン | Linux は `bash production/setup_voicevox.sh`。mac/Windows は VOICEVOX 本体を起動しておく(`127.0.0.1:50021`) |
| ffmpeg | `brew install ffmpeg` / winget / apt |
| 日本語フォント | Noto Sans CJK JP を推奨。`setup_fonts()` が名前でも探すので、Hiragino・Yu Gothic・Meiryo でも動く |
| `assets/irasuto/*.png` | **再配布禁止なのでコミットしていない**。無くても落ちないが、絵が自前のベクター図に変わる。一覧は `assets/irasuto/README.md` |
| `videos/*/output/work/` | 中間フレーム。無くてよい(焼き直せば再生成される) |

## 焼く

```bash
bash production/bake.sh videos/Z003-sumaho-oku /tmp/z003.log
```

`nohup python3 render.py &` は**わざと動かないようにしてある**(見張りなしで焼くと、
止まっても誰も気づかないため)。現況は `bash production/bake_status.sh` で見る。
