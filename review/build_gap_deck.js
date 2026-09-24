const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';              // 13.333 x 7.5
pres.author = 'Saponin Stage 1 prior — evaluation coverage';
pres.title  = 'Where the Field Stops';

const W = 13.333, H = 7.5, M = 0.62;      // margins

// ---- palette (validated: node scripts/validate_palette.js "2C7A3E,C98A1E,B5482F") ----
const DARK='16211A', PAPER='FFFFFF', INK='1A1F1B', INK2='39413A', MUTED='6B7268',
      LINE='DCE0DA', TRACK='EDEFEA',
      GREEN='2C7A3E', AMBER='C98A1E', RED='B5482F',
      GREEN_S='E4EFE7', AMBER_S='F7EDD8', RED_S='F4E0DB',
      ONDARK='E8EDE6', ONDARK_M='9AA79A';
const SERIF='Cambria', SANS='Calibri';

const tb = o => Object.assign({isTextBox:true, margin:0}, o);

/* ============ helpers ============ */
function slideBase(title, kicker, sub, opts){
  opts = opts || {};
  const s = pres.addSlide();
  s.background = {color: PAPER};
  s.addText(kicker.toUpperCase(), tb({x:M, y:0.42, w:W-2*M, h:0.24,
    fontFace:SANS, fontSize:11, bold:true, color:GREEN, charSpacing:2}));
  s.addText(title, tb({x:M, y:0.72, w:W-2*M, h:0.52, valign:'top',
    fontFace:SERIF, fontSize:opts.titleSize || 31, bold:true, color:INK}));
  if(sub) s.addText(sub, tb({x:M, y:1.32, w:W-2*M-0.4, h:0.34, valign:'top',
    fontFace:SANS, fontSize:13, color:MUTED}));
  return s;
}
function footer(s, txt){
  s.addText(txt, tb({x:M, y:H-0.40, w:W-2*M, h:0.26, valign:'top',
    fontFace:SANS, fontSize:9.5, color:MUTED}));
}
function takeaway(s, rich, y){
  s.addShape(pres.ShapeType.rect, {x:M, y:y, w:W-2*M, h:0.01, fill:{color:LINE}});
  s.addText(rich, tb({x:M, y:y+0.15, w:W-2*M, h:0.74, valign:'top',
    fontFace:SANS, fontSize:12, color:INK2, lineSpacing:16}));
}

/* ================= 1. TITLE ================= */
{
  const s = pres.addSlide();
  s.background = {color: DARK};
  s.addText('SAPONIN STAGE 1 PRIOR  ·  EVALUATION COVERAGE  ·  2026-09-23', tb({
    x:M, y:1.55, w:W-2*M, h:0.3, fontFace:SANS, fontSize:12, bold:true, color:GREEN, charSpacing:2}));
  s.addText('Where the Field Stops', tb({
    x:M, y:1.95, w:W-2*M, h:1.25, fontFace:SERIF, fontSize:60, bold:true, color:PAPER}));
  s.addText([
    {text:'What published molecular generative models actually report, drawn to scale against the metrics this project needs. '},
    {text:'Nothing here is computed, estimated or filled in', options:{bold:true, color:PAPER}},
    {text:' — every value is transcribed from a source. The empty space is the finding.'}
  ], tb({x:M, y:3.35, w:8.4, h:1.1, fontFace:SANS, fontSize:16, color:ONDARK, lineSpacing:24}));

  // motif: filled vs hollow cells
  const cx = M, cy = 4.95;
  for(let i=0;i<24;i++){
    const on = i<5;
    s.addShape(pres.ShapeType.rect, {x:cx+i*0.30, y:cy, w:0.22, h:0.22,
      fill: on?{color:GREEN}:{color:DARK}, line:{color:on?GREEN:'34443A', width:0.75}});
  }
  s.addText('5 of every 27 metrics this project measures has ever been reported by anyone',
    tb({x:M, y:5.34, w:9, h:0.3, fontFace:SANS, fontSize:11, color:ONDARK_M}));
  s.addNotes('Companion to evaluation_protocol.md v3.3, metric_coverage_gap_analysis.md and reported_metrics_record.md. Every plotted value is transcribed from a published source; where a table could not be retrieved it is recorded as such, not estimated.');
}

