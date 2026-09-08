#!/usr/bin/env python3
"""Finance Zundamon pilot: narration, animated holdings and character, one MP4."""
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
import os
import subprocess
import sys
import urllib.parse
import urllib.request
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'output'
WORK = OUT / 'work'
W, H, FPS = 1080, 1920, 24
BG, INK, GREEN, BLUE, GOLD = '#F7F5EC', '#183D32', '#477D2A', '#3568A0', '#C07624'
FONT = ROOT / 'assets/fonts/RocknRollOne.ttf'
PARTS = ROOT / 'production/assets/zunda/parts'
VOICE_URL = 'http://127.0.0.1:50021'
BOTTOM_UI_PX = 360
CONTENT_BOTTOM = H - BOTTOM_UI_PX
PANEL_LEFT, PANEL_RIGHT = 32, W - 32
RIGHT_UI_RESERVE = 0
SOURCES = json.loads(Path(__file__).with_name('sources.json').read_text())

@dataclass
class Unit:
    scene: str
    subtitle: str
    note: str
    expr: str = 'normal'
    speaker: int = 3
    speed: float = 1.17
    @property
    def narration(self):
        return self.subtitle.replace('S&P500', 'エスアンドピーごひゃく').replace('QQQ', 'キューキューキュー')

UNITS = [
    Unit('cover', '投資信託を3本買えば、分散？', '本数だけで分散？', 'normal'),
    Unit('cover', 'ボクは、まず中身を見るのだ。', '中身を見るのだ', 'smug'),
    Unit('intro', '投資信託は、お金をまとめて、いろいろな投資先へ投資する商品。', 'お金をまとめて投資', 'normal'),
    Unit('intro', '別の商品でも、投資先が重なることはある。', '名前より投資先', 'normal'),
    Unit('products', '例えば、オルカン、S&P500連動商品、QQQ。', 'この3商品で見る', 'normal'),
    Unit('names', 'エヌビディア、アップル、マイクロソフト。', '中身を並べると？', 'normal'),
    Unit('common', 'この3社は、どれにも入っているのだ。', 'また会ったのだ', 'smug'),
    Unit('routes', '別の商品から買っても、同じ会社への投資は重なる。', '別の商品から同じ企業へ', 'smug'),
    Unit('different', 'もちろん、全部同じ中身ではない。投資先も割合も違う。', '全部同じではない', 'normal'),
    Unit('count', 'でも、商品が3本あるだけでは、どれだけ分散したかは分からない。', '本数だけでは分からない', 'normal'),
    Unit('check', 'だから、買う前に月次レポートで、投資先と割合を見る。', 'レポートの中身を確認', 'normal'),
    Unit('check', '商品をまたいで、同じ企業への投資が重なっていないか確かめる。', '商品をまたいで確認', 'smug'),
    Unit('close', '袋を3つに分けても、', '袋は3つでも……', 'normal'),
    Unit('close', '中身まで別物にはならないのだ。', '見るのは中身と割合', 'happy'),
]
SUBTITLE_LINES = ['投資信託を3本買えば、分散？', 'ボクは、まず中身を見るのだ。', '投資信託は、お金をまとめて、\nいろいろな投資先へ投資する商品。', '別の商品でも、\n投資先が重なることはある。', '例えば、オルカン、\nS&P500連動商品、QQQ。', 'エヌビディア、アップル、\nマイクロソフト。', 'この3社は、\nどれにも入っているのだ。', '別の商品から買っても、\n同じ会社への投資は重なる。', 'もちろん、全部同じ中身ではない。\n投資先も割合も違う。', 'でも、商品が3本あるだけでは、\nどれだけ分散したかは分からない。', 'だから、買う前に月次レポートで、\n投資先と割合を見る。', '商品をまたいで、同じ企業への投資が\n重なっていないか確かめる。', '袋を3つに分けても、', '中身まで別物にはならないのだ。']
assert len(SUBTITLE_LINES)==len(UNITS)
assert all(t.replace('\n','') == u.subtitle for t,u in zip(SUBTITLE_LINES,UNITS))

