from pathlib import Path
import urllib.request, urllib.parse, json, hashlib, wave, math
import numpy as np
R=Path(__file__).resolve().parent
O=R/'output';O.mkdir(exist_ok=True)
def req(path,data=None):
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:50021'+path,data=data,headers={'Content-Type':'application/json'}),timeout=120) as f:return f.read()
def writewav(path,a):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes((np.clip(a,-1,1)*32767).astype('int16').tobytes())
def main():
    script=json.loads((R/'script.json').read_text());parts=[];cursor_frames=0;scene_starts={}
    for i,s in enumerate(script):
        if s.get('kind')=='time_cut':
            frames=round(s['cut_duration']*30);a=np.zeros(frames*800)
            scene_starts[s['scene_id']]=cursor_frames/30
            s.update(scene_start=cursor_frames/30,start=cursor_frames/30,start_frame=cursor_frames,end_frame=cursor_frames+frames,duration=frames/30,frames=frames,voice_file=None)
            cursor_frames+=frames;parts.append(a)
            print(i,'time cut',s['scene_id'],s['duration'],flush=True);continue
        key=hashlib.sha256(json.dumps(s,ensure_ascii=False).encode()).hexdigest()[:10]
        p=O/f'voice-{i:02}-{key}.wav'
        if not p.exists():
            q=json.loads(req('/audio_query?'+urllib.parse.urlencode({'text':s['text'],'speaker':s['speaker']}),b''))
            q.update(speedScale=s['speed'],intonationScale=1.18,prePhonemeLength=.02,postPhonemeLength=.03,outputSamplingRate=24000)
            for a in q['accent_phrases']:
                if a.get('pause_mora'):a['pause_mora']['vowel_length']=s.get('pause_seconds',.26)
            (O/f'query-{i:02}.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
            (O/f'query-{i:02}-original.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
            p.write_bytes(req('/synthesis?speaker='+str(s['speaker']),json.dumps(q).encode()))
        with wave.open(str(p)) as f:a=np.frombuffer(f.readframes(f.getnframes()),np.int16).astype(float)/32768
        tail=s.get('tail_seconds',.08)
        frames=math.ceil((len(a)/24000+tail)*30);a=np.pad(a,(0,frames*800-len(a)))
        q=json.loads((O/f'query-{i:02}.json').read_text())
        elapsed=q['prePhonemeLength']/q['speedScale'];donation_offset=None
        for phrase in q['accent_phrases']:
            if donation_offset is None and ''.join(m['text'] for m in phrase['moras']).startswith('キフ'):donation_offset=elapsed
            for m in phrase['moras']:elapsed+=(float(m.get('consonant_length') or 0)+m['vowel_length'])/q['speedScale']
            if phrase.get('pause_mora'):elapsed+=phrase['pause_mora']['vowel_length']/q['speedScale']
        scene_starts.setdefault(s['scene_id'],cursor_frames/30)
        s.update(scene_start=scene_starts[s['scene_id']],start=cursor_frames/30,start_frame=cursor_frames,end_frame=cursor_frames+frames,duration=frames/30,frames=frames,voice_file=p.name,donation_offset=donation_offset)
        cursor_frames+=frames;parts.append(a)
        print(i,round(s['duration'],2),json.loads((O/f'query-{i:02}.json').read_text())['kana'],flush=True)
    voice=np.concatenate(parts);writewav(O/'voice.wav',voice)
    (O/'timeline.json').write_text(json.dumps(script,ensure_ascii=False,indent=2))
    print('duration',cursor_frames/30,flush=True)
if __name__=='__main__':main()
