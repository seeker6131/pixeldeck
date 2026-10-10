# b153: turns the 6-frame effect sheets (one row on magenta) into small 6-cell strips in fx/. Glow and smoke that the artist blended into the magenta
# are un-mixed from it, so they come out as real transparency instead of a pink fringe.
import numpy as np
from PIL import Image
D='/home/claude/pixeldeck/tools/fx_in/';OUT='/home/claude/pixeldeck/fx/'
def key(im):
    a=np.asarray(im.convert('RGB')).astype(float);bg=np.median(np.concatenate([a[:12].reshape(-1,3),a[-12:].reshape(-1,3)]),0);r,g,b=a[...,0],a[...,1],a[...,2]
    m=np.minimum(r,b)-g;mb=min(bg[0],bg[2])-bg[1];al=np.clip((mb-22-m)/(mb-22-70),0,1)
    k=np.clip(al,.08,1)[...,None];f=np.clip((a-(1-al[...,None])*bg)/k,0,255)   # colour with the magenta taken back out
    al[al<.06]=0;return np.dstack([f,al*255]).astype('uint8')
J=[('p01-arrow','arrow','p',26),('p02-fire-arrow','farrow','p',52),('p03-fireball','fball','p',56),('p04-ice-shard','shard','p',52),('p05-light-orb','orb','p',56),
   ('h06-sword-slash','slash','h',150),('h07-claw-marks','claw','h',150),('h08-ground-smash','smash','h',150),('h09-fire-explosion','boom','h',150),('h10-ice-burst','ice','h',150),('h11-lightning','bolt','h',190),('h12-hit-impact','hit','h',130),
   ('s13-blood-drain','drain','h',140),('s15-shield','shield','h',150)]
for src,name,kind,size in J:
    rgba=key(Image.open(D+src+'.png'));H,W=rgba.shape[:2]
    if name in('smash','bolt'):   # their dust / halo was painted pinkish over the magenta: pull what is left of it to a neutral tan
        f=rgba[...,:3].astype(float);g=f[...,1];mm=np.minimum(f[...,0],f[...,2])-g;z=mm>12;f[...,0]=np.where(z,g+(f[...,0]-g)*.55,f[...,0]);f[...,2]=np.where(z,g+(f[...,2]-g)*.25,f[...,2]);rgba[...,:3]=f.astype('uint8')
    # the artist did not space the six frames evenly, so find them by the gaps between them: runs of used columns, the closest runs merged until six are left
    on=(rgba[...,3]>60).sum(0)>1;runs=[];st=None
    for x,v in enumerate(list(on)+[False]):
        if v and st is None:st=x
        if not v and st is not None:runs.append([st,x]);st=None
    while len(runs)>6:
        i=min(range(len(runs)-1),key=lambda k:runs[k+1][0]-runs[k][1]);runs[i:i+2]=[[runs[i][0],runs[i+1][1]]]
    assert len(runs)==6,(name,len(runs))
    ws=sorted(b-a for a,b in runs)
    if ws[-1]>1.5*ws[2] or ws[-1]>W/6*1.15:   # frames touch each other here, so gaps cannot separate them: use the six equal cells and one shared box
        cw=W/6;xs=np.concatenate([np.where(on[int(round(i*cw)):int(round((i+1)*cw))])[0] for i in range(6)]);runs=[[int(round(i*cw))+xs.min(),int(round(i*cw))+xs.max()+1] for i in range(6)]
    ys=np.where((rgba[...,3]>60).sum(1)>3)[0];y0,y1=ys.min(),ys.max()+1;bh=y1-y0;bw=max(b-a for a,b in runs)
    s=size/(bh if kind=='p' else max(bw,bh));w,h=max(1,round(bw*s)),max(1,round(bh*s));strip=Image.new('RGBA',(w*6,h),(0,0,0,0))
    for i,(a,b) in enumerate(runs):   # every frame centred on its own box, so the effect does not wander between frames
        im=Image.fromarray(rgba[y0:y1,a:b],'RGBA');im=im.resize((max(1,round((b-a)*s)),h),Image.LANCZOS);strip.paste(im,(i*w+(w-im.width)//2,0))
    strip.save(OUT+name+'.webp',quality=88,method=6);print(name,w,'x',h)
