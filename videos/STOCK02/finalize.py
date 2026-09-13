from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parent;O=R/'output';D=R.parent/'deliverables';D.mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'mix.wav'),'-af','loudnorm=I=-15.5:TP=-1.3:LRA=8','-ar','48000','-c:a','aac','-b:a','160k',str(O/'mixed.m4a')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'silent.mp4'),'-i',str(O/'mixed.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-metadata','title=借金でオルカンを買った結果｜STOCK02',str(D/'STOCK02-orukan-leverage.mp4')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(D/'STOCK02-orukan-leverage.mp4'),'-vf','scale=540:960','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(D/'STOCK02-mobile.mp4')],check=True)
print('Publication and mobile video ready')
