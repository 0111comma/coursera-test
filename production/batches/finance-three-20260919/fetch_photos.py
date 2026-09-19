from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlsplit
import json,re
R=Path(__file__).resolve().parent/'photos';R.mkdir(exist_ok=True)
class Photos(HTMLParser):
 def __init__(self):super().__init__();self.urls=[];self.meta=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta' and a.get('property')=='og:image':self.meta.append(a.get('content',''))
  if tag=='img':
   for key in ('data-src','src','data-original'):
    if a.get(key):self.urls.append(a[key])
pages={'manhole':'https://www.furusato-tax.jp/product/detail/29425/4715332','porsche':'https://www.furusato-tax.jp/product/detail/12206/5952042','sword':'https://www.furusato-tax.jp/product/detail/26212/6143463'}
report={}
for name,url in pages.items():
 try:
  html=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read().decode('utf-8')
  (R/(name+'.html')).write_text(html)
  p=Photos();p.feed(html)
  # Limit collection to this page's product-image family, starting with its declared hero.
  candidates=list(dict.fromkeys(p.meta+p.urls))
  og=p.meta[0] if p.meta else ''
  family=og.split('?')[0].rsplit('/',1)[0] if og else ''
  assets=[u for u in candidates if u==og or (family and u.startswith(family) and re.search(r'\.(jpg|jpeg|png|webp)(\?|$)',u,re.I))]
  if len(assets)<2:assets=list(dict.fromkeys(p.meta+[u for u in p.urls if 'img.furusato-tax.jp' in u and ('product' in u or 'x_' in u)]))
  report[name]={'page':url,'og':og,'candidates':candidates,'saved':[]}
  for i,u in enumerate(assets[:10]):
   try:
    u=urljoin(url,u);data=urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0','Referer':url}),timeout=30).read()
    dest=R/f'{name}-{i:02}.jpg';dest.write_bytes(data)
    report[name]['saved'].append({'file':dest.name,'url':u,'bytes':len(data)})
   except Exception as e:report[name].setdefault('errors',[]).append(str(e))
  print(name,len(report[name]['saved']),'photos',flush=True)
 except Exception as e:report[name]={'error':str(e),'page':url};print(name,type(e).__name__,str(e),flush=True)
(R/'sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