/* ================= 2. HEADLINE STATS ================= */
{
  const s = slideBase('Four numbers that frame the problem','The headline',
    'Coverage of the Stage 1 evaluation protocol by the published literature.');
  const stats = [
    ['~150','metrics in the\nevaluation protocol', GREEN],
    ['25–30','of them ever reported\nby published models', INK],
    ['23','field ceiling — the widest\npublished evaluation', INK],
    ['0','published values describing\na sugar or a glycoside', RED]
  ];
  const cw = (W-2*M-3*0.34)/4;
  stats.forEach(([n,l,c],i)=>{
    const x = M+i*(cw+0.34);
    s.addShape(pres.ShapeType.rect, {x:x, y:2.05, w:cw, h:2.45,
      fill:{color:i===3?RED_S:'F7F8F5'}, line:{color:i===3?RED:LINE, width:i===3?1.25:0.75}});
    s.addText(n, tb({x:x+0.3, y:2.42, w:cw-0.6, h:1.0,
      fontFace:SERIF, fontSize:54, bold:true, color:c}));
    s.addText(l, tb({x:x+0.3, y:3.52, w:cw-0.6, h:0.75,
      fontFace:SANS, fontSize:12, color:INK2, lineSpacing:16}));
  });
  takeaway(s,[
    {text:'The field ceiling is '},{text:'[Skinnider2021]',options:{bold:true}},
    {text:' at 23 metrics across 8,447 models — and it covers three of the protocol’s nineteen sections. On roughly 25–30 metrics you will be compared to the field. On the rest there is no baseline, so the A↔B reference distribution is not good practice — it is the only comparator that exists.'}
  ], 4.85);
  footer(s,'Sources: metric_coverage_gap_analysis.md §1 · reported_metrics_record.md §11');
}

/* ================= 3. COVERAGE GRID ================= */
{
  const s = slideBase('The protocol, and the part of it anyone has measured','Coverage',
    'One cell per metric. Filled = reported by at least one published generative model.');
  const COLS=30, ROWS=5, ON=27, cell=0.33, gap=0.055;
  const gw = COLS*cell+(COLS-1)*gap, gx = (W-gw)/2, gy = 2.15;
  for(let i=0;i<COLS*ROWS;i++){
    const r=Math.floor(i/COLS), c=i%COLS, on=i<ON;
    s.addShape(pres.ShapeType.rect, {
      x:gx+c*(cell+gap), y:gy+r*(cell+gap), w:cell, h:cell,
      fill: on?{color:GREEN}:{color:PAPER}, line:{color:on?GREEN:LINE, width:0.75}});
  }
  const ly = gy+ROWS*(cell+gap)+0.24;
  s.addShape(pres.ShapeType.rect,{x:gx, y:ly+0.04, w:0.17, h:0.17, fill:{color:GREEN}, line:{color:GREEN,width:0.75}});
  s.addText('reported somewhere in the literature  (~27)', tb({x:gx+0.28, y:ly, w:3.9, h:0.26, fontFace:SANS, fontSize:11.5, color:INK2}));
  s.addShape(pres.ShapeType.rect,{x:gx+4.35, y:ly+0.04, w:0.17, h:0.17, fill:{color:PAPER}, line:{color:LINE,width:0.75}});
  s.addText('no published precedent  (~123)', tb({x:gx+4.63, y:ly, w:3.6, h:0.26, fontFace:SANS, fontSize:11.5, color:INK2}));

  takeaway(s,[
    {text:'The filled cells are not spread evenly — they cluster almost entirely in '},
    {text:'core distribution learning, the property panel and the failure detectors',options:{bold:true}},
    {text:'. Cell positions here are schematic, not metric IDs.'}
  ], 4.95);
  footer(s,'Source: metric_coverage_gap_analysis.md §1–§2');
}

