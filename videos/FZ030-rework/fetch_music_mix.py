from pathlib import Path
import requests, subprocess, json, wave, numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urljoin
root=Path('videos/FZ030-rework')
url='https://dova-s.jp/bgm/detail/14621/download'
session=requests.Session()
response=session.get(url,timeout=40)
response.raise_for_status()
soup=BeautifulSoup(response.text,'html.parser')
form=next((f for f in soup.find_all('form') if f.find('select',attrs={'name':'track'})),None)
if form is None:
    raise RuntimeError('Normal track download form not found; no alternative bypass attempted')
data={t.get('name'):t.get('value','') for t in form.find_all('input') if t.get('name')}
data['track']='2'
response=session.post(urljoin(response.url,form.get('action') or response.url),data=data,headers={'Referer':url},timeout=60)
response.raise_for_status()
content_type=response.headers.get('Content-Type','')
print('download response:',response.status_code,content_type,len(response.content),flush=True)
if 'audio' not in content_type and 'octet-stream' not in content_type:
    raise RuntimeError('Download did not return media. Stop without trying alternate private endpoints.')
bgm=Path('/tmp/fz030-bgm.mp3');bgm.write_bytes(response.content)
timeline=json.loads((root/'timeline.json').read_text())
rate=24000;dur=timeline[-1]['end_frame']/30
dialogue=np.zeros(round(dur*rate),dtype=np.float64)
for row in timeline:
    if row['speaker']=='T':continue
    wav=Path('/tmp')/f'fz030-{row["id"]}.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'audio'/f'{row["id"]:02d}.flac'),'-ar',str(rate),'-ac','1',str(wav)],check=True)
    with wave.open(str(wav)) as w: voice=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
    at=round((row['start_frame']/30+row['audio_lead'])*rate)
    dialogue[at:at+len(voice)]+=voice
# Purposeful, short editorial accents: title action, time passage, bad news, resale reveal.
fx=np.zeros_like(dialogue)
for row in timeline:
    if row['id'] not in [0,5,7,14,15,19]:continue
    at=round(row['start_frame']/30*rate); length=.16 if row['id'] in [5,14] else .24
    t=np.arange(round(rate*length))/rate
    f0,f1=(720,360) if row['id'] in [7,15,19] else (520,1040)
    s=.085*np.sin(2*np.pi*(f0*t+(f1-f0)/(2*length)*t*t))*np.exp(-t*17)
    fx[at:at+len(s)]+=s
spoken=Path('/tmp/fz030-spoken.wav')
with wave.open(str(spoken),'w') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
    w.writeframes((np.clip(dialogue+fx,-.95,.95)*32767).astype(np.int16).tobytes())
# Raw BGM remains only in the temporary runner. Persist only the narrated audiovisual-program mix.
out=root/'audio'/'FZ030-mixed-dialogue.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(spoken),'-stream_loop','-1','-i',str(bgm),
 '-filter_complex',f'[0:a]volume=1.7,alimiter=limit=0.94:level=false[v];[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-5:LRA=9,afade=t=in:d=0.25,afade=t=out:st={dur-.5}:d=.5[b];[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=false[a]',
 '-map','[a]','-ar','44100','-ac','2','-c:a','libmp3lame','-b:a','128k',str(out)],check=True)
report={'song':'しゅわしゅわハニーレモン350ml','artist':'しゃろう','source':url,'license':'https://dova-s.jp/help/articles/license/','selected_track':2,'music_embedded_only':True,'duration':dur,'file_bytes':out.stat().st_size,'raw_audio_in_repository':False,'bed_target_lufs':-28}
(root/'audio'/'music-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False),flush=True)
