"""STOCK02: shared frame-accurate financial skits, original sprites and aligned graphics."""
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageFilter
import numpy as np
import json,math,bisect,wave,subprocess,sys,os
R=Path(os.environ['FINANCE_PROJECT']).resolve();A=R/'assets';O=R/'output';D=R/'deliverables';D.mkdir(exist_ok=True)
BASE=R.parent/'STOCK02/assets'
C=json.loads((R/'project.json').read_text())
W,H,FPS,BOTTOM=1080,1920,30,1560
S=json.loads((O/'timeline.json').read_text());START=[s['start_frame'] for s in S];N=S[-1]['end_frame'];DURATION=N/FPS
with wave.open(str(O/'voice.wav')) as f:V=np.frombuffer(f.readframes(f.getnframes()),np.int16)/32768.
INK='#18252c';WHITE='#fffbed';GREEN='#2b6539';ROSE='#843459';RED='#ca354d';GOLD='#ffd45f';DEBT='#7463ad';MINT='#8ed59c'

def asset(name):
    for root in [A,BASE]:
        p=root/name
        if p.exists():return p
        if p.with_suffix('.webp').exists():return p.with_suffix('.webp')
    raise FileNotFoundError(name)

@lru_cache(None)
def font(n,role='caption'):
    try:p=asset('DejaVuSans-Bold.ttf' if role=='number' else 'RocknRollOne.ttf')
    except FileNotFoundError:p=asset('DejaVuSans-Bold-subset.ttf')
    return ImageFont.truetype(str(p),n)
def text(d,xy,t,n=54,fill=INK,role='caption',anchor='mm',maxw=970,stroke=0):
    assert font(n,role).getlength(t)<=maxw,(t,n,font(n,role).getlength(t),maxw)
    d.text(xy,t,font=font(n,role),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=WHITE)
def card(d,b,fill=WHITE,radius=23):
    d.rounded_rectangle((b[0],b[1]+7,b[2],b[3]+7),radius,fill=(14,20,33,80))
    d.rounded_rectangle(b,radius,fill=fill)
def ease(u,secs=.5):return 1-(1-max(0,min(1,u/secs)))**3
def current(i):return bisect.bisect_right(START,min(N-1,max(0,i)))-1

def mora_offset(idx,word):
    q=json.loads((O/f'query-{idx:02}.json').read_text());chars=[];times=[];t=q['prePhonemeLength']/q['speedScale']
    if q.get('timed_moras'):
        for m in q['timed_moras']:
            for ch in m['text']:chars.append(ch);times.append(m['seconds'])
        pos=''.join(chars).find(word)
        if pos<0:raise ValueError((idx,word,''.join(chars)))
        return times[pos]
    for a in q['accent_phrases']:
        for m in a['moras']:
            for ch in m['text']:chars.append(ch);times.append(t)
            t+=(float(m.get('consonant_length') or 0)+m['vowel_length'])/q['speedScale']
        if a.get('pause_mora'):t+=a['pause_mora']['vowel_length']/q['speedScale']
    spelling=''.join(chars);pos=spelling.find(word)
    if pos<0:raise ValueError((idx,word,spelling))
    return times[pos]
PAGE_STARTS={}
for i,s in enumerate(S):
    q=json.loads((O/f'query-{i:02}.json').read_text())
    PAGE_STARTS[i]=[0.0]+[b['start'] for b in q['performance_segments'][1:]]
    assert len(PAGE_STARTS[i])==len(s['caption_pages'])
REVEAL_PAGES={'fx':{'hook':1,'interest':1,'reveal':1},'nisa':{'reveal':1,'setting':1}}
REVEALS={s['scene_id']:PAGE_STARTS[i][REVEAL_PAGES[C['theme']][s['scene_id']]] for i,s in enumerate(S) if s['scene_id'] in REVEAL_PAGES[C['theme']]}
(O/'reveal-times.json').write_text(json.dumps({'page_starts':PAGE_STARTS,'amount_offsets':REVEALS},indent=2))

@lru_cache(None)
def bg_asset(kind):return ImageOps.fit(Image.open(asset(f'{kind}.png')).convert('RGB'),(W,H),Image.Resampling.LANCZOS)
@lru_cache(None)
def bg(idx):
    s=S[idx];im=bg_asset(s['background']).copy()
    if s['camera']!='wide':
        x=0 if s['camera']=='mclose' else 110
        im=im.crop((x,85,x+960,1792)).resize((W,H),Image.Resampling.LANCZOS)
    if s.get('kind'):im=ImageEnhance.Brightness(im).enhance(.26)
    return im.convert('RGBA')

