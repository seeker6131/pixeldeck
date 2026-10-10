# b151: turns a 16:9 painted battle background into the game's 1280x512 map. The ground line goes 46% from the top (the back row stands just below it);
# the full width is kept, the ground keeps its proportions and the scenery above the ground line is squeezed a little (x0.8) so more of it fits.
from PIL import Image
D='/home/claude/pixeldeck/tools/maps_in/';J=[('01-desert-ruins.png',7,585),('02-haunted-graveyard.png',8,548),('06-shipwreck-beach.png',9,552),('09-ice-tundra.png',10,550),('10-sakura-shrine.png',11,565)]
HZ,SQ=236,.8
for f,n,hz in J:
    im=Image.open(D+f).convert('RGB');W,H=im.size;sx=1280/W;g=min(H-hz,round((512-HZ)/sx));top=max(0,round(hz-HZ/(sx*SQ)))
    out=Image.new('RGB',(1280,512));out.paste(im.crop((0,top,W,hz)).resize((1280,HZ),Image.LANCZOS),(0,0));out.paste(im.crop((0,hz,W,hz+g)).resize((1280,512-HZ),Image.LANCZOS),(0,HZ))
    out.save(f'/home/claude/pixeldeck/bg/m{n}.webp',quality=84,method=6);print(n,f,'sky rows',top,'-',hz)
