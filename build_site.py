import json
with open('./nfl_data.json') as f:
    data = json.load(f)
DATA_JS = json.dumps(data, separators=(',', ':'))

HTML = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Edge Board — NFL Model vs Market</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root{--bg:#0e1116;--panel:#161b22;--panel2:#1d232e;--line:#2a3340;--text:#e9edf3;--muted:#8b95a6;
    --amber:#f4b740;--amber-dim:#7a5f1f;--up:#5aa87a;--down:#d1685e;--fd:#6aa0e0;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Archivo',system-ui,sans-serif;background:var(--bg);color:var(--text);
    font-feature-settings:"tnum" 1;line-height:1.4;-webkit-font-smoothing:antialiased}
  .wrap{max-width:960px;margin:0 auto;padding:20px}
  header{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:14px}
  .brand{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
  .brand h1{font-weight:900;font-size:28px;letter-spacing:-.02em;line-height:1}.brand .b{color:var(--amber)}
  .asof{color:var(--muted);font-size:13px;font-weight:600}
  .disc{margin-top:10px;font-size:12px;color:var(--muted);max-width:80ch;line-height:1.5}
  .tabs{display:flex;gap:6px;margin-bottom:18px;flex-wrap:wrap}
  .tab{background:var(--panel);border:1px solid var(--line);color:var(--muted);padding:9px 18px;border-radius:8px;font-weight:800;font-size:14px;cursor:pointer}
  .tab.on{background:var(--panel2);color:var(--amber);border-color:var(--amber-dim)}
  .selbar{display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap}
  .seasonbtn{background:var(--panel);border:1px solid var(--line);color:var(--muted);font-family:inherit;font-weight:800;font-size:13px;padding:9px 16px;border-radius:9px;cursor:pointer}
  .seasonbtn:hover{background:var(--panel2)}.seasonbtn.on{background:var(--panel2);color:var(--amber);border-color:var(--amber-dim)}
  .vdiv{width:1px;height:24px;background:var(--line)}
  .arw{width:36px;height:38px;border:1px solid var(--line);background:var(--panel);color:var(--text);border-radius:9px;font-size:17px;font-weight:800;cursor:pointer;display:flex;align-items:center;justify-content:center}
  .arw:hover{background:var(--panel2)}.arw:disabled{opacity:.3;cursor:default}
  .selwrap{position:relative}
  .sel{min-width:150px;background:var(--panel);border:1px solid var(--amber-dim);color:var(--amber);font-family:inherit;font-weight:800;font-size:15px;padding:9px 32px 9px 14px;border-radius:9px;cursor:pointer;appearance:none;-webkit-appearance:none}
  .selwrap::after{content:'▾';position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none;font-size:11px}
  .daylabel{font-size:11.5px;font-weight:800;color:var(--muted);margin:18px 0 8px;letter-spacing:.02em;display:flex;align-items:center;gap:10px}
  .daylabel::after{content:'';flex:1;height:1px;background:var(--line)}
  .board{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--panel)}
  .cols{display:grid;grid-template-columns:1.1fr repeat(4,1fr) 24px;gap:8px}
  @media(max-width:600px){.cols{grid-template-columns:1fr repeat(4,1fr) 16px;gap:5px}}
  .colhdr{padding:8px 14px;border-bottom:1px solid var(--line);font-size:10px;font-weight:800;color:var(--muted)}
  .colhdr .bk{text-align:center}.colhdr .model{color:var(--amber)}.colhdr .fd{color:var(--fd)}
  .game{padding:11px 14px;border-bottom:1px solid var(--line);cursor:pointer;align-items:center}
  .game:last-child{border-bottom:none}.game:hover{background:var(--panel2)}
  .gmu{font-weight:800;font-size:14.5px}@media(max-width:600px){.gmu{font-size:12.5px}}
  .gkick{font-size:10.5px;color:var(--muted);font-weight:600;margin-top:2px}
  .bkcell{text-align:center}.bkcell .sp{font-weight:800;font-size:13.5px}@media(max-width:600px){.bkcell .sp{font-size:11px}}
  .bkcell .ou{font-size:10.5px;color:var(--muted);font-weight:600;margin-top:1px}
  .mcell{text-align:center;background:rgba(244,183,64,.06);border-radius:7px;padding:4px 2px}
  .mcell .sp{font-weight:900;font-size:13.5px;color:var(--amber)}@media(max-width:600px){.mcell .sp{font-size:11px}}
  .mcell .ou{font-size:10.5px;color:#b8933f;font-weight:700;margin-top:1px}
  .chev{color:var(--muted);font-size:12px;text-align:center}
  .rccards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:6px}
  @media(max-width:640px){.rccards{grid-template-columns:1fr 1fr}}
  .rccard{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:13px 14px}
  .rclbl{font-size:11px;font-weight:800;color:var(--muted);margin-bottom:9px}.rclbl.model{color:var(--amber)}.rclbl.fdl{color:var(--fd)}
  .rcline{display:flex;justify-content:space-between;align-items:baseline;font-size:13px;color:var(--muted);font-weight:600;margin-bottom:4px}
  .rcline b{color:var(--text);font-size:17px;font-weight:900;margin-left:auto;margin-right:6px}.rcp{color:var(--muted);font-weight:700;font-size:12px;min-width:34px;text-align:right}
  .rcbuild{font-size:12px;color:var(--muted);padding:4px 0;line-height:1.4}
  .sec{font-size:12px;font-weight:800;color:var(--muted);margin:18px 0 9px}
  .rec-note{font-size:12.5px;color:var(--muted);line-height:1.55;margin:14px 0 6px;max-width:82ch}.rec-note b{color:#c7ad6a}
  .grow{display:grid;grid-template-columns:1.3fr auto auto auto;gap:9px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--line);cursor:pointer}
  .grow:last-child{border-bottom:none}.grow:hover{background:var(--panel2)}
  .gfin{font-weight:800;font-size:14px;text-align:right;white-space:nowrap}.gfin .w{color:var(--up)}
  .gb{font-size:10.5px;font-weight:900;padding:3px 7px;border-radius:6px;min-width:70px;text-align:center}
  .gb.hit{background:rgba(90,168,122,.16);color:var(--up)}.gb.miss{background:rgba(209,104,94,.16);color:var(--down)}.gb.push{background:var(--panel2);color:var(--muted)}
  .trend{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--panel)}
  .trow{display:grid;grid-template-columns:80px 1fr 1fr;align-items:center;padding:13px 18px;border-bottom:1px solid var(--line);cursor:pointer}
  .trow:last-child{border-bottom:none}.trow:hover{background:var(--panel2)}.trow.head{cursor:default;font-size:11px;color:var(--muted);font-weight:800;padding:10px 18px}
  .twk{font-weight:900;font-size:15px}.tcell{display:flex;align-items:baseline;gap:8px}.tcell .rec{font-weight:900;font-size:15px}.tcell .pct{color:var(--muted);font-size:12.5px;font-weight:700}
  .search{width:100%;background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:10px 12px;font-family:inherit;font-weight:600;font-size:14px;margin-bottom:12px}
  .trrow{display:grid;grid-template-columns:32px 1fr auto;gap:10px;align-items:center;padding:11px 14px;border-bottom:1px solid var(--line);cursor:pointer}.trrow:last-child{border-bottom:none}.trrow:hover{background:var(--panel2)}
  .trk{font-weight:900;color:var(--amber);text-align:center}.tnm{font-weight:700;font-size:14.5px}.trec{font-size:12.5px;color:var(--muted);font-weight:700}
  .prow{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:11px 14px;border-bottom:1px solid var(--line);cursor:pointer}.prow:last-child{border-bottom:none}.prow:hover{background:var(--panel2)}
  .pnm{font-weight:700;font-size:14.5px}.ppos{font-size:12px;color:var(--muted);font-weight:700}
  .pst{font-size:10px;font-weight:900;padding:2px 7px;border-radius:5px;margin-left:8px}.pst.q{background:rgba(244,183,64,.13);color:var(--amber)}.pst.o{background:rgba(209,104,94,.18);color:var(--down)}.pst.a{background:rgba(90,168,122,.14);color:var(--up)}
  .back{display:inline-flex;align-items:center;gap:6px;color:var(--muted);font-weight:700;font-size:13px;cursor:pointer;margin-bottom:14px}.back:hover{color:var(--amber)}
  .gp-head{border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:4px}
  .gp-mu{font-size:25px;font-weight:900;letter-spacing:-.02em}.gp-mu .lnk{cursor:pointer}.gp-mu .lnk:hover{color:var(--amber)}
  .gp-kick{color:var(--muted);font-size:13px;font-weight:600;margin-top:3px}
  .gp-fscore{font-size:22px;font-weight:900;margin-top:12px}.gp-fscore .w{color:var(--up)}
  .gp-verdict{display:flex;gap:8px;margin-top:10px}
  .lines4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
  .lc{border:1px solid var(--line);border-radius:9px;padding:11px 8px;text-align:center;background:var(--panel)}
  .lc.model{border-color:var(--amber-dim);background:rgba(244,183,64,.06)}
  .lc .l{font-size:10px;font-weight:800;color:var(--muted);margin-bottom:5px}.lc.model .l{color:var(--amber)}.lc.fd .l{color:var(--fd)}
  .lc .sp{font-size:16px;font-weight:900}.lc.model .sp{color:var(--amber)}.lc .ou{font-size:11px;color:var(--muted);font-weight:600;margin-top:2px}
  .take{border:1px solid var(--amber-dim);background:rgba(244,183,64,.06);border-radius:11px;padding:15px 16px}
  .takelean{font-size:17px;font-weight:900;color:var(--amber);margin-bottom:8px}.takewhy{font-size:14px;line-height:1.6;color:#d5dbe6}
  .vd{border:1px solid var(--line);border-radius:10px;overflow:hidden}
  .vdr{display:grid;grid-template-columns:62px 1fr auto;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--line)}.vdr:last-child{border-bottom:none}
  .vdk{font-size:12px;font-weight:800;color:var(--muted)}.vdt{font-size:13.5px;line-height:1.5}.vdt b{font-weight:800}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:560px){.two{grid-template-columns:1fr}}
  .card{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:14px}
  .card h3{font-size:11.5px;font-weight:800;color:var(--muted);margin-bottom:10px}
  .wx{display:flex;align-items:center;gap:14px;flex-wrap:wrap}.wx .big{font-size:18px;font-weight:800}.wx .s{font-size:13px;color:var(--muted);font-weight:600}
  .wxflag{font-size:11px;font-weight:800;color:var(--amber);border:1px solid var(--amber-dim);border-radius:6px;padding:3px 8px;display:inline-block;margin-top:8px}
  .injrow{display:flex;align-items:center;gap:8px;font-size:13px;padding:5px 0;border-bottom:1px solid var(--line)}.injrow:last-child{border-bottom:none}
  .injs{font-size:10px;font-weight:900;padding:2px 6px;border-radius:4px;min-width:36px;text-align:center}.injs.out{background:rgba(209,104,94,.18);color:var(--down)}.injs.dbt{background:rgba(244,183,64,.15);color:var(--amber)}.injs.q{background:rgba(244,183,64,.12);color:var(--amber)}
  .injp{color:var(--muted);font-weight:800;font-size:11px}.injn{font-weight:700}.injn.lnk{cursor:pointer}.injn.lnk:hover{color:var(--amber)}.injnote{color:var(--muted);font-size:12px}
  .tm h4{font-size:15px;font-weight:800;margin-bottom:2px}.tm h4 .lnk{cursor:pointer}.tm h4 .lnk:hover{color:var(--amber)}
  .tm .rk{font-size:12px;color:var(--amber);font-weight:800;margin-bottom:10px}
  .stat{margin-bottom:10px}.stat .top{display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:3px}.stat .lab{color:var(--muted);font-weight:700}.stat .num{font-weight:800}
  .tier{font-size:10.5px;font-weight:800;padding:1px 5px;border-radius:4px;background:var(--panel2);color:var(--muted)}
  .bar{height:6px;background:var(--panel2);border-radius:3px;position:relative;overflow:hidden}.bar .mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:#3a4453}.bar .fill{position:absolute;top:0;bottom:0;border-radius:3px}
  .boxt{width:100%;border-collapse:collapse;font-size:13.5px}.boxt th{font-size:11px;color:var(--muted);font-weight:700;text-align:center;padding:5px 4px;border-bottom:1px solid var(--line)}.boxt th:first-child{text-align:left}
  .boxt td{text-align:center;padding:7px 4px;font-weight:700;border-bottom:1px solid var(--line)}.boxt td:first-child{text-align:left;font-weight:800}.boxt tr:last-child td{border-bottom:none}.boxt .qtot{color:var(--amber);font-weight:900}
  .propstat{padding:14px 0;border-bottom:1px solid var(--line)}.propstat:last-child{border-bottom:none}
  .ps-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}.ps-name{font-size:15px;font-weight:800}.ps-proj{font-size:14px;color:var(--amber);font-weight:800}
  .ps-games{font-size:12.5px;color:var(--muted);font-weight:600;margin-bottom:12px}
  .ps-calc{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.ps-calc label{font-size:12.5px;color:var(--muted);font-weight:700}
  .lineinput{width:90px;background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:7px;padding:8px 10px;font-family:inherit;font-size:14px;font-weight:700}
  .ps-out{font-size:13.5px;font-weight:700}.ps-out .ov{color:var(--up);font-weight:900}.ps-out .un{color:var(--down);font-weight:900}
  .ps-lean{font-size:12.5px;font-weight:900;padding:3px 9px;border-radius:6px;border:1px solid var(--amber-dim);color:var(--amber)}
  .logtbl{width:100%;border-collapse:collapse;font-size:13.5px}.logtbl th{text-align:left;color:var(--muted);font-weight:700;font-size:11.5px;padding:6px 8px;border-bottom:1px solid var(--line)}
  .logtbl td{padding:7px 8px;border-bottom:1px solid var(--line);font-weight:600}.logtbl tr:last-child td{border-bottom:none}
  .wl{font-weight:900}.wl.W{color:var(--up)}.wl.L{color:var(--down)}.kick{color:var(--muted);font-weight:600}
  .schrow.next td{background:rgba(244,183,64,.06)}
  .none{color:var(--muted);font-size:13px;padding:14px}
  .plr{display:grid;grid-template-columns:1.2fr repeat(4,1fr);gap:8px;align-items:center;padding:11px 14px;border-bottom:1px solid var(--line)}.plr:last-child{border-bottom:none}
  .plr.head{font-size:10px;font-weight:800;color:var(--muted)}.plr.head .pcell{color:var(--muted)}
  .pcell{text-align:center}.pcell .n{font-weight:900;font-size:13px}@media(max-width:600px){.pcell .n{font-size:11px}}
  .pcell .n.hit{color:var(--up)}.pcell .n.miss{color:var(--down)}.pcell .n.push{color:var(--muted)}
  .pcell .r{font-size:9.5px;color:var(--muted);font-weight:700;margin-top:1px}
  .twobtn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:8px}@media(max-width:520px){.twobtn{grid-template-columns:1fr}}
  .bigbtn{border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:26px 20px;cursor:pointer;text-align:center}
  .bigbtn:hover{background:var(--panel2);border-color:var(--amber-dim)}
  .bigbtn .t{font-size:18px;font-weight:900;color:var(--amber)}.bigbtn .s{font-size:12px;color:var(--muted);font-weight:600;margin-top:4px}
  .pgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:6px}@media(max-width:600px){.pgrid{grid-template-columns:repeat(3,1fr)}}
  .gbtn{background:var(--panel);border:1px solid var(--line);color:var(--text);font-weight:900;font-size:18px;padding:18px 10px;border-radius:11px;cursor:pointer;text-align:center}
  .gbtn:hover{background:var(--panel2)}.gbtn.on{background:var(--panel2);color:var(--amber);border-color:var(--amber-dim)}
  .gbtn .sub{display:block;font-size:11px;color:var(--muted);font-weight:700;margin-top:4px}
  .projtbl{display:grid;grid-template-columns:1.2fr repeat(4,1fr);gap:8px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line)}.projtbl:last-child{border-bottom:none}
  .projtbl.head{font-size:10px;font-weight:800;color:var(--muted)}
  .pjc{text-align:center;font-weight:800;font-size:13.5px}.pjc.amber{color:var(--amber)}.pjc.dash{color:#3a4453}
  .hint{font-size:12px;color:var(--muted);text-align:center;margin-top:16px;font-style:italic}
</style></head><body>
<div class="wrap">
  <header>
    <div class="brand"><h1>Edge <span class="b">Board</span></h1><span class="asof">__ASOF__</span></div>
    <p class="disc">Our model's read vs. the market for every game. Lines from Vegas, DraftKings, and FanDuel; leans are talking points, not locks. Bet responsibly.</p>
  </header>
  <div class="tabs">
    <div class="tab on" data-t="matchups">Matchups</div>
    <div class="tab" data-t="results">Results</div>
    <div class="tab" data-t="props">Props</div>
    <div class="tab" data-t="teams">Teams</div>
    <div class="tab" data-t="players">Players</div>
  </div>
  <div id="view"></div>
  <div id="gamepage" style="display:none"></div>
  <div class="hint" id="hint"></div>
</div>
<script>
const DATA=__DATA__;
const T=DATA.teams,C=DATA.cal,P=DATA.players||{},GAMES=DATA.games||[],RES=DATA.results||[];
const PR=DATA.prop_results||[],PRC=DATA.prop_record||{};
const PROPSTATS={QB:['pass_yds','rush_yds'],RB:['rush_yds','rec_yds','receptions'],WR:['rec_yds','receptions'],TE:['rec_yds','receptions']};
const PSHORT=['rec_yds','receptions','rush_yds','pass_yds'],PSLBL={rec_yds:'Rec Yds',receptions:'Rec',rush_yds:'Rush Yds',pass_yds:'Pass Yds'};
const PSFULL={rec_yds:'Receiving Yards',receptions:'Receptions (catches)',rush_yds:'Rushing Yards',pass_yds:'Passing Yards'};
const view=document.getElementById('view'),gpage=document.getElementById('gamepage'),hintEl=document.getElementById('hint');
function tier(r){return r<=6?'elite':r<=13?'good':r<=20?'average':'weak';}
function project(a,h,adjH,adjA){adjH=adjH||0;adjA=adjA||0;const H=T[h],A=T[a];
  const sd=(H.off+H.def)-(A.off+A.def)+adjH-adjA,comb=(H.off-A.def)+(A.off-H.def)+adjH+adjA;
  return {margin:C.B0+C.B1*sd,total:C.TB0+C.TB1*comb};}
function lineStr(m,h,a){const f=m>0?h:a;return T[f].abbr+' -'+Math.abs(m).toFixed(1);}
function erf(x){const t=1/(1+0.3275911*Math.abs(x));const y=1-(((((1.061405429*t-1.453152027)*t+1.421413741)*t-0.284496736)*t+0.254829592)*t)*Math.exp(-x*x);return x>=0?y:-y;}
function normCdf(x,mu,sd){return sd<=0?(x>=mu?1:0):0.5*(1+erf((x-mu)/(sd*Math.SQRT2)));}
function projStat(v){const n=v.length;let sw=0,m=0;for(let i=0;i<n;i++){const w=0.5+0.5*(n>1?i/(n-1):1);sw+=w;m+=v[i]*w;}m/=sw;const mean=v.reduce((a,b)=>a+b,0)/n;const sd=Math.sqrt(v.reduce((a,b)=>a+(b-mean)*(b-mean),0)/(n>1?n-1:1));return {proj:m,sd};}
function wxText(c){if(c===0)return 'Clear';if([1,2].includes(c))return 'Partly cloudy';if(c===3)return 'Overcast';if([45,48].includes(c))return 'Fog';if([51,53,55,56,57].includes(c))return 'Drizzle';if([61,63,65,66,67,80,81,82].includes(c))return 'Rain';if([71,73,75,77,85,86].includes(c))return 'Snow';if([95,96,99].includes(c))return 'Thunderstorm';return 'Cloudy';}
function fmtKick(d,t){const dt=new Date(d+'T12:00:00');let s=dt.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});if(!t)return s;let p=t.split(':').map(Number),h=p[0],m=p[1];const ap=h>=12?'PM':'AM';h=h%12;if(h===0)h=12;return s+' · '+h+':'+String(m).padStart(2,'0')+' '+ap+' ET';}
function slot(d,t){const wd=new Date(d+'T12:00:00').toLocaleDateString('en-US',{weekday:'long'});const h=t?parseInt(t.split(':')[0]):13;
  if(wd==='Thursday')return['Thursday night',1];if(wd==='Friday'||wd==='Saturday')return[wd,2];
  if(wd==='Monday')return['Monday night',6];
  if(wd==='Sunday'){if(h<15)return['Sunday — early afternoon',3];if(h<19)return['Sunday — late afternoon',4];return['Sunday night',5];}
  return[wd,7];}
