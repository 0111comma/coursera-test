"""Exact checkout arithmetic with speech-aligned reveals."""
from PIL import Image,ImageDraw
from functools import lru_cache
import math

@lru_cache(None)
def duck(path,width):
    p=Image.open(path).convert('RGBA')
    box=p.getchannel('A').getbbox()
    if box:p=p.crop(box)
    return p.resize((width,round(p.height*width/p.width)),Image.Resampling.LANCZOS)

def draw_graphics(r,idx,u):
    s=r.S[idx];sid=s['scene_id'];im=Image.new('RGBA',(r.W,r.H));d=ImageDraw.Draw(im)
    T=lambda xy,t,n=44,c=r.INK,w=940:r.text(d,xy,t,n,c,maxw=w)
    card=lambda b:r.card(d,b)
    show=u>=r.REVEALS.get(sid,0)
    def side(title,main,foot='',color=r.GREEN):
        x=57 if s['camera']=='zclose' else 661
        card((x,555,x+361,946));T((x+180,609),title,35,w=335)
        if show:T((x+180,726),main,49,color,w=335)
        if foot and show:T((x+180,844),foot,29,w=335)
    def top(lines,color=r.GREEN):
        card((62,368,1018,650))
        for i,t in enumerate(lines):T((540,422+i*83),t,45 if i==1 else 38,color if i==1 else r.INK)
    def totals(revealed=True,delta=False):
        card((57,365,1023,700))
        T((540,409),'同じ4,000円の商品を買うなら',37)
        T((291,474),'送料を払う',36,r.GREEN,w=445)
        T((791,474),'不要な物を追加',36,r.RED,w=445)
        T((291,535),'4,000 ＋ 500',37,w=443)
        T((791,535),'4,000 ＋ 1,000',36,w=443)
        T((291,609),'4,500円',56,r.GREEN,w=443)
        if revealed:T((791,609),'5,000円',56,r.RED,w=443)
        T((540,674),'送料は0円でも、支払総額は増える',29)
        if delta and show:
            q=r.ease(u-r.REVEALS.get(sid,0),.3)
            x=round(110*(1-q));card((85+x,724,995+x,812))
            T((540+x,767),'余計な支出 ＋500円',43,r.RED)
    if sid=='hook':
        side('ネットで買い物','送料 500円','送料が気になる…',r.RED)
    elif sid=='cart':
        card((67,366,1013,675));T((540,419),'購入予定の商品',40)
        T((540,490),'商品4,000円 ＋ 送料500円',43)
        if show:
            q=r.ease(u-r.REVEALS[sid],.32)
            d.rounded_rectangle((138,543,138+max(2,804*q),636),18,fill=r.GREEN)
            if q>.8:T((540,588),'支払い 4,500円',59,r.WHITE)
    elif sid=='threshold':
        top(['この店の条件','5,000円以上で送料無料']+(['あと1,000円を買い足す'] if show else []))
        T((540,691),'架空の買い物例・価格は税込',25)
    elif sid=='extra':
        card((54,441,429,976));T((241,493),'追加する置物',36,w=350)
        pic=duck(str(r.asset('duck.png')),230);im.alpha_composite(pic,(125,540))
        T((241,851),'1,000円',57,r.RED,w=348);T((241,923),'送料は0円に！',31,r.GREEN,w=348)
    elif sid=='reveal':totals(show)
    elif sid=='panic':side('送料は消えたけど','支出は増加','支払い5,000円',r.RED)
    elif sid=='difference':totals(True,True)
    elif sid=='question':
        side('その置物…','本当に必要？','送料無料のため？',r.ROSE)
    elif sid=='ending':
        card((54,495,429,966));T((241,546),'買ったもの',36,w=350)
        pic=duck(str(r.asset('duck.png')),218);im.alpha_composite(pic,(131,589))
        T((241,889),'使い道、なし…',33,r.RED,w=350)
    elif sid=='advice':
        card((58,365,1022,685));T((540,411),'買い足す前に',40)
        T((540,494),'もともと買う予定の物？',43,r.GREEN)
        if u>=r.PAGE_STARTS[idx][1]:
            T((540,571),'不要な物なら、送料を払う方が安い',36,r.RED)
            T((540,643),'値引き額より、必要性と支払総額',30)
    elif sid=='cta':
        top(['お金の失敗を減らそう','チャンネル登録','家計・税金・投資を寸劇で'],r.RED)
    return im