@lru_cache(None)
def font(size):
    return ImageFont.truetype(str(FONT), size)

def text(d, xy, value, size=50, fill=INK, anchor='mm', width=None):
    ft = font(size)
    box = d.textbbox(xy, value, font=ft, anchor=anchor)
    if width is not None and box[2] - box[0] > width:
        raise ValueError(f'Text too wide ({box[2]-box[0]} > {width}): {value}')
    if box[0] < 0 or box[1] < 0 or box[2] > W or box[3] > CONTENT_BOTTOM:
        raise ValueError(f'Text outside canvas: {value}: {box}')
    d.text(xy, value, font=ft, fill=fill, anchor=anchor)

def lines(d, xy, value, size=60, gap=84, fill=INK, width=840):
    for k, line in enumerate(value.split('\n')):
        text(d, (xy[0], xy[1]+k*gap), line, size, fill, width=width)

def wrap(value, size=58, width=790):
    # Same words as narration; no ellipsis or subtitle truncation.
    out, line = [], ''
    for char in value:
        if font(size).getlength(line+char) > width and line:
            if char in '、。？！':
                out.append(line[:-1]); line=line[-1]+char
            else:
                out.append(line); line=char
        else:
            line += char
    if line: out.append(line)
    return out

def roundbox(d, box, fill='white', outline=None, radius=28, width=3):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def ease(t):
    t = min(1, max(0, t))
    return 1-(1-t)**3

FUND_LABELS = ['オルカン','S&P500連動','QQQ']
COMPANIES = [('エヌビディア','#28694F'),('アップル','#AD642D'),('マイクロソフト','#66558C')]

def heading(scene):
    if scene=='cover': return '3本買えば、\n分散できる？'
    if scene=='intro': return '商品の向こうに、\n投資先がある。'
    if scene=='products': return 'この3つを、\n開いてみるのだ。'
    if scene in ('names','common'): return 'あれ？\n同じ企業がいる。'
    if scene in ('routes','count'): return '商品は3つ。\nでも、同じ企業へ。'
    if scene=='different': return '共通する部分も、\n違う部分もある。'
    if scene=='check': return '買う前に見るのは、\n投資先と割合。'
    return '袋を分けても、\n中身は重なる。'

def base(unit, number):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((0,42,W,111),fill=INK)
    text(d,(540,76),'やけに金融リテラシーの高いずんだもん',32,'white',width=1000)
    for i,line in enumerate(heading(unit.scene).split('\n')):
        text(d,(62,200+i*92),line,72,INK,anchor='lm',width=956)
    d.rectangle((62,349,172,357),fill=GREEN)
    # No generic diagram panel or repeated speech bubble: each visual owns its shape.
    d.rectangle((0,1360,W,1507),fill=INK)
    sub=SUBTITLE_LINES[number].split('\n')
    lines(d,(540,1433-(len(sub)-1)*33),'\n'.join(sub),52,66,'white',width=1008)
    text(d,(540,1536),'VOICEVOX:ずんだもん ｜ 立ち絵：坂本アヒル',23,INK,width=1016)
    return im

def arrow(d,a,b,color=INK,width=5):
    d.line((*a,*b),fill=color,width=width)
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);length=15
    pts=[b,(b[0]-length*math.cos(angle-.55),b[1]-length*math.sin(angle-.55)),(b[0]-length*math.cos(angle+.55),b[1]-length*math.sin(angle+.55))]
    d.polygon(pts,fill=color)

def source_note(d,single=False):
    value='出典：オルカン 2026年7月月報（一部を図示）' if single else '保有資料：オルカン26/7・S&P500連動26/8・QQQ26/9/4'
    text(d,(540,1035),value,23,INK,width=980)

def company(d,box,idx,size=32):
    name,color=COMPANIES[idx];roundbox(d,box,color,radius=12)
    text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),name,size,'white',width=box[2]-box[0]-20)

