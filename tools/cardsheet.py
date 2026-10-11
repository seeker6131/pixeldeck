# b160: the five new cards (h23-h27). Sources in tools/cards_in: <id>-...-art.png (5:3 illustration) and <id>-...-sheet.png (6x4 on magenta, facing LEFT like every card sheet).
# Makes spr/<id>.webp (6x4 cells of 252x204: idle, ready, attack, front), art/<id>.webp (400x240) and cards/<id>.webp (the illustration set into the rank frame's window).
import sys,glob,numpy as np
from PIL import Image,ImageEnhance
from scipy import ndimage as nd
sys.argv=sys.argv[:1]+['__none__']+sys.argv[1:]
import importlib.util
P='/home/claude/pixeldeck/';U=P+'tools/cards_in/'
src=open(P+'tools/monsheet2.py').read().split("TINT={")[0]
ns={};exec(src,ns);key,bands,frames=ns['key'],ns['bands'],ns['frames'];CW,CH,BASE=252,204,196
CARDS={'h23':('C',136,()),'h24':('UC',150,()),'h25':('UC',156,()),'h26':('L',164,()),'h27':('SL',160,())}
def sheet(id,th,only):
    f=glob.glob(U+id+'-*-sheet.png')[0];rgba=key(Image.open(f));al=rgba[...,3];rb=bands(al,1);assert len(rb)==4,(id,rb)
    rows=[frames(rgba,*rb[i]) for i in range(4)]
    def tidy(fr):   # drop flat slivers (the feet of the row above caught in a tall attack frame's band)
        c,box=fr;c=c.copy();m=c[...,3]>40;lab,n=nd.label(m)
        for i in range(1,n+1):
            ys,xs=np.where(lab==i)
            if len(ys)<160 and ys.max()-ys.min()<=4 and xs.max()-xs.min()>=6 and ys.max()<box[2]+6:c[lab==i]=0
        return c,box
    rows=[[tidy(f) for f in r] for r in rows]
    idle=rows[0];bh=np.median([b[3]-b[2] for _,b in idle]);bw=np.median([b[1]-b[0] for _,b in idle]);sc=min(th/bh,236/bw)
    out=Image.new('RGBA',(CW*6,CH*4),(0,0,0,0));clip=0
    for r in range(4):
        rbw=np.median([b[1]-b[0] for _,b in rows[r]]);right=CW/2+min(rbw,bw*1.25)*sc/2
        for c in range(6):
            cimg,(x0,x1,y0,y1)=rows[r][c];im=Image.fromarray(cimg,'RGBA');im=im.resize((max(1,round(cimg.shape[1]*sc)),max(1,round(cimg.shape[0]*sc))),Image.LANCZOS)
            if r==2:ox=round(right-(x1+1)*sc)
            else:ox=round(CW/2-(x0+x1+1)/2*sc)
            oy=round(BASE-(y1+1)*sc);clip=max(clip,-ox,ox+im.width-CW,-oy)
            tmp=Image.new('RGBA',(CW,CH),(0,0,0,0));tmp.paste(im,(ox,oy),im);out.paste(tmp,(c*CW,r*CH))
    out.save(P+f'spr/{id}.webp',quality=90,method=6);print(id,'scale %.2f body %dx%d clipped %d'%(sc,bw*sc,bh*sc,max(0,clip)))
def faces(id,rank):
    a=Image.open(glob.glob(U+id+'-*-art.png')[0]).convert('RGB')
    a=ImageEnhance.Color(a).enhance(1.06)
    w,h=a.size;t=400/240
    if w/h>t:nw=round(h*t);a2=a.crop(((w-nw)//2,0,(w-nw)//2+nw,h))
    else:nh=round(w/t);a2=a.crop((0,0,w,nh))
    a2.resize((400,240),Image.LANCZOS).save(P+f'art/{id}.webp',quality=88,method=6)
    fr=Image.open(P+f'cards/frame_{rank}.webp').convert('RGB');f=np.asarray(fr).astype(int)
    # the art window = where the finished cards of this rank differ from the bare frame (their illustrations), limited to the frame's dark panel
    from PIL import ImageChops
    acc=None
    for o in OLD[rank]:
        d=np.asarray(ImageChops.difference(fr,Image.open(P+f'cards/{o}.webp').convert('RGB'))).sum(-1)>45;acc=d if acc is None else acc|d
    rows=np.where(acc.mean(1)>.55)[0];y0,y1=rows.min(),rows.max()+1;cols=np.where(acc[y0+20:y1-20].mean(0)>.7)[0];x0,x1=cols.min(),cols.max()+1
    win=np.zeros(acc.shape,bool);win[y0:y1,x0:x1]=True;win&=nd.binary_dilation((f.max(-1)<60),iterations=2)|nd.binary_erosion(win,iterations=6)
    ww,wh=x1-x0,y1-y0;s=max(ww/w,wh/h);b=a.resize((round(w*s)+1,round(h*s)+1),Image.LANCZOS);bx=(b.width-ww)//2;by=(b.height-wh)//2;b=b.crop((bx,by,bx+ww,by+wh))
    out=Image.open(P+f'cards/frame_{rank}.webp').convert('RGBA');m=Image.fromarray((win[y0:y1,x0:x1]*255).astype('uint8'));out.paste(b.convert('RGBA'),(x0,y0),m)   # keep the frame's own transparent edge
    out.save(P+f'cards/{id}.webp',quality=86,method=6);print(id,'window',x0,y0,x1,y1)
OLD={'C':['h17','h12','h01'],'UC':['h02','h16','h21'],'L':['h15','h13','h14','h19','h04'],'SL':['h03','h22','h07']}
for id,(rank,th,_) in CARDS.items():
    if len(sys.argv)>2 and id not in sys.argv[2:]:continue
    sheet(id,th,None);faces(id,rank)