/* ================= 4. SECTION-BY-SECTION ================= */
{
  const s = slideBase('Nineteen sections, ranked by whether anyone has been here before','Section by section',
    'Status and best available precedent for each part of the protocol.', {titleSize:27});
  const S=[
    ['2','Corpus readiness','p','Practice only'], ['3','Design: splits & controls','n','No control'],
    ['4','Core distribution learning','o','Field standard'], ['5','Physical validity','n','No precedent'],
    ['6','Saponin-specific (S1–S19)','n','Total gap'], ['7','Chemical ontology','n','Opportunity'],
    ['8','Property panel','o','Field standard'], ['9','Synthesizability / biosynthesis','p','Biosynth: none'],
    ['10','Coverage and diversity','p','Newer only'], ['11','Failure detectors','o','Over-relied on'],
    ['12','Memorisation / leakage','p','Diagnostics rare'], ['13','Likelihood / calibration','n','Aggregate only'],
    ['14','Optimisability','o','Recently strong'], ['15','Robustness / sampling','p','Retrain var. rare'],
    ['15A','Training dynamics','n','Not molecular'], ['16','Tokenisation diagnostics','n','Not measured'],
    ['17','Engineering / operational','n','Unreported'], ['18','Governance / licensing','n','Total gap'],
    ['19','Qualitative review','n','Ad hoc only'], ['19A','Comparison / decision rule','p','Newly opened']
  ];
  const col={o:GREEN,p:AMBER,n:RED}, soft={o:GREEN_S,p:AMBER_S,n:RED_S};
  const rowH=0.41, colW=(W-2*M-0.5)/2, y0=1.95;
  S.forEach((r,i)=>{
    const c=i<10?0:1, k=i%10;
    const x=M+c*(colW+0.5), y=y0+k*rowH;
    s.addShape(pres.ShapeType.rect,{x:x, y:y, w:colW, h:rowH-0.05, fill:{color:'F9FAF7'}, line:{color:LINE,width:0.5}});
    s.addText('§'+r[0], tb({x:x+0.12, y:y+0.09, w:0.55, h:0.22, fontFace:SANS, fontSize:11, bold:true, color:MUTED}));
    s.addText(r[1], tb({x:x+0.70, y:y+0.08, w:colW-2.55, h:0.24, fontFace:SANS, fontSize:12, color:INK}));
    s.addShape(pres.ShapeType.rect,{x:x+colW-1.78, y:y+0.07, w:1.66, h:0.24, fill:{color:soft[r[2]]}, line:{color:col[r[2]], width:0.5}});
    s.addText(r[3], tb({x:x+colW-1.78, y:y+0.10, w:1.66, h:0.20, fontFace:SANS, fontSize:9.5, bold:true,
      color:col[r[2]], align:'center'}));
  });
  takeaway(s,[
    {text:'The nine enumerated as having '},{text:'no precedent at all',options:{bold:true}},
    {text:': physical validity, saponin-specific structure, chemical ontology, biosynthetic plausibility, NLL by subgroup, tokenisation, engineering throughput, governance, ring-fusion stereochemistry.'}
  ], 6.24);
  footer(s,'Source: metric_coverage_gap_analysis.md §2 — verdict column verbatim');
}

