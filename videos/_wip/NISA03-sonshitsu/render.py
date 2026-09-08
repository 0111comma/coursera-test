#!/usr/bin/env python3
"""NISAショート初稿。既存リポジトリのルートへ配置して使用。"""
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "production" / "shortlib.py").exists())
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S
import fplib as F
TITLE = 'NISAの損、税金から引ける？'
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
    'toi': sf.person_bubble("03_troubled", "損した分は引ける？"),
    'answer': sf.hero("引けない", "NISAで出た売却損", name=None, role="loss", count=False, size="reference"),
    'example': sf.hero(f"{V.LOSS_MAN}万円の損", "NISA口座・仮定の例", name=None, role="loss", count=False, size="reference"),
    'other': sf.hero(f"{V.PROFIT_MAN}万円の利益", "課税口座・仮定の例", name=None, role="gain", count=False, size="reference"),
    'wallet': sf.formula("利益20万円 − 損20万円", answer="合計0円", title="2つの売買を合計", name=None, emph_color=F.INK_DARK),
    'tax': sf.hero(f"{V.TAXABLE_MAN}万円", "税金の計算に使う利益", name=None, role="neutral", count=False, size="reference"),
    'term': sf.formula("利益 − 損", answer="損益通算", title="税金を計算するときの仕組み", name=None, emph_color=F.INK_DARK),
    'exclude': sf.hero("対象外", "NISAの売却損", name=None, role="loss", count=False, size="reference"),
    'later': sf.arrow("今年の損", "持越し不可", "NISA口座", "翌年以降の税金", role="loss"),
    'close': sf.person_bubble("02_point", "売る前に口座を確認"),
}

UNITS = [
    Unit('toi', 'NISAで損した分、ほかの株の利益から引ける？', narration='ニーサで損した分、ほかの株の利益から引ける？', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('answer', '税金の計算では、引けない。', narration='税金の計算では、引けない。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('example', 'たとえば、NISAの商品を売って20万円の損。', narration='たとえば、ニーサの商品を売って20万円の損。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('other', '別の課税口座では、株を売って20万円の利益。', narration='別の課税口座では、株を売って20万円の利益。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('wallet', '合計すると、もうけはゼロだ。', narration='合計すると、もうけはゼロだ。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('tax', 'それでも、課税口座の20万円の利益には税金がかかる。', narration='それでも、課税口座の20万円の利益には税金がかかる。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('term', '利益と損を差し引くのを、損益通算という。', narration='利益と損を差し引くのを、損益通算という。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('exclude', 'NISAの損は、この損益通算に使えない。', narration='ニーサの損は、この損益通算に使えない。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('later', '損を翌年以降の税金の計算に持ち越すこともできない。', narration='損を翌年以降の税金の計算に持ち越すこともできない。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('close', '税金を減らすために売るなら、NISAかどうかを確認しよう。', narration='税金を減らすために売るなら、ニーサかどうかを確認しよう。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, 'NISA03.mp4', speaker=3, chara=False)
    print(result)
