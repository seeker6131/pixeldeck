# b152: cuts the 13-icon sheet (rows of 4, 4, 5 on magenta) into 128x128 skill icons; the last one (hourglass) is not used
import numpy as np,sys
from PIL import Image
from scipy import ndimage as nd
sys.argv=sys.argv[:1];exec(open('/home/claude/pixeldeck/tools/monsheet2.py').read().split("def frames(")[0])   # reuse key() and bands()
rgba=key(Image.open('/home/claude/pixeldeck/tools/icons_in/skill-icons-sheet-12plus1.png'));al=rgba[...,3]
rows=bands(al,1,minrun=60);print('rows',rows)
names=[['bolt','holy','wind','earth'],['poison','bow','spear','bite'],['punch','blast','meteor','taunt',None]]
for (y0,y1),nm in zip(rows,names):
    band=rgba[y0:y1];col=(band[...,3]>40).sum(0);segs=bands(band[...,3],0,minrun=40)
    while len(segs)<len(nm):   # touching neighbours: split the widest piece at its thinnest column
        i=max(range(len(segs)),key=lambda k:segs[k][1]-segs[k][0]);a,b=segs[i];lo=int(a+(b-a)*.3);hi=int(a+(b-a)*.7);x=lo+int(np.argmin(col[lo:hi]));segs[i:i+1]=[(a,x),(x+1,b)]
    print(segs)
    for (x0,x1),n in zip(segs,nm):
        if not n:continue
        c=band[:,x0:x1].copy();m=c[...,3]>40;lab,k=nd.label(m,structure=np.ones((3,3)));sz=nd.sum(m,lab,range(1,k+1));big=int(np.argmax(sz))+1
        for j in range(1,k+1):   # stray bits of the neighbour hugging the cut edge
            xs=np.where(lab==j)[1]
            if j!=big and sz[j-1]<sz[big-1]*.03 and (xs.min()<4 or xs.max()>c.shape[1]-5):c[lab==j]=0
        ys,xs=np.where(c[...,3]>40);c=c[ys.min():ys.max()+1,xs.min():xs.max()+1];im=Image.fromarray(c,'RGBA');s=118/max(im.size);im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS)
        out=Image.new('RGBA',(128,128),(0,0,0,0));out.paste(im,((128-im.width)//2,(128-im.height)//2),im);out.save(f'/home/claude/pixeldeck/ic/{n}.webp',quality=92,method=6)
