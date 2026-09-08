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
    Unit('cover', 'オルカンに、S&P500とQQQも追加。', '買い足せば分散？'),
    Unit('cover', 'これで分散？ボクは中身を見るのだ。', '中身を開けるのだ', 'smug'),
    Unit('ac', 'オルカンは、全世界株の投資信託。', '世界の株に投資'),
    Unit('sp', 'S&P500連動の商品は、米国の大型株へ。', '米国の大型株に投資'),
    Unit('qqq', 'QQQは、米ナスダック市場の大きな非金融企業へ。', '金融企業は除く'),
    Unit('names', 'でも、エヌビディア、アップル、マイクロソフト。', 'あれ、同じ顔ぶれ？'),
    Unit('common', 'この3社は、どれにも入っているのだ。', 'また会ったのだ', 'smug'),
    Unit('routes', '別の商品から、同じ会社の株を買い足している。', '別の商品から同じ企業へ', 'smug'),
    Unit('different', 'もちろん、3つの中身が全部同じではない。', '全部同じではない'),
    Unit('different', '違う会社も入るし、1社ごとの割合も違う。', '配分もそれぞれ違う'),
    Unit('broaden', 'だから、投資先をもっと広げたいのか、', '広げたいのか？'),
    Unit('tilt', 'すでに持つ米国大型株を、もっと厚く持ちたいのか。', '厚く持ちたいのか？'),
    Unit('decide', '買う前に、投資先と割合を見て決める。', '目的と中身を照合', 'smug'),
    Unit('close', '袋の数より、中身の配分なのだ。', '何を増やすか決める', 'happy'),
]
SUBTITLE_LINES = [
    'オルカンに、S&P500と\nQQQも追加。',
    'これで分散？\nボクは中身を見るのだ。',
    'オルカンは、\n全世界株の投資信託。',
    'S&P500連動の商品は、\n米国の大型株へ。',
    'QQQは、米ナスダック市場の\n大きな非金融企業へ。',
    'でも、エヌビディア、アップル、\nマイクロソフト。',
    'この3社は、\nどれにも入っているのだ。',
    '別の商品から、\n同じ会社の株を買い足している。',
    'もちろん、3つの中身が\n全部同じではない。',
    '違う会社も入るし、\n1社ごとの割合も違う。',
    'だから、投資先を\nもっと広げたいのか、',
    'すでに持つ米国大型株を、\nもっと厚く持ちたいのか。',
    '買う前に、\n投資先と割合を見て決める。',
    '袋の数より、\n中身の配分なのだ。',
]
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

def heading(scene):
    if scene=='cover': return 'オルカンに追加で\n分散は増える？'
    if scene in ('ac','sp','qqq'): return '名前が違うと\n投資先も違う？'
    if scene in ('names','common'): return '3つに共通する\n米国の企業'
    if scene=='routes': return '別の商品から\n同じ会社を買う'
    if scene=='different': return '全部同じ、\nではないのだ'
    return '広げたい？\n厚く持ちたい？'

def base(unit, number):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    # Full-width bands, symmetric interior padding; no reserved right rail.
    d.rectangle((0,48,W,120),fill=INK)
    text(d,(W/2,84),'やけに金融リテラシーの高いずんだもん',35,'white',width=W-64)
    lines(d,(W/2,206),heading(unit.scene),70,88,width=W-64)
    roundbox(d,(PANEL_LEFT,355,PANEL_RIGHT,1014),'white',radius=32)
    roundbox(d,(433,1117,PANEL_RIGHT,1304),'#E9EFDF',radius=26)
    text(d,(735,1210),unit.note,39,INK,width=558)
    d.rectangle((0,1360,W,1507),fill=INK)
    subtitles=SUBTITLE_LINES[number].split('\n')
    lines(d,(W/2,1433-(len(subtitles)-1)*33),'\n'.join(subtitles),52,66,'white',width=W-72)
    text(d,(W/2,1536),'VOICEVOX:ずんだもん ｜ 立ち絵：坂本アヒル',23,INK,width=W-64)
    return im

def source_note(d):
    text(d,(540,990),'資料：オルカン26/7・S&P500連動26/8・QQQ26/9/4',24,INK,width=976)

def product_cards(d,scene,t):
    labels=['オルカン','S&P500連動','QQQ']
    scopes=['世界の株','米国の大型株','米ナスダックの\n大型・非金融']
    ids=['ac','sp','qqq']
    for i,x in enumerate((52,390,728)):
        y=485-int(24*(1-ease((t-i*.08)/.45)))
        selected=scene==ids[i]
        fill='#E9EFDF' if selected else '#F7F7F2'
        roundbox(d,(x,y,x+300,y+354),fill,outline=GREEN if selected else '#B9C4AE',radius=22)
        text(d,(x+150,y+59),labels[i],44,INK,width=272)
        d.line((x+24,y+108,x+276,y+108),fill='#CBD3C2',width=3)
        lines(d,(x+150,y+188),scopes[i],37,63,INK,width=272)
    if scene=='ac':
        text(d,(540,901),'eMAXIS Slim 全世界株式（オール・カントリー）',29,INK,width=976)
    elif scene=='sp':
        text(d,(540,901),'例：MAXIS米国株式（S&P500）上場投信',30,INK,width=976)
    elif scene=='qqq':
        text(d,(540,901),'Invesco QQQ：Nasdaq-100に連動するETF',30,INK,width=976)
    elif scene=='different':
        text(d,(540,901),'投資対象も、各企業の組入比率も異なる',36,GREEN,width=976)
    else:
        text(d,(540,901),'3つの商品。中身はどう重なる？',40,GREEN,width=976)
    source_note(d)

