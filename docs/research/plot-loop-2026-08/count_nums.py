"""1本の動画が視聴者に投げる「初出の数値」の個数を数える。"""
import importlib.util, re, sys
from pathlib import Path
sys.path.insert(0, "/home/user/coursera-test/production")
import check_teinei as T

def load(p):
    spec = importlib.util.spec_from_file_location(f"c_{p.parent.name}", p)
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m
    spec.loader.exec_module(m); return m

def key(t):
    return re.sub(r"(%|倍|割|円|年|歳|日|ドル)$", "", t.replace(" ", "").replace(",", ""))

for d in sorted(Path("/home/user/coursera-test/videos").iterdir()):
    rp = d / "render.py"
    if not rp.exists(): continue
    subs = [u.subtitle.replace("【","").replace("】","") for u in load(rp).UNITS]
    seen, fresh = set(), []
    for s in subs:
        for m in T.NUM.finditer(s):
            k = key(m.group().replace(" ", ""))
            if k not in seen:
                seen.add(k); fresh.append(m.group().strip())
    print(f"{d.name:26} ユニット{len(subs):3}  初出の数値 {len(fresh):3} — {'、'.join(fresh)}")
