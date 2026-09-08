#!/usr/bin/env python3
"""NISAショート初稿。既存リポジトリのルートへ配置して使用。"""
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "production" / "shortlib.py").exists())
sys.path.insert(0, str(ROOT / "production"))
import shortlib as S
import fplib as F
TITLE = 'NISAを売ると何円分戻る？'
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
    'toi': sf.person_bubble("03_troubled", "売ると戻る？"),
    'name': sf.hero("保有の上限", "NISAの非課税保有限度額", name=None, role="neutral", count=False, size="reference"),
    'rule': sf.arrow("購入額", "再利用", "売った商品の", "できる金額", role="neutral"),
    'timing': sf.arrow("売却した年", "翌年以降", "再利用はまだ", "再利用できる", role="neutral"),
    'example': sf.hero(f"{V.BUY_MAN}万円", "購入額の例", name=None, role="neutral", count=False, size="reference"),
    'up': sf.arrow("100万円", "120万円", "購入額", "売却額の例", role="gain"),
    'base': sf.hero(f"{V.REUSE_MAN}万円分", "再利用できる金額", name=None, role="neutral", count=False, size="reference"),
    'down': sf.arrow("100万円", "80万円", "購入額", "売却額の例", role="loss"),
    'again': sf.hero(f"{V.REUSE_MAN}万円分", "購入額で決まる", name=None, role="neutral", count=False, size="reference"),
    'annual': sf.person_bubble("02_point", "年間の上限は別"),
    'noadd': sf.hero("上乗せなし", "年間投資枠", name=None, role="neutral", count=False, size="reference"),
    'close': sf.person_bubble("01_base", "購入額と年を確認"),
}

UNITS = [
    Unit('toi', 'NISAで買った商品、売れば買える金額も戻る？', narration='ニーサで買った商品、売れば買える金額も戻る？', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('name', 'NISAには、保有できる金額の上限がある。', narration='ニーサには、保有できる金額の上限がある。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('rule', '売ると、買ったときの金額分を再利用できる。', narration='売ると、買ったときの金額分を再利用できる。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('timing', '再利用できるのは、売った翌年以降だ。', narration='再利用できるのは、売った翌年以降だ。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('example', 'たとえば、100万円で買った投資信託を売る。', narration='たとえば、100万円で買った投資信託を売る。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('up', '120万円に値上がりして売っても、', narration='120万円に値上がりして売っても、', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('base', '再利用できるのは、買ったときの100万円分。', narration='再利用できるのは、買ったときの100万円分。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('down', '80万円に値下がりして売った場合も同じだ。', narration='80万円に値下がりして売った場合も同じだ。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('again', '翌年以降に、100万円分を再利用できる。', narration='翌年以降に、100万円分を再利用できる。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('annual', 'ただし、1年に買える金額の上限は別にある。', narration='ただし、1年に買える金額の上限は別にある。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('noadd', '再利用できる金額は、年間の上限には上乗せされない。', narration='再利用できる金額は、年間の上限には上乗せされない。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
    Unit('close', '売る前に、購入額と買い直す年を確認しよう。', narration='売る前に、購入額と買い直す年を確認しよう。', chara="none", speaker=3, anim=1.0, speed=1.2, pad=0.12),
]

if __name__ == "__main__":
    require_voicevox()
    result = render_video(UNITS, SCENES, OUTDIR, 'NISA02.mp4', speaker=3, chara=False)
    print(result)