/* ================= 5. SIZE CLIFF ================= */
{
  const s = slideBase('Every benchmark ends before saponins begin','Size',
    'Heavy-atom ranges of the datasets the field’s numbers come from, drawn on one scale.');
  const px=M+1.55, pw=W-M-px-1.05, py=2.15, rowH=0.86;
  const X=v=>px+(v/100)*pw;
  // gridlines
  [0,20,40,60,80,100].forEach(v=>{
    s.addShape(pres.ShapeType.rect,{x:X(v), y:py-0.12, w:0.008, h:rowH*4+0.12, fill:{color:LINE}});
    s.addText(v===100?'100+':String(v), tb({x:X(v)-0.3, y:py+rowH*4+0.02, w:0.6, h:0.24,
      fontFace:SANS, fontSize:10.5, color:MUTED, align:'center'}));
  });
  s.addText('heavy atoms per molecule', tb({x:px, y:py+rowH*4+0.32, w:2.6, h:0.24, valign:'top',
    fontFace:SANS, fontSize:10.5, bold:true, color:MUTED}));

  const bands=[['QM9',1,9,'max 9',0],['MOSES',8,27,'8–27',0],['GuacaMol',2,88,'2–88',0],
               ['Saponins',40,100,'',1]];
  bands.forEach(([lab,lo,hi,note,open],i)=>{
    const y=py+i*rowH;
    s.addText(lab, tb({x:M, y:y+0.08, w:1.45, h:0.3, fontFace:SERIF, fontSize:14, bold:true,
      color: open?GREEN:INK, align:'right'}));
    s.addShape(pres.ShapeType.rect,{x:X(lo), y:y, w:X(hi)-X(lo), h:0.46,
      fill: open?{color:GREEN, transparency:78}:{color:MUTED, transparency:28},
      line: open?{color:GREEN, width:1.75, dashType:'dash'}:{type:'none'}});
    if(open){
      s.addShape(pres.ShapeType.triangle,{x:X(100)+0.09, y:y+0.03, w:0.40, h:0.40,
        fill:{color:GREEN}, rotate:90});
      s.addText('> 40 — distribution not yet measured', tb({x:X(lo)+0.16, y:y+0.11, w:4.6, h:0.26,
        fontFace:SANS, fontSize:11.5, bold:true, color:GREEN}));
    } else {
      s.addText(note, tb({x:X(hi)+0.12, y:y+0.11, w:1.2, h:0.26, fontFace:SANS, fontSize:11.5, color:INK}));
    }
  });
  // GEOM-DRUGS marker, different unit
  s.addShape(pres.ShapeType.rect,{x:X(44.2), y:py-0.14, w:0.015, h:rowH*4+0.14, fill:{color:AMBER}});
  s.addShape(pres.ShapeType.ellipse,{x:X(44.2)-0.065, y:py-0.21, w:0.13, h:0.13, fill:{color:AMBER}});
  s.addText('GEOM-DRUGS mean 44.2 — atoms incl. H, not directly comparable',
    tb({x:px+2.95, y:py+rowH*4+0.32, w:6.3, h:0.26, valign:'top', fontFace:SANS, fontSize:10.5, color:AMBER}));

  takeaway(s,[
    {text:'MOSES caps at '},{text:'27 heavy atoms',options:{bold:true}},{text:', GuacaMol at 88. The corpus sits '},
    {text:'above 40 and routinely past both caps',options:{bold:true}},
    {text:' — the bar runs off the axis because that distribution is not yet measured (Q4a). Their metric code is reusable; their scores are not.'}
  ], 6.24);
  footer(s,'Sources: [Polykovskiy2020] · [Brown2019] · [Xu2023] · corpus figure from this review §6');
}

/* ================= 6. 3D COLLAPSE ================= */
{
  const s = slideBase('The number the field reports by refusing to report it','3D diffusion',
    'Molecule stability for every 3D method on QM9 — then the same metric on drug-sized molecules.');
  const labels=['Data (ref.)','GeoLDM','EDM-Bridge','EDM','GraphLDM-AUG','GDM-AUG','GraphLDM','G-SchNet','GDM','ENF'];
  const vals  =[95.2,89.4,84.6,82.0,78.7,71.6,70.5,68.1,63.2,4.9];
  s.addChart(pres.ChartType.bar, [{name:'Molecule stability %', labels:labels, values:vals}], {
    x:M, y:2.02, w:6.55, h:4.05,
    barDir:'bar', barGapWidthPct:38,
    chartColors:[GREEN, ...Array(8).fill('3E6B57'), RED],
    showValue:true, dataLabelPosition:'outEnd', dataLabelColor:INK,
    dataLabelFontFace:SANS, dataLabelFontSize:10.5, dataLabelFormatCode:'0.0',
    showLegend:false, showTitle:true, title:'QM9 — molecule stability %   (130k molecules · max 9 heavy atoms)',
    titleColor:MUTED, titleFontFace:SANS, titleFontSize:11.5,
    catAxisLabelColor:INK2, catAxisLabelFontFace:SANS, catAxisLabelFontSize:11,
    valAxisLabelColor:MUTED, valAxisLabelFontFace:SANS, valAxisLabelFontSize:10,
    valAxisMaxVal:100, valAxisMinVal:0,
    valGridLine:{color:TRACK, size:0.75}, catGridLine:{style:'none'},
    valAxisLineShow:false, catAxisLineShow:false
  });

  const vx=M+6.95, vw=W-M-vx;
  s.addShape(pres.ShapeType.rect,{x:vx, y:2.02, w:vw, h:4.05,
    fill:{color:RED_S}, line:{color:RED, width:1.25, dashType:'dash'}});
  s.addText('GEOM-DRUGS — MOLECULE STABILITY', tb({x:vx+0.34, y:2.36, w:vw-0.68, h:0.28,
    fontFace:SANS, fontSize:11, bold:true, color:RED, charSpacing:1.5}));
  s.addText('≈ 0%', tb({x:vx+0.34, y:2.72, w:vw-0.68, h:0.95,
    fontFace:SERIF, fontSize:58, bold:true, color:RED}));
  s.addText('“omitted since they are nearly 0% and 100% respectively for all the methods… DRUG molecules contain larger and more complex structures, creating errors during bond type prediction.”',
    tb({x:vx+0.50, y:3.80, w:vw-0.86, h:1.35, fontFace:SANS, fontSize:13, italic:true, color:INK2, lineSpacing:19}));
  s.addShape(pres.ShapeType.rect,{x:vx+0.34, y:3.82, w:0.035, h:1.25, fill:{color:RED}});
  s.addText('~450,000 molecules  ·  average 44.2 atoms  ·  every method tested',
    tb({x:vx+0.34, y:5.42, w:vw-0.68, h:0.4, fontFace:SANS, fontSize:10.5, color:MUTED}));

  takeaway(s,[
    {text:'At nine heavy atoms 3D diffusion reaches 89.4% stability. At an average of 44.2 atoms the authors '},
    {text:'stop publishing the metric, because it is near zero for every method',options:{bold:true}},
    {text:'. Saponins are larger than that average — the strongest evidence against 3D diffusion at Stage 1, and it is an omission rather than a number.'}
  ], 6.26);
  footer(s,'Source: [Xu2023] Table 1, fetched in full · EDM originally [Hoogeboom2022]');
}