def takeaway(d,scene):
    msg={
        'cover':'名前を数える前に、\n中身を見るのだ。',
        'intro':'買っているのは、\nその先の投資対象。',
        'products':'別の商品名。\n投資先はどうだろう？',
        'names':'この顔ぶれ、\nどの商品にも。',
        'common':'同じ色は、\n同じ企業なのだ。',
        'routes':'別々の商品から、\n同じ企業を持つ。',
        'different':'一部が共通でも、\n全部が同じではない。',
        'count':'本数だけで\n分散は決められない。',
        'check':'投資先と、その割合。\n保有全体で確認する。',
        'close':'見るのは、\n袋の数より中身。',
    }[scene]
    lines(d,(387,1168),msg,43,72,INK,width=680)

def selection(d,t):
    roundbox(d,(62,406,1018,1000),'#FFFFFF',radius=26)
    text(d,(107,457),'購入候補',36,INK,anchor='lm',width=780)
    text(d,(940,457),'3商品',30,GREEN,width=130)
    for i,name in enumerate(FUND_LABELS):
        y=576+i*137
        if i: d.line((108,y-67,972,y-67),fill='#DDE3D9',width=2)
        d.ellipse((108,y-24,156,y+24),fill=GREEN)
        d.line((119,y,128,y+10,145,y-11),fill='white',width=5)
        text(d,(194,y-9),name,51,INK,anchor='lm',width=725)
        desc=['全世界株式','米国の大型株','Nasdaq-100に連動するETF'][i]
        text(d,(194,y+41),desc,25,'#607568',anchor='lm',width=725)

def pooling(d,t):
    text(d,(540,430),'投資家のお金',36,INK,width=980)
    for x in (240,440,640,840):
        d.ellipse((x-37,477,x+37,551),fill='#EAD5A4',outline=GOLD,width=3)
        text(d,(x,514),'円',35,INK,width=62)
        arrow(d,(x,562),(540,662),'#9AAA99',4)
    roundbox(d,(308,664,772,778),INK,radius=22)
    text(d,(540,721),'投資信託',53,'white',width=420)
    for x in (238,540,842):
        arrow(d,(540,789),(x,874),GREEN,5)
        d.rectangle((x-50,884,x+50,972),fill='#CCD9CC')
        for dx in (-25,0,25):
            for y in (902,928):d.rectangle((x+dx-5,y,x+dx+5,y+12),fill=INK)
    text(d,(540,1018),'企業の株など、いろいろな投資対象へ',30,INK,width=980)

def folders(d,scene,t):
    opened=scene in ('names','common','different')
    for i,x in enumerate((62,397,732)):
        roundbox(d,(x+8,441,x+294,990),'#DDE5D9',radius=13)
        roundbox(d,(x,420,x+286,977),'white',outline='#B5C3B0',radius=13)
        d.rectangle((x,448,x+286,531),fill=INK)
        text(d,(x+143,489),FUND_LABELS[i],37,'white',width=260)
        if not opened:
            text(d,(x+143,649),'運用レポート',34,INK,width=260)
            for y,w in ((724,186),(755,158),(786,174)):
                d.line((x+47,y,x+47+w,y),fill='#D0D9CB',width=7)
            text(d,(x+143,899),'投資先を見る',30,GREEN,width=260)
        else:
            for j in range(3):
                y=568+j*104
                shown=scene!='names' or t>j*.32
                if shown: company(d,(x+14,y,x+272,y+74),j,29)
            d.line((x+27,895,x+259,895),fill='#D9E1D4',width=2)
            detail=['全世界の株式へ','米国の大型株へ','Nasdaq-100へ'][i] if scene=='different' else 'ほかの保有企業も'
            text(d,(x+143,936),detail,26,INK,width=258)
    source_note(d)

