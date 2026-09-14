from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfilt
import wave,json,subprocess,hashlib
import os
R=Path(os.environ['FINANCE_PROJECT']).resolve();O=R/'output';A=R/'assets/audio';SR=24000
C=json.loads((R/'project.json').read_text())
S=json.loads((O/'timeline.json').read_text());by={s['scene_id']:s for s in S}
with wave.open(str(O/'voice.wav')) as f:v=np.frombuffer(f.readframes(f.getnframes()),np.int16).astype(float)/32768
raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(A/C['bgm_file']),'-f','f32le','-ar',str(SR),'-ac','2','-']),np.float32).reshape(-1,2)
assert len(raw)>=len(v)
music=raw[:len(v)].astype(float)
vrms=np.sqrt(np.mean(v[np.abs(v)>.02]**2));music*=vrms*10**(-13.7/20)/np.sqrt(np.mean(music**2))
env=sosfilt(butter(1,6,fs=SR,output='sos'),np.abs(v));music*=(1-.18*np.clip(env/.12,0,1))[:,None]
# Leave room for the shout and the quiet, defeated ending without stopping BGM.
acting_ducks=[]
for sid,db in [('panic',-2.0),('ending',-4.5)]:
    scene=by[sid];i=round(scene['start']*SR);j=round((scene['start']+scene['duration'])*SR)
    n=j-i;ramp=min(round(.09*SR),n//2);depth=np.ones(n)
    depth[:ramp]=np.linspace(0,1,ramp);depth[-ramp:]=np.linspace(1,0,ramp)
    music[i:j]*=10**(db*depth[:,None]/20)
    acting_ducks.append({'scene':sid,'gain_db':db,'start':scene['start'],'duration':scene['duration']})
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
add(.07,'pop',-25)
for s in S:
    sid=s['scene_id']
    if s.get('fx'):
        offset=r.get(sid,0)
        if sid=='panic':offset=.03
        add(s['start']+offset,s['fx'],-23 if sid=='panic' else -27)
    if sid=='ending':add(s['start']+.02,'down',-32)
music[:240]*=np.linspace(0,1,240)[:,None];music[-960:]*=np.linspace(1,0,960)[:,None]
mix=v[:,None]+music+fx;p=np.max(abs(mix))
if p>.98:mix*=.98/p
with wave.open(str(O/'mix.wav'),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('int16').tobytes())
report={'bgm':C['bgm'],'composer':'Kevin MacLeod','catalog_bpm':C['bgm_bpm'],'source':C['bgm_url'],'license':'https://creativecommons.org/licenses/by/4.0/','source_sha256':C['bgm_original_sha256'],'used_asset_sha256':hashlib.sha256((A/C['bgm_file']).read_bytes()).hexdigest(),'source_clip_seconds':C['bgm_clip_seconds'],'music_db_below_active_voice':float(20*np.log10(np.sqrt(np.mean(music**2))/vrms)),'continuous_bgm':True,'sfx':'Original synthesized cues','cues':cues,'pre_normalization_peak':float(p)}
report['acting_ducks']=acting_ducks
(O/'audio-design.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Mixed',len(v)/SR,'seconds',len(cues),'SFX events',flush=True)
