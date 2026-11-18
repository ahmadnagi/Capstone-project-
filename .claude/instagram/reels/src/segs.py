import sys, wave, re, subprocess, json, numpy as np, sherpa_onnx
wavp, M = sys.argv[1], sys.argv[2]
log = subprocess.run(["ffmpeg","-i",wavp,"-af","silencedetect=n=-38dB:d=0.35","-f","null","-"],capture_output=True,text=True).stderr
ss=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",log)]; se=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",log)]
w=wave.open(wavp); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; dur=len(a)/16000
# speech = gaps between silences
bounds=[]; prev=0.0
for s,e in zip(ss,se+[dur]*(len(ss)-len(se))):
    if s-prev>0.15: bounds.append((prev,s))
    prev=e
if dur-prev>0.15: bounds.append((prev,dur))
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/turbo-encoder.int8.onnx",decoder=f"{M}/turbo-decoder.int8.onnx",tokens=f"{M}/turbo-tokens.txt",language="en",task="transcribe",num_threads=4)
out=[]
for s0,s1 in bounds:
    st=rec.create_stream(); st.accept_waveform(16000,a[int(max(0,s0-0.1)*16000):int((s1+0.1)*16000)]); rec.decode_stream(st)
    out.append({"start":round(s0,2),"end":round(s1,2),"text":st.result.text.strip()}); print(f"{s0:6.2f}-{s1:6.2f}  {st.result.text.strip()}")
json.dump(out,open(sys.argv[3],"w"),indent=1)