def tick(d,x,y,active):
    d.ellipse((x-27,y-27,x+27,y+27),fill=GREEN if active else '#E3E8DD')
    if active:d.line((x-13,y,x-3,y+12,x+15,y-13),fill='white',width=7)

def diagram(im,scene,t):
    d=ImageDraw.Draw(im)
    if scene in ('cover','ac','sp','qqq','different'):
        text(d,(540,405),'実際の投資対象で比べる',34,GREEN,width=976)
        product_cards(d,scene,t)
    elif scene in ('names','common'):
        text(d,(540,405),'共通する保有企業の例',36,GREEN,width=976)
        for x,label in zip((505,718,930),('オルカン','S&P500連動','QQQ')):
            text(d,(x,492),label,31,INK,width=204)
        d.line((60,537,1020,537),fill='#CDD5C4',width=3)
        for i,company in enumerate(SOURCES['companies']):
            y=604+i*132
            roundbox(d,(52,y-49,1028,y+49),'#F0F3E8',radius=15)
            text(d,(224,y),company['name'],36,INK,width=330)
            for j,x in enumerate((505,718,930)):
                present=company['ticker'] in SOURCES['funds'][j]['examples']
                tick(d,x,y,present and (scene=='common' or t>i*.20+j*.07))
        text(d,(540,939),'各資料で保有を確認。全銘柄の一致ではありません',29,INK,width=976)
        source_note(d)
    elif scene=='routes':
        for x,label in zip((202,540,878),('オルカン','S&P500連動','QQQ')):
            roundbox(d,(x-150,442,x+150,544),'#E9EFDF',radius=20)
            text(d,(x,493),label,39,INK,width=276)
            d.line((x,550,540,720),fill='#92A783',width=6)
        roundbox(d,(332,588,748,645),'white',radius=12)
        text(d,(540,615),'投資額の一部が',39,INK,width=396)
        roundbox(d,(160,724,920,865),INK,radius=24)
        text(d,(540,796),'エヌビディア',76,'white',width=712)
        text(d,(540,928),'同じ企業への投資を重ねることになる',34,GREEN,width=976)
        source_note(d)
    else:
        if scene=='close':
            text(d,(540,462),'買う前に確かめるのは',38,GREEN,width=976)
            lines(d,(540,638),'投資先と\nその割合',104,145,INK,width=976)
            text(d,(540,929),'商品数を増やすこと自体が、目的ではない',33,GREEN,width=976)
        else:
            for i,(x,title,detail) in enumerate([
                (52,'投資先を\n広げたい','今の保有資産と\n違う投資先か確認'),
                (558,'米国大型株を\n厚く持ちたい','同じ企業を増やす\n意図があるか確認')]):
                bright=(scene=='broaden' and i==0) or (scene=='tilt' and i==1) or scene=='decide'
                roundbox(d,(x,464,x+470,910),'#E9EFDF' if bright else '#F7F7F2',outline=GREEN if bright else '#CBD3C2',radius=24)
                lines(d,(x+235,567),title,48,79,INK,width=426)
                lines(d,(x+235,760),detail,35,60,INK,width=426)
            text(d,(540,965),'重ね買いが悪いのではなく、目的と配分を合わせる',30,GREEN,width=976)

@lru_cache(None)
def sprite(expr,mouth,eyes):
    p=PARTS/f'{expr}_{mouth}_{eyes}.png'
    if not p.exists(): p=PARTS/f'{expr}_{mouth}_open.png'
    if not p.exists(): p=PARTS/'normal_0_open.png'
    return Image.open(p).convert('RGBA').resize((288,329),Image.Resampling.LANCZOS)

def frame(unit,number,time,voice,rate):
    im=base_cache[number].copy()
    diagram(im,unit.scene,time)
    a=int(max(0,time-.02)*rate); b=min(len(voice),a+int(rate*.10))
    rms=float(np.sqrt(np.mean(voice[a:b]**2))) if b>a else 0
    mouth=2 if rms>.055 else 1 if rms>.012 else 0
    eyes='closed' if 1.70 < time%3.6 < 1.84 else 'open'
    dy=round(4*math.sin(time*2))
    im.paste(sprite(unit.expr,mouth,eyes),(80,1020+dy),sprite(unit.expr,mouth,eyes))
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
    report={'voicevox_version':version,'speaker_name':'ずんだもん','speaker_style':'ノーマル','speaker_id':3,'duration':cursor,'frame_count':sum(s['frames'] for s in segments),'source_sha':os.environ.get('GITHUB_SHA'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'probe':probe(target),'validation':{'real_holdings_examples':[c['ticker'] for c in SOURCES['companies']],'bottom_ui_reserved_px':BOTTOM_UI_PX,'right_ui_reserved_px':RIGHT_UI_RESERVE,'text_bounds':'checked for every rendered frame','full_decode':'pending'}}
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(target),'-f','null','-'],check=True)
    report['validation']['full_decode']='passed'
    stream=next(s for s in report['probe']['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'])==(W,H)
    assert 20<cursor<60, f'Duration outside short target: {cursor}'
    assert any(s['codec_type']=='audio' for s in report['probe']['streams'])
    (OUT/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'[draw] COMPLETE {target} {cursor:.2f}s',flush=True)

if __name__=='__main__': main()
