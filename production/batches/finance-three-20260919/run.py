from pathlib import Path
import os,subprocess,sys
root=Path(__file__).resolve().parent
for ep in sorted(root.glob("*/script.json")):
 env=os.environ.copy();env["FINANCE_PROJECT"]=str(ep.parent)
 subprocess.run([sys.executable,str(root/"engine/synthesize.py")],env=env,check=True)
if (root/"fetch_photos.py").exists():
 subprocess.run([sys.executable,str(root/"fetch_photos.py")],check=True)