@lru_cache(None)
def sprite(who,pose,opened,width):
    p=Image.open(asset(f'intro-{who}-{pose}{"-open" if opened else ""}.png')).convert('RGBA')
    if who=='maki':p=ImageOps.mirror(p)
    return p.resize((width,round(p.height*width/p.width)),Image.Resampling.LANCZOS)
def mouth(i,s,who):
    if s['speaker']!=(3 if who=='zunda' else 2):return False
    v=V[max(0,i*800):min(len(V),i*800+800)]
    return bool(len(v) and np.sqrt(np.mean(v*v))>.023)

@lru_cache(None)
def caption(idx,page=0):
    s=S[idx];im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
    if s.get('kind'):return im
    lines=s['caption_pages'][page];col=GREEN if s['speaker']==3 else ROSE
    size=64
    if s['scene_id']=='panic' and page==0:size=90;col=RED
    while max(font(size).getlength(t) for t in lines)>944:size-=1
    assert size>=56,(idx,page,size)
    bottom=326 if len(lines)==2 else 252
    card(d,(38,134,1042,bottom),(255,252,245,247))
    d.rounded_rectangle((38,134,50,bottom),6,fill=col)
    cy=(134+bottom)/2
    for k,line in enumerate(lines):text(d,(540,cy+(k-(len(lines)-1)/2)*78),line,size,col,maxw=950)
    return im

from graphics import draw_graphics
@lru_cache(maxsize=48)
def graphics(idx,step):
    return draw_graphics(sys.modules[__name__],idx,step/30)

def foreground(i):
    idx=current(i);s=S[idx];sid=s['scene_id'];u=(i-s['start_frame'])/FPS
    im=Image.new('RGBA',(W,H))
    if not s.get('kind'):
        for who in ['maki','zunda']:
            cam=s['camera']
            if cam=='mclose' and who!='maki':continue
            if cam=='zclose' and who!='zunda':continue
            if cam=='wide':width=324;cx=246 if who=='maki' else 824
            else:width=450;cx=260 if who=='maki' else 822
            pic=sprite(who,s['pose_m'] if who=='maki' else s['pose_z'],mouth(i,s,who),width)
            x=round(cx-pic.width/2);y=1540-pic.height
            if who=='zunda' and s['emotion']=='shock':
                strength=10 if sid=='panic' else 5;x+=round(strength*math.sin(u*54)*(.75+.25*math.sin(u*5)))
                y-=round(5*(.5+.5*math.sin(u*35)))
            if who==('zunda' if s['speaker']==3 else 'maki') and u<.2 and sid!='ending':y-=round(8*math.sin(u*math.pi/.2))
            if who=='zunda' and sid=='ending':y+=round(9*min(1,u/.55))
            sd=ImageDraw.Draw(im);sx=x+pic.width*(.51 if who=='maki' else .39)
            sd.ellipse((sx-width*.20,1525,sx+width*.20,1544),fill=(25,26,31,48))
            im.alpha_composite(pic,(x,y))
            if who=='zunda' and s['emotion']=='shock':
                # Manga motion accents around the actor, without replacing the original face art.
                sd=ImageDraw.Draw(im)
                for k in range(3):
                    xx=x+35+k*24;yy=y+155+(k%2)*13
                    sd.line((xx,yy,xx-20,yy-65),fill='#86c9f2',width=7)
                if int(u*5)%2==0:
                    sd.arc((x+pic.width-24,y+135,x+pic.width+9,y+189),-20,200,fill='#b7e5fb',width=6)
    im.alpha_composite(graphics(idx,round(u*30)))
    im.alpha_composite(caption(idx,max(0,bisect.bisect_right(PAGE_STARTS.get(idx,[0]),u)-1)))
    assert im.getchannel('A').crop((0,BOTTOM,W,H)).getbbox() is None,('bottom',i)
    return im

def frame(i):
    idx=current(i);return Image.alpha_composite(bg(idx),foreground(i)).convert('RGB')

def preview():
    for start in range(0,len(S),6):
        sheet=Image.new('RGB',(1080,1280),INK)
        for k,s in enumerate(S[start:start+6]):
            i=min(s['end_frame']-1,s['start_frame']+round(s['frames']*.72));f=frame(i)
            f.save(O/f'preview-{start+k:02}.png');sheet.paste(f.resize((360,640)),((k%3)*360,(k//3)*640))
        sheet.save(O/f'contact-{start//6}.jpg',quality=94)
    print('preview ready',N,DURATION,flush=True)
def main():
    if '--preview' in sys.argv:preview();return
    p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(O/'silent.mp4')],stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
        if i%180==0:print('render',i,'/',N,flush=True)
    p.stdin.close();assert p.wait()==0
    print('render done',flush=True)
if __name__=='__main__':main()
