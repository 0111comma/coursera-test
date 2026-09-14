from PIL import Image,ImageDraw
import math,bisect

def draw_graphics(r,idx,u):
    s=r.S[idx];sid=s['scene_id'];theme=r.C['theme'];im=Image.new('RGBA',(r.W,r.H));d=ImageDraw.Draw(im)
    page=max(0,bisect.bisect_right(r.PAGE_STARTS[idx],u)-1)
    def t(x,y,txt,n=54,c=r.INK,role='caption',maxw=940):r.text(d,(x,y),txt,n,c,role,maxw=maxw)
    def box(b,fill=r.WHITE):r.card(d,b,fill)
    def arrow(x,y,length=90,color=r.INK):
        d.line((x,y,x,y+length),fill=color,width=12)
        d.polygon([(x-19,y+length-22),(x+19,y+length-22),(x,y+length+8)],fill=color)
    def amount(y,value,color=r.INK,label='',size=105):
        if label:t(540,y-86,label,45,color)
        t(540,y,value,size,color)
    def panel(top=435,bottom=875):box((66,top,1014,bottom),(255,252,245,249))
    def popnumber(y,v,target,unit='円',label='',color=r.INK,secs=.3,delay=None):
        delay=r.REVEALS.get(sid,0) if delay is None else delay
        p=r.ease(u-delay,secs);value=round(v+(target-v)*p)
        amount(y,f'{value:,}{unit}',color,label,size=95)
    def pill(label):
        box((200,39,880,107),r.INK);t(540,73,label,39,r.WHITE)
    def small_note(a,b=None):
        box((114,341,966,403 if b else 395),(255,252,245,242))
        t(540,361 if b else 368,a,28 if b else 31,r.INK)
        if b:t(540,387,b,26,r.INK)
    if s['camera']=='zclose':
        navy='#082e44';gold='#ffe075';cyan='#71e1dd'
        pill('外貨預金・両替シミュレーション' if theme=='fx' else 'NISA・日本株の配当')
        small_note('仮の例：年利5％で1年間','税金・為替手数料を除く') if theme=='fx' else small_note('国内上場株式の配当・仮の例')
        def ct(y,txt,n=54,col=None):t(291,y,txt,n,col or (gold if theme=='fx' else r.INK),maxw=450)
        d.rounded_rectangle((47,476,537,991),12,fill=navy if theme=='fx' else '#fffff9')
        if theme=='fx':
            if sid=='hook':
                ct(547,'外貨預金',46,cyan);ct(683,'年利5％',84)
                if page>=1:ct(863,'100万円',73)
            elif sid=='happy':
                ct(548,'1年後の残高',40,cyan);ct(700,'7,000ドル',68);ct(891,'ドルは増えた',43,cyan)
            else:
                ct(545,'円に戻した金額',36,cyan);ct(690,'945,000円',65);ct(842,'5.5万円減',66);ct(933,'元の100万円から',32,cyan)
        else:
            d.line((82,581,502,581),fill='#b5b8b2',width=2)
            if sid=='hook':
                ct(538,'配当金のお知らせ',35);ct(696,'20万円',92,r.GREEN)
                if page>=1:ct(885,'旅行の準備！',51,r.GREEN)
            elif sid=='ending':
                ct(539,'配当の受取設定',37);ct(677,'株式数比例',66,r.GREEN);ct(760,'配分方式',66,r.GREEN);ct(913,'証券口座で受取',38)
            else:
                ct(539,'配当20万円の明細',34);ct(644,'源泉徴収',40,r.RED);ct(731,'40,630円',76,r.RED);ct(904,'入金159,370円',44)
        return im
    # Each topic has its own diagram language. FX is a currency board;
    # dividends use a paper statement and the actual payment-setting choice.
    if theme=='fx':
        navy='#082e44';cyan='#71e1dd';gold='#ffe075';light='#effbfb'
        d.rounded_rectangle((72,420,1008,875),16,fill=navy)
        d.rectangle((72,420,1008,430),fill=cyan)
        def row(y,label,value,color=light,size=70):
            d.text((117,y-17),label,font=r.font(37),fill=cyan)
            t(590,y+42,value,size,color,maxw=815)
        def line(y):d.line((112,y,966,y),fill='#3b6977',width=2)
        pill('外貨預金・両替シミュレーション')
        small_note('仮の例：年利5％で1年間','税金・為替手数料を除く')
        delay=r.REVEALS.get(sid,0)
        if sid=='hook':
            t(540,475,'金利を見て大喜び',41,cyan)
            t(540,610,'年利5％',111,gold)
            if page>=1:line(700);t(540,790,'100万円をドル預金へ',58,light)
        elif sid=='setup':
            row(477,'日本円','1,000,000円',gold,75);line(590)
            t(540,634,'1ドル150円で交換',49,light)
            row(724,'米ドル','約6,666.67ドル',light,65)
        elif sid in ['interest','happy']:
            t(540,479,'1年後・ドルに利息がつく',42,cyan)
            value=round(6667+333*r.ease(u-delay,.38))
            if sid=='happy':value=7000
            t(540,619,f'{value:,}ドル' if sid=='happy' or page>=1 else '年利5％',103,gold)
            line(713);t(540,798,'ドルでは増えている',55,light)
        elif sid=='rate':
            t(540,480,'1ドルを円に戻すと…',47,cyan)
            t(540,597,'150円',83,light)
            arrow(540,643,52,gold)
            t(540,782,'135円',103,gold)
            if page>=1:t(857,683,'円高',38,cyan,maxw=190)
        elif sid in ['reveal','panic','ending']:
            t(540,486,'7,000ドル × 135円',56,cyan)
            ready=sid!='reveal' or page>=1
            amount_jpy=round(1000000-55000*r.ease(u-delay,.35)) if sid=='reveal' else 945000
            t(540,643,f'{amount_jpy:,}円' if ready else '円ではいくら？',95 if ready else 71,gold)
            line(723)
            if ready:t(540,802,'元の100万円から 5.5万円減',44,light)
        elif sid=='explain':
            t(540,480,'利息と為替は別',53,light)
            d.rounded_rectangle((113,543,967,665),8,fill='#165763');t(540,604,'ドル残高 5％増',64,cyan)
            if page>=1:
                d.rounded_rectangle((113,712,967,835),8,fill='#704635');t(540,771,'1ドルの円価値 10％減',52,gold)
        elif sid=='advice':
            t(540,503,'金利だけで決めない',64,gold)
            t(540,651,'金利 ＋ 為替の変動',66,light)
            if page>=1:line(725);t(540,802,'円では元本割れする可能性も',43,cyan)
        else:
            t(540,493,'今日の学び',44,cyan);t(540,627,'外貨預金には',70,light);t(540,772,'為替リスクがある',68,gold)
        return im
    if theme=='nisa':
        pill('NISA・日本株の配当')
        small_note('国内上場株式の配当・仮の例')
        paper=(255,255,249,253);red='#ae2e29';gray='#696b68'
        # Paper-shaped statement, intentionally distinct from FX's currency board.
        d.polygon([(113,421),(967,421),(967,825),(938,850),(909,825),(880,850),(851,825),(822,850),(793,825),(764,850),(735,825),(706,850),(677,825),(648,850),(619,825),(590,850),(561,825),(532,850),(503,825),(474,850),(445,825),(416,850),(387,825),(358,850),(329,825),(300,850),(271,825),(242,850),(213,825),(184,850),(155,825),(126,850),(113,839)],fill=paper)
        def rule(y):d.line((151,y,929,y),fill='#b5b8b2',width=2)
        if sid=='hook':
            t(540,483,'配当金のお知らせ',48);rule(526)
            t(540,640,'200,000円',103,r.GREEN)
            if page>=1:t(540,769,'旅行の準備は万全！',56,r.GREEN)
        elif sid in ['reveal','panic','question','admit']:
            t(540,479,'配当金の明細',49);rule(521)
            t(540,572,'配当金　200,000円',51)
            if sid!='reveal' or page>=1:
                d.rectangle((143,614,937,692),fill='#ffe3dc');t(540,653,'源泉徴収　40,630円',51,red)
                value=round(200000-40630*r.ease(u-r.REVEALS.get(sid,0),.32)) if sid=='reveal' else 159370
                t(540,762,f'入金 {value:,}円',66)
            else:t(540,710,'実際の入金は…',63,gray)
        elif sid=='rule':
            t(540,480,'配当金の受取方法',46);rule(524)
            t(540,625,'銀行口座へ直接',62)
            if page>=2:
                d.rectangle((218,708,862,797),outline=red,width=7);t(540,753,'NISAでも課税',65,red)
            else:t(540,757,'受取設定に注意',56,red)
        elif sid in ['setting','ending']:
            t(540,480,'配当金の受取設定',47);rule(523)
            if sid=='ending' or page>=1:
                d.rounded_rectangle((139,560,941,690),8,fill='#e2efd8',outline=r.GREEN,width=3)
                t(540,625,'株式数比例配分方式',62,r.GREEN)
                if sid=='ending' or page>=2:t(540,766,'証券口座で受け取る',54)
            else:t(540,656,'非課税にするには？',63)
        elif sid=='advice':
            t(540,489,'設定の確認',49);rule(534)
            t(540,616,'配当の権利が決まる前に',51,red)
            t(540,705,'証券会社で確認',65,r.GREEN)
            if page>=1:t(540,793,'手続きの日数は証券会社ごと',37,gray)
        else:
            t(540,488,'今日の学び',44,r.GREEN);rule(536)
            t(540,631,'NISAの日本株は',64);t(540,755,'配当の受取方法も確認',51,red)
        return im
