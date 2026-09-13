"""Slow numerical dialogue without changing pitch, preserving phoneme alignment."""
from pathlib import Path
import json,subprocess,wave,math,numpy as np
R=Path(__file__).resolve().parent;O=R/'output'
T=json.loads((O/'timeline.json').read_text());report=[];parts=[];cursor=0
for i,s in enumerate(T):
    if s.get('kind'):
        frames=round(s.get('cut_duration',.7)*30) if s['scene_id']=='downturn' else 21
        a=np.zeros(frames*800)
    else:
        qpath=O/f'query-{i:02}.json';q=json.loads(qpath.read_text())
        if not (O/f'query-{i:02}-original.json').exists():(O/f'query-{i:02}-original.json').write_text(qpath.read_text())
        q=json.loads((O/f'query-{i:02}-original.json').read_text())
        target=1.12 if i in [2,8,10,11,12] else 1.22 if i in [3,14] else 1.20 if i==16 else s['speed']
        tempo=target/q['speedScale'];src=O/Path(s['voice_file']).with_suffix('.flac')
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-af',f'atempo={tempo:.10f}','-ar','24000','-ac','1','-f','s16le','-'])
        a=np.frombuffer(raw,np.int16).astype(float)/32768
        tail=.20 if i in [11,17] else .075
        frames=math.ceil((len(a)/24000+tail)*30);a=np.pad(a,(0,frames*800-len(a)))
        q['speedScale']=target;qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2))
        with wave.open(str(O/s['voice_file']),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes((a*32767).astype('int16').tobytes())
        report.append(dict(index=i,old_speed=s['speed'],new_speed=target,atempo=tempo,preserved_pitch=True,tail=tail))
        s['speed']=target
    s.update(start=cursor/30,scene_start=cursor/30,start_frame=cursor,end_frame=cursor+frames,frames=frames,duration=frames/30)
    cursor+=frames;parts.append(a)
with wave.open(str(O/'voice.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes((np.concatenate(parts)*32767).astype('int16').tobytes())
(O/'timeline.json').write_text(json.dumps(T,ensure_ascii=False,indent=2));(O/'retiming.json').write_text(json.dumps(report,indent=2))
print('Final narration',cursor/30,'seconds',cursor,'frames')