/* ================= 7. MOSES FCD ================= */
{
  const s = slideBase('MOSES publishes your reference floor for you','Distribution',
    'Fréchet ChemNet Distance vs the test set, log scale. Lower is better.');
  const D=[['Train (reference)',0.008,GREEN],['CharRNN',0.073,'3E6B57'],['VAE',0.099,'3E6B57'],
           ['LatentGAN',0.296,'3E6B57'],['JTN-VAE',0.3954,'3E6B57'],['AAE',0.556,'3E6B57'],
           ['Combinatorial',4.2375,RED],['NGram',5.5069,RED],['HMM',24.4661,RED]];
  const px=M+1.95, pw=W-M-px-1.35, py=1.96, rowH=0.40;
  const lo=Math.log10(0.005), hi=Math.log10(40);
  const X=v=>px+((Math.log10(v)-lo)/(hi-lo))*pw;
  [0.01,0.1,1,10].forEach(t=>{
    s.addShape(pres.ShapeType.rect,{x:X(t), y:py-0.10, w:0.008, h:rowH*D.length+0.06, fill:{color:LINE}});
    s.addText(String(t), tb({x:X(t)-0.35, y:py+rowH*D.length, w:0.7, h:0.24,
      fontFace:SANS, fontSize:10.5, color:MUTED, align:'center'}));
  });
  s.addText('FCD vs test set — log scale, lower is better',
    tb({x:M, y:py+rowH*D.length+0.02, w:1.85, h:0.5, valign:'top',
        fontFace:SANS, fontSize:10.5, bold:true, color:MUTED, align:'right'}));
  D.forEach(([n,v,c],i)=>{
    const y=py+i*rowH, cy=y+rowH/2;
    s.addText(n, tb({x:M, y:cy-0.135, w:1.85, h:0.27, fontFace:SANS, fontSize:11.5,
      bold:i===0, color:i===0?GREEN:INK2, align:'right'}));
    s.addShape(pres.ShapeType.rect,{x:px, y:cy-0.008, w:X(v)-px, h:0.016, fill:{color:c, transparency:62}});
    const r=i===0?0.19:0.155;
    s.addShape(pres.ShapeType.ellipse,{x:X(v)-r/2, y:cy-r/2, w:r, h:r, fill:{color:c}});
    s.addText(String(v), tb({x:X(v)+0.16, y:cy-0.13, w:1.15, h:0.26, fontFace:SANS, fontSize:11, bold:true, color:INK}));
  });
  takeaway(s,[
    {text:'The training set scores '},{text:'0.008',options:{bold:true}},
    {text:' — that is the A↔B reference the protocol asks for, published by the benchmark itself, and it is the model to copy. The range spans three decades, so a small absolute difference near the floor is not a small difference.'}
  ], 6.22);
  footer(s,'Source: [Polykovskiy2020], full baseline tables · mean of three initialisations');
}