def convergence(d,t):
    for i,(x,name) in enumerate(zip((213,540,867),FUND_LABELS)):
        text(d,(x,450),name,36,INK,width=294)
        company(d,(x-139,510,x+139,587),0,31)
        arrow(d,(x,601),(540,784),'#7C9C86',5)
        u=(t*.40+i*.22)%1
        px=x+(540-x)*u;py=611+(774-611)*u
        d.ellipse((px-7,py-7,px+7,py+7),fill=GREEN)
    roundbox(d,(346,657,734,714),BG,radius=10)
    text(d,(540,685),'投資額の一部が',32,INK,width=360)
    company(d,(183,795,897,924),0,67)
    text(d,(540,979),'同じ企業への投資が重なる',38,INK,width=980)
    source_note(d)

def report(d,t):
    # One sourced real row demonstrates WHERE to inspect names and weights.
    d.polygon([(120,424),(960,424),(960,1001),(120,1001)],fill='#D7DED1')
    d.rectangle((104,410,944,985),fill='white')
    text(d,(146,461),'月次レポート',43,INK,anchor='lm',width=742)
    text(d,(146,519),'オルカン｜2026年7月31日',29,INK,anchor='lm',width=742)
    d.line((146,565,902,565),fill=INK,width=3)
    text(d,(147,625),'組入銘柄',34,INK,anchor='lm',width=430)
    text(d,(800,625),'比率',34,INK,width=172)
    roundbox(d,(132,677,916,789),'#EBF2E5',outline=GREEN,radius=13)
    text(d,(158,733),'NVIDIA',55,INK,anchor='lm',width=470)
    text(d,(791,733),'4.4%',62,INK,width=210)
    for y,w in ((827,636),(863,583),(899,620)):
        d.line((150,y,150+w,y),fill='#E3E7DE',width=9)
    arrow(d,(292,652),(292,691),GREEN,4)
    arrow(d,(800,652),(800,691),GREEN,4)
    source_note(d,True)

def bags(d,t):
    for i,x in enumerate((62,397,732)):
        d.arc((x+74,420,x+212,595),180,360,fill=INK,width=7)
        d.polygon([(x+19,502),(x+267,502),(x+286,915),(x,915)],fill='#E4EBD9',outline=INK,width=3)
        text(d,(x+143,565),FUND_LABELS[i],36,INK,width=257)
        for j in range(3):company(d,(x+20,631+j*84,x+266,691+j*84),j,27)
        text(d,(x+143,890),'ほか',23,INK,width=250)
    source_note(d)

def diagram(im,scene,t,number):
    d=ImageDraw.Draw(im)
    if scene=='cover':selection(d,t)
    elif scene=='intro' and number==2:pooling(d,t)
    elif scene=='intro':folders(d,'products',t)
    elif scene in ('products','names','common','different'):folders(d,scene,t)
    elif scene in ('routes','count'):convergence(d,t)
    elif scene=='check' and number==10:report(d,t)
    elif scene=='check':convergence(d,t)
    elif scene=='close':bags(d,t)
    takeaway(d,scene)

@lru_cache(None)
def sprite(expr,mouth,eyes):
    p=PARTS/f'{expr}_{mouth}_{eyes}.png'
    if not p.exists(): p=PARTS/f'{expr}_{mouth}_open.png'
    if not p.exists(): p=PARTS/'normal_0_open.png'
    return Image.open(p).convert('RGBA').resize((258,295),Image.Resampling.LANCZOS)

def frame(unit,number,time,voice,rate):
    im=base_cache[number].copy()
    diagram(im,unit.scene,time,number)
    a=int(max(0,time-.02)*rate); b=min(len(voice),a+int(rate*.10))
    rms=float(np.sqrt(np.mean(voice[a:b]**2))) if b>a else 0
    mouth=2 if rms>.055 else 1 if rms>.012 else 0
    eyes='closed' if 1.70 < time%3.6 < 1.84 else 'open'
    dy=round(4*math.sin(time*2))
    im.paste(sprite(unit.expr,mouth,eyes),(790,1055+dy),sprite(unit.expr,mouth,eyes))
    if np.any(np.asarray(im)[CONTENT_BOTTOM:] != np.array([247,245,236])):
        raise ValueError('Bottom UI reserve is not empty')
    if tuple(im.getpixel((W-1,1400))) != (24,61,50):
        raise ValueError('Right rail margin reintroduced')
    return im

