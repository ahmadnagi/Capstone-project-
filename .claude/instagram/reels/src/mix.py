# usage: mix.py voice.wav events.json total out.wav
import sys, json, wave, numpy as np
vp, evp, total, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
SR=44100; rng=np.random.default_rng(7)
w=wave.open(vp); vsr=w.getframerate(); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
v=np.interp(np.linspace(0,len(v)-1,int(len(v)*SR/vsr)),np.arange(len(v)),v).astype(np.float32)
N=int(total*SR)+SR; out=np.zeros(N,np.float32); out[:min(N,len(v))]+=v[:N]
env=lambda n,d: np.exp(-np.arange(n)/(d*SR)); db=lambda x: 10**(x/20)
def bn(n,lo,hi):
    X=np.fft.rfft(rng.standard_normal(n)); f=np.fft.rfftfreq(n,1/SR); X[(f<lo)|(f>hi)]=0; y=np.fft.irfft(X,n); return y/np.abs(y).max()
def sweep(n,f0,f1): return np.sin(2*np.pi*np.cumsum(np.linspace(f0,f1,n))/SR)
FX={
 'tick':  lambda: (np.sin(2*np.pi*1900*np.arange(int(.05*SR))/SR)*.7+bn(int(.05*SR),2500,7000)*.3)*env(int(.05*SR),.008)*db(-22),
 'whoosh':lambda: (lambda n:(bn(n,300,5000))*np.sin(np.linspace(0,np.pi,n))**2*db(-25))(int(.42*SR)),
 'pop':   lambda: (lambda n: sweep(n,500,950)*env(n,.03)*db(-20))(int(.12*SR)),
 'thud':  lambda: (lambda n:(sweep(n,110,45)*env(n,.12)+bn(n,80,900)*env(n,.03)*.6)*db(-10))(int(.5*SR)),
 'swish': lambda: (lambda n: bn(n,2000,9000)*np.sin(np.linspace(0,np.pi,n))**3*db(-25))(int(.22*SR)),
 'ding':  lambda: (lambda n,t:(np.sin(2*np.pi*1318.5*t)+.6*np.sin(2*np.pi*1975.5*t)+.3*np.sin(2*np.pi*2637*t))*env(n,.35)*db(-21))(int(1.4*SR),np.arange(int(1.4*SR))/SR),
}
beat=lambda: (lambda n: np.sin(2*np.pi*52*np.arange(n)/SR)*env(n,.06)*db(-11))(int(.18*SR))
def add(x,t):
    i=int(max(0,t)*SR); j=min(N,i+len(x)); out[i:j]+=x[:j-i]
for e in json.load(open(evp)):
    t,k=e['t'],e['type']
    if k=='heart':
        for b in np.arange(t,t+2.1,.72): add(beat(),b); add(beat()*.7,b+.2)
    elif k=='whoosh': add(FX[k](),t-.18)
    else: add(FX[k](),t)
pk=np.abs(out).max(); out=out/pk*.95 if pk>.95 else out
o=wave.open(outp,"wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.clip(np.stack([out,out],1),-1,1)*32767).astype(np.int16).tobytes()); o.close(); print("ok")
