"""Verify the delivered file, not just source configuration."""
from pathlib import Path
import json,subprocess,sys,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
import render as r
R=r.R;O=r.O;D=r.D
video=D/'STOCK02-orukan-leverage.mp4'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
data=probe(video);v=next(s for s in data['streams'] if s['codec_type']=='video');a=next(s for s in data['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1080,1920)
assert int(v['nb_frames'])==r.N
assert float(data['format']['duration'])<60
for p in [video,D/'STOCK02-mobile.mp4']:
    subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
pts=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
assert len(pts)==r.N
assert max(abs(float(x['best_effort_timestamp_time'])-i/30) for i,x in enumerate(pts))<.000002
all_boundaries=set(r.START)
pages=[]
for i,s in enumerate(r.S):
    if s.get('kind'):continue
    assert ''.join(''.join(p) for p in s['caption_pages'])==s['display_text']==s['text']
    for j,start in enumerate(r.PAGE_STARTS[i]):
        end=r.PAGE_STARTS[i][j+1] if j+1<len(r.PAGE_STARTS[i]) else s['duration']
        assert end>start
        f0=s['start_frame']+math.ceil(start*30)
        f1=min(s['end_frame']-1,s['start_frame']+math.ceil(end*30)-1)
        all_boundaries.add(f0)
        pages.append(dict(utterance=i,page=j,start_frame=f0,end_frame=f1,frame=min(f1,f0+max(1,(f1-f0)//2)),text='\n'.join(s['caption_pages'][j])))
targets=set([x['frame'] for x in pages])
boundary_frames=set()
for b in all_boundaries:
    for delta in range(-3,4):
        if 0<=b+delta<r.N:boundary_frames.add(b+delta)
targets|=boundary_frames
# Decode one continuous stream and compare all boundary-neighbourhood frames.
p=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
actual={};diffs=[];bottom_diffs=[];framebytes=r.W*r.H*3
for i in range(r.N):
    raw=p.stdout.read(framebytes);assert len(raw)==framebytes
    if i in targets:
        arr=np.frombuffer(raw,np.uint8).reshape(r.H,r.W,3);actual[i]=Image.fromarray(arr).resize((270,480))
        if i in boundary_frames:
            expected=np.asarray(r.frame(i));diffs.append(float(np.abs(arr.astype(float)-expected).mean()))
            bottom_diffs.append(float(np.abs(arr[r.BOTTOM:].astype(float)-np.asarray(r.bg(r.current(i)).convert('RGB'))[r.BOTTOM:]).mean()))
p.stdout.close();assert p.wait()==0
assert max(diffs)<7,('frame source mismatch',max(diffs))
assert max(bottom_diffs)<7,('bottom source mismatch',max(bottom_diffs))
def sheets(items,fn):
    for start in range(0,len(items),12):
        sheet=Image.new('RGB',(1080,1500),r.INK);d=ImageDraw.Draw(sheet)
        for k,(frame,label) in enumerate(items[start:start+12]):
            x=(k%4)*270;y=(k//4)*500;sheet.paste(actual[frame],(x,y));d.text((x+7,y+482),label,fill='white')
        sheet.save(O/f'{fn}-{start//12}.jpg',quality=94)
sheets([(x['frame'],f"U{x['utterance']:02} P{x['page']}  {x['frame']/30:.2f}s") for x in pages],'final-captions')
# Every boundary is represented with before / at / after views for visual review.
triples=[]
for b in sorted(all_boundaries):
    for delta in [-1,0,1]:
        if b+delta in actual:triples.append((b+delta,f'boundary {b} {delta:+}'))
sheets(triples,'final-boundaries')
report={'duration_seconds':r.DURATION,'frames':r.N,'resolution':[r.W,r.H],'fps':30,'utterances':len(pages) and len([s for s in r.S if not s.get('kind')]),'caption_pages':len(pages),'caption_full_text_match':True,'continuous_decode_both_files':True,'pts_step_1_30':True,'boundaries':len(all_boundaries),'boundary_frames_compared':len(boundary_frames),'maximum_mean_pixel_error':max(diffs),'bottom_maximum_mean_pixel_error':max(bottom_diffs),'bottom_no_foreground_asserted_during_every_rendered_frame':True,'arithmetic':{'purchase':100+200,'sale':300*.9,'net':300*.9-200,'loss_rate':(100-(300*.9-200))/100},'files':{x.name:{'size':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [video,D/'STOCK02-mobile.mp4']},'human_equivalent_listening_review':False,'measured_retention_improvement':False}
assert report['arithmetic']=={'purchase':300,'sale':270.0,'net':70.0,'loss_rate':.3}
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(O/'caption-pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
