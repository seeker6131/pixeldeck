# b151 batch: the source sheets already face LEFT like the game's sheets, so nothing is mirrored here.
# builds game sprite sheets (6x4 cells of 252x204: idle, walk, attack, front) from 6-column source sheets on magenta
import sys,numpy as np
from PIL import Image
from scipy import ndimage as nd
U='/home/claude/pixeldeck/tools/monsters_in/'
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
    near=nd.binary_dilation(al<.5,iterations=2)
    spill=(m>30)&(al>0)&near            # pull magenta fringe toward neutral, only next to the cut edge
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
        tmp=Image.new('RGBA',(CW,CH),(0,0,0,0));tmp.paste(im,(ox,oy),im);return tmp   # the game's sheets face LEFT (allies are mirrored in battle)
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
    art=Image.fromarray(bg.astype('uint8')).convert('RGBA');art.alpha_composite(f0,((400-f0.width)//2,240-f0.height-8));art.convert('RGB').save(f'/home/claude/pixeldeck/art/{name}.webp',quality=86)
    print(name,'scale %.2f body %dx%d'%(sc,bw*sc,bh*sc))
def frames(rgba,y0,y1,cuts=()):
    """split one row into 6 frames by connected parts instead of fixed columns: the 6 biggest parts are the bodies, every smaller part (sparks, fire, drops) joins the nearest body"""
    y0=max(0,y0-6);y1=min(rgba.shape[0],y1+6);band=rgba[y0:y1].copy()
    for x in cuts:band[:,x-1:x+2,3]=0   # hand-placed cut where two frames overlap
    for x in cuts:   # and wipe the neighbour's pale swing arc that pokes over the cut
        z=band[:,x-26:x];pale=(z[...,:3].min(-1)>150);z[pale,3]=0
    for _ in range(4):   # two neighbours that touch come out as one wide part: cut it at its thinnest column and look again
        m=band[...,3]>40;lab,n=nd.label(m,structure=np.ones((3,3)));sz=nd.sum(m,lab,range(1,n+1));top=[int(i)+1 for i in np.argsort(sz)[::-1][:6]]
        ws={i:(np.where(lab==i)[1].min(),np.where(lab==i)[1].max()) for i in top};med=np.median([b-a for a,b in ws.values()][:5]);wide=[i for i in top if ws[i][1]-ws[i][0]>1.6*med]
        if not wide:break
        a,b=ws[wide[0]];lo=int(a+(b-a)*.3);hi=int(a+(b-a)*.7);col=(lab[:,lo:hi]==wide[0]).sum(0);x=lo+int(np.argmin(col));band[:,x-1:x+2,3]=0
    m=band[...,3]>40;lab,n=nd.label(m,structure=np.ones((3,3)))
    sz=nd.sum(m,lab,range(1,n+1));order=np.argsort(sz)[::-1];bodies=sorted([int(i)+1 for i in order[:6]],key=lambda i:np.where(lab==i)[1].mean())
    assert len(bodies)==6,len(bodies)
    bb={i:(np.where(lab==i)[1].min(),np.where(lab==i)[1].max(),np.where(lab==i)[0].min(),np.where(lab==i)[0].max()) for i in bodies}
    own={i:[i] for i in bodies}
    for j in range(1,n+1):
        if j in bodies or sz[j-1]<4:continue
        ys,xs=np.where(lab==j);x0,x1,ya,yb=xs.min(),xs.max(),ys.min(),ys.max()
        def dist(b):
            dx=max(b[0]-x1,x0-b[1],0);dy=max(b[2]-yb,ya-b[3],0);return np.hypot(dx,dy)
        k=min(bodies,key=lambda i:dist(bb[i]))
        if dist(bb[k])<=70:own[k].append(j)
    out=[]
    for i in bodies:
        mask=np.isin(lab,own[i]);c=band.copy();c[~mask]=0;ys,xs=np.where(mask);X0,X1,Y0,Y1=xs.min(),xs.max(),ys.min(),ys.max()
        b=bb[i];out.append((c[Y0:Y1+1,X0:X1+1],(b[0]-X0,b[1]-X0,b[2]-Y0,b[3]-Y0)))   # frame image + its body's box inside it
    return out
def build2(src,name,target_h,maxw=236,cuts=()):
    rgba=key(Image.open(U+src));al=rgba[...,3];rb=bands(al,1);assert len(rb)==2,rb
    idle=frames(rgba,*rb[0]);atk=frames(rgba,*rb[1],cuts)
    bh=np.median([b[3]-b[2] for _,b in idle]);bw=np.median([b[1]-b[0] for _,b in idle]);sc=min(target_h/bh,maxw/bw)
    right=CW/2+bw*sc/2
    def place(fr,by_right):
        c,(x0,x1,y0,y1)=fr;im=Image.fromarray(c,'RGBA');im=im.resize((max(1,round(c.shape[1]*sc)),max(1,round(c.shape[0]*sc))),Image.LANCZOS)
        ox=round(right-(x1+1)*sc) if by_right else round(CW/2-(x0+x1+1)/2*sc);oy=round(BASE-(y1+1)*sc)
        tmp=Image.new('RGBA',(CW,CH),(0,0,0,0));tmp.paste(im,(ox,oy),im);return tmp,ox,im.width
    sheet=Image.new('RGBA',(CW*6,CH*4),(0,0,0,0));clip=0
    for c in range(6):
        fi,_,_=place(idle[c],False);fa,ox,w=place(atk[c],True);clip=max(clip,-ox,ox+w-CW)
        for r in (0,1,3):sheet.paste(fi,(c*CW,r*CH))
        sheet.paste(fa,(c*CW,2*CH))
    sheet.save(f'/home/claude/pixeldeck/spr/{name}.webp',quality=90,method=6)
    f0=Image.fromarray(idle[0][0],'RGBA');k=min(360/f0.width,216/f0.height);f0=f0.resize((round(f0.width*k),round(f0.height*k)),Image.LANCZOS)
    bg=np.zeros((240,400,3),float);yy,xx=np.mgrid[0:240,0:400];d=np.hypot((xx-200)/260,(yy-130)/170);col=np.array(TINT[name]);bg[:]=col*np.clip(1.15-d,0.18,1)[...,None]
    art=Image.fromarray(bg.astype('uint8')).convert('RGBA');art.alpha_composite(f0,((400-f0.width)//2,240-f0.height-8));art.convert('RGB').save(f'/home/claude/pixeldeck/art/{name}.webp',quality=86)
    print(name,'scale %.2f body %dx%d clipped %d px'%(sc,bw*sc,bh*sc,max(0,clip)))
TINT={'m04':(70,36,96),'m05':(44,40,56),'m06':(40,84,36),'m07':(110,70,20),'m08':(110,52,24),'m09':(40,48,96),'m10':(24,56,110),'b02':(70,50,24),'b03':(100,40,30),'b04':(120,50,14),'b05':(70,16,22)}
J=[('07-poison-mushroom.png','m04',124),('03-tar-slime.png','m05',100),('05-cactus-brawler.png','m06',128),('08-mimic-chest.png','m07',116),('10-clockwork-beetle.png','m08',104),('06-storm-jellyfish.png','m09',136),('11-lantern-ghost.png','m10',134),
   ('02-tree-demon-BOSS.png','b02',184),('09-castle-crab-BOSS.png','b03',170),('04-lava-golem-BOSS.png','b04',180),('01-black-dragon-BOSS.png','b05',176)]
import sys
for src,name,h in J:
    if len(sys.argv)>1 and name not in sys.argv[1:]:continue
    build2(src,name,h,maxw=200 if name[0]=='b' else 236,cuts=(524,) if name=='b02' else ())
