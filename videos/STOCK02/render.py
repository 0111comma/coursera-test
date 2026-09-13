"""STOCK02: frame-accurate skit, original character mouth parts and synchronized graphics."""
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageFilter
import numpy as np
import json,math,bisect,wave,subprocess,sys
R=Path(__file__).resolve().parent;A=R/'assets';O=R/'output';D=R.parent/'deliverables';D.mkdir(exist_ok=True)
W,H,FPS,BOTTOM=1080,1920,30,1560
S=json.loads((O/'timeline.json').read_text());START=[s['start_frame'] for s in S];N=S[-1]['end_frame'];DURATION=N/FPS
with wave.open(str(O/'voice.wav')) as f:V=np.frombuffer(f.readframes(f.getnframes()),np.int16)/32768.
INK='#18252c';WHITE='#fffbed';GREEN='#2b6539';ROSE='#843459';RED='#ca354d';GOLD='#ffd45f';DEBT='#7463ad';MINT='#8ed59c'

def asset(name):
    p=A/name
    return p if p.exists() else p.with_suffix('.webp')

@lru_cache(None)
def font(n,role='caption'):
    p=A/('DejaVuSans-Bold.ttf' if role=='number' else 'RocknRollOne.ttf')
    if not p.exists() and role=='number':p=A/'DejaVuSans-Bold-subset.ttf'
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
    for a in q['accent_phrases']:
        for m in a['moras']:
            for ch in m['text']:chars.append(ch);times.append(t)
            t+=(float(m.get('consonant_length') or 0)+m['vowel_length'])/q['speedScale']
        if a.get('pause_mora'):t+=a['pause_mora']['vowel_length']/q['speedScale']
    spelling=''.join(chars);pos=spelling.find(word)
    if pos<0:raise ValueError((idx,word,spelling))
    return times[pos]
PAGE_STARTS={i:[0.0]+[mora_offset(i,c) for c in s.get('caption_cues',[])] for i,s in enumerate(S) if not s.get('kind')}
REVEALS={
    'fund_own':mora_offset(2,'ヒャクマン'),
    'fund_debt':mora_offset(2,'ニヒャクマン'),
    'fund_total':mora_offset(2,'サンビャクマン'),
    'crash':mora_offset(6,'ジュッパアセント'),
    'proceeds':mora_offset(8,'ニヒャクナナジュウ'),
    'debt':mora_offset(10,'ニヒャクマン'),
    'net':mora_offset(11,'ナナジュウマン'),
    'thirty':mora_offset(12,'サンジュッパアセント'),
}
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
    while max(font(size).getlength(t) for t in lines)>944:size-=1
    assert size>=56,(idx,page,size)
    bottom=326 if len(lines)==2 else 252
    card(d,(38,134,1042,bottom),(255,252,245,247))
    d.rounded_rectangle((38,134,50,bottom),6,fill=col)
    cy=(134+bottom)/2
    for k,line in enumerate(lines):text(d,(540,cy+(k-(len(lines)-1)/2)*78),line,size,col,maxw=950)
    return im

def note(d,y=668):
    t='仮定の例・利息等を除く';w=font(28).getlength(t)
    d.rounded_rectangle((540-w/2-14,y-23,540+w/2+14,y+23),12,fill=(255,251,239,242))
    text(d,(540,y),t,28)
def label(d,xy,t,n=32,fill=INK):text(d,xy,t,n,fill)
def arrow(d,x,y,fill=INK):
    d.line((x-25,y,x+25,y),fill=fill,width=7);d.line((x+10,y-16,x+26,y,x+10,y+16),fill=fill,width=7)