function barFill(v,s){const p=Math.max(-1,Math.min(1,v/s)),w=Math.abs(p)*50,l=p>=0?50:50-w,c=p>=0?'var(--up)':'var(--down)';return '<div class="fill" style="left:'+l+'%;width:'+w+'%;background:'+c+'"></div>';}
function americanFromProb(pr){if(pr<=0.02)return '+2500';if(pr>=0.98)return '-5000';let ml=pr>=0.5?-100*pr/(1-pr):100*(1-pr)/pr;ml=Math.round(ml/5)*5;return (ml>0?'+':'')+ml;}
const injCls={'Out':'out','Doubtful':'dbt','Questionable':'q'},injShort={'Out':'OUT','Doubtful':'DBT','Questionable':'Q'};
function nrm(s){return s.toLowerCase().replace(/\./g,'').replace(/'/g,'').replace(/-/g,' ').replace(/\b(jr|sr|ii|iii|iv)\b/g,'').replace(/\s+/g,' ').trim();}
const pkeyByNT={};Object.keys(P).forEach(k=>{pkeyByNT[nrm(P[k].name)+'|'+P[k].team]=k;});
const STATLABEL={pass_yds:'Passing yards',rush_yds:'Rushing yards',rec_yds:'Receiving yards',receptions:'Receptions'};

const matchWeeks=[...new Set(GAMES.map(g=>g.week))].sort((a,b)=>a-b);
let mWeek=matchWeeks[0];
const resWeeks=[...new Set(RES.map(r=>r.week))].sort((a,b)=>b-a);
let rMode='week', rWeek=resWeeks[0];
const propWeeks=[...new Set(PR.map(e=>e.w))].sort((a,b)=>b-a);
let pMode='week', pWeek=propWeeks[0];
let plWeek=null;
let propNav='home', propPick=null;

function bkCell(o,h,a){return o?'<div class="bkcell"><div class="sp">'+lineStr(o.s,h,a)+'</div><div class="ou">o/u '+o.t.toFixed(1)+'</div></div>':'<div class="bkcell"><div class="sp" style="color:var(--muted)">—</div><div class="ou">—</div></div>';}
function vegasObj(g){return g.spread!=null?{s:g.spread,t:g.total}:null;}
function matchups(){
  let h='<div class="selbar"><button class="arw" id="mprev">‹</button><div class="selwrap"><select class="sel" id="msel">'+matchWeeks.map(w=>'<option value="'+w+'" '+(w===mWeek?'selected':'')+'>Week '+w+'</option>').join('')+'</select></div><button class="arw" id="mnext">›</button></div>';
  const gs=GAMES.filter(g=>g.week===mWeek).map(g=>{const sl=slot(g.date,g.time);return Object.assign({},g,{sl:sl[0],ord:sl[1]});}).sort((x,y)=>x.ord-y.ord);
  const groups={},order=[];gs.forEach(g=>{if(!groups[g.sl]){groups[g.sl]=[];order.push(g.sl);}groups[g.sl].push(g);});
  h+=order.map(sl=>'<div class="daylabel">'+sl+'</div><div class="board"><div class="cols colhdr"><div></div><div class="bk">VEGAS</div><div class="bk">DK</div><div class="bk fd">FANDUEL</div><div class="bk model">OUR MODEL</div><div></div></div>'+
    groups[sl].map(g=>{const qa=g.qbadj||{};const p=project(g.away,g.home,qa.home||0,qa.away||0);
      return '<div class="cols game" onclick="showGame(\''+g.away+'\',\''+g.home+'\','+g.week+')">'+
        '<div><div class="gmu">'+g.away+' @ '+g.home+'</div><div class="gkick">'+fmtKick(g.date,g.time)+'</div></div>'+
        bkCell(vegasObj(g),g.home,g.away)+bkCell(g.dk,g.home,g.away)+bkCell(g.fd,g.home,g.away)+
        '<div class="mcell"><div class="sp">'+lineStr(p.margin,g.home,g.away)+'</div><div class="ou">o/u '+p.total.toFixed(1)+'</div></div>'+
        '<div class="chev">▾</div></div>';}).join('')+'</div>').join('');
  view.innerHTML=h;hintEl.textContent='Four columns per game — three books plus our model. Tap a game for the full breakdown.';
  document.getElementById('msel').onchange=e=>{mWeek=+e.target.value;matchups();};
  document.getElementById('mprev').onclick=()=>{const i=matchWeeks.indexOf(mWeek);if(i>0){mWeek=matchWeeks[i-1];matchups();}};
  document.getElementById('mnext').onclick=()=>{const i=matchWeeks.indexOf(mWeek);if(i<matchWeeks.length-1){mWeek=matchWeeks[i+1];matchups();}};
  document.getElementById('mprev').disabled=matchWeeks.indexOf(mWeek)<=0;
  document.getElementById('mnext').disabled=matchWeeks.indexOf(mWeek)>=matchWeeks.length-1;
}

function recOf(list,key){let w=0,l=0,p=0;list.forEach(r=>{if(r[key]==='W')w++;else if(r[key]==='L')l++;else if(r[key]==='P')p++;});const n=w+l;return {w,l,p,wr:n?Math.round(w/n*1000)/10:0};}
function recCards(list){
  const wl=o=>o.w+'-'+o.l+(o.p?('-'+o.p):'');
  const card=(lbl,cls,sp,tt,building)=>'<div class="rccard"><div class="rclbl '+cls+'">'+lbl+'</div>'+(building?'<div class="rcbuild">building — fills in going forward</div>':'<div class="rcline"><span>Spread</span><b>'+wl(sp)+'</b><span class="rcp">'+sp.wr+'%</span></div><div class="rcline"><span>Total</span><b>'+wl(tt)+'</b><span class="rcp">'+tt.wr+'%</span></div>')+'</div>';
  return '<div class="rccards">'+card('OUR MODEL','model',recOf(list,'ats'),recOf(list,'ou'),false)+card('VEGAS','',recOf(list,'vats'),recOf(list,'vou'),false)+card('DRAFTKINGS','',null,null,true)+card('FANDUEL','fdl',null,null,true)+'</div>';
}
function results(){
  let h='<div class="selbar"><button class="seasonbtn '+(rMode==='season'?'on':'')+'" id="seasonbtn">Full season</button><div class="vdiv"></div><button class="arw" id="rprev">‹</button><div class="selwrap"><select class="sel" id="rsel">'+resWeeks.map(w=>'<option value="'+w+'" '+(w===rWeek?'selected':'')+'>Week '+w+'</option>').join('')+'</select></div><button class="arw" id="rnext">›</button></div>';
  if(rMode==='season'){
    h+=recCards(RES);
    h+='<div class="rec-note">Each pick graded <b>against our own number</b>: the spread hits if our pick covers the margin we projected, the total hits if the game landed <b>under</b> our projected total. Vegas is graded the same way. DraftKings &amp; FanDuel build up going forward.</div>';
    h+='<div class="sec">WEEK BY WEEK</div><div class="trend"><div class="trow head"><div>Week</div><div>Spread</div><div>Total</div></div>'+
      resWeeks.slice().sort((a,b)=>a-b).map(w=>{const L=RES.filter(r=>r.week===w);const s=recOf(L,'ats'),t=recOf(L,'ou');
        return '<div class="trow" onclick="jumpWeek('+w+')"><div class="twk">W'+w+'</div><div class="tcell"><span class="rec">'+s.w+'-'+s.l+(s.p?('-'+s.p):'')+'</span><span class="pct">'+s.wr+'%</span></div><div class="tcell"><span class="rec">'+t.w+'-'+t.l+'</span><span class="pct">'+t.wr+'%</span></div></div>';}).join('')+'</div>';
  }else{
    const L=RES.filter(r=>r.week===rWeek);h+=recCards(L);
    h+='<div class="sec">GAMES — WEEK '+rWeek+'</div><div class="board">'+
      L.map(r=>{const bc=x=>x==='W'?'hit':x==='L'?'miss':'push',bs=x=>x==='W'?'✓':x==='L'?'✗':'P';
        return '<div class="grow" onclick="showGame(\''+r.away+'\',\''+r.home+'\','+r.week+')">'+
          '<div class="gmu">'+r.away+' @ '+r.home+'</div>'+
          '<div class="gfin">'+r.away+' <span class="'+(r.ascore>r.hscore?'w':'')+'">'+r.ascore+'</span>–<span class="'+(r.hscore>r.ascore?'w':'')+'">'+r.hscore+'</span> '+r.home+'</div>'+
          '<div class="gb '+bc(r.ats)+'">SPREAD '+bs(r.ats)+'</div><div class="gb '+bc(r.ou)+'">TOTAL '+bs(r.ou)+' ▾</div></div>';}).join('')+'</div>';
  }
  view.innerHTML=h;hintEl.textContent=rMode==='season'?'Season totals up top · week-by-week trend below (click a week to open it).':'Records for this week up top · tap a game for the full breakdown.';
  document.getElementById('seasonbtn').onclick=()=>{rMode='season';results();};
  document.getElementById('rsel').onchange=e=>{rMode='week';rWeek=+e.target.value;results();};
  document.getElementById('rprev').onclick=()=>{rMode='week';const i=resWeeks.indexOf(rWeek);if(i<resWeeks.length-1){rWeek=resWeeks[i+1];results();}};
  document.getElementById('rnext').onclick=()=>{rMode='week';const i=resWeeks.indexOf(rWeek);if(i>0){rWeek=resWeeks[i-1];results();}};
}
function jumpWeek(w){rMode='week';rWeek=w;results();}

function propRec(list,k){let w=0,l=0,p=0;list.forEach(e=>{if(e.s[k]){const r=e.s[k][2];if(r==='W')w++;else if(r==='L')l++;else p++;}});const n=w+l;return {w,l,p,wr:n?Math.round(w/n*1000)/10:0};}
function props(){
  let h='<div class="selbar"><button class="seasonbtn '+(pMode==='season'?'on':'')+'" id="pseasonbtn">Full season</button><div class="vdiv"></div><button class="arw" id="pprev">‹</button><div class="selwrap"><select class="sel" id="psel">'+propWeeks.map(w=>'<option value="'+w+'" '+(w===pWeek?'selected':'')+'>Week '+w+'</option>').join('')+'</select></div><button class="arw" id="pnext">›</button></div>';
  const list=pMode==='season'?PR:PR.filter(e=>e.w===pWeek);
  const card=k=>{const r=propRec(list,k);return '<div class="rccard"><div class="rclbl model">'+PSFULL[k].toUpperCase()+'</div><div class="rcline"><span>Over / Under</span><b>'+r.w+'-'+r.l+'</b><span class="rcp">'+r.wr+'%</span></div><div class="rcline"><span style="font-size:11px">over our number = hit</span></div></div>';};
  h+='<div class="rccards">'+PSHORT.map(card).join('')+'</div>';
  h+='<div class="rec-note">Each player prop graded <b>against our own projection</b> — over our number is a hit, under is a miss. Projections come from the player\'s recent games. <b>Props are the highest-variance thing here</b>, so these swing hard week to week — read them over a large sample. DraftKings/FanDuel prop lines aren\'t graded (that needs a paid feed); this is our number vs the real result.</div>';
  if(pMode==='season'){
    h+='<div class="sec">WEEK BY WEEK — hit rate (all props)</div><div class="trend"><div class="trow head"><div>Week</div><div>Over / Under</div><div>Hit rate</div></div>'+
      propWeeks.slice().sort((a,b)=>a-b).map(w=>{const L=PR.filter(e=>e.w===w);let ww=0,ll=0;L.forEach(e=>PSHORT.forEach(k=>{if(e.s[k]){if(e.s[k][2]==='W')ww++;else if(e.s[k][2]==='L')ll++;}}));const n=ww+ll;return '<div class="trow" onclick="jumpProp('+w+')"><div class="twk">W'+w+'</div><div class="tcell"><span class="rec">'+ww+'-'+ll+'</span></div><div class="tcell"><span class="rec">'+(n?Math.round(ww/n*1000)/10:0)+'%</span></div></div>';}).join('')+'</div>';
  }else{
    const wlist=PR.filter(e=>e.w===pWeek);
    const cell=c=>c?'<div class="pcell"><div class="n"><span style="color:var(--amber)">'+c[0]+'</span> <span style="color:var(--muted)">→</span> <b>'+c[1]+'</b></div><div class="r" style="color:'+(c[2]==='W'?'var(--up)':c[2]==='L'?'var(--down)':'var(--muted)')+'">'+(c[2]==='W'?'✓ over':c[2]==='P'?'push':'✗ under')+'</div></div>':'<div class="pcell"><div class="n" style="color:#3a4453">—</div></div>';
    const renderList=(rows,title)=>{
      const sorted=rows.slice().sort((a,b)=>{const la=a.p.split(' ').slice(-1)[0].toLowerCase(),lb=b.p.split(' ').slice(-1)[0].toLowerCase();return la<lb?-1:la>lb?1:0;});
      return '<div class="sec">'+title+' — WEEK '+pWeek+' · '+sorted.length+' players (alphabetical by last name)</div>'+
        '<div class="rec-note" style="margin:0 0 10px">Each cell: <b style="color:var(--amber)">our projection</b> → <b>actual result</b>. Green ✓ = went <b>over</b> our number (hit); red ✗ = under. &nbsp; <b>Rec Yds</b> = receiving yards · <b>Rec</b> = receptions (catches) · <b>Rush Yds</b> = rushing yards · <b>Pass Yds</b> = passing yards.</div>'+
        '<div class="board"><div class="plr head"><div>Player</div>'+PSHORT.map(k=>'<div class="pcell">'+PSLBL[k]+'</div>').join('')+'</div>'+
        sorted.map(e=>{const key=pkeyByNT[nrm(e.p)+'|'+e.tm];const nm=key?'<span class="lnk" style="cursor:pointer" onclick="playerDetail(\''+key.replace(/'/g,"\\'")+'\')">'+e.p+'</span>':e.p;
          return '<div class="plr"><div><b>'+nm+'</b> <span style="color:var(--muted);font-size:11px">'+e.pos+'·'+e.tm+'</span></div>'+PSHORT.map(k=>cell(e.s[k])).join('')+'</div>';}).join('')+'</div>';};
    if(propNav==='home'){
      h+='<div class="twobtn"><div class="bigbtn" onclick="propGo(\'team\')"><div class="t">PICK A TEAM</div><div class="s">browse every team\'s players</div></div><div class="bigbtn" onclick="propGo(\'pos\')"><div class="t">PICK A POSITION</div><div class="s">QB · RB · WR · TE</div></div></div>';
    }else if(propNav==='team'){
      const teams=[...new Set(wlist.map(e=>e.tm))].sort();const cnt={};teams.forEach(t=>cnt[t]=wlist.filter(e=>e.tm===t).length);
      h+='<div class="back" onclick="propGo(\'home\')">‹ Back</div><div class="sec">PICK A TEAM</div><div class="pgrid">'+
        teams.map(t=>'<div class="gbtn '+(propPick===t?'on':'')+'" onclick="propSetPick(\''+t+'\')">'+t+'<span class="sub">'+cnt[t]+'</span></div>').join('')+'</div>';
      h+=(propPick&&teams.includes(propPick))?renderList(wlist.filter(e=>e.tm===propPick),propPick):'<div class="none">Pick a team above to see its players.</div>';
    }else if(propNav==='pos'){
      const poss=['QB','RB','WR','TE'];const cnt={};poss.forEach(p=>cnt[p]=wlist.filter(e=>e.pos===p).length);
      h+='<div class="back" onclick="propGo(\'home\')">‹ Back</div><div class="sec">PICK A POSITION</div><div class="pgrid">'+
        poss.map(p=>'<div class="gbtn '+(propPick===p?'on':'')+'" onclick="propSetPick(\''+p+'\')">'+p+'<span class="sub">'+cnt[p]+'</span></div>').join('')+'</div>';
      h+=(propPick&&poss.includes(propPick))?renderList(wlist.filter(e=>e.pos===propPick),propPick):'<div class="none">Pick a position above to see its players.</div>';
    }
  }
  view.innerHTML=h;hintEl.textContent=pMode==='season'?'Season prop hit-rate up top · week-by-week below.':'Each player: actual vs our projection, over/under. Tap a name for their projections & why.';
  document.getElementById('pseasonbtn').onclick=()=>{pMode='season';props();};
  document.getElementById('psel').onchange=e=>{pMode='week';pWeek=+e.target.value;props();};
  document.getElementById('pprev').onclick=()=>{pMode='week';const i=propWeeks.indexOf(pWeek);if(i<propWeeks.length-1){pWeek=propWeeks[i+1];props();}};
  document.getElementById('pnext').onclick=()=>{pMode='week';const i=propWeeks.indexOf(pWeek);if(i>0){pWeek=propWeeks[i-1];props();}};
}
function jumpProp(w){pMode='week';pWeek=w;props();}
function propGo(m){propNav=m;propPick=null;props();}
function propSetPick(v){propPick=v;props();}

function teamsList(){
  const abbrs=Object.keys(T).filter(a=>a!=='LA').sort((x,y)=>T[x].ovr_rank-T[y].ovr_rank);
  let h='<input class="search" id="tsearch" placeholder="Search a team…"><div class="board" id="tlist">'+
    abbrs.map(ab=>{const t=T[ab];const w=(t.log||[]).filter(g=>g.res==='W').length,l=(t.log||[]).filter(g=>g.res==='L').length;
      return '<div class="trrow" data-n="'+(t.city+' '+t.name).toLowerCase()+'" onclick="teamDetail(\''+ab+'\')"><div class="trk">'+t.ovr_rank+'</div><div class="tnm">'+t.city+' '+t.name+'</div><div class="trec">'+w+'-'+l+'</div></div>';}).join('')+'</div>';
  view.innerHTML=h;hintEl.textContent='Search or scroll the power ranks. Tap a team for its profile, game line, injuries, and schedule.';
  document.getElementById('tsearch').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('#tlist .trrow').forEach(r=>r.style.display=r.dataset.n.includes(q)?'':'none');});
}
function teamDetail(ab){
  const t=T[ab];const ng=t.next;let gl='';
  if(ng){const home=ng.home?ab:ng.opp,away=ng.home?ng.opp:ab;const p=project(away,home);const pH=1-normCdf(0,p.margin,13.2),pA=1-pH;
    const s=ng.spread,tot=ng.total;
    const spc=side=>s==null?'<div class="bkcell"><div class="sp">—</div></div>':(function(){const v=side==='home'?-s:s;return '<div class="bkcell"><div class="sp">'+(v>0?'+':'')+v.toFixed(1)+'</div><div class="ou">−110</div></div>';})();
    const toc=ou=>tot==null?'<div class="bkcell"><div class="sp">—</div></div>':'<div class="bkcell"><div class="sp">'+ou+' '+tot.toFixed(1)+'</div><div class="ou">−110</div></div>';
    gl='<div class="sec">NEXT GAME · WEEK '+ng.week+' · '+fmtKick(ng.date,ng.time)+'</div><div class="board"><div class="cols" style="grid-template-columns:1fr repeat(3,1fr);padding:6px 14px"><div class="colhdr" style="border:none;padding:2px 0"></div><div class="colhdr bk" style="border:none;padding:2px 0">Spread</div><div class="colhdr bk" style="border:none;padding:2px 0">Total</div><div class="colhdr bk" style="border:none;padding:2px 0">Moneyline</div></div>'+
      '<div class="cols game" style="grid-template-columns:1fr repeat(3,1fr);cursor:default"><div class="gmu">'+away+'</div>'+spc('away')+toc('O')+'<div class="bkcell"><div class="sp" style="color:var(--up)">'+americanFromProb(pA)+'</div></div></div>'+
      '<div class="cols game" style="grid-template-columns:1fr repeat(3,1fr);cursor:default"><div class="gmu">'+home+'</div>'+spc('home')+toc('U')+'<div class="bkcell"><div class="sp" style="color:var(--up)">'+americanFromProb(pH)+'</div></div></div></div>'+
      '<div class="none" style="padding:8px 0;font-size:11.5px">Spread &amp; total: consensus line. Moneyline is model-implied (a fair price vs the book\'s number).</div>';}
  const inj=(t.inj||[]);
  const injH=inj.length?inj.map(x=>{const key=pkeyByNT[nrm(x.name)+'|'+ab];const nm=key?'<span class="injn lnk" onclick="playerDetail(\''+key.replace(/'/g,"\\'")+'\')">'+x.name+'</span>':'<span class="injn">'+x.name+'</span>';return '<div class="injrow"><span class="injs '+(injCls[x.status]||'')+'">'+(injShort[x.status]||x.status)+'</span><span class="injp">'+x.pos+'</span>'+nm+(x.note?'<span class="injnote">'+x.note+'</span>':'')+'</div>';}).join(''):'<div class="none">No injuries on this week\'s report.</div>';
  const sched=(t.sched||[]).map(g=>{const right=g.played?'<span class="wl '+g.res+'">'+g.res+'</span> '+g.pf+'-'+g.pa:'<span class="kick">'+fmtKick(g.date,g.time)+'</span>';const isN=(!g.played)&&(t.next&&t.next.week===g.week);return '<tr class="schrow '+(isN?'next':'')+'"><td>'+g.week+'</td><td>'+(g.home?'vs':'@')+' '+g.opp+'</td><td>'+right+'</td></tr>';}).join('');
  gpage.innerHTML='<div class="back" onclick="showTab(\'teams\')">‹ Back to teams</div>'+
    '<div class="gp-head"><div class="gp-mu">'+t.city+' '+t.name+'</div><div class="gp-kick">Power rank #'+t.ovr_rank+' of 32 · '+DATA.as_of+'</div></div>'+
    gl+
    '<div class="sec">RATINGS</div><div class="card tm">'+
      '<div class="stat"><div class="top"><span class="lab">Offense <span class="tier">#'+t.off_rank+' '+tier(t.off_rank)+'</span></span><span class="num">'+(t.off>=0?'+':'')+t.off.toFixed(3)+' EPA/play</span></div><div class="bar"><div class="mid"></div>'+barFill(t.off,0.15)+'</div></div>'+
      '<div class="stat"><div class="top"><span class="lab">Defense <span class="tier">#'+t.def_rank+' '+tier(t.def_rank)+'</span></span><span class="num">'+(t.def>=0?'+':'')+t.def.toFixed(3)+' EPA saved</span></div><div class="bar"><div class="mid"></div>'+barFill(t.def,0.15)+'</div></div>'+
      '<div class="stat"><div class="top"><span class="lab">Last 4 — offense</span><span class="num">'+(t.form_off>=0?'+':'')+t.form_off.toFixed(3)+'</span></div><div class="bar"><div class="mid"></div>'+barFill(t.form_off,0.2)+'</div></div></div>'+
    '<div class="sec">INJURY REPORT'+(DATA.inj_week?' — WEEK '+DATA.inj_week:'')+'</div><div class="card">'+injH+'</div>'+
    '<div class="sec">SEASON SCHEDULE</div><div class="card"><table class="logtbl"><thead><tr><th>Wk</th><th>Matchup</th><th>Result / Kickoff</th></tr></thead><tbody>'+(sched||'<tr><td colspan=3>—</td></tr>')+'</tbody></table></div>';
  goPage();
}

function playersList(){
  const keys=Object.keys(P).sort((a,b)=>P[a].name.localeCompare(P[b].name));
  const badge=inj=>inj?'<span class="pst '+(inj.status==='Out'?'o':'q')+'">'+inj.status+'</span>':'<span class="pst a">Active</span>';
  let h='<input class="search" id="psearch" placeholder="Search a player…"><div class="board" id="plist">'+
    keys.map(k=>{const pl=P[k];return '<div class="prow" data-n="'+pl.name.toLowerCase()+'" onclick="playerDetail(\''+k.replace(/'/g,"\\'")+'\')"><div><span class="pnm">'+pl.name+'</span>'+badge(pl.inj)+'</div><div class="ppos">'+pl.pos+' · '+pl.team+'</div></div>';}).join('')+'</div>';
  view.innerHTML=h;hintEl.textContent='Search a player. Tap to see prop projections — type the book\'s line to get the over/under read.';
  document.getElementById('psearch').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('#plist .prow').forEach(r=>r.style.display=r.dataset.n.includes(q)?'':'none');});
}
function playerDetail(key,wk){
  const pl=P[key];if(!pl)return;
  const badge=pl.inj?'<span class="pst '+(pl.inj.status==='Out'?'o':'q')+'">'+pl.inj.status+(pl.inj.note?' — '+pl.inj.note:'')+'</span>':'<span class="pst a">Active — no injury reported</span>';
  const myres=PR.filter(e=>e.p===pl.name&&e.tm===pl.team);
  const playedW=[...new Set(myres.map(e=>e.w))].sort((a,b)=>a-b);
  const teamNext=(T[pl.team]&&T[pl.team].next)?T[pl.team].next.week:null;
  const weeks=playedW.slice();if(teamNext&&!weeks.includes(teamNext))weeks.push(teamNext);
  if(!weeks.length)weeks.push(1);
  const upcoming=teamNext&&!playedW.includes(teamNext)?teamNext:null;
  let sel=wk!=null?wk:(plWeek!=null&&weeks.includes(plWeek)?plWeek:weeks[weeks.length-1]);
  plWeek=sel;
  const stats=(PROPSTATS[pl.pos]||[]).filter(s=>pl.stats[s]);
  let blocks=stats.map(s=>{
    const played=myres.find(e=>e.w===sel&&e.s[s]);
    if(played){const c=played.s[s];const cls=c[2]==='W'?'var(--up)':c[2]==='L'?'var(--down)':'var(--muted)';const lbl=c[2]==='W'?'✓ OVER our number':c[2]==='P'?'PUSH':'✗ under our number';
      return '<div class="propstat"><div class="ps-head"><span class="ps-name">'+STATLABEL[s]+'</span></div><div class="ps-calc" style="gap:20px"><div><div style="font-size:11px;color:var(--muted);font-weight:700">OUR PROJECTION</div><div style="font-size:20px;font-weight:900;color:var(--amber)">'+c[0]+'</div></div><div><div style="font-size:11px;color:var(--muted);font-weight:700">ACTUAL</div><div style="font-size:20px;font-weight:900">'+c[1]+'</div></div><div class="ps-lean" style="color:'+cls+';border-color:'+cls+'">'+lbl+'</div></div></div>';}
    else{const pr=projStat(pl.stats[s]);
      return '<div class="propstat"><div class="ps-head"><span class="ps-name">'+STATLABEL[s]+'</span></div><div class="ps-calc" style="gap:20px"><div><div style="font-size:11px;color:var(--muted);font-weight:700">OUR PROJECTION</div><div style="font-size:20px;font-weight:900;color:var(--amber)">'+pr.proj.toFixed(1)+'</div></div><div><div style="font-size:11px;color:var(--muted);font-weight:700">ACTUAL</div><div style="font-size:15px;font-weight:700;color:var(--muted)">not played yet</div></div></div></div>';}
  }).join('');
  const wsel='<div class="selbar" style="margin:14px 0"><button class="arw" id="plprev">‹</button><div class="selwrap"><select class="sel" id="plsel">'+weeks.slice().sort((a,b)=>b-a).map(w=>'<option value="'+w+'" '+(w===sel?'selected':'')+'>Week '+w+(w===upcoming?' (upcoming)':'')+'</option>').join('')+'</select></div><button class="arw" id="plnext">›</button></div>';
  let why='';const ms=stats[0];
  if(ms&&sel===upcoming){const v=pl.stats[ms];const pr=projStat(v);const avg=v.reduce((x,y)=>x+y,0)/v.length;const last=pl.name.split(' ').slice(-1)[0];
    why='<div class="take" style="margin-bottom:14px"><div class="takewhy">This week we project <b style="color:var(--amber)">'+pr.proj.toFixed(1)+' '+STATLABEL[ms].toLowerCase()+'</b> for '+last+' — he\'s averaged '+avg.toFixed(1)+' over his last '+v.length+' games, weighted recent. '+(pl.inj?'<b style="color:var(--amber)">On the injury report ('+pl.inj.status+').</b> ':'')+'<span style="color:var(--muted)">"Over" means the actual beats our number.</span></div></div>';}
  gpage.innerHTML='<div class="back" onclick="showTab(\'players\')">‹ Back to players</div>'+
    '<div class="gp-head"><div class="gp-mu">'+pl.name+'</div><div class="gp-kick">'+pl.pos+' · '+pl.team+'</div><div style="margin-top:8px">'+badge+'</div></div>'+
    wsel+why+blocks+
    '<div class="none" style="line-height:1.5">Pick a week to see our projection vs the actual result. Book prop lines (Vegas/DraftKings/FanDuel) aren\'t shown — player props aren\'t in the free odds feed (that needs a paid props feed). Props are high-variance; judge over a large sample.</div>';
  goPage();
  document.getElementById('plsel').onchange=e=>playerDetail(key,+e.target.value);
  document.getElementById('plprev').onclick=()=>{const i=weeks.indexOf(sel);if(i>0)playerDetail(key,weeks[i-1]);};
  document.getElementById('plnext').onclick=()=>{const i=weeks.indexOf(sel);if(i<weeks.length-1)playerDetail(key,weeks[i+1]);};
  document.getElementById('plprev').disabled=weeks.indexOf(sel)<=0;
  document.getElementById('plnext').disabled=weeks.indexOf(sel)>=weeks.length-1;
}

function injBlock(ab){const inj=(T[ab].inj||[]).slice(0,6);if(!inj.length)return '<div class="none" style="padding:6px 0">No injuries reported.</div>';
  return inj.map(x=>{const key=pkeyByNT[nrm(x.name)+'|'+ab];const nm=key?'<span class="injn lnk" onclick="playerDetail(\''+key.replace(/'/g,"\\'")+'\')">'+x.name+'</span>':'<span class="injn">'+x.name+'</span>';return '<div class="injrow"><span class="injs '+(injCls[x.status]||'')+'">'+(injShort[x.status]||x.status)+'</span><span class="injp">'+x.pos+'</span>'+nm+(x.note?'<span class="injnote">'+x.note+'</span>':'')+'</div>';}).join('');}
function teamCardHTML(ab,side){const t=T[ab];return '<div class="card tm"><h4><span class="lnk" onclick="teamDetail(\''+ab+'\')">'+t.city+' '+t.name+'</span> <span style="color:var(--muted);font-size:11px">'+side+'</span></h4><div class="rk">Power rank #'+t.ovr_rank+' of 32</div>'+
    '<div class="stat"><div class="top"><span class="lab">Offense <span class="tier">#'+t.off_rank+' '+tier(t.off_rank)+'</span></span><span class="num">'+(t.off>=0?'+':'')+t.off.toFixed(3)+'</span></div><div class="bar"><div class="mid"></div>'+barFill(t.off,0.15)+'</div></div>'+
    '<div class="stat"><div class="top"><span class="lab">Defense <span class="tier">#'+t.def_rank+' '+tier(t.def_rank)+'</span></span><span class="num">'+(t.def>=0?'+':'')+t.def.toFixed(3)+'</span></div><div class="bar"><div class="mid"></div>'+barFill(t.def,0.15)+'</div></div></div>';}
function whyText(a,h,p){const H=T[h],A=T[a];const f=p.margin>0?h:a;return 'Our model has the '+H.city+' '+H.name+' at #'+H.ovr_rank+' overall ('+tier(H.off_rank)+' offense, '+tier(H.def_rank)+' defense) and the '+A.city+' '+A.name+' at #'+A.ovr_rank+' ('+tier(A.off_rank)+' offense, '+tier(A.def_rank)+' defense). After home field, we make it '+T[f].name+' by '+Math.abs(p.margin).toFixed(1)+'.';}
function projTable(a,h){
  const rows=Object.keys(P).filter(k=>P[k].team===a||P[k].team===h).map(k=>({key:k,pl:P[k]})).sort((x,y)=>x.pl.team<y.pl.team?-1:x.pl.team>y.pl.team?1:(x.pl.name<y.pl.name?-1:1));
  if(!rows.length)return '';
  const order=['rec_yds','receptions','rush_yds','pass_yds'];
  const body=rows.map(o=>{const pl=o.pl;const st=PROPSTATS[pl.pos]||[];
    const cell=k=>(st.includes(k)&&pl.stats[k])?'<div class="pjc amber">'+projStat(pl.stats[k]).proj.toFixed(1)+'</div>':'<div class="pjc dash">—</div>';
    return '<div class="projtbl"><div><b class="lnk" style="cursor:pointer" onclick="playerDetail(\''+o.key.replace(/'/g,"\\'")+'\')">'+pl.name+'</b> <span style="color:var(--muted);font-size:11px">'+pl.pos+'·'+pl.team+'</span></div>'+order.map(cell).join('')+'</div>';}).join('');
  return '<div class="sec">PLAYER PROJECTIONS — our numbers</div><div class="board"><div class="projtbl head"><div>Player</div><div class="pjc">Rec Yds</div><div class="pjc">Rec</div><div class="pjc">Rush Yds</div><div class="pjc">Pass Yds</div></div>'+body+'</div><div class="none" style="font-size:11.5px">Our projection for each notable player (from recent form). Tap a name for the full read and the "why"; bet over/under vs the book\'s posted line.</div>';
}
function showGame(a,h,week){
  const r=RES.find(x=>x.away===a&&x.home===h&&x.week===week);
  const g=GAMES.find(x=>x.away===a&&x.home===h&&x.week===week);
  const qa=(g&&g.qbadj)||{};const p=project(a,h,qa.home||0,qa.away||0);
  const vegas=r?{s:r.cs,t:r.ct}:(g&&g.spread!=null?{s:g.spread,t:g.total}:null);
  const dk=g?g.dk:null,fd=g?g.fd:null;
  const lc=(lbl,cls,o)=>'<div class="lc '+cls+'">'+(o?'<div class="l">'+lbl+'</div><div class="sp">'+lineStr(o.s,h,a)+'</div><div class="ou">o/u '+o.t.toFixed(1)+'</div>':'<div class="l">'+lbl+'</div><div class="sp" style="color:var(--muted);font-size:15px">—</div><div class="ou">not logged</div>')+'</div>';
  let head='<div class="gp-mu"><span class="lnk" onclick="teamDetail(\''+a+'\')">'+T[a].city+' '+T[a].name+'</span> <span style="color:var(--muted);font-weight:600">at</span> <span class="lnk" onclick="teamDetail(\''+h+'\')">'+T[h].city+' '+T[h].name+'</span></div>';
  head+='<div class="gp-kick">'+(g?fmtKick(g.date,g.time):('Week '+week))+'</div>';
  let box='';
  if(r){head+='<div class="gp-fscore">'+a+' <span class="'+(r.ascore>r.hscore?'w':'')+'">'+r.ascore+'</span> — <span class="'+(r.hscore>r.ascore?'w':'')+'">'+r.hscore+'</span> '+h+'</div>';
    const bc=x=>x==='W'?'hit':x==='L'?'miss':'push';
    head+='<div class="gp-verdict"><span class="gb '+bc(r.ats)+'">SPREAD '+(r.ats==='W'?'✓ HIT':r.ats==='P'?'PUSH':'✗ MISS')+'</span><span class="gb '+bc(r.ou)+'">TOTAL '+(r.ou==='W'?'✓ HIT':r.ou==='P'?'PUSH':'✗ MISS')+'</span></div>';
    if(r.aq&&r.aq.length)box='<div class="sec">BOX SCORE</div><div class="card"><table class="boxt"><thead><tr><th>Team</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Final</th></tr></thead><tbody><tr><td>'+a+'</td>'+r.aq.map(x=>'<td>'+x+'</td>').join('')+'<td class="qtot">'+r.ascore+'</td></tr><tr><td>'+h+'</td>'+r.hq.map(x=>'<td>'+x+'</td>').join('')+'<td class="qtot">'+r.hscore+'</td></tr></tbody></table></div>';
  }
  const modelLine=r?{s:r.pm,t:r.ptot}:{s:p.margin,t:p.total};
  const lines='<div class="sec">THE LINE — us vs the books</div><div class="lines4">'+lc('VEGAS','',vegas)+lc('DRAFTKINGS','',dk)+lc('FANDUEL','fd',fd)+lc('OUR MODEL','model',modelLine)+'</div>';
  let take;
  if(r){
    const won=r.result>0?r.home:(r.result<0?r.away:'tie');const mg=Math.abs(r.result);
    const spOut=r.result===0?'Game tied':won+' won by '+mg;
    const spTag=r.ats==='W'?'covered':r.ats==='P'?'push':'needed '+r.pick+' by '+Math.abs(r.pm).toFixed(1)+'+';
    const spBadge=r.ats==='W'?'<span class="gb hit">HIT</span>':r.ats==='P'?'<span class="gb push">PUSH</span>':'<span class="gb miss">MISS</span>';
    const toTag=r.ou==='W'?'under our number':r.ou==='P'?'landed on our number':'over our number';
    const toBadge=r.ou==='W'?'<span class="gb hit">HIT</span>':r.ou==='P'?'<span class="gb push">PUSH</span>':'<span class="gb miss">MISS</span>';
    take='<div class="sec">DID WE HIT?</div><div class="vd">'+
      '<div class="vdr"><div class="vdk">SPREAD</div><div class="vdt">We had <b>'+lineStr(r.pm,h,a)+'</b> · '+spOut+' <span style="color:var(--muted)">('+spTag+')</span></div>'+spBadge+'</div>'+
      '<div class="vdr"><div class="vdk">TOTAL</div><div class="vdt">We projected <b>'+r.ptot.toFixed(1)+'</b> · game landed on '+r.tot+' <span style="color:var(--muted)">('+toTag+')</span></div>'+toBadge+'</div></div>';
  }else{const book=dk||vegas;let lean;
    if(book){const edge=p.margin-book.s;const side=edge>0?h:a;const tside=p.total>book.t?'Over':'Under';
      lean=(Math.abs(edge)<0.5?'Right in line with the market · '+tside+' '+book.t.toFixed(1):'We lean '+T[side].abbr+' ('+(edge>=0?'+':'')+edge.toFixed(1)+' vs the line) · '+tside+' '+book.t.toFixed(1));}
    else lean='Our number: '+lineStr(p.margin,h,a)+' · total '+p.total.toFixed(1);
    take='<div class="sec">OUR TAKE</div><div class="take"><div class="takelean">'+lean+'</div><div class="takewhy">'+whyText(a,h,p)+' <span style="color:var(--muted)">A lean is a talking point, not a lock.</span></div></div>';}
  let cond='';
  if(!r){const wx=g?g.wx:null;let wxH;
    if(wx&&wx.indoor)wxH='<div class="wx"><span class="s">Indoor — '+wx.roof+'. Weather isn\'t a factor.</span></div>';
    else if(wx){const imp=(wx.wind>=15||wx.precip>=50);wxH='<div class="wx"><span class="big">'+wx.temp+'°F · '+wxText(wx.code)+'</span><span class="s">Wind '+wx.wind+' mph · '+wx.precip+'% precip</span></div>'+(imp?'<div class="wxflag">wind/precip may lower the total</div>':'');}
    else wxH='<div class="wx"><span class="s">Forecast posts closer to kickoff.</span></div>';
    let qbH='';if(g&&g.qbadj){const q=g.qbadj;const parts=[];if(q.home)parts.push(h+': '+q.hnote);if(q.away)parts.push(a+': '+q.anote);if(parts.length)qbH='<div class="wxflag" style="margin-top:8px">QB: '+parts.join(' · ')+' — model adjusted</div>';}
    cond='<div class="sec">CONDITIONS</div><div class="two"><div class="card"><h3>PROJECTED WEATHER</h3>'+wxH+qbH+'</div><div class="card"><h3>KEY INJURIES</h3><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div><div style="font-size:11px;font-weight:800;color:var(--muted);margin-bottom:6px">'+a+'</div>'+injBlock(a)+'</div><div><div style="font-size:11px;font-weight:800;color:var(--muted);margin-bottom:6px">'+h+'</div>'+injBlock(h)+'</div></div></div></div>';
  }
  const backTo=r?"showTab('results')":"showTab('matchups')";
  gpage.innerHTML='<div class="back" onclick="'+backTo+'">‹ Back</div><div class="gp-head">'+head+'</div>'+box+lines+take+cond+
    '<div class="sec">THE MATCHUP</div><div class="two">'+teamCardHTML(a,'AWAY')+teamCardHTML(h,'HOME')+'</div>'+projTable(a,h);
  goPage();
}

function goPage(){view.style.display='none';document.querySelector('.tabs').style.display='none';hintEl.style.display='none';gpage.style.display='block';window.scrollTo({top:0});}
const VIEWS={matchups:matchups,results:results,props:props,teams:teamsList,players:playersList};
function showTab(t){gpage.style.display='none';view.style.display='block';document.querySelector('.tabs').style.display='flex';hintEl.style.display='block';
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x.dataset.t===t));VIEWS[t]();window.scrollTo({top:0});}
document.querySelectorAll('.tab').forEach(x=>x.onclick=()=>showTab(x.dataset.t));
showTab('matchups');
</script></body></html>'''

HTML = HTML.replace('__DATA__', DATA_JS).replace('__ASOF__', data['as_of'])
with open('./index.html', 'w') as f:
    f.write(HTML)
print('Built index.html —', len(HTML), 'bytes')