/* ================= 8. FOCUSED-DATASET TRADE-OFF ================= */
{
  const s = slideBase('The trade-off to expect on a focused corpus','Closest analogue',
    'Patent-derived focused datasets — the nearest published regime to a 40k domain-specific corpus.');
  const px=M+1.05, py=1.96, pw=6.5, ph=3.42;
  const X=v=>px+v*pw, Y=v=>py+ph-v*ph;
  [0,0.2,0.4,0.6,0.8,1.0].forEach(t=>{
    s.addShape(pres.ShapeType.rect,{x:px, y:Y(t), w:pw, h:0.008, fill:{color:TRACK}});
    s.addShape(pres.ShapeType.rect,{x:X(t), y:py, w:0.008, h:ph, fill:{color:TRACK}});
    s.addText(t.toFixed(1), tb({x:px-0.62, y:Y(t)-0.13, w:0.5, h:0.26, fontFace:SANS, fontSize:10, color:MUTED, align:'right'}));
    s.addText(t.toFixed(1), tb({x:X(t)-0.3, y:py+ph+0.06, w:0.6, h:0.26, fontFace:SANS, fontSize:10, color:MUTED, align:'center'}));
  });
  s.addText('FCD score  →  distribution match', tb({x:px, y:py+ph+0.36, w:4.5, h:0.26, valign:'top',
    fontFace:SANS, fontSize:10.5, bold:true, color:MUTED}));
  s.addText('Novelty ↑', tb({x:px-0.95, y:py-0.34, w:1.6, h:0.26, fontFace:SANS, fontSize:10.5, bold:true, color:MUTED}));
  // 0.9 reference
  s.addShape(pres.ShapeType.rect,{x:X(0.9), y:py, w:0.014, h:ph, fill:{color:AMBER}});
  s.addText('~0.9 typical on\nlarge drug datasets', tb({x:X(0.9)-1.86, y:py+0.06, w:1.74, h:0.5, valign:'top',
    fontFace:SANS, fontSize:10, color:AMBER, lineSpacing:13, align:'right'}));
  const boxes=[
    ['RNN + SELFIES',0.60,0.61,0.55,0.58,GREEN,'distribution match ≈ 2× better','left'],
    ['JT-VAE',0.28,0.32,0.89,1.00,AMBER,'wins novelty, loses the distribution','right']
  ];
  boxes.forEach(([n,x0,x1,y0,y1,c,tip,side])=>{
    const bx=X(x0), bw=Math.max(X(x1)-X(x0),0.16), by=Y(y1), bh=Math.max(Y(y0)-Y(y1),0.16);
    s.addShape(pres.ShapeType.rect,{x:bx, y:by, w:bw, h:bh, fill:{color:c, transparency:76}, line:{color:c, width:2}});
    const cy=by+bh/2;
    if(side==='left'){
      s.addText(n, tb({x:bx-3.3, y:cy-0.26, w:3.1, h:0.28, fontFace:SERIF, fontSize:14, bold:true, color:INK, align:'right'}));
      s.addText(tip, tb({x:bx-3.3, y:cy+0.02, w:3.1, h:0.26, fontFace:SANS, fontSize:10.5, color:MUTED, align:'right'}));
    } else {
      s.addText(n, tb({x:bx+bw+0.18, y:cy-0.26, w:3.1, h:0.28, fontFace:SERIF, fontSize:14, bold:true, color:INK}));
      s.addText(tip, tb({x:bx+bw+0.18, y:cy+0.02, w:3.1, h:0.26, fontFace:SANS, fontSize:10.5, color:MUTED}));
    }
  });
  // side note
  const nx=px+pw+0.95;
  s.addShape(pres.ShapeType.rect,{x:nx, y:py, w:W-M-nx, h:ph+0.42, fill:{color:'F7F8F5'}, line:{color:LINE, width:0.75}});
  s.addText('Why this one matters', tb({x:nx+0.28, y:py+0.26, w:W-M-nx-0.56, h:0.32, valign:'top',
    fontFace:SERIF, fontSize:16, bold:true, color:INK}));
  s.addText([
    {text:'Both models sit far below the ~0.9 FCD typical of large drug datasets. On small, domain-focused data the string model matched the distribution '},
    {text:'roughly twice as well',options:{bold:true, color:GREEN}},
    {text:' while losing decisively on novelty.\n\nFor a Stage 1 prior whose likelihood stays inside the Stage 2 objective, '},
    {text:'distribution match is the axis that matters',options:{bold:true}},
    {text:' — novelty is Stage 2’s job.'}
  ], tb({x:nx+0.28, y:py+0.70, w:W-M-nx-0.56, h:2.95, valign:'top',
    fontFace:SANS, fontSize:11.5, color:INK2, lineSpacing:16}));
  takeaway(s,[{text:'Reported: FCD 0.60–0.61 against 0.28–0.32 · Novelty 0.55–0.58 against 0.89–1.00. That is the trade-off to expect at 40k.'}], 6.26);
  footer(s,'Source: [Subramanian2023] Table 1, GuacaMol distribution-learning suite');
}

