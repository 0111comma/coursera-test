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
LAYOUT = []

@dataclass
class Unit:
    scene: str
    subtitle: str
    note: str
    expr: str = 'normal'
    speaker: int = 3
    speed: float = 1.12
    @property
    def narration(self):
        return self.subtitle.replace('X', 'エックス').replace('Y', 'ワイ')

UNITS = [
    Unit('cover', '投資信託を3本買えば、分散になる？', '本数だけで大丈夫？'),
    Unit('inspect', 'ボクは、まず中身を見るのだ。', 'まず中身を確認', 'smug'),
    Unit('definition', '投資信託は、お金をまとめて運用する商品。', 'お金をまとめて運用'),
    Unit('inspect', '名前が違っても、投資先は重なることがある。', '名前が違っても…'),
    Unit('example', 'たとえば、この3つ。', '架空の例で比べる'),
    Unit('inside', 'どれも、投資先Xが半分、Yが半分だとする。', 'どれも同じ割合'),
    Unit('equal', 'これを、同じ金額ずつ買う。', '購入額も同じ'),
    Unit('merge', '全部合わせたら、割合はどうなる？', 'まとめてみると？', 'smug'),
    Unit('result', 'Xが半分。Yも半分。', 'やっぱり半分ずつ'),
    Unit('result', '商品は3つでも、中身の割合は同じなのだ。', '割合は変わらない', 'smug'),
    Unit('report', '3本がダメ、という話ではないのだ。', '本数だけで決めない'),
    Unit('report', '買う前に、運用の報告書で投資先と割合を見る。', '投資先と割合を確認', 'smug'),
    Unit('bags', '袋を3つに分けても、', '袋は3つだけど…'),
    Unit('bags', '中身まで別物にはならないのだ。', '中身は同じなのだ', 'happy'),
]

# Deliberate Japanese phrase breaks. Whitespace never changes narration words.
SUBTITLE_LINES = [
    '投資信託を3本買えば、\n分散になる？',
    'ボクは、まず\n中身を見るのだ。',
    '投資信託は、お金を\nまとめて運用する商品。',
    '名前が違っても、\n投資先は重なることがある。',
    'たとえば、この3つ。',
    'どれも、投資先Xが半分、\nYが半分だとする。',
    'これを、同じ金額ずつ買う。',
    '全部合わせたら、\n割合はどうなる？',
    'Xが半分。Yも半分。',
    '商品は3つでも、\n中身の割合は同じなのだ。',
    '3本がダメ、\nという話ではないのだ。',
    '買う前に、運用の報告書で\n投資先と割合を見る。',
    '袋を3つに分けても、',
    '中身まで別物には\nならないのだ。',
]
THOUGHT_LINES = [
    '本数だけで\n大丈夫？', 'まず中身を\n確認', 'お金を\nまとめて運用',
    '名前が\n違っても…', '架空の例で\n比べる', 'どれも\n同じ割合',
    '購入額も同じ', 'まとめて\nみると？', 'やっぱり\n半分ずつ',
    '割合は\n変わらない', '本数だけで\n決めない', '投資先と\n割合を確認',
    '袋は3つ\nだけど…', '中身は\n同じなのだ',
]
assert all(s.replace('\n','') == u.subtitle for s,u in zip(SUBTITLE_LINES,UNITS))

@lru_cache(None)
def font(size):
    return ImageFont.truetype(str(FONT), size)

def text(d, xy, value, size=50, fill=INK, anchor='mm', width=None):
    ft = font(size)
    box = d.textbbox(xy, value, font=ft, anchor=anchor)
    if width is not None and box[2] - box[0] > width:
        raise ValueError(f'Text too wide ({box[2]-box[0]} > {width}): {value}')
    if box[0] < 0 or box[1] < 0 or box[2] > W or box[3] > H:
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
    if scene in ('cover','inspect'): return '3本買えば\n分散になる？'
    if scene == 'definition': return '投資信託って\nどんな商品？'
    if scene in ('example','inside','equal'): return '違う商品でも\n中身が同じなら？'
    if scene in ('merge','result'): return '全部合わせると\nどうなる？'
    if scene == 'report': return '買う前に\n投資先を確認'
    return '袋を分けても\n中身は同じ'

