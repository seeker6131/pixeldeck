# builds game sprite sheets (6x4 cells of 252x204: idle, walk, attack, front) from 6-column source sheets on magenta
import sys,numpy as np
from PIL import Image
from scipy import ndimage as nd
U='/root/.claude/uploads/388a5c6f-68e0-528b-b3e1-4ec8a2a8c150/'
CW,CH,BASE=252,204,196
def key(im):
    a=np.asarray(im.convert('RGB')).astype(float);r,g,b=a[...,0],a[...,1],a[...,2]
    m=np.minimum(r,b)-g
    al=np.clip((165-m)/50,0,1)          # strong magenta -> transparent
    al[(r<150)|(b<150)]=1               # only bright magenta counts
    solid=al>0.5
    solid=nd.binary_opening(solid,iterations=1)
    lab,n=nd.label(solid);sz=nd.sum(solid,lab,range(1,n+1));keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>=30])
    al=np.where(keep,al,0)
    spill=(m>30)&(al>0)                 # pull magenta fringe toward neutral
    a[...,0]=np.where(spill,g+(r-g)*.45,r);a[...,2]=np.where(spill,g+(b-g)*.45,b)
    return np.dstack([a,al*255]).astype('uint8')
def bands(al,axis,minrun=25):
    p=(al>40).sum(axis);on=p>3;out=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        if not v and s is not None:
            if i-s>=minrun:out.append((s,i))
            s=None
    if s is not None:out.append((s,len(on)))
    return out
def build(src,rows,name,target_h,maxw=236):
    rgba=key(Image.open(U+src));al=rgba[...,3];H,W=al.shape;rb=bands(al,1)
    print(name,'row bands',rb)
    idle_y0,idle_y1=rb[rows[0]];atk_y0,atk_y1=rb[rows[1]];cw=W/6
    def cells(y0,y1):
        y0=max(0,y0-4);y1=min(H,y1+4);return [rgba[y0:y1,int(round(c*cw)):int(round((c+1)*cw))] for c in range(6)]
    def clean(c):
        c=c.copy();m=c[...,3]>40;lab,n=nd.label(m)
        if n<2:return c
        sz=nd.sum(m,lab,range(1,n+1));big=int(np.argmax(sz))+1;w=c.shape[1]
        for i in range(1,n+1):
            if i==big:continue
            xs=np.where(lab==i)[1];cxx=xs.mean()
            if cxx<w*.13 or cxx>w*.87 or (sz[i-1]<sz[big-1]*.02 and (xs.min()<3 or xs.max()>w-4)):c[lab==i]=0
        return c
    idle=[clean(c) for c in cells(idle_y0,idle_y1)];atk=[clean(c) for c in cells(atk_y0,atk_y1)]
    def bbox(c):
        ys,xs=np.where(c[...,3]>40);return xs.min(),xs.max(),ys.min(),ys.max()
    ib=[bbox(c) for c in idle];bh=np.median([b[3]-b[2] for b in ib]);bw=np.median([b[1]-b[0] for b in ib])
    sc=min(target_h/bh,maxw/bw);cx=np.mean([(b[0]+b[1])/2 for b in ib])
    def place(c,base=None):
        x0,x1,y0,y1=bbox(c);foot=y1 if base is None else base
        im=Image.fromarray(c,'RGBA');w=max(1,round(c.shape[1]*sc));h=max(1,round(c.shape[0]*sc));im=im.resize((w,h),Image.LANCZOS)
        cell=Image.new('RGBA',(CW,CH),(0,0,0,0));cell.alpha_composite(im,(0,0)) if False else None
        ox=round(CW/2-cx*sc);oy=round(BASE-foot*sc)
        tmp=Image.new('RGBA',(CW,CH),(0,0,0,0));tmp.paste(im,(ox,oy),im);return tmp.transpose(Image.FLIP_LEFT_RIGHT)   # the game's sheets face LEFT (allies are mirrored in battle)
    ibase=np.median([b[3] for b in ib])
    # attack frames keep the idle row's ground line unless the frame's own feet are close to it
    ab=[bbox(c) for c in atk];off=(atk_y1-atk_y0)-(idle_y1-idle_y0)
    sheet=Image.new('RGBA',(CW*6,CH*4),(0,0,0,0))
    for c in range(6):
        fi=place(idle[c],ib[c][3]);fa=place(atk[c],max(ab[c][3],0))
        for r in (0,1,3):sheet.paste(fi,(c*CW,r*CH))
        sheet.paste(fa,(c*CW,2*CH))
    sheet.save(f'/home/claude/pixeldeck/spr/{name}.webp',quality=90,method=6)
    # portrait for the turn-order strip / VS screen: 400x240
    f0=Image.fromarray(idle[0],'RGBA');x0,x1,y0,y1=ib[0];f0=f0.crop((x0,y0,x1+1,y1+1));k=min(360/f0.width,216/f0.height);f0=f0.resize((round(f0.width*k),round(f0.height*k)),Image.LANCZOS)
    bg=np.zeros((240,400,3),float);yy,xx=np.mgrid[0:240,0:400];d=np.hypot((xx-200)/260,(yy-130)/170);col=np.array(TINT[name]);bg[:]=col*np.clip(1.15-d,0.18,1)[...,None]
    art=Image.fromarray(bg.astype('uint8')).convert('RGBA');art.alpha_composite(f0,((400-f0.width)//2,240-f0.height-8));art.transpose(Image.FLIP_LEFT_RIGHT).convert('RGB').save(f'/home/claude/pixeldeck/art/{name}.webp',quality=86)
    print(name,'scale %.2f body %dx%d'%(sc,bw*sc,bh*sc))
TINT={'m01':(120,40,36),'m02':(128,62,24),'m03':(70,44,60),'b01':(96,24,34)}
build('edae5ddc-image.png',(0,1),'m01',112)   # imp
build('edae5ddc-image.png',(2,3),'m02',112)   # hellhound pup
build('037a62b7-image.png',(0,1),'m03',138)   # dire wolf
build('6a141c2c-image.png',(0,1),'b01',176)   # alpha wolf boss