/* ================= 9. SECTIONS TOUCHED ================= */
{
  const s = slideBase('How much of the protocol each published model touches','Per model',
    'Protocol sections where the paper reports something at all, out of nineteen. Touching is not covering.');
  const labels=['Skinnider2021','MOSES','MolGAN','DiGress','Ozcelik2025','MolScore','GuacaMol',
                'Aug. Memory','S4 CLM','Moret2020','Tom2025','EDM / GeoLDM','PMO','NPGPT',
                'REINVENT 4','JT-VAE','Ochiai2023'];
  const values=[5,4,3,3,3,2,2,2,2,2,2,2,1,1,1,1,0];
  s.addChart(pres.ChartType.bar, [{name:'Protocol sections touched', labels:labels, values:values}], {
    x:M, y:1.98, w:8.5, h:4.25,
    barDir:'bar', barGapWidthPct:34,
    chartColors:[GREEN, GREEN, ...Array(14).fill('3E6B57'), RED],
    showValue:true, dataLabelPosition:'outEnd', dataLabelColor:INK,
    dataLabelFontFace:SANS, dataLabelFontSize:10.5,
    showLegend:false, showTitle:false,
    catAxisLabelColor:INK2, catAxisLabelFontFace:SANS, catAxisLabelFontSize:10.5,
    valAxisLabelColor:MUTED, valAxisLabelFontFace:SANS, valAxisLabelFontSize:10,
    valAxisMaxVal:19, valAxisMinVal:0, valAxisMajorUnit:19,
    valGridLine:{style:'none'}, catGridLine:{style:'none'},
    valAxisLineShow:false, catAxisLineShow:false, valAxisHidden:true
  });
  const nx=M+8.95;
  s.addText('out of 19', tb({x:nx, y:1.98, w:2, h:0.3, fontFace:SANS, fontSize:11, bold:true, color:MUTED}));
  s.addText('5', tb({x:nx, y:2.36, w:2.4, h:1.0, fontFace:SERIF, fontSize:62, bold:true, color:GREEN}));
  s.addText('is the field ceiling — one model, five sections.', tb({x:nx, y:3.36, w:W-M-nx, h:0.6,
    fontFace:SANS, fontSize:13, color:INK, lineSpacing:18}));
  s.addText('No published model reports anything in saponin-specific structure, chemical ontology, biosynthetic plausibility, tokenisation or governance.',
    tb({x:nx, y:4.10, w:W-M-nx, h:1.5, fontFace:SANS, fontSize:12, color:INK2, lineSpacing:17}));
  takeaway(s,[
    {text:'For more than half the protocol, the question “how does this compare to published work” has '},
    {text:'no answer other than your own reference distribution',options:{bold:true}},{text:'.'}
  ], 6.34);
  footer(s,'Counts from metric_coverage_gap_analysis.md §3');
}