def base(unit, number):
    im = Image.new('RGB', (W,H), BG); d=ImageDraw.Draw(im)
    roundbox(d,(66,70,918,139),INK,radius=22)
    text(d,(492,105),'やけに金融リテラシーの高いずんだもん',31,'white',width=808)
    lines(d,(492,236),heading(unit.scene),74,104,width=880)
    roundbox(d,(64,416,924,1004),'#E9E7DD',radius=40)
    roundbox(d,(64,406,924,994),'white',radius=40)
    text(d,(492,451),'商品名より、投資先を見る',32,GREEN,width=800)
    # Character and thought bubble occupy a separate stage below the diagram.
    roundbox(d,(552,1130,923,1348),'#E9EFDF',radius=30)
    bubble=THOUGHT_LINES[number].split('\n')
    lines(d,(737,1192), '\n'.join(bubble),43,65,width=325)
    # Fixed narration zone: clear of mobile UI and diagram.
    roundbox(d,(64,1458,924,1724),INK,radius=30)
    subtitles=SUBTITLE_LINES[number].split('\n')
    if len(subtitles)>3: raise ValueError('Subtitle exceeds three lines')
    y=1592-(len(subtitles)-1)*42
    lines(d,(492,y),'\n'.join(subtitles),58,84,'white',width=800)
    text(d,(492,1770),'VOICEVOX:ずんだもん',27,INK,width=800)
    text(d,(492,1810),'立ち絵：坂本アヒル',25,INK,width=800)
    d.rounded_rectangle((65,1860,923,1870),5,fill='#DEE4D4')
    d.rounded_rectangle((65,1860,65+858*(number+1)/len(UNITS),1870),5,fill=GREEN)
    if unit.scene in ('example','inside','equal','merge','result','bags'):
        text(d,(492,960),'架空の単純化例・実在商品ではありません',27,INK,width=800)
    return im

def token(d, box, label, color):
    roundbox(d,box,color,radius=14)
    text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),label,40,'white',width=box[2]-box[0]-6)

def diagram(im, scene, time):
    d=ImageDraw.Draw(im)
    if scene == 'definition':
        for x in (185,492,799):
            d.ellipse((x-42,525,x+42,609),fill='#E8EDD7',outline=GREEN,width=3)
            text(d,(x,567),'¥',44,GREEN)
            d.line((x,615,492,680),fill=GREEN,width=5)
        roundbox(d,(285,681,699,772),INK,radius=20)
        text(d,(492,727),'まとめて運用',50,'white')
        for x,lab in [(270,'投資先'),(710,'投資先')]:
            d.line((492,772,x,817),fill=GREEN,width=5)
            roundbox(d,(x-140,817,x+140,905),'#EAF0E0',radius=20)
            text(d,(x,861),lab,40)
    elif scene in ('cover','inspect','example','inside','equal'):
        show = scene not in ('cover','example')
        for i,x in enumerate((116,378,640)):
            offset=int(50*(1-ease((time-i*.11)/.55)))
            y=536+offset
            roundbox(d,(x,y,x+228,y+300),'#F7F7F2',outline='#B9C4AE',radius=22)
            text(d,(x+114,y+47),'商品'+str(i+1),43)
            if show:
                token(d,(x+18,y+98,x+210,y+174),'X 50%',BLUE)
                token(d,(x+18,y+183,x+210,y+259),'Y 50%',GOLD)
            else:
                text(d,(x+114,y+193),'？',94,GREEN)
        if scene == 'equal':
            text(d,(492,895),'同じ金額ずつ買う',45,GREEN)
        elif scene=='inside':
            text(d,(492,895),'投資先 X：半分 ／ Y：半分',36,INK)
        elif scene=='inspect':
            text(d,(492,895),'名前が違っても、重なることがある',31,INK)
        else:
            text(d,(492,895),'本数だけでは、まだ分からない',35,INK)
    elif scene in ('merge','result'):
        p=ease(time/1.0) if scene=='merge' else 1
        for i,x in enumerate((116,378,640)):
            for j,(lab,color) in enumerate((('X',BLUE),('Y',GOLD))):
                sx=x; sy=565+j*120
                ex=180+j*350; ey=542+i*104
                xx=sx+(ex-sx)*p; yy=sy+(ey-sy)*p
                token(d,(xx,yy,xx+228,yy+87),lab,color)
        if p>.92:
            text(d,(294,899),'X 50%',52,BLUE)
            text(d,(644,899),'Y 50%',52,GOLD)
    elif scene=='report':
        roundbox(d,(179,514,805,917),'#F8F9F5',outline='#B9C4AE',radius=15)
        text(d,(492,565),'運用の報告書',48)
        text(d,(492,617),'（月次レポートなど）',29)
        d.line((224,655,759,655),fill='#CED6C5',width=3)
        for y,a,b in ((710,'投資先','どこに投資？'),(806,'割合','どれくらい？')):
            roundbox(d,(216,y-38,766,y+41),'#E9EFDF',radius=15)
            text(d,(321,y),a,43,GREEN)
            text(d,(598,y),b,38,INK)
    elif scene=='bags':
        for i,x in enumerate((116,378,640)):
            dy=int(5*math.sin(time*2+i))
            y=596+dy
            d.arc((x+54,y-89,x+172,y+55),180,360,fill=GREEN,width=9)
            roundbox(d,(x,y,x+228,y+266),'#EEF2E6',outline=GREEN,radius=18,width=5)
            token(d,(x+20,y+40,x+208,y+119),'X',BLUE)
            token(d,(x+20,y+137,x+208,y+216),'Y',GOLD)
        text(d,(492,904),'見るのは「袋」より「中身」',39,GREEN)

