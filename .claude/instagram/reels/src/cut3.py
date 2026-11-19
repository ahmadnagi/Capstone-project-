import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
d = sys.argv[1]; K = 1908/1125
# jaw + beard outline (display coords 1125x2000), left cheek -> beard tip -> right cheek
LOW = {
 "normal": [(290,800),(310,870),(345,920),(385,990),(430,1060),(480,1130),(520,1165),(565,1120),(610,1060),(650,1000),(685,930),(710,870),(740,800)],
 "strain": [(300,800),(320,870),(360,930),(395,1000),(440,1080),(490,1150),(520,1170),(560,1140),(610,1080),(650,1010),(690,930),(720,870),(750,800)],
 "happy":  [(290,820),(315,880),(350,940),(390,1010),(440,1100),(495,1180),(530,1215),(570,1170),(620,1090),(670,1010),(720,930),(750,870),(765,820)],
 "smug":   [(290,800),(310,860),(335,920),(365,1000),(410,1090),(470,1160),(530,1190),(580,1150),(630,1080),(680,1000),(715,920),(745,860),(775,800)],
}
for n, low in LOW.items():
    im = Image.open(f"{d}/{n}_up.jpg").convert("RGB"); m = Image.open(f"{d}/{n}_up_mask_u2net_human_seg.png").convert("L")
    W, H = im.size
    poly = [(150,0),(975,0),(975,640),(900,740)] + list(reversed(low[len(low)//2:])) + list(reversed(low[:len(low)//2])) + [(230,740),(150,640)]
    # (reversed halves keep the polygon walking right side down to the tip, then up the left side)
    poly = [(150,0),(975,0),(975,640),(900,740)] + list(reversed(low)) + [(230,740),(150,640)]
    pm = Image.new("L", (W, H), 0); ImageDraw.Draw(pm).polygon([(x*K, y*K) for x, y in poly], fill=255)
    pm = pm.filter(ImageFilter.GaussianBlur(7))
    a = ImageChops.multiply(m, pm)
    cut = im.copy(); cut.putalpha(a)
    bb = a.point(lambda v: 255 if v > 40 else 0).getbbox(); cut = cut.crop(bb)
    s = 520 / cut.height; cut = cut.resize((round(cut.width*s), 520), Image.LANCZOS)
    pad = 24; big = Image.new("RGBA", (cut.width+2*pad, cut.height+2*pad), (0,0,0,0)); big.paste(cut, (pad, pad), cut)
    al = big.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    ring = al.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(1.5))
    sticker = Image.new("RGBA", big.size, (255,255,255,0)); sticker.putalpha(ring)
    shadow = Image.new("RGBA", big.size, (0,0,0,0)); shadow.putalpha(ring.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v*.45)))
    out = Image.new("RGBA", big.size, (0,0,0,0)); out.alpha_composite(shadow, (3, 5)); out.alpha_composite(sticker); out.alpha_composite(big)
    out.save(f"{d}/face3_{n}.png"); print(n, out.size)
