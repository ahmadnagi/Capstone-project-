import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
d = sys.argv[1]
# beard tip (x, y) in the 1125x2000 display frame of each photo
TIPS = {"happy": (535, 1215), "smug": (560, 1185), "strain": (520, 1175), "normal": (590, 1160)}
K = 1908/1125
for n, (tx, ty) in TIPS.items():
    im = Image.open(f"{d}/{n}_up.jpg").convert("RGB"); m = Image.open(f"{d}/{n}_up_mask_u2net_human_seg.png").convert("L")
    W, H = im.size
    poly = [(150,0),(975,0),(975,640),(900,760),(830,920),(tx+150,ty-170),(tx+40,ty+40),(tx-60,ty+40),(tx-170,ty-170),(300,920),(230,760),(150,640)]
    pm = Image.new("L", (W, H), 0); ImageDraw.Draw(pm).polygon([(x*K, y*K) for x, y in poly], fill=255)
    pm = pm.filter(ImageFilter.GaussianBlur(14))
    a = ImageChops.multiply(m, pm)
    cut = im.copy(); cut.putalpha(a)
    bb = a.point(lambda v: 255 if v > 40 else 0).getbbox(); cut = cut.crop(bb)
    # scale to 520px tall, then add white sticker outline
    s = 520 / cut.height; cut = cut.resize((round(cut.width*s), 520), Image.LANCZOS)
    pad = 24; big = Image.new("RGBA", (cut.width+2*pad, cut.height+2*pad), (0,0,0,0)); big.paste(cut, (pad, pad), cut)
    al = big.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    ring = al.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(1.5))
    sticker = Image.new("RGBA", big.size, (255,255,255,0)); sticker.putalpha(ring)
    shadow = Image.new("RGBA", big.size, (0,0,0,0)); shadow.putalpha(ring.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v*.45)))
    out = Image.new("RGBA", big.size, (0,0,0,0)); out.alpha_composite(shadow, (3, 5)); out.alpha_composite(sticker); out.alpha_composite(big)
    out.save(f"{d}/face_{n}.png"); print(n, out.size)
