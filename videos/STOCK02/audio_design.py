from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfilt
import wave,json,subprocess,hashlib
R=Path(__file__).resolve().parent;O=R/'output';A=R/'assets/audio';SR=24000
S=json.loads((O/'timeline.json').read_text());by={s['scene_id']:s for s in S}
with wave.open(str(O/'voice.wav')) as f:v=np.frombuffer(f.readframes(f.getnframes()),np.int16).astype(float)/32768
raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(A/'fluffing-a-duck.mp3'),'-f','f32le','-ar',str(SR),'-ac','2','-']),np.float32).reshape(-1,2)
# The original track has two arrangements separated by a pause. Loop the first arrangement.
start,end=0.12,31.1
loop=raw[round(start*SR):round(end*SR)].astype(float)
cross=round(.14*SR);loop[-cross:]=loop[-cross:]*(1-np.linspace(0,1,cross))[:,None]+loop[:cross]*np.linspace(0,1,cross)[:,None]
loop=loop[cross:];music=np.tile(loop,(int(np.ceil(len(v)/len(loop))),1))[:len(v)]
vrms=np.sqrt(np.mean(v[np.abs(v)>.02]**2));music*=vrms*10**(-13.7/20)/np.sqrt(np.mean(music**2))
env=sosfilt(butter(1,6,fs=SR,output='sos'),np.abs(v));music*=(1-.18*np.clip(env/.12,0,1))[:,None]
fx=np.zeros_like(music);cues=[];rng=np.random.default_rng(913)
def add(t,kind,db):
    dur={'pop':.16,'impact':.34,'cash':.25,'click':.09,'swoosh':.3,'down':.5}[kind];x=np.arange(round(SR*dur))/SR
    if kind=='pop':w=np.sin(2*np.pi*(650*x-1300*x*x))*np.exp(-x*30)
    elif kind=='impact':w=np.sin(2*np.pi*(135*x-160*x*x))*np.exp(-x*15)+rng.normal(0,.12,len(x))*np.exp(-x*32)
    elif kind=='cash':w=(np.sin(2*np.pi*1430*x)+.4*np.sin(2*np.pi*2145*x))*np.exp(-x*19)
    elif kind=='down':w=np.sin(2*np.pi*(640*x-400*x*x))*np.exp(-x*8)
    elif kind=='swoosh':w=rng.normal(0,1,len(x))*np.sin(np.pi*x/dur)**2
    else:w=rng.normal(0,1,len(x))*np.exp(-x*95)
    w*=10**(db/20)/max(abs(w));w[:70]*=np.linspace(0,1,70);i=round(t*SR);n=min(len(w),len(v)-i)
    fx[i:i+n]+=w[:n,None];cues.append({'seconds':round(t,3),'kind':kind,'peak_dbfs':db})
r=json.loads((O/'reveal-times.json').read_text())['amount_offsets']
add(.08,'pop',-23)
for key in ['fund_own','fund_debt','fund_total']:add(by['funding']['start']+r[key],'cash',-25)
add(by['month']['start'],'swoosh',-26)
add(by['panic']['start']+r['crash'],'impact',-19)
add(by['proceeds']['start']+r['proceeds'],'down',-23)
add(by['debt']['start']+r['debt'],'impact',-23)
add(by['reveal']['start']+r['net'],'impact',-18)
add(by['lesson']['start']+r['sixty'],'down',-25)
add(by['escape']['start']+.40,'click',-21)
add(by['ending']['start']+.1,'pop',-25)
music[:240]*=np.linspace(0,1,240)[:,None];music[-960:]*=np.linspace(1,0,960)[:,None]
mix=v[:,None]+music+fx;p=np.max(abs(mix))
if p>.98:mix*=.98/p
with wave.open(str(O/'mix.wav'),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('int16').tobytes())
report={'bgm':'Fluffing a Duck','composer':'Kevin MacLeod','catalog_bpm':122,'source':'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768','license':'https://creativecommons.org/licenses/by/4.0/','source_sha256':hashlib.sha256((A/'fluffing-a-duck.mp3').read_bytes()).hexdigest(),'loop_source_seconds':[start,end],'crossfade_seconds':cross/SR,'music_db_below_active_voice':float(20*np.log10(np.sqrt(np.mean(music**2))/vrms)),'continuous_bgm':True,'sfx':'Original synthesized cues','cues':cues,'pre_normalization_peak':float(p)}
(O/'audio-design.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Mixed',len(v)/SR,'seconds',len(cues),'SFX events',flush=True)