def request(path,data=None):
    req=urllib.request.Request(VOICE_URL+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=90) as response: return response.read()

def synth(unit,k):
    digest=hashlib.sha256((unit.narration+str(unit.speed)+'speaker3-v1').encode()).hexdigest()[:14]
    wav=WORK/f'{k:02d}-{digest}.wav'
    query_file=wav.with_suffix('.json')
    if not wav.exists():
        params=urllib.parse.urlencode({'text':unit.narration,'speaker':3})
        query=json.loads(request('/audio_query?'+params,b''))
        query.update(speedScale=unit.speed,intonationScale=1.12,prePhonemeLength=.07,postPhonemeLength=.13,outputSamplingRate=24000)
        query_file.write_text(json.dumps(query,ensure_ascii=False),encoding='utf-8')
        wav.write_bytes(request('/synthesis?speaker=3',json.dumps(query).encode()))
    with wave.open(str(wav),'rb') as reader:
        assert reader.getsampwidth()==2 and reader.getnchannels()==1
        rate=reader.getframerate()
        samples=np.frombuffer(reader.readframes(reader.getnframes()),dtype=np.int16).astype(np.float32)/32768
    return wav,samples,rate

def write_wav(path,samples,rate):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes((np.clip(samples,-1,1)*32767).astype(np.int16).tobytes())

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))

