#!/usr/bin/env python3
"""script.md(台本+投稿キット)を render.py から組み立てる。

ナレーション全文を手で写すと、render.py を直したときに必ずズレる
(S010で実際にズレた)。ここでは UNITS を唯一の出典にして生成する。

使い方:
    python3 production/make_script.py videos/<ID>-<slug> meta.json
meta.json の形は videos/*/script_meta.json を参照。
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "production"))

# 1文字あたりの秒数(ループ58で再較正)。話速を1.3倍にしたので、
# 実測 0.1462秒/字(S011+S012の全543字を新しい速度で合成して測定)に4%の余裕を足した
SEC_PER_CHAR = 0.152

CREDITS = """---
※本動画は情報提供を目的としており、投資助言ではありません。特定の銘柄・商品・業者を推奨するものではありません。
※{assume}2026年8月時点の一般的な仕組みの説明です。
出典: {sources}(確認日2026-08-15)
音声: VOICEVOX:ずんだもん
立ち絵: 坂本アヒル 様(ずんだもん立ち絵素材)/ずんだもんは「東北ずん子・ずんだもんプロジェクト」のキャラクターです(キャラクター利用ガイドライン https://zunko.jp/guideline.html 準拠)
制作: 台本・数値の検証・図解はすべて運営者が作成・確認しています

{tags}"""


def main(vdir: Path, meta: dict):
    spec = importlib.util.spec_from_file_location("rp", vdir / "render.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rp"] = mod
    spec.loader.exec_module(mod)
    units = mod.UNITS
    narration = "\n".join(u.subtitle.replace("【", "").replace("】", "") for u in units)
    chars = sum(len(u.subtitle.replace("【", "").replace("】", "")) for u in units)
    est = chars * SEC_PER_CHAR + len(units) * 0.15
    # 横型の長尺かどうか(render.py が use_landscape() を呼んでいるか)で見出しを変える
    long_form = "use_landscape" in (vdir / "render.py").read_text()
    kind = "長尺・横型" if long_form else "ショート"
    length = f"約{est / 60:.1f}分" if long_form else f"約{est:.0f}秒"

    body = f"""# 台本({kind}): {meta['title']}

- **ID**: {meta['id']} / **テンプレ**: {meta.get('template', '仕組み解説型')} / **想定尺**: {length}
- **投稿タイトル**: {meta['post_title']}({len(meta['post_title'])}字)
- **調声・構成**: render.pyが正(共通シーンはproduction/scenes_common.py)

## ネタ選定ゲート(プレイブックF1)

- **視聴者の予想**: {meta['expect']}
- **この動画の結論**: {meta['conclusion']}

## 構成の意図

{meta['design']}

## ナレーション全文

{narration}

({len(units)}ユニット)

## タグ(YouTubeのタグ欄。説明欄のハッシュタグとは別)

{meta.get('yt_tags', '(未設定)')}

## 概要欄テキスト

{meta['description']}
{meta['cta']}

{CREDITS.format(assume=meta['assume'], sources=meta['sources'], tags=meta['tags'])}

## 固定コメント(投稿直後に設置)

{meta['pinned']}

- 運用: 投稿直後に固定、初動1〜3時間は返信最優先 / 禁止: URL貼り
"""
    (vdir / "script.md").write_text(body)
    print(f"{vdir.name}: script.md を生成({len(units)}ユニット / 推定{length})")


if __name__ == "__main__":
    d = Path(sys.argv[1])
    main(d, json.loads(Path(sys.argv[2]).read_text()))