/* ================= 10. THE ZEROS ================= */
{
  const s = slideBase('Published values describing saponin chemistry','The gap itself',
    'Across 317 transcribed values — nine MOSES baselines, six GuacaMol baselines, ten 3D methods, two focused-dataset models, four optimisation entries.');
  const items=[['glycosylation rate','or glycoside fraction'],['monosaccharide identity','or sugars per molecule'],
               ['anomeric configuration','validity (α/β)'],['ring-fusion','stereochemistry']];
  const cw=(W-2*M-3*0.32)/4;
  items.forEach(([a,b],i)=>{
    const x=M+i*(cw+0.32);
    s.addShape(pres.ShapeType.rect,{x:x, y:2.15, w:cw, h:2.35, fill:{color:PAPER}, line:{color:RED, width:1.25, dashType:'dash'}});
    s.addText('0', tb({x:x, y:2.42, w:cw, h:1.15, fontFace:SERIF, fontSize:76, bold:true, color:RED, align:'center'}));
    s.addText(a+'\n'+b, tb({x:x+0.2, y:3.66, w:cw-0.4, h:0.62, fontFace:SANS, fontSize:12, color:INK2, align:'center', lineSpacing:16}));
  });
  takeaway(s,[
    {text:'The only stereochemistry metric anywhere is Skinnider’s '},
    {text:'aggregate stereocentre fraction',options:{bold:true}},
    {text:' — and [Skinnider2024] found it was the one metric where SMILES did not significantly beat SELFIES (JSD p = 0.10, against p = 3.6 × 10⁻⁶ for scaffolds). [Tom2025], the single paper dedicated to stereochemistry-aware generation, '},
    {text:'explicitly excludes ring isomers',options:{bold:true}},
    {text:' — exactly the A/B, B/C, C/D ring fusion that defines a triterpenoid skeleton’s shape. The gap is a stated scope boundary in the state of the art, not an artefact of the search.'}
  ], 4.85);
  footer(s,'Source: reported_metrics_record.md §11 · [Skinnider2024] · [Tom2025]');
}

/* ================= 11. WHAT FOLLOWS ================= */
{
  const s = pres.addSlide();
  s.background={color:DARK};
  s.addText('WHAT FOLLOWS FROM THIS', tb({x:M, y:0.72, w:W-2*M, h:0.3,
    fontFace:SANS, fontSize:12, bold:true, color:GREEN, charSpacing:2}));
  s.addText('Three consequences', tb({x:M, y:1.06, w:W-2*M, h:0.7,
    fontFace:SERIF, fontSize:38, bold:true, color:PAPER}));
  const items=[
    ['Inherit where the field is strong','On roughly 25–30 metrics you will be compared to the field. Cover distribution learning, the property panel, coverage and the failure detectors with standard implementations — MolScore, the MOSES metric code, CLMeval — and inherit their tooling rather than rebuilding it.'],
    ['Build your own baseline everywhere else','There is no published comparator for more than half the protocol, which makes the A↔B reference distribution mandatory, not optional. Benchmark scores from MOSES and GuacaMol are not transferable to this size class; only their code is.'],
    ['Three contributions look genuinely first','NPClassifier pointed at generated molecules · the saponin-specific structural metrics · biosynthetic plausibility via BioNavi-NP or the TeroENZ set already inside TeroKit. Ring-fusion stereochemistry has the clearest claim.']
  ];
  const cw=(W-2*M-2*0.42)/3;
  items.forEach(([h,b],i)=>{
    const x=M+i*(cw+0.42);
    s.addShape(pres.ShapeType.ellipse,{x:x, y:2.28, w:0.44, h:0.44, fill:{color:GREEN}});
    s.addText(String(i+1), tb({x:x, y:2.355, w:0.44, h:0.30, fontFace:SANS, fontSize:15, bold:true, color:PAPER, align:'center'}));
    s.addText(h, tb({x:x, y:2.92, w:cw, h:0.66, valign:'top',
      fontFace:SERIF, fontSize:17, bold:true, color:PAPER, lineSpacing:22}));
    s.addText(b, tb({x:x, y:3.70, w:cw, h:2.3, valign:'top',
      fontFace:SANS, fontSize:12, color:ONDARK, lineSpacing:18}));
  });
  s.addShape(pres.ShapeType.rect,{x:M, y:6.18, w:W-2*M, h:0.01, fill:{color:'34443A'}});
  s.addText('One caution on the record: the “no generative paper uses NPClassifier” claim rests on not having found something in a bounded search. A citation-graph check on [Kim2021] should close it before it is asserted in a write-up.',
    tb({x:M, y:6.38, w:W-2*M, h:0.5, fontFace:SANS, fontSize:11.5, italic:true, color:ONDARK_M, lineSpacing:16}));
  s.addNotes('Every value in this deck is transcribed from a published source. Cross-paper comparison is mostly invalid — different datasets, sample sizes, RDKit versions and preprocessing — and library size alone can reverse model rankings [Ozcelik2025].');
}

pres.writeFile({fileName:'/home/claude/saponin_review/Saponin_Evaluation_Gap.pptx'})
  .then(f=>console.log('WROTE', f));
