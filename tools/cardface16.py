# card face: portrait art into the landscape window, crop chosen around the subject's head instead of the middle
import sys,glob,numpy as np
from PIL import Image,ImageEnhance,ImageFilter,ImageChops
from scipy import ndimage as nd
P='/home/claude/r16/';U=P+'tools/r16_in/'
OLD={'C':['h17','h12','h01'],'UC':['h02','h16','h21'],'L':['h15','h13','h14','h19','h04'],'SL':['h03','h22','h07'],'LT':['h28','h18'],'R':['h05','h09','h10','h08'],'ST':['h06','h20','h11']}
RANK={'h29':'SL','h30':'SL','h31':'SL','h27':'SL','h03':'SL','h22':'SL','h07':'SL','h18':'LT','h28':'LT','h15':'L','h13':'L','h14':'L','h19':'L','h04':'L','h26':'L','h34':'L','h05':'R','h09':'R','h10':'R','h08':'R','h02':'UC','h21':'UC','h24':'UC','h25':'UC','h16':'UC','h17':'C','h12':'C','h23':'C','h01':'C','h06':'ST','h20':'ST','h11':'ST'}
TOP={'h28':0.30,'h26':0.17}   # manual offsets (fraction of the scaled height) if the automatic one is wrong
win_cache={}
def window(rank):
    if rank in win_cache:return win_cache[rank]
    fr=Image.open(P+f'cards/frame_{rank}.webp').convert('RGB');f=np.asarray(fr).astype(int);acc=None
    for o in OLD[rank]:
        d=np.asarray(ImageChops.difference(fr,Image.open('/home/claude/pixeldeck/cards/'+o+'.webp').convert('RGB'))).sum(-1)>45;acc=d if acc is None else acc|d
    rows=np.where(acc.mean(1)>.55)[0];y0,y1=rows.min(),rows.max()+1;cols=np.where(acc[y0+20:y1-20].mean(0)>.7)[0];x0,x1=cols.min(),cols.max()+1
    win=np.zeros(acc.shape,bool);win[y0:y1,x0:x1]=True;win&=nd.binary_dilation((f.max(-1)<60),iterations=2)|nd.binary_erosion(win,iterations=6)
    win_cache[rank]=(x0,y0,x1,y1,win);return win_cache[rank]
def head_y(a):
    # the subject = where detail (edges) and saturation are strongest; the head is the top of that mass
    g=np.asarray(a.convert('L').filter(ImageFilter.FIND_EDGES)).astype(float)
    hsv=np.asarray(a.convert('HSV')).astype(float);sat=hsv[...,1]/255
    H,W=g.shape;cx=np.exp(-((np.arange(W)-W/2)/(W*.28))**2)   # centre columns count most
    e=(g*(.6+sat))*cx[None,:];prof=nd.uniform_filter1d(e.sum(1),size=H//20)
    thr=prof.max()*.45;top=np.where(prof>thr)[0].min()
    return top/H
def build(id):
    rank=RANK[id];a=Image.open(U+id+'/art.png').convert('RGB');a=ImageEnhance.Color(a).enhance(1.06);w,h=a.size
    x0,y0,x1,y1,win=window(rank);ww,wh=x1-x0,y1-y0;s=max(ww/w,wh/h);b=a.resize((round(w*s)+1,round(h*s)+1),Image.LANCZOS)
    hy=TOP.get(id,head_y(a))
    by=int(np.clip(hy*b.height-wh*.10,0,b.height-wh))   # head sits ~10% below the window top, never cut
    bx=(b.width-ww)//2;c=b.crop((bx,by,bx+ww,by+wh))
    out=Image.open(P+f'cards/frame_{rank}.webp').convert('RGBA');m=Image.fromarray((win[y0:y1,x0:x1]*255).astype('uint8'));out.paste(c.convert('RGBA'),(x0,y0),m)
    out.save(P+f'cards/{id}.webp',quality=86,method=6)
    # art/ (400x240, used in cut-ins and the VS screen): same head-aware crop
    t=400/240;nh=round(w/t);ay=int(np.clip(hy*h-nh*.10,0,h-nh));a.crop((0,ay,w,ay+nh)).resize((400,240),Image.LANCZOS).save(P+f'art/{id}.webp',quality=88,method=6)
    return hy
ids=sys.argv[1:] or list(RANK)
import os
for i in ids:print(i,'head at %.2f'%build(i))
