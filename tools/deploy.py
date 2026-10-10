s=open('bit8-clash.html',encoding='utf8').read()
head='<!doctype html>\n<html lang="th">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">\n<meta name="theme-color" content="#0c1030">\n<title>Pixeldeck Battle</title>\n<link rel="manifest" href="manifest.json">\n<link rel="icon" href="icon-192.png">\n<link rel="apple-touch-icon" href="icon-192.png">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n</head>\n<body>\n'
cfg=open('FB_CFG.json').read().strip()
assert "const FB_CFG=null;" in s
w=s.replace("const FB_CFG=null;","const FB_CFG=%s;"%cfg)
open('/home/claude/pixeldeck/index.html','w',encoding='utf8').write(head+w+'\n</body>\n</html>\n')

import re,json
b=re.search(r"const BUILD='(b\d+)'",s).group(1)
open('/home/claude/pixeldeck/version.json','w').write(json.dumps({'b':b}))
print('version',b)

# owner's admin page: same Firebase config, plus card and amulet names pulled from the game source
cards={m.group(1):[m.group(2),m.group(3)] for m in re.finditer(r"\b(h\d\d):\{n:\"([^\"]+)\"[^}]*?\br:'([A-Z]+)'",s)}
i=s.index("const AM={");j=s.index("};",i)
ams={m.group(1):[m.group(2),m.group(3)] for m in re.finditer(r"(\w+):\{n:'([^']+)',r:'([A-Z]+)'",s[i:j])}
assert len(cards)>=20 and len(ams)>=6,(len(cards),len(ams))
a=open('admin.src.html',encoding='utf8').read()
a=a.replace('__FB_CFG__',cfg).replace('__CARDS__',json.dumps(cards,ensure_ascii=False)).replace('__AMS__',json.dumps(ams,ensure_ascii=False)).replace('__BUILD__',b)
open('/home/claude/pixeldeck/admin.html','w',encoding='utf8').write(a)
print('admin',len(cards),'cards',len(ams),'amulets')