def phone(d,x,y,w=250,h=430,screen='loss',progress=1):
    d.rounded_rectangle((x+10,y+12,x+w+10,y+h+12),32,fill=(12,15,20,60))
    d.rounded_rectangle((x,y,x+w,y+h),32,fill='#25313f',outline='#d0d5dc',width=5)
    d.rounded_rectangle((x+13,y+21,x+w-13,y+h-21),20,fill='#121724' if screen=='off' else WHITE)
    d.rounded_rectangle((x+w*.36,y+8,x+w*.64,y+17),4,fill='#06090d')
    if screen=='loss':
        text(d,(x+w/2,y+80),'オルカン',33,maxw=w-30)
        pts=[(x+28,y+155),(x+72,y+174),(x+100,y+155),(x+138,y+236),(x+170,y+221),(x+w-30,y+283)]
        n=min(len(pts),max(2,round(len(pts)*progress)))
        d.line(pts[:n],fill=RED,width=8)
        if progress>.85:text(d,(x+w/2,y+344),'−10%',43,RED,role='number',maxw=w-22)
    elif screen=='jobs':
        text(d,(x+w/2,y+80),'求人',46,maxw=w-30)
        for k in range(3):
            yy=y+149+k*69;d.rounded_rectangle((x+27,yy,x+w-27,yy+46),8,fill='#d8e6df')
            d.line((x+42,yy+17,x+w-52,yy+17),fill='#80968a',width=5)

@lru_cache(maxsize=32)
def graphics(idx,step):
    s=S[idx];sid=s['scene_id'];u=step/30;im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
    if s.get('kind'):
        text(d,(540,750),s['title'],88,WHITE)
        if s.get('subtitle'):text(d,(540,918),s['subtitle'],47,WHITE)
        d.line((240,843,840,843),fill='#656775',width=5)
        d.line((240,843,240+600*ease(u,.48),843),fill=GOLD,width=8)
        return im
    if sid=='funding':
        card(d,(62,377,1018,646));x=100;y=504
        if u>=REVEALS['fund_own']:
            q=ease(u-REVEALS['fund_own'],.38);d.rounded_rectangle((x,y,x+max(1,270*q),y+52),10,fill=MINT)
            text(d,(235,434),'自分 100万円',37)
        if u>=REVEALS['fund_debt']:
            q=ease(u-REVEALS['fund_debt'],.38);d.rounded_rectangle((370,y,370+max(1,540*q),y+52),10,fill=DEBT)
            text(d,(662,434),'借入 200万円',37)
        if u>=REVEALS['fund_total']:text(d,(540,602),'投資額 300万円',46,GREEN)
        note(d,688)
    elif sid=='panic':
        phone(d,62,562,290,456,'loss',ease(max(0,u-REVEALS['crash']),.55))
        text(d,(210,1080),'架空の下落例',28,WHITE,stroke=0,maxw=350)
    elif sid=='proceeds':
        card(d,(70,380,1010,625));text(d,(540,423),'売却代金',35)
        text(d,(270,513),'300万円',55,maxw=375);arrow(d,535,513)
        if u>=REVEALS['proceeds']:
            text(d,(806,513),'270万円',55,RED,maxw=375)
            q=ease(u-REVEALS['proceeds']);d.rounded_rectangle((145,571,935,592),7,fill='#ded9d4')
            d.rounded_rectangle((145,571,145+790*(1-.1*q),592),7,fill=RED)
        note(d,665)
    elif sid=='relief':
        card(d,(50,557,412,816));text(d,(231,612),'売却代金',34,maxw=330)
        text(d,(231,715),'270',76,GREEN,role='number',maxw=340);text(d,(340,780),'万円',34,maxw=110)
    elif sid=='debt':
        card(d,(646,548,1033,823));text(d,(840,603),'借金',42,maxw=330)
        if u>=REVEALS['debt']:text(d,(840,692),'200',83,DEBT,role='number',maxw=340)
        text(d,(840,775),'万円',34,maxw=330)
    elif sid=='reveal':
        card(d,(40,524,430,873));text(d,(235,578),'借金を引くと',31,maxw=370)
        if u>=REVEALS['net']:
            age=u-REVEALS['net'];size=110+round(13*math.exp(-age*7)*math.sin(min(1,age/.32)*math.pi))
            text(d,(225,704),'70',size,RED,role='number',maxw=350)
            text(d,(346,790),'万円',39,maxw=120)
        text(d,(235,851),'利息等は別',26,maxw=350)
    elif sid=='lesson':
        card(d,(55,370,1025,635))
        text(d,(83,431),'オルカン',37,anchor='lm',maxw=350)
        text(d,(83,535),'自己資金',37,anchor='lm',maxw=350)
        d.rounded_rectangle((400,414,870,450),8,fill='#e7e1db');d.rounded_rectangle((400,518,870,554),8,fill='#e7e1db')
        d.rounded_rectangle((400,414,400+470*.9,450),8,fill='#6d96b1')
        text(d,(947,431),'−10%',35,RED,role='number',maxw=140)
        if u>=REVEALS['thirty']:
            q=ease(u-REVEALS['thirty'],.58);d.rounded_rectangle((400,518,400+470*(1-.3*q),554),8,fill=RED)
            text(d,(947,535),'−30%',35,RED,role='number',maxw=140)
        else:d.rounded_rectangle((400,518,870,554),8,fill=MINT)
        text(d,(540,597),'借金を差し引いて比較',28)
        note(d,672)
    elif sid=='interest':
        card(d,(646,537,1032,839));text(d,(839,599),'借金',40,maxw=330)
        text(d,(839,684),'200万円',45,DEBT,maxw=370)
        if u>=PAGE_STARTS[idx][1]:text(d,(839,774),'＋利息',44,RED,maxw=350)
    elif sid in ['escape','ending']:
        screen='jobs' if sid=='ending' else ('off' if u>.40 else 'loss')
        phone(d,60,558,290,456,screen,1)
        if sid=='escape' and u<.43:
            x,y=350,731;d.ellipse((x-16,y-16,x+16,y+16),outline=GOLD,width=6)
    elif sid=='retort':
        card(d,(656,549,1028,828));text(d,(842,610),'返済日',47,RED,maxw=340)
        # Calendar symbol has no arbitrary due date or repayment number.
        d.rounded_rectangle((759,669,925,784),13,outline=DEBT,width=6)
        d.line((759,702,925,702),fill=DEBT,width=6)
        for x in [796,838,879]:d.ellipse((x-6,728,x+6,740),fill=DEBT)
    return im

