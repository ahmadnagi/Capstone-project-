# usage: assemble.py plan.json out.wav times.json   (plan: {"sources":{name:path}, "lines":[[text,[[src,s,e],...],join,gap],...], "cuts":[[src,t],...]})
import sys, wave, json, numpy as np
plan=json.load(open(sys.argv[1])); SR=48000
def load(p):
    w=wave.open(p); assert w.getframerate()==SR; return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
SRC={k:load(v) for k,v in plan["sources"].items()}; cuts={(a,b) for a,b in plan.get("cuts",[])}
PRE,POST=0.08,0.18
def piece(src,s,e):
    a=SRC[src]; pre=0 if (src,s) in cuts else PRE; post=0 if (src,e) in cuts else POST
    y=a[int(max(0,s-pre)*SR):int(min(len(a)/SR,e+post)*SR)].copy(); fi,fo=int(.012*SR),int(.06*SR)
    y[:fi]*=np.linspace(0,1,fi); y[-fo:]*=np.linspace(1,0,fo); return y,pre,post
out=[np.zeros(int(.25*SR),np.float32)]; t=.25; times=[]
for text,pcs,join,gap in plan["lines"]:
    start=None
    for k,(src,s,e) in enumerate(pcs):
        y,pre,post=piece(src,s,e)
        # match loudness of each source to -22.5 dB speech level
        if start is None: start=t+pre
        out.append(y); t+=len(y)/SR
        if k<len(pcs)-1: out.append(np.zeros(int(join*SR),np.float32)); t+=join
    times.append({"text":text,"start":round(start,3),"dur":round(t-start-post,3)})
    out.append(np.zeros(int(gap*SR),np.float32)); t+=gap
out.append(np.zeros(int(.9*SR),np.float32)); y=np.concatenate(out); y=y/np.abs(y).max()*.9
o=wave.open(sys.argv[2],"wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes((y*32767).astype(np.int16).tobytes()); o.close()
json.dump(times,open(sys.argv[3],"w"),indent=1); print("total %.2f"%(len(y)/SR))
