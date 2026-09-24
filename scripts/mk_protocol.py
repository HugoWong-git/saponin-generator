import re, csv
REV="/home/user/saponin-generator/review/"

# ---- 1. per-section published coverage, from the gap analysis section-2 table
gap={}
lines=open(REV+"metric_coverage_gap_analysis.md").read().split("\n")
inblk=False
for ln in lines:
    if ln.startswith("| **§**") or ln.startswith("| § |"): inblk=True; continue
    if inblk:
        if not ln.startswith("|"): 
            if gap: inblk=False
            continue
        cells=[c.strip() for c in ln.strip().strip("|").split("|")]
        if set("".join(cells).replace(" ",""))<=set("-:"): continue
        if len(cells)<5: continue
        sid=re.sub(r'\*','',cells[0]).strip()
        gap[sid]=dict(coverage=re.sub(r'\*\*(.*?)\*\*',r'\1',cells[2]).strip(),
                      precedent=re.sub(r'\*\*(.*?)\*\*',r'\1',cells[3]).strip(),
                      verdict=re.sub(r'\*\*(.*?)\*\*',r'\1',cells[4]).strip())

# ---- 2. values measured in THIS session (2026-09-24). Only what was actually run.
MEAS={
 "D1":("training corpus","100.0% — 45,966/45,966 parsed by RDKit 2026.3.6"),
 "D9":("training corpus","157 out-of-vocabulary tokens across 93 molecules (0.20% of corpus)"),
 "D10":("training corpus","isomeric SMILES chars: median 117, p95 300, max 623; 11.83% >250 (Skinnider cap), 71.0% >100 (GuacaMol cap)"),
 "D11":("training corpus","40.58% glycosides (18,654) / 59.42% aglycones (27,312)"),
 "D12":("training corpus","65.71% fully specified / 24.68% partial / 9.61% flat; 87.5% carry any @; mean 2.44 undefined centres (p95 15)"),
 "D14":("training corpus","hexopyranose-like 47.13%, pentopyranose-like 23.19%, deoxyhexose-like 19.31%, uronic-like 7.22%, furanose-like 3.15% (shape heuristic, NOT monosaccharide identification)"),
 "D15":("training corpus","heavy atoms median 42, p95 93, max 185; MW median 586.8, p95 1337.5, max 2662.9; bimodal — aglycone mean MW 515.1, glycoside 987.7"),
 "D16":("training corpus","internal diversity 0.8439; SEDiv@Tc<0.65 0.637; 7,900 unique Murcko scaffolds (17.19%); top scaffold 6.17% (n=3,000 sample)"),
 "1.1":("generated sample","88.58% valid (own reconstruction, epoch 3, n=10,000). Published pipeline reports 86.97%"),
 "2.1":("training corpus","0.637 @ Tc<0.65 — corpus reference only; NOT computed on generated molecules"),
 "2.3":("training corpus","7,900 Murcko scaffolds (17.19% of molecules) — corpus reference only; NOT computed on generated"),
 "3.1":("generated sample","97.54% unique among valid (8,640/8,858). Note the published pipeline forces uniqueness via unique_molecules=true, making its 1.0 trivial"),
 "S1":("both","23.38% of generated carry >=1 sugar, vs 40.58% of training corpus"),
 "S2":("both","0.38 sugars/molecule generated vs 1.27 training; molecules with >=4 sugars 0.23% vs 14.7% — 64-fold collapse"),
 "S7":("both","0.0% — 0 of 8,858 valid generated molecules carry a stereocentre, vs 87.5% of corpus"),
 "S11":("both","corpus median 10 defined stereocentres (p95 33, max 67); generated 0"),
 "S12":("both","generated mean MW 553.9 vs corpus 706.9; sits on the aglycone mode (515.1), not the glycoside mode (987.7)"),
 "T1":("model internals","131 tokens, of which 18 are stereo tokens. Vocabulary inherited from reinvent_pubchem.prior"),
 "T2":("training corpus","157 OOV tokens across 93 of 45,966 molecules"),
 "T6":("both","corpus tokens: median 82, p95 170, max 342. Model context window = 128 → 17.2% of corpus exceeds it"),
 "T7":("training corpus","41.4% of glycosides exceed the 128-token cap vs 0.7% of aglycones — a 59-fold selective filter"),
 "T11":("generated sample","5.46% of sampled sequences hit the 128-token cap without emitting an end token (truncated, therefore invalid)"),
}
MEAS_NOTE={k:"measured 2026-09-24; see reports/corpus_and_prior_audit.md" for k in MEAS}

