import json, re
h = open("reel.html", encoding="utf-8").read()
times = json.load(open("../tts/times_en.json"))
disp = [("You don't need 8–12 reps.", ["8–12"]),
 ("We all learned that's the muscle range.", ["muscle","range."]),
 ("But research says 6 to 30 reps all build muscle.", ["6","30","muscle."]),
 ("On one condition.", ["one"]),
 ("Push the set until you've got 1 or 2 reps left.", ["1","2"]),
 ("Stop at 12 when you could do 20?", ["12","20?"]),
 ("That's not a set. That's a warm-up.", ["warm-up."]),
 ("It's not the number.", ["number."]),
 ("It's the last 2 reps.", ["last","2"]),
 ("So pick the range you like.", ["like."]),
 ("6, 10, 15, 20.", []),
 ("You don't need 8–12 reps.", ["8–12"]),
 ("The last 2 reps need to be tough.", ["tough."])]
beats = [[d, hl, t["start"], t["dur"]] for (d, hl), t in zip(disp, times)]
new = ("const BEATS = " + json.dumps(beats, ensure_ascii=False) + ";\n"
  "const T = BEATS.map(([s,h,st,d]) => ({s, h, start:st, dur:d, n:s.split(/\\s+/).length}));\n"
  "const TOTAL = " + str(round(times[-1]['start'] + times[-1]['dur'] + 0.6, 3)) + ";\nwindow.TOTAL = TOTAL;\n"
  "const NS = i => T[i].start;\n"
  "const OLD = [NS(0), NS(1), NS(2), NS(2)+0.35*T[2].dur, NS(2)+0.72*T[2].dur, NS(3), NS(4), NS(5), NS(6), NS(7), NS(8), NS(9), NS(10), NS(11), NS(12)];\n"
  "const ODUR = {3: 0.37*T[2].dur, 6: T[4].dur, 12: T[10].dur};")
h = re.sub(r"const WPM = 130;.*?window.TOTAL = TOTAL;", lambda m: new, h, flags=re.S)
h = h.replace("const S = i => T[i].start;", "const S = i => OLD[i];")
h = h.replace("T[3].dur", "ODUR[3]").replace("T[6].dur", "ODUR[6]").replace("T[12].dur", "ODUR[12]")
h = h.replace('<html lang="ar" dir="rtl">', '<html lang="en" dir="ltr">')
rep = {"رقم التضخيم<span": "The muscle range<span", "📄 الأبحاث": "📄 Research", "💪 كلهم بيبنوا عضل": "💪 All build muscle",
 "قرّب من الآخر": "Get close to failure", "فاضلك <span class=\"hl\">1–2</span> بس": "<span class=\"hl\">1–2</span> reps left",
 "كان ممكن تكمل لـ20": "You could've done 20", ">تسخين<": ">WARM-UP<", "↑ آخر عدتين": "↑ The last 2 reps",
 "اختار اللي يريحك": "Pick your range", "آخر عدتين = صعبين 🔥": "Last 2 reps = tough 🔥", '<div class="lbl">عدة</div>': '<div class="lbl">reps</div>',
 'color:var(--lime)">؟</span>': 'color:var(--lime)">?</span>'}
for a, b in rep.items():
    assert a in h, a; h = h.replace(a, b)
h = h.replace("font-size:150px;color:var(--red)", "font-size:120px;color:var(--red)")
open("reel_en.html", "w", encoding="utf-8").write(h)
print("arabic left:", re.findall(r"[؀-ۿ]+", h)[:10])
