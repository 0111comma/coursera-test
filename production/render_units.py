#!/usr/bin/env python3
"""render.py から UNITS を取り出す、ゲート共通の入り口(2026-09-07)。

**なぜ共通にしたか。**ゲートはそれぞれ
`re.findall(r'Unit\\(\\s*"([^"]+)",\\s*"([^"]+)"', src)` と、render.py の**字面**を
正規表現で拾っていた。Z002/Z003 が

    def U(scene, sub, **kw):
        d = dict(_F); d.update(kw); return Unit(scene, sub, **d)

という助け関数で Unit を作った瞬間、**どのゲートも1件も拾えず、
ユニット0本として黙って素通りした**。check_video の字幕の行数判定がそれで空振りし、
**2時間焼いたあとにレンダラが「字幕が3行」で落ちた**(2026-09-07 Z002)。

台本の書き方を変えるとゲートが効かなくなるのは、ゲートの作りのほうが悪い。
**render.py を実際に読み込んで UNITS を取る。**読めないときは黙って通さず、例外を上げる。
"""
import importlib.util
import re
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
_RE = re.compile(r'Unit\(\s*"([^"]+)",\s*"([^"]+)"')


class UnreadableRender(RuntimeError):
    """render.py を読めない(文法エラー等)。**0ユニットとして通してはいけない。**"""


def load_units(render_py, src=None):
    """[(場面, 字幕), ...] を返す。読めなければ UnreadableRender。"""
    render_py = Path(render_py)
    src = src if src is not None else render_py.read_text()
    err = None
    if str(PRODUCTION) not in sys.path:
        sys.path.insert(0, str(PRODUCTION))
    try:
        spec = importlib.util.spec_from_file_location(f"ru_{render_py.parent.name}", render_py)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        us = getattr(mod, "UNITS", [])
        if us:
            return [(u.scene, u.subtitle) for u in us]
    except Exception as e:      # noqa: BLE001 — 読めない理由は問わず、呼び手に返す
        err = e
    got = _RE.findall(src)
    if got:
        return got
    raise UnreadableRender(f"{render_py} から UNITS を取れない" + (f": {err}" if err else ""))


def subtitles(render_py, src=None):
    """字幕だけ。【】は落とす(強調の印はゲートの判定対象ではない)。"""
    return [s.replace("【", "").replace("】", "") for _, s in load_units(render_py, src)]


def strip_units(src: str) -> str:
    """SCENES の文字列だけを見たいゲート用に、**字幕の行を消した**ソースを返す。

    Unit(...) だけでなく U(...) の呼び出しも消す(助け関数を使う台本があるため)。
    """
    src = _RE.sub("", src)
    return re.sub(r'\bU\(\s*"[^"]+",\s*"[^"]+"', "", src)
