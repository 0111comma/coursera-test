from pathlib import Path
import subprocess,json,os
R=Path(os.environ['FINANCE_PROJECT']).resolve();O=R/'output';D=R/'deliverables';D.mkdir(exist_ok=True)
C=json.loads((R/'project.json').read_text());CODE=C['code'];MAIN=CODE+'-'+C['slug']+'.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'mix.wav'),'-af','loudnorm=I=-15.5:TP=-1.3:LRA=8','-ar','48000','-c:a','aac','-b:a','160k',str(O/'mixed.m4a')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'silent.mp4'),'-i',str(O/'mixed.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-metadata','title='+C['title'],str(D/MAIN)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(D/MAIN),'-vf','scale=540:960','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(D/(CODE+'-mobile.mp4'))],check=True)
measurement=subprocess.run(['ffmpeg','-hide_banner','-i',str(D/MAIN),'-af','loudnorm=I=-15.5:TP=-1.3:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
(O/'audio-loudness.txt').write_text(measurement.stderr)
print('Publication and mobile video ready')