def main():
    if os.environ.get('BAKE_SUPERVISED')!='1':
        raise SystemExit('Run through production/bake.sh so progress is monitored.')
    OUT.mkdir(parents=True,exist_ok=True); WORK.mkdir(exist_ok=True)
    speakers=json.loads(request('/speakers'))
    assert any(s['name']=='ずんだもん' and any(t['id']==3 and t['name']=='ノーマル' for t in s['styles']) for s in speakers)
    version=json.loads(request('/version'))
    segments=[]; voices=[]; cursor=0
    global base_cache
    base_cache=[base(u,i) for i,u in enumerate(UNITS)]
    assert PANEL_LEFT == W-PANEL_RIGHT and RIGHT_UI_RESERVE==0
    assert BOTTOM_UI_PX==360
    assert all(set(f['examples']) >= {'NVDA','AAPL','MSFT'} for f in SOURCES['funds'])
    assert not any('50%' in u.subtitle or '投資先X' in u.subtitle for u in UNITS)
    # Check layout at the start, during motion and at rest before any rendering.
    for i,u in enumerate(UNITS):
        for t in (0,.10,.35,1.1):
            frame(u,i,t,np.zeros(24000,dtype=np.float32),24000)
    for k,unit in enumerate(UNITS):
        print(f'[tts] {k+1}/{len(UNITS)} {unit.subtitle}',flush=True)
        wav,voice,rate=synth(unit,k)
        frames=math.ceil((len(voice)/rate+.10)*FPS)
        duration=frames/FPS
        padded=np.pad(voice,(0,round(duration*rate)-len(voice)))
        voices.append(padded)
        segment=WORK/f'seg_{k:02d}.mp4'
        png=WORK/f'frame_{k:02d}.png'
        sample=frame(unit,k,min(1.1,duration*.5),voice,rate)
        sample.save(png)
        if not segment.exists():
            command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(segment)]
            process=subprocess.Popen(command,stdin=subprocess.PIPE)
            try:
                for n in range(frames):
                    process.stdin.write(frame(unit,k,n/FPS,voice,rate).tobytes())
                    if n%120==0: print(f'[draw] {k+1}/{len(UNITS)} frame {n}/{frames}',flush=True)
                process.stdin.close()
                if process.wait()!=0: raise RuntimeError('ffmpeg failed')
            except Exception:
                process.kill(); process.wait(); segment.unlink(missing_ok=True); raise
        print(f'[draw] {k+1}/{len(UNITS)} complete {duration:.2f}s',flush=True)
        segments.append({'index':k,'scene':unit.scene,'subtitle':unit.subtitle,'narration':unit.narration,'speaker':3,'start':cursor,'duration':duration,'frames':frames})
        cursor+=duration
    narration=np.concatenate(voices)
    write_wav(OUT/'voice.wav',narration,rate)
    listing=WORK/'concat.txt'
    listing.write_text(''.join(f"file 'seg_{k:02d}.mp4'\n" for k in range(len(UNITS))))
    target=OUT/'FZ002-nakami.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(OUT/'voice.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-af','loudnorm=I=-14:TP=-1.5:LRA=7','-movflags','+faststart','-shortest',str(target)],check=True)
    Image.open(WORK/'frame_00.png').save(OUT/'thumbnail.png')
    sheet=Image.new('RGB',(1080,1920),'white')
    for k,idx in enumerate((0,1,4,6,7,9,11,13)):
        thumb=Image.open(WORK/f'frame_{idx:02d}.png').resize((270,480))
        sheet.paste(thumb,((k%4)*270,(k//4)*480))
    # Two rows at native aspect ratio; crop unused sheet space.
    sheet.crop((0,0,1080,960)).save(OUT/'contact-sheet.jpg',quality=92)
    (OUT/'segments.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
    report={'voicevox_version':version,'speaker_name':'ずんだもん','speaker_style':'ノーマル','speaker_id':3,'duration':cursor,'frame_count':sum(s['frames'] for s in segments),'source_sha':os.environ.get('GITHUB_SHA'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'probe':probe(target),'validation':{'main_message':'商品数だけで分散を判断せず、投資先と割合を見る','real_holdings_examples':[c['ticker'] for c in SOURCES['companies']],'bottom_ui_reserved_px':BOTTOM_UI_PX,'right_ui_reserved_px':RIGHT_UI_RESERVE,'text_bounds':'checked for every rendered frame','full_decode':'pending'}}
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(target),'-f','null','-'],check=True)
    report['validation']['full_decode']='passed'
    stream=next(s for s in report['probe']['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'])==(W,H)
    assert 20<cursor<60, f'Duration outside short target: {cursor}'
    assert any(s['codec_type']=='audio' for s in report['probe']['streams'])
    (OUT/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'[draw] COMPLETE {target} {cursor:.2f}s',flush=True)

def preview():
    import base64
    OUT.mkdir(parents=True,exist_ok=True)
    assets={str(FONT.relative_to(ROOT)):base64.b64encode(FONT.read_bytes()).decode()}
    for expr in ('normal','smug','happy'):
        for p in PARTS.glob(expr+'*.png'):
            assets[str(p.relative_to(ROOT))]=base64.b64encode(p.read_bytes()).decode()
    (OUT/'preview-assets.json').write_text(json.dumps(assets))
    global base_cache
    base_cache=[base(u,i) for i,u in enumerate(UNITS)]
    sheet=Image.new('RGB',(1080,1440),'white')
    for k,idx in enumerate((0,2,4,5,6,7,8,9,10,11,12,13)):
        for t in (0,.15,.5,1.2):frame(UNITS[idx],idx,t,np.zeros(24000,dtype=np.float32),24000)
        im=frame(UNITS[idx],idx,1.2,np.zeros(24000,dtype=np.float32),24000)
        im.save(OUT/f'preview-{idx:02d}.png')
        sheet.paste(im.resize((270,480)),((k%4)*270,(k//4)*480))
    sheet.save(OUT/'storyboard-preview.jpg',quality=94)
    print('Static storyboard ready for visual review',flush=True)

if __name__=='__main__':
    preview() if '--preview' in sys.argv else main()