@lru_cache(None)
def sprite(expr,mouth,eyes):
    p=PARTS/f'{expr}_{mouth}_{eyes}.png'
    if not p.exists(): p=PARTS/f'{expr}_{mouth}_open.png'
    if not p.exists(): p=PARTS/'normal_0_open.png'
    return Image.open(p).convert('RGBA').resize((380,435),Image.Resampling.LANCZOS)

def frame(unit,number,time,voice,rate):
    im=base_cache[number].copy()
    diagram(im,unit.scene,time)
    a=int(max(0,time-.02)*rate); b=min(len(voice),a+int(rate*.10))
    rms=float(np.sqrt(np.mean(voice[a:b]**2))) if b>a else 0
    mouth=2 if rms>.055 else 1 if rms>.012 else 0
    eyes='closed' if 1.70 < time%3.6 < 1.84 else 'open'
    dy=round(4*math.sin(time*2))
    im.paste(sprite(unit.expr,mouth,eyes),(105,1014+dy),sprite(unit.expr,mouth,eyes))
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
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(OUT/'voice.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-af','loudnorm=I=-14:TP=-1.5:LRA=7','-movflags','+faststart','-shortest',str(target)],check=True)
    Image.open(WORK/'frame_00.png').save(OUT/'thumbnail.png')
    sheet=Image.new('RGB',(1080,1920),'white')
    for k,idx in enumerate((0,1,4,6,7,9,11,13)):
        thumb=Image.open(WORK/f'frame_{idx:02d}.png').resize((270,480))
        sheet.paste(thumb,((k%4)*270,(k//4)*480))
    # Two rows at native aspect ratio; crop unused sheet space.
    sheet.crop((0,0,1080,960)).save(OUT/'contact-sheet.jpg',quality=92)
    (OUT/'segments.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
    report={'voicevox_version':version,'speaker_name':'ずんだもん','speaker_style':'ノーマル','speaker_id':3,'duration':cursor,'frame_count':sum(s['frames'] for s in segments),'source_sha':os.environ.get('GITHUB_SHA'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'probe':probe(target),'validation':{'xy_allocations':'50% / 50%','text_bounds':'checked for every rendered frame','full_decode':'pending'}}
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(target),'-f','null','-'],check=True)
    report['validation']['full_decode']='passed'
    stream=next(s for s in report['probe']['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'])==(W,H)
    assert 20<cursor<60, f'Duration outside short target: {cursor}'
    assert any(s['codec_type']=='audio' for s in report['probe']['streams'])
    (OUT/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'[draw] COMPLETE {target} {cursor:.2f}s',flush=True)

if __name__=='__main__': main()
