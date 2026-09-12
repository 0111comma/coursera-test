import json, urllib.request, urllib.parse, pathlib, wave, hashlib, subprocess
root=pathlib.Path(__file__).parent
out=root/'audio'; out.mkdir(exist_ok=True)
lines=json.loads((root/'script.json').read_text())
manifest=[]
for line in lines:
 if line['speaker']=='T': continue
 i=line['id']; speaker=3 if line['speaker']=='Z' else 2
 params=urllib.parse.urlencode({'text':line['text'],'speaker':speaker})
 req=urllib.request.Request('http://127.0.0.1:50021/audio_query?'+params,data=b'',method='POST')
 q=json.load(urllib.request.urlopen(req,timeout=120))
 q.update(speedScale=line['speed'],prePhonemeLength=0.035,postPhonemeLength=0.075,volumeScale=1.0,outputSamplingRate=24000)
 (out/f'{i:02d}.query.json').write_text(json.dumps(q,ensure_ascii=False))
 req=urllib.request.Request('http://127.0.0.1:50021/synthesis?speaker='+str(speaker),data=json.dumps(q).encode(),headers={'Content-Type':'application/json'},method='POST')
 data=urllib.request.urlopen(req,timeout=180).read()
 wav=out/f'{i:02d}.wav'; wav.write_bytes(data)
 with wave.open(str(wav)) as w: seconds=w.getnframes()/w.getframerate()
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),str(out/f'{i:02d}.flac')],check=True)
 wav.unlink()
 manifest.append(dict(line,seconds=seconds,speaker_id=speaker,sha256=hashlib.sha256(data).hexdigest()))
 print(f"[voicevox] {i:02d} {seconds:.3f}s {line['text']}",flush=True)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Voice duration',sum(x['seconds'] for x in manifest))
