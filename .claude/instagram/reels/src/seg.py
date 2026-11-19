import sys, os
os.environ["U2NET_HOME"] = sys.argv[1]
from rembg import remove, new_session
from PIL import Image
sess = new_session(sys.argv[2])
for p in sys.argv[3:]:
    im = Image.open(p).convert("RGB"); m = remove(im, session=sess, only_mask=True)
    m.save(p.replace(".jpg", f"_mask_{sys.argv[2]}.png")); print(p, im.size)
