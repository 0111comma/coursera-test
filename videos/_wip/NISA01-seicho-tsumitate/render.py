#!/usr/bin/env python3
"""NISAショート初稿。既存リポジトリのルートへ配置して使用。"""
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "production" / "shortlib.py").exists())
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S
import fplib as F
TITLE = '成長投資枠は株専用？'
# UbuntuのNoto CJKパッケージはBlackを含まないことがある。
# その場合は実在するBoldと700を組で登録し、900→400の警告を防ぐ。
if not Path(F.NUM_FONT_PATH).exists():
    bold = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
    if bold.exists():
        F.NUM_FONT_PATH = str(bold)
        F.NUM_WEIGHT = 700
F.use_fp_theme(TITLE, speaker=3, badge="2026年9月時点の制度。金額の例は仮定")
from shortlib import Unit, render_video, require_voicevox
import scenes_fp as sf
import importlib.util
spec = importlib.util.spec_from_file_location("nisa_verify", Path(__file__).with_name("verify.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
OUTDIR = Path(__file__).resolve().parent / "output"
SCENES = {
    'toi': sf.person_bubble("03_troubled", "株しか買えない？"),
    'answer': sf.hero("積立もできる", "成長投資枠", name="02_point", role="neutral", count=False, size="reference"),
    'choice': sf.person_bubble("01_base", "どっちで買う？"),
    'example': sf.hero("月3万円", "積立額の例", name=None, role="neutral", count=False, size="reference"),
    'eligible': sf.arrow("投資信託", "積立", "対象の商品", "つみたて投資枠", role="neutral"),
    'year': sf.formula(f"月{V.MONTHLY_MAN}万円 × {V.MONTHS}か月", answer=f"年{V.ANNUAL_MAN}万円", title="1年分に直すと", name=None, emph_color=F.GROW),
    'limit': sf.bars([("積立額の例", V.ANNUAL_MAN, "36万円"), ("年間上限", V.TSUMITATE_MAN, "120万円")], title="つみたて投資枠", ymax=120, gain=0),
    'within': sf.compare("年36万円", "年120万円", "積立額の例", "年間上限", title="この積立額なら収まる", role="neutral"),
    'stock': sf.arrow("株", "購入", "対象の商品", "成長投資枠", role="neutral"),
    'lump': sf.arrow("投資信託", "一括購入", "対象の商品", "成長投資枠", role="neutral"),
    'growth': sf.hero(f"年{V.GROWTH_MAN}万円", "成長投資枠の年間上限", name=None, role="neutral", count=False, size="reference"),
    'same': sf.person_bubble("02_point", "同じ商品も買える"),
    'close': sf.person_bubble("01_base", "商品と買い方で選ぶ"),
}

UNITS = [
    Unit('toi', 'NISAの成長投資枠、株専用だと思ってない？', narration='ニーサの成長投資枠、株専用だと思ってない？', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('answer', '実は、対象の投資信託を積み立てるのにも使える。', narration='実は、対象の投資信託を積み立てるのにも使える。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('choice', 'じゃあ、つみたて投資枠とどう使い分ける？', narration='じゃあ、つみたて投資枠とどう使い分ける？', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('example', 'たとえば、月3万円で積立を始めたい人。', narration='たとえば、月3万円で積立を始めたい人。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('eligible', '対象の投資信託なら、つみたて投資枠で買える。', narration='対象の投資信託なら、つみたて投資枠で買える。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('year', '3万円を12か月で、年36万円。', narration='3万円を12か月で、年36万円。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('limit', 'つみたて投資枠の年間上限は120万円。', narration='つみたて投資枠の年間上限は120万円。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('within', '月3万円の積立なら、その範囲内だ。', narration='月3万円の積立なら、その範囲内だ。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('stock', '対象の株を買いたいときは、成長投資枠を使える。', narration='対象の株を買いたいときは、成長投資枠を使える。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('lump', '対象の投資信託を、まとめて買うときも使える。', narration='対象の投資信託を、まとめて買うときも使える。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('growth', '成長投資枠の年間上限は240万円。', narration='成長投資枠の年間上限は240万円。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('same', '両方の対象なら、同じ投資信託も買える。', narration='両方の対象なら、同じ投資信託も買える。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('close', '名前だけで決めず、買いたい商品と買い方で選ぼう。', narration='名前だけで決めず、買いたい商品と買い方で選ぼう。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, 'NISA01.mp4', speaker=3, chara=False)
    print(result)
