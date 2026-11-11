import sys, wave, json, re, difflib, numpy as np, sherpa_onnx
D, LEX_EN, VOC, prompt, ptext, outdir, M = sys.argv[1:8]
lines = json.loads(sys.argv[8])
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(tokens=f"{D}/tokens.txt", encoder=f"{D}/encoder.int8.onnx",
        decoder=f"{D}/decoder.int8.onnx", vocoder=VOC, lexicon=f"{D}/lexicon.txt,{LEX_EN}"), num_threads=4)))
asr = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/turbo-encoder.int8.onnx", decoder=f"{M}/turbo-decoder.int8.onnx",
        tokens=f"{M}/turbo-tokens.txt", language="en", task="transcribe", num_threads=4)
w = wave.open(prompt); ps = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
NUM = {"8":"eight","12":"twelve","6":"six","30":"thirty","10":"ten","15":"fifteen","20":"twenty","2":"two","1":"one"}
norm = lambda s: re.sub(r"[^a-z' ]", " ", " ".join(NUM.get(t, t) for t in re.findall(r"[\w']+", s.lower()))).split()
def resample16(x, sr):
    n = int(len(x) * 16000 / sr); return np.interp(np.linspace(0, len(x)-1, n), np.arange(len(x)), x).astype(np.float32)
meta = []
for i, l in enumerate(lines):
    best = None
    for k, (sp, st) in enumerate([(1.0, 8), (0.9, 16), (0.95, 12), (0.85, 16), (1.0, 16), (0.9, 8)]):
        g = sherpa_onnx.GenerationConfig(); g.speed = sp; g.num_steps = st
        g.reference_audio = ps.tolist(); g.reference_sample_rate = w.getframerate(); g.reference_text = ptext
        a = tts.generate(l, g); x = np.array(a.samples, np.float32)
        s = asr.create_stream(); s.accept_waveform(16000, resample16(x, a.sample_rate)); asr.decode_stream(s)
        heard = s.result.text.strip(); score = difflib.SequenceMatcher(None, norm(l), norm(heard)).ratio()
        if best is None or score > best[0]: best = (score, x, a.sample_rate, heard, sp, st)
        if score >= 0.999: break
    score, x, sr, heard, sp, st = best
    o = wave.open(f"{outdir}/line{i:02d}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); o.close()
    meta.append({"i": i, "text": l, "heard": heard, "score": round(score, 3), "dur": len(x)/sr, "sr": sr})
    print(f"{i:2d} {score:.2f} tries={k+1} {len(x)/sr:.2f}s | {heard}", flush=True)
json.dump(meta, open(f"{outdir}/lines.json", "w"), indent=1)