def foreground(i):
    idx=current(i);s=S[idx];sid=s['scene_id'];u=(i-s['start_frame'])/FPS
    im=Image.new('RGBA',(W,H))
    if not s.get('kind'):
        for who in ['maki','zunda']:
            cam=s['camera']
            if cam=='mclose' and who!='maki':continue
            if cam=='zclose' and who!='zunda':continue
            if cam=='wide':width=430 if who=='maki' else 423;cx=253 if who=='maki' else 826
            else:width=563;cx=339 if who=='maki' else 744
            pic=sprite(who,s['pose_m'] if who=='maki' else s['pose_z'],mouth(i,s,who),width)
            x=round(cx-pic.width/2);y=1540-pic.height
            if who=='zunda' and sid in ['panic','reveal','bargain']:
                strength=11 if sid!='bargain' else 5;x+=round(strength*math.sin(u*54)*(.75+.25*math.sin(u*5)))
                y-=round(5*(.5+.5*math.sin(u*35)))
            if who==('zunda' if s['speaker']==3 else 'maki') and u<.2:y-=round(8*math.sin(u*math.pi/.2))
            if who=='zunda' and sid=='ending':y-=round(5*math.sin(min(1,u/.3)*math.pi))
            sd=ImageDraw.Draw(im);sx=x+pic.width*(.51 if who=='maki' else .39)
            sd.ellipse((sx-width*.20,1525,sx+width*.20,1544),fill=(25,26,31,48))
            im.alpha_composite(pic,(x,y))
            if who=='zunda' and sid in ['panic','reveal','bargain']:
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
