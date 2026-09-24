import re, csv, sys
SRC="/home/user/saponin-generator/review/reported_metrics_record.md"
lines=open(SRC).read().split("\n")

def clean(s):
    s=re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s=re.sub(r'\*(.*?)\*', r'\1', s)
    return s.strip()

def direction(h):
    if "↑" in h: return "higher is better"
    if "↓" in h: return "lower is better"
    return ""

def stripdir(h): return clean(h.replace("↑","").replace("↓","")).strip()

out=[]
sec=""; sub=""; conf=""; cite=""; dataset=""; note=""
hdr=None; block=[]

def flush(sec,sub,conf,cite,dataset,hdr,block):
    if not hdr or not block: return
    n=sec.split(".")[0].strip()
    title=clean(re.sub(r'\*\*\[[A-Z-]+\]\*\*','',sec)).strip()
    ctx=clean(sub) if sub else ""
    h0=hdr[0]
    # already-long tables
    if [stripdir(x).lower() for x in hdr][:3]==["model","metric","value"]:
        for r in block:
            out.append(dict(block_num=n, block_title=title, subsection=ctx,
                source_confidence=clean(r[3]) if len(r)>3 else conf, citation=cite,
                dataset=dataset, model=clean(r[0]), metric=clean(r[1]),
                value=clean(r[2]), direction="", notes=""))
        return
    # transposed: first col is the metric, headers are models
    if stripdir(h0).lower() in ("benchmark","metric") and n in ("2","6"):
        for r in block:
            met=clean(r[0])
            for i,mod in enumerate(hdr[1:], start=1):
                if i>=len(r): continue
                v=clean(r[i])
                rep = v not in ("","—","-")
                out.append(dict(block_num=n, block_title=title, subsection=ctx,
                    source_confidence=conf, citation=cite, dataset=dataset,
                    model=stripdir(mod), metric=met, value=v if rep else "not reported",
                    reported="yes" if rep else "no",
                    direction=direction(met), notes=""))
        return
    # DiGress: col0 = "Dataset — model"
    if n=="4":
        for r in block:
            lbl=clean(r[0]); parts=re.split(r'\s*—\s*', lbl, maxsplit=1)
            ds=parts[0]; mod=parts[1] if len(parts)>1 else lbl
            for i,met in enumerate(hdr[1:], start=1):
                if i>=len(r): continue
                v=clean(r[i])
                rep = v not in ("","—","-")
                out.append(dict(block_num=n, block_title=title, subsection=ctx,
                    source_confidence=conf, citation=cite, dataset=ds,
                    model=mod, metric=stripdir(met), value=v if rep else "not reported",
                    reported="yes" if rep else "no",
                    direction=direction(met), notes="two FCD columns in source: GuacaMol-style (higher better) and MOSES-style (lower better)"))
        return
    # wide: col0 = model, headers = metrics
    if stripdir(h0).lower() in ("model","method"):
        for r in block:
            mod=clean(r[0])
            for i,met in enumerate(hdr[1:], start=1):
                if i>=len(r): continue
                v=clean(r[i])
                rep = v not in ("","—","-")
                out.append(dict(block_num=n, block_title=title, subsection=ctx,
                    source_confidence=conf, citation=cite, dataset=dataset,
                    model=mod, metric=stripdir(met), value=v if rep else "not reported",
                    reported="yes" if rep else "no",
                    direction=direction(met), notes=""))
        return
    # not retrieved
    if n=="10":
        for r in block:
            out.append(dict(block_num=n, block_title=title, subsection=ctx,
                source_confidence="NOT RETRIEVED", citation=cite, dataset="",
                model=clean(r[0]), metric="(all)", value="NOT RETRIEVED",
                direction="", notes=clean(r[1]) if len(r)>1 else ""))
        return
    # meta findings
    if n=="9":
        for r in block:
            out.append(dict(block_num=n, block_title=title, subsection=ctx,
                source_confidence=conf, citation=clean(r[1]) if len(r)>1 else cite,
                dataset="", model="(meta-finding)", metric="(narrative)",
                value="", direction="", notes=clean(r[0])))
        return

for ln in lines+[""]:
    if ln.startswith("## ") or ln.startswith("### ") or (not ln.startswith("|") and hdr):
        flush(sec,sub,conf,cite,dataset,hdr,block); hdr=None; block=[]
    if ln.startswith("## "):
        sec=ln[3:].strip(); sub=""; cite=""; dataset=""
        m=re.search(r'\*\*\[([A-Z-]+)\]\*\*', sec); conf=m.group(1) if m else ""
        continue
    if ln.startswith("### "): sub=ln[4:].strip(); continue
    if ln.startswith("Source:"): cite=clean(ln[7:]); continue
    if ln.startswith("Dataset:"): dataset=clean(ln[8:]); continue
    if ln.startswith("|"):
        cells=[x.strip() for x in ln.strip().strip("|").split("|")]
        if set("".join(cells).replace(" ",""))<=set("-:"): continue
        if hdr is None: hdr=cells
        else: block.append(cells)

out=[r for r in out if r["block_num"] not in ("",) and r["block_title"]!="How to read this"]
cols=["block_num","block_title","subsection","model","metric","value","reported","direction",
      "dataset","citation","source_confidence","notes"]
dst="/home/user/saponin-generator/review/published_reported_metrics.csv"
with open(dst,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in out: w.writerow({c:r.get(c,"yes" if c=="reported" else "") for c in cols})
print(f"wrote {len(out)} rows -> {dst}")
from collections import Counter
for k,v in sorted(Counter((r["block_num"],r["block_title"][:38]) for r in out).items(), key=lambda x:int(x[0][0])):
    print(f"  block {k[0]:>2s}  {k[1]:40s} {v:4d} rows")
