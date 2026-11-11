import sys, wave, json, numpy as np, sherpa_onnx
D, LEX_EN, VOC, prompt, ptext, outdir = sys.argv[1:7]
lines = json.loads(sys.argv[7])
cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(tokens=f"{D}/tokens.txt", encoder=f"{D}/encoder.int8.onnx",
        decoder=f"{D}/decoder.int8.onnx", vocoder=VOC, lexicon=f"{D}/lexicon.txt,{LEX_EN}"), num_threads=4))
tts = sherpa_onnx.OfflineTts(cfg)
w = wave.open(prompt); ps = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
meta = []
for i, l in enumerate(lines):
    g = sherpa_onnx.GenerationConfig(); g.speed = 1.0; g.num_steps = int(__import__("os").environ.get("STEPS", "8"))
    g.reference_audio = ps.tolist(); g.reference_sample_rate = w.getframerate(); g.reference_text = ptext
    g.extra = {"min_char_in_sentence": 10} if False else g.extra
    a = tts.generate(l, g)
    x = np.array(a.samples, np.float32)
    o = wave.open(f"{outdir}/line{i:02d}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(a.sample_rate)
    o.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); o.close()
    meta.append({"i": i, "text": l, "dur": len(x)/a.sample_rate}); print(i, round(len(x)/a.sample_rate,2), l, flush=True)
json.dump(meta, open(f"{outdir}/lines.json","w"), indent=1)