# ---- 3. parse the protocol
rows=[]
sec=""; sub=""; hdr=None
for ln in open(REV+"evaluation_protocol.md").read().split("\n")+[""]:
    if ln.startswith("## "): sec=ln[3:].strip(); sub=""; hdr=None; continue
    if ln.startswith("### "): sub=ln[4:].strip(); hdr=None; continue
    if not ln.startswith("|"): hdr=None; continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    if set("".join(cells).replace(" ",""))<=set("-:"): continue
    if hdr is None: hdr=cells; continue
    rows.append((sec,sub,tuple(hdr),cells))

def clean(s):
    s=re.sub(r'\*\*(.*?)\*\*',r'\1',s); s=re.sub(r'\*(.*?)\*',r'\1',s)
    return s.strip()

METRIC_HDRS={"#"}
out=[]
for sec,sub,hdr,cells in rows:
    m=re.match(r'^(\d+[A-Z]?)\.\s*(.*)$', sec)
    if not m: continue
    snum, stitle = m.group(1), clean(m.group(2))
    h0=hdr[0]
    if h0=="#":
        rtype="metric"
        mid=clean(cells[0]); name=clean(cells[1]) if len(cells)>1 else ""
        detail=" | ".join(clean(c) for c in cells[2:] if clean(c)) if len(cells)>2 else ""
    elif h0=="Gate":
        rtype="acceptance gate"
        mid=clean(cells[0]); name=clean(cells[1]) if len(cells)>1 else ""
        detail=("If it fails: "+clean(cells[2])) if len(cells)>2 and clean(cells[2]) else ""
    elif h0=="Failure":
        rtype="failure mode"
        mid=""; name=clean(cells[0])
        detail=" | ".join(clean(c) for c in cells[1:] if clean(c))
    elif h0=="Group":
        rtype="property group"
        mid=""; name=clean(cells[0]); detail=clean(cells[1]) if len(cells)>1 else ""
    elif h0=="Split":
        rtype="split"
        mid=""; name=clean(cells[0]); detail=clean(cells[1]) if len(cells)>1 else ""
    else:
        continue
    risk=""
    rm=re.findall(r'\bR\d+\b', " ".join(cells))
    if "Risk" in hdr:
        ri=hdr.index("Risk")
        if ri<len(cells): risk=clean(cells[ri])
    elif rm: risk=", ".join(sorted(set(rm)))
    g=gap.get(snum,{})
    out.append(dict(
        section=snum, section_title=stitle, subsection=clean(sub),
        row_type=rtype, metric_id=mid, metric=name, detail=detail, risk_ref=risk,
        published_coverage=g.get("coverage",""),
        best_published_precedent=g.get("precedent",""),
        gap_verdict=g.get("verdict",""),
        measured_this_project=MEAS.get(mid,("",""))[1],
        measurement_scope=MEAS.get(mid,("",""))[0],
        measurement_note=MEAS_NOTE.get(mid,""),
    ))

cols=["section","section_title","subsection","row_type","metric_id","metric","detail",
      "risk_ref","published_coverage","best_published_precedent","gap_verdict",
      "measurement_scope","measured_this_project","measurement_note"]
dst=REV+"evaluation_protocol.csv"
with open(dst,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in out: w.writerow(r)
print(f"wrote {len(out)} rows -> {dst}")
from collections import Counter
print("\nby row_type:", dict(Counter(r["row_type"] for r in out)))
print("with a measured value:", sum(1 for r in out if r["measured_this_project"]))
print("sections with gap-analysis coverage joined:", len({r['section'] for r in out if r['published_coverage']}))
print("\nper section:")
for s,n in sorted(Counter(r["section"] for r in out).items(), key=lambda x:(len(x[0]),x[0])):
    t=next(r["section_title"] for r in out if r["section"]==s)
    print(f"  §{s:<4s} {t[:44]:44s} {n:3d}")
