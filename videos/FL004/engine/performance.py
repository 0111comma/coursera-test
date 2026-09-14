"""Synthesize each acting beat separately, retaining sample-based word timing."""
from pathlib import Path
import copy, io, json, math, urllib.parse, wave
import numpy as np

STYLE_CACHE = None

def style_id(name, request, output, actor):
    global STYLE_CACHE
    if STYLE_CACHE is None:
        speakers = json.loads(request('/speakers'))
        cast = [s for s in speakers if s['name'] in ['ずんだもん', '四国めたん']]
        (output/'voicevox-styles.json').write_text(json.dumps(cast, ensure_ascii=False, indent=2))
        STYLE_CACHE = {s['name']:{t['name']:t['id'] for t in s['styles']} for s in cast}
    return STYLE_CACHE['ずんだもん' if actor==3 else '四国めたん'][name]

def synthesize_performance(scene, request, output):
    assert ''.join(x['text'] for x in scene['delivery']) == scene['text']
    chunks=[]; cursor=0; beats=[]; timed=[]; phrases=[]
    for beat in scene['delivery']:
        speaker=style_id(beat.get('style','ノーマル'),request,output,scene['speaker'])
        q=json.loads(request('/audio_query?'+urllib.parse.urlencode({'text':beat['text'],'speaker':speaker}),b''))
        speed=beat.get('speed',1.2)
        q.update(speedScale=speed, intonationScale=beat.get('intonation',1.2), pitchScale=beat.get('pitch',0), volumeScale=beat.get('volume',1), prePhonemeLength=beat.get('lead',.02)*speed, postPhonemeLength=beat.get('tail',.03)*speed, outputSamplingRate=24000)
        for phrase in q['accent_phrases']:
            if phrase.get('pause_mora'):phrase['pause_mora']['vowel_length']=beat.get('pause',.1)*speed
        moras=[m for p in q['accent_phrases'] for m in p['moras']]
        for k,length in beat.get('vowel_seconds',{}).items():moras[int(k)]['vowel_length']=length*speed
        voiced=[m for m in moras if m['pitch']>0]
        # A shout swells then falls; a defeated sentence trails downward.
        contour=beat.get('contour')
        if contour and voiced:
            for i,m in enumerate(voiced):
                u=i/max(1,len(voiced)-1)
                m['pitch'] += (.28*math.sin(math.pi*u)-.04*u) if contour=='shout' else (-.28*u)
        wav=request('/synthesis?'+urllib.parse.urlencode({'speaker':speaker,'enable_interrogative_upspeak':'false'}),json.dumps(q).encode())
        with wave.open(io.BytesIO(wav)) as f:
            assert f.getframerate()==24000 and f.getnchannels()==1
            a=np.frombuffer(f.readframes(f.getnframes()),np.int16).astype(float)/32768
        start=cursor/24000; elapsed=q['prePhonemeLength']/speed
        for phrase in q['accent_phrases']:
            for m in phrase['moras']:
                timed.append({'text':m['text'],'seconds':start+elapsed})
                elapsed+=(float(m.get('consonant_length') or 0)+m['vowel_length'])/speed
            if phrase.get('pause_mora'):elapsed+=phrase['pause_mora']['vowel_length']/speed
        gap=round(beat.get('gap',0)*24000)
        beats.append({'text':beat['text'],'style':beat.get('style','ノーマル'),'style_id':speaker,'start':start,'duration':len(a)/24000,'gap_after':gap/24000,'query':q})
        phrases.extend(copy.deepcopy(q['accent_phrases']))
        chunks.extend([a,np.zeros(gap)]);cursor+=len(a)+gap
    audio=np.concatenate(chunks)
    # This combined query describes alignment only; individual queries synthesized the voice.
    combined={'speedScale':1.0,'intonationScale':1.0,'prePhonemeLength':0.0,'postPhonemeLength':0.0,'outputSamplingRate':24000,'accent_phrases':phrases,'kana':' / '.join(b['query']['kana'] for b in beats),'timed_moras':timed,'performance_segments':beats,'alignment_only':True}
    assert all(0<=m['seconds']<len(audio)/24000 for m in timed)
    return audio,combined
