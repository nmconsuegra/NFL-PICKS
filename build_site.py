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
  :root{--bg:#0e1116;--panel:#161b22;--panel2:#1d232e;--line:#2a3340;--text:#e9edf3;
    --muted:#8b95a6;--amber:#f4b740;--amber-dim:#7a5f1f;--up:#5aa87a;--down:#d1685e;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Archivo',system-ui,sans-serif;background:var(--bg);color:var(--text);
    font-feature-settings:"tnum" 1;line-height:1.4;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1180px;margin:0 auto;padding:20px}
  header{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:16px}
  .brand{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
  .brand h1{font-weight:900;font-size:30px;letter-spacing:-.02em;line-height:1}
  .brand h1 .b{color:var(--amber)}
  .asof{color:var(--muted);font-size:13px;font-weight:600}
  .disclaimer{margin-top:12px;font-size:12.5px;color:var(--muted);max-width:78ch;line-height:1.5}
  .disclaimer b{color:#c7ad6a;font-weight:700}
  .tabs{display:flex;gap:6px;margin-bottom:20px}
  .tab{background:var(--panel);border:1px solid var(--line);color:var(--muted);
    padding:9px 18px;border-radius:8px;font-family:inherit;font-weight:800;font-size:14px;cursor:pointer}
  .tab.on{background:var(--panel2);color:var(--amber);border-color:var(--amber-dim)}
  .grid{display:grid;grid-template-columns:minmax(320px,420px) 1fr;gap:22px;align-items:start}
  @media(max-width:820px){.grid{grid-template-columns:1fr}}
  .hidden{display:none}
  .section-label{font-size:13px;font-weight:800;color:var(--muted);margin-bottom:10px;
    display:flex;justify-content:space-between;align-items:center}
  .count{color:var(--amber);font-weight:800}
  .board{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--panel)}
  .game{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;
    padding:13px 14px;border-bottom:1px solid var(--line);cursor:pointer;transition:background .12s}
  .game:last-child{border-bottom:none}
  .game:hover{background:var(--panel2)}
  .game.active{background:var(--panel2);box-shadow:inset 3px 0 0 var(--amber)}
  .matchup{font-weight:700;font-size:15.5px}
  .matchup .at{color:var(--muted);font-weight:500;margin:0 5px}
  .gtime{font-size:11.5px;color:var(--muted);font-weight:600;margin-top:3px}
  .mkt{font-size:13px;color:var(--muted);text-align:right;white-space:nowrap}
  .num-agree{color:var(--up);font-weight:800}
  .num-disagree{color:var(--down);font-weight:800}
  .legend{font-size:12px;color:var(--muted);margin:-4px 0 10px;display:flex;gap:16px}
  .legend .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}
  .legend .g{background:var(--up)}.legend .r{background:var(--down)}
  .dk-inputs{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;margin-top:4px}
  .dk-inputs label{font-size:11px;color:var(--muted);font-weight:700;width:100%}
  .dk-inputs .hint{font-weight:600}
  .dk-inputs .lineinput{width:120px}
  .dk-hint{font-size:11.5px;color:var(--muted);margin-top:10px}
  .dktag{display:inline-block;font-size:10px;font-weight:900;color:#1a1400;background:var(--amber);
    border-radius:4px;padding:1px 5px;margin-right:6px;vertical-align:middle}
  .leanchip{font-size:12px;font-weight:800;padding:3px 8px;border-radius:6px;border:1px solid var(--amber-dim);
    color:var(--amber);white-space:nowrap;min-width:64px;text-align:center}
  .leanchip.none{border-color:var(--line);color:var(--muted)}
  .builder{margin-top:20px;padding:16px;border:1px dashed var(--line);border-radius:10px}
  .pickrow{display:flex;gap:8px;align-items:center}
  select{flex:1;background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:8px;
    padding:10px;font-family:inherit;font-size:14px;font-weight:600}
  .atlabel{color:var(--muted);font-weight:700}
  .gobtn{margin-top:10px;width:100%;background:var(--amber);color:#1a1400;border:none;border-radius:8px;
    padding:11px;font-family:inherit;font-weight:800;font-size:14px;cursor:pointer}
  .gobtn:hover{filter:brightness(1.06)}
  /* team list */
  .trow{display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;
    padding:11px 14px;border-bottom:1px solid var(--line);cursor:pointer;transition:background .12s}
  .trow:last-child{border-bottom:none}
  .trow:hover{background:var(--panel2)}
  .trow.active{background:var(--panel2);box-shadow:inset 3px 0 0 var(--amber)}
  .trk{font-weight:900;color:var(--amber);font-size:15px;text-align:center}
  .tnm{font-weight:700;font-size:15px}
  .trec{font-size:12.5px;color:var(--muted);font-weight:700}
  /* detail */
  .detail{border:1px solid var(--line);border-radius:10px;background:var(--panel);min-height:420px}
  .empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:420px;
    color:var(--muted);text-align:center;padding:30px}
  .empty .big{font-size:19px;font-weight:800;color:#c3ccdb;margin-bottom:8px}
  .d-head{padding:20px 22px;border-bottom:1px solid var(--line)}
  .d-title{font-size:26px;font-weight:900;letter-spacing:-.02em}
  .d-sub{color:var(--muted);font-size:13px;font-weight:600;margin-top:3px}
  .lines{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--line)}
  .linebox{padding:16px 15px;border-right:1px solid var(--line)}
  .linebox:last-child{border-right:none}
  @media(max-width:900px){.lines{grid-template-columns:1fr 1fr}.linebox{border-bottom:1px solid var(--line)}}
  @media(max-width:640px){.lines{grid-template-columns:1fr}.linebox{border-right:none;border-bottom:1px solid var(--line)}.linebox:last-child{border-bottom:none}}
  .mktline{white-space:nowrap;line-height:1.5}
  .mlbl{color:var(--muted);font-weight:800;font-size:10.5px;margin-right:5px}
  .mdot{color:#3a4453;margin:0 4px}
  .linelabel{font-size:12px;font-weight:800;color:var(--muted);margin-bottom:6px}
  .lineval{font-size:30px;font-weight:900;letter-spacing:-.02em;line-height:1}
  .lineval.model{color:var(--amber)}
  .linetotal{font-size:14px;color:var(--muted);font-weight:600;margin-top:6px}
  .leans{padding:16px 22px;border-bottom:1px solid var(--line);display:flex;gap:10px;flex-wrap:wrap}
  .lean{border:1px solid var(--line);border-radius:8px;padding:9px 13px;font-size:13.5px;font-weight:700}
  .lean .k{color:var(--muted);margin-right:7px}.lean .v{font-weight:900}
  .lean-note{padding:0 22px 16px;color:var(--muted);font-size:12px;line-height:1.5}
  .lean-note b{color:#c7ad6a}
  .teams2{display:grid;grid-template-columns:1fr 1fr}
  .tcard{padding:18px 22px}.tcard:first-child{border-right:1px solid var(--line)}
  .tname{font-size:18px;font-weight:800;display:flex;align-items:baseline;gap:8px}
  .tname .side{font-size:11px;font-weight:800;color:var(--muted)}
  .trank{font-size:13px;color:var(--amber);font-weight:800;margin:6px 0 14px}
  .stat{margin-bottom:12px}
  .stat .top{display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px}
  .stat .top .lab{color:var(--muted);font-weight:700}.stat .top .num{font-weight:800}
  .bar{height:6px;background:var(--panel2);border-radius:3px;position:relative;overflow:hidden}
  .bar .mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:#3a4453}
  .bar .fill{position:absolute;top:0;bottom:0;border-radius:3px}
  .tier{font-size:11px;font-weight:800;padding:1px 6px;border-radius:4px;background:var(--panel2);color:var(--muted)}
  .why{padding:18px 22px;border-top:1px solid var(--line)}
  .why h3{font-size:12px;font-weight:800;color:var(--muted);margin-bottom:9px}
  .why p{font-size:14.5px;line-height:1.6;color:#d5dbe6}
  /* game log */
  .log{padding:6px 22px 18px}
  .log h3{font-size:12px;font-weight:800;color:var(--muted);margin:12px 0 8px}
  .logtbl{width:100%;border-collapse:collapse;font-size:13.5px}
  .logtbl th{text-align:left;color:var(--muted);font-weight:700;font-size:11.5px;padding:5px 8px;border-bottom:1px solid var(--line)}
  .logtbl td{padding:7px 8px;border-bottom:1px solid var(--line);font-weight:600}
  .logtbl tr:last-child td{border-bottom:none}
  .wl{font-weight:900;width:22px}.wl.W{color:var(--up)}.wl.L{color:var(--down)}
  .oe{font-weight:800}.oe.pos{color:var(--up)}.oe.neg{color:var(--down)}
  .search{width:100%;background:var(--panel2);color:var(--text);border:1px solid var(--line);
    border-radius:8px;padding:10px 12px;font-family:inherit;font-size:14px;font-weight:600;margin-bottom:10px}
  .search::placeholder{color:var(--muted)}
  .prow{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:11px 14px;
    border-bottom:1px solid var(--line);cursor:pointer;transition:background .12s}
  .prow:last-child{border-bottom:none}.prow:hover{background:var(--panel2)}
  .prow.active{background:var(--panel2);box-shadow:inset 3px 0 0 var(--amber)}
  .pnm{font-weight:700;font-size:15px}
  .ppos{font-size:12px;color:var(--muted);font-weight:700}
  .propstat{padding:16px 22px;border-bottom:1px solid var(--line)}
  .propstat:last-child{border-bottom:none}
  .ps-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}
  .ps-name{font-size:15px;font-weight:800}
  .ps-proj{font-size:14px;color:var(--amber);font-weight:800}
  .ps-games{font-size:12.5px;color:var(--muted);font-weight:600;margin-bottom:12px}
  .ps-calc{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .ps-calc label{font-size:12.5px;color:var(--muted);font-weight:700}
  .lineinput{width:90px;background:var(--panel2);color:var(--text);border:1px solid var(--line);
    border-radius:7px;padding:8px 10px;font-family:inherit;font-size:14px;font-weight:700}
  .ps-out{font-size:13.5px;font-weight:700;color:var(--text)}
  .ps-out .ov{color:var(--up);font-weight:900}.ps-out .un{color:var(--down);font-weight:900}
  .ps-lean{font-size:12.5px;font-weight:900;padding:3px 9px;border-radius:6px;border:1px solid var(--amber-dim);color:var(--amber)}
  .ps-note{padding:14px 22px;color:var(--muted);font-size:12px;line-height:1.5}
  .ps-note b{color:#c7ad6a}
  .gl{padding:16px 22px;border-bottom:1px solid var(--line)}
  .gl-date{font-size:12px;font-weight:800;color:var(--muted);margin-bottom:10px}
  .gl-grid{display:grid;grid-template-columns:minmax(0,1.3fr) 1fr 1fr 1fr;gap:6px;align-items:center}
  .gl-h{font-size:11px;font-weight:700;color:var(--muted);text-align:center;padding-bottom:2px}
  .gl-team{font-weight:800;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .gl-team .ab{color:var(--muted);font-weight:700;margin-right:6px}
  .glcell{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:8px 4px;text-align:center}
  .glnum{font-weight:800;font-size:14px}
  .glprice{font-size:12px;font-weight:800;color:var(--up);margin-top:2px}
  .gl-at{font-size:10px;font-weight:800;color:var(--muted);margin:2px 0 2px 2px}
  .gl-note{font-size:11.5px;color:var(--muted);margin-top:12px;line-height:1.5}
  .injsec{padding:16px 22px;border-top:1px solid var(--line)}
  .injsec h3{font-size:12px;font-weight:800;color:var(--muted);margin-bottom:10px}
  .injrow{display:flex;align-items:center;gap:9px;padding:5px 0;font-size:13.5px;border-bottom:1px solid var(--line)}
  .injrow:last-child{border-bottom:none}
  .injstat{font-size:10px;font-weight:900;padding:2px 6px;border-radius:4px;min-width:38px;text-align:center}
  .injstat.out{background:rgba(209,104,94,.18);color:var(--down)}
  .injstat.dbt{background:rgba(244,183,64,.15);color:var(--amber)}
  .injstat.qst{background:var(--panel2);color:var(--muted)}
  .injpos{color:var(--muted);font-weight:800;font-size:11px;min-width:22px}
  .injname{font-weight:700}
  .injnote{color:var(--muted);font-size:12px}
  .inj-none{color:var(--muted);font-size:13px}
  .inj-note{font-size:11.5px;color:var(--muted);margin-top:10px;line-height:1.5}
  .pstatus{display:inline-block;font-size:11px;font-weight:900;padding:3px 10px;border-radius:5px;margin-top:9px}
  .pstatus.out{background:rgba(209,104,94,.18);color:var(--down)}
  .pstatus.dbt{background:rgba(244,183,64,.15);color:var(--amber)}
  .pstatus.qst{background:rgba(244,183,64,.12);color:var(--amber)}
  .pstatus.active{background:rgba(90,168,122,.15);color:var(--up)}
  .schrow td{padding:7px 8px;border-bottom:1px solid var(--line);font-weight:600;font-size:13.5px}
  .schrow:last-child td{border-bottom:none}
  .schrow.next td{background:rgba(244,183,64,.06)}
  .kick{color:var(--muted);font-weight:600}
  .lnk{cursor:pointer;transition:color .12s}
  .lnk:hover{color:var(--amber);text-decoration:underline}
  .wxsec{padding:14px 22px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:16px;flex-wrap:wrap}
  .wx-l{font-size:11px;font-weight:800;color:var(--muted);letter-spacing:.02em}
  .wx-main{font-weight:800;font-size:15px}
  .wx-sub{color:var(--muted);font-weight:600;font-size:13px}
  .wx-flag{font-size:12px;font-weight:800;color:var(--amber);border:1px solid var(--amber-dim);border-radius:6px;padding:3px 8px}
  .wx-indoor{color:var(--muted);font-weight:700;font-size:13.5px}
  .rec-cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
  @media(max-width:640px){.rec-cards{grid-template-columns:1fr}}
  .rec-card{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:16px 18px}
  .rec-card h4{font-size:12px;font-weight:800;color:var(--muted);margin-bottom:8px}
  .rec-big{font-size:26px;font-weight:900;letter-spacing:-.02em}
  .rec-sub{font-size:13px;color:var(--muted);font-weight:600;margin-top:4px}
  .rec-note{font-size:12.5px;color:var(--muted);line-height:1.55;margin-bottom:16px;max-width:82ch}
  .rec-note b{color:#c7ad6a}
  .restbl{width:100%;border-collapse:collapse;font-size:13.5px}
  .restbl th{text-align:left;color:var(--muted);font-weight:700;font-size:11.5px;padding:8px;border-bottom:1px solid var(--line)}
  .restbl td{padding:9px 8px;border-bottom:1px solid var(--line);font-weight:600}
  .restbl tr:last-child td{border-bottom:none}
  .res-w{color:var(--up);font-weight:900}.res-l{color:var(--down);font-weight:900}.res-p{color:var(--muted);font-weight:800}
  .grow{border:1px solid var(--line);border-radius:0}
  .grow{border-bottom:1px solid var(--line)}.grow:last-child{border-bottom:none}
  .ghead{display:grid;grid-template-columns:1.4fr auto auto auto;gap:10px;align-items:center;padding:13px 14px;cursor:pointer;transition:background .12s}
  .ghead:hover{background:var(--panel2)}.grow.open .ghead{background:var(--panel2)}
  .gmu{font-weight:800;font-size:15px}.gmu .gwk{color:var(--muted);font-weight:700;font-size:12px;margin-right:7px}
  .gfin{font-weight:800;font-size:14.5px;text-align:right;white-space:nowrap}.gfin .w{color:var(--up)}
  .gbadge{font-size:10.5px;font-weight:900;padding:3px 7px;border-radius:6px;min-width:70px;text-align:center;white-space:nowrap}
  .gbadge.hit{background:rgba(90,168,122,.16);color:var(--up)}
  .gbadge.miss{background:rgba(209,104,94,.16);color:var(--down)}
  .gbadge.push{background:var(--panel2);color:var(--muted)}
  .gchev{margin-left:5px}
  .gdetail{display:none;padding:2px 14px 16px;border-top:1px solid var(--line);background:#12161d}
  .grow.open .gdetail{display:block}
  .gdh{font-size:11px;font-weight:800;color:var(--muted);margin:15px 0 8px}
  .boxt{width:100%;border-collapse:collapse;font-size:13.5px}
  .boxt th{font-size:11px;color:var(--muted);font-weight:700;text-align:center;padding:5px 4px;border-bottom:1px solid var(--line)}
  .boxt th:first-child{text-align:left}
  .boxt td{text-align:center;padding:7px 4px;font-weight:700;border-bottom:1px solid var(--line)}
  .boxt td:first-child{text-align:left;font-weight:800}.boxt tr:last-child td{border-bottom:none}
  .boxt .qtot{color:var(--amber);font-weight:900}
  .cmp4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
  @media(max-width:560px){.cmp4{grid-template-columns:1fr 1fr}}
  .c4{border:1px solid var(--line);border-radius:8px;padding:9px 6px;text-align:center;background:var(--panel)}
  .c4 .l{font-size:10px;font-weight:800;color:var(--muted);margin-bottom:4px}
  .c4.mdl .l{color:var(--amber)}.c4.fdl .l{color:#6aa0e0}
  .c4 .sp{font-size:15px;font-weight:900}.c4 .to{font-size:11.5px;color:var(--muted);font-weight:600;margin-top:2px}
  .vd{border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .vdr{display:grid;grid-template-columns:62px 1fr auto;gap:10px;align-items:center;padding:11px 12px;border-bottom:1px solid var(--line)}
  .vdr:last-child{border-bottom:none}
  .vdk{font-size:12px;font-weight:800;color:var(--muted)}.vdt{font-size:13px;line-height:1.5}.vdt b{font-weight:800}
  .vdres{font-size:11.5px;font-weight:900;padding:4px 9px;border-radius:6px;white-space:nowrap}
  .vdres.hit{background:rgba(90,168,122,.16);color:var(--up)}
  .vdres.miss{background:rgba(209,104,94,.16);color:var(--down)}
  .vdres.push{background:var(--panel2);color:var(--muted)}
  .rccards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:6px}
  @media(max-width:640px){.rccards{grid-template-columns:1fr 1fr}}
  .rccard{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:13px 14px}
  .rclbl{font-size:11px;font-weight:800;color:var(--muted);margin-bottom:9px;letter-spacing:.02em}
  .rclbl.model{color:var(--amber)}.rclbl.fdl{color:#6aa0e0}
  .rcline{display:flex;justify-content:space-between;align-items:baseline;font-size:13px;color:var(--muted);font-weight:600;margin-bottom:4px}
  .rcline b{color:var(--text);font-size:17px;font-weight:900;margin-left:auto;margin-right:6px}
  .rcp{color:var(--muted);font-weight:700;font-size:12px;min-width:34px;text-align:right}
  .rcbuild{font-size:12px;color:var(--muted);line-height:1.4;padding:4px 0}
  .inj2{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line)}
  .inj2 .col{padding:16px 22px}
  .inj2 .col:first-child{border-right:1px solid var(--line)}
  @media(max-width:640px){.inj2{grid-template-columns:1fr}.inj2 .col:first-child{border-right:none;border-bottom:1px solid var(--line)}}
</style></head><body>
<div class="wrap">
  <header>
    <div class="brand"><h1>Edge <span class="b">Board</span></h1><span class="asof">__ASOF__</span></div>
    <p class="disclaimer">Model read vs. the market for each game, plus a profile for every team.
      A <b>lean</b> is where the model disagrees with the line — a talking point, not a proven edge.
      This model tracks the market closely, and early-season ratings lean on last year's data.
      Shop for the best number, and bet responsibly.</p>
  </header>

  <div class="tabs">
    <button class="tab on" id="tab-games">Matchups</button>
    <button class="tab" id="tab-teams">Teams</button>
    <button class="tab" id="tab-players">Players &amp; props</button>
    <button class="tab" id="tab-results">Results</button>
  </div>

  <!-- GAMES VIEW -->
  <div class="grid" id="view-games">
    <div>
      <div class="section-label">This week's slate <span class="count" id="gcount"></span></div>
      <div class="legend"><span><span class="dot g"></span>model agrees with the line</span><span><span class="dot r"></span>model differs — tap for the full breakdown</span></div>
      <div class="board" id="board"></div>
      <div class="builder">
        <div class="section-label">Build any matchup</div>
        <div class="pickrow"><select id="away"></select><span class="atlabel">@</span><select id="home"></select></div>
        <button class="gobtn" id="go">Show matchup</button>
      </div>
    </div>
    <div class="detail" id="detail">
      <div class="empty"><div class="big">Pick a game</div>
        <div>Tap any matchup to see the model's read, both teams' profiles, and the plain-English why.</div></div>
    </div>
  </div>

  <!-- TEAMS VIEW -->
  <div class="grid hidden" id="view-teams">
    <div>
      <div class="section-label">All teams <span class="count">by power rank</span></div>
      <input class="search" id="team-search" placeholder="Search a team…">
      <div class="board" id="teamlist"></div>
    </div>
    <div class="detail" id="teamdetail">
      <div class="empty"><div class="big">Pick a team</div>
        <div>Tap any team to see its ratings, ranks, recent form, and game log.</div></div>
    </div>
  </div>

  <!-- PLAYERS VIEW -->
  <div class="grid hidden" id="view-players">
    <div>
      <div class="section-label">Players <span class="count" id="pcount"></span></div>
      <input class="search" id="player-search" placeholder="Search a player…">
      <div class="board" id="playerlist"></div>
    </div>
    <div class="detail" id="playerdetail">
      <div class="empty"><div class="big">Pick a player</div>
        <div>Search a player, then type the line your sportsbook is showing<br>to see the over/under probabilities and the model's lean.</div></div>
    </div>
  </div>

  <!-- RESULTS VIEW -->
  <div class="hidden" id="view-results">
    <div class="section-label">Model track record <span class="count" id="rec-count"></span></div>
    <div id="results-body"></div>
  </div>
</div>

<script>
const DATA = __DATA__;
const T = DATA.teams, C = DATA.cal;
const abbrs = Object.keys(T).filter(a=>a!=='LA').sort((x,y)=>T[x].city.localeCompare(T[y].city));
function tier(r){return r<=6?'elite':r<=13?'good':r<=20?'average':'weak';}
function project(away,home,adjH,adjA){adjH=adjH||0;adjA=adjA||0;const h=T[home],a=T[away];
  const sd=(h.off+h.def)-(a.off+a.def)+adjH-adjA, comb=(h.off-a.def)+(a.off-h.def)+adjH+adjA;
  return {margin:C.B0+C.B1*sd, total:C.TB0+C.TB1*comb};}
function lineStr(m,home,away){const f=m>0?home:away;return T[f].abbr+' -'+Math.abs(m).toFixed(1);}
function barFill(v,s){const p=Math.max(-1,Math.min(1,v/s)),w=Math.abs(p)*50,l=p>=0?50:50-w,
  c=p>=0?'var(--up)':'var(--down)';return `<div class="fill" style="left:${l}%;width:${w}%;background:${c}"></div>`;}

function teamCard(abbr,side){const t=T[abbr];return `<div class="tcard">
  <div class="tname"><span class="lnk" onclick="goTeam('${abbr}')">${t.city} ${t.name}</span> <span class="side">${side}</span></div>
  <div class="trank">Power rank #${t.ovr_rank} of 32</div>
  <div class="stat"><div class="top"><span class="lab">Offense <span class="tier">#${t.off_rank} ${tier(t.off_rank)}</span></span><span class="num">${t.off>=0?'+':''}${t.off.toFixed(3)}</span></div><div class="bar"><div class="mid"></div>${barFill(t.off,0.15)}</div></div>
  <div class="stat"><div class="top"><span class="lab">Defense <span class="tier">#${t.def_rank} ${tier(t.def_rank)}</span></span><span class="num">${t.def>=0?'+':''}${t.def.toFixed(3)}</span></div><div class="bar"><div class="mid"></div>${barFill(t.def,0.15)}</div></div>
  <div class="stat"><div class="top"><span class="lab">Last 4 — offense</span><span class="num">${t.form_off>=0?'+':''}${t.form_off.toFixed(3)}</span></div><div class="bar"><div class="mid"></div>${barFill(t.form_off,0.2)}</div></div>
</div>`;}

function bkKey(bk,a,h){return bk+':'+a+'@'+h;}
function getBk(bk,a,h){try{const v=localStorage.getItem(bkKey(bk,a,h));return v?JSON.parse(v):null;}catch(e){return null;}}
function setBk(bk,a,h,o){try{localStorage.setItem(bkKey(bk,a,h),JSON.stringify(o));}catch(e){}}

function fillLean(away,home,p,s,t,label){
  const h=T[home],a=T[away];
  const lz=document.getElementById('leanzone'),wt=document.getElementById('whytext');
  const f=p.margin>0?home:away;
  let why=`Our ratings have ${h.city} ${h.name} at #${h.ovr_rank} overall (${tier(h.off_rank)} offense, ${tier(h.def_rank)} defense) and ${a.city} ${a.name} at #${a.ovr_rank} (${tier(a.off_rank)} offense, ${tier(a.def_rank)} defense). After ~${C.B0.toFixed(1)} points of home field, the model projects ${T[f].name} by ${Math.abs(p.margin).toFixed(1)}.`;
  if(s==null){lz.innerHTML=`<div class="lean-note">No book line posted for this game yet.</div>`;wt.textContent=why;return;}
  const edge=p.margin-s,side=edge>0?home:away,tside=p.total>t?'Over':'Under';
  const agree=((p.margin>0)===(s>0))&&Math.abs(p.margin-s)<2;
  lz.innerHTML=`<div class="leans">
    <div class="lean"><span class="k">Spread lean</span><span class="v">${T[side].abbr} (${edge>=0?'+':''}${edge.toFixed(1)})</span></div>
    <div class="lean"><span class="k">Total lean</span><span class="v">${tside} (${(p.total-t>=0?'+':'')}${(p.total-t).toFixed(1)})</span></div></div>
    <div class="lean-note">Model vs <b>${label} ${lineStr(s,home,away)}, total ${t.toFixed(1)}</b>. A lean is a talking point, not a bet signal — this model wins about half its leans against the number.</div>`;
  why+=agree?` ${label} lands in the same place — no real disagreement, a "bet only if you love it" game.`:` That differs from ${label}'s ${lineStr(s,home,away)} by ${Math.abs(p.margin-s).toFixed(1)} points, a lean worth noting but not a lock.`;
  wt.textContent=why;
}

function qbNote(g){
  if(!g||!g.qbadj)return '';
  const q=g.qbadj, parts=[];
  if(q.home)parts.push(`${g.home}: ${q.hnote} (${C.B1*q.home>=0?'+':''}${(C.B1*q.home).toFixed(1)} pts)`);
  if(q.away)parts.push(`${g.away}: ${q.anote} (${C.B1*q.away>=0?'+':''}${(C.B1*q.away).toFixed(1)} pts)`);
  if(!parts.length)return '';
  return `<div class="wxsec"><span class="wx-l">QB ADJUSTMENT</span><span class="wx-sub">${parts.join(' · ')} — model reflects the backup</span></div>`;
}
function wxText(c){
  if(c===0)return 'Clear';if([1,2].includes(c))return 'Partly cloudy';if(c===3)return 'Overcast';
  if([45,48].includes(c))return 'Fog';if([51,53,55,56,57].includes(c))return 'Drizzle';
  if([61,63,65,66,67,80,81,82].includes(c))return 'Rain';if([71,73,75,77,85,86].includes(c))return 'Snow';
  if([95,96,99].includes(c))return 'Thunderstorm';return 'Cloudy';
}
function wxHTML(g){
  const wx=g?g.wx:undefined;
  if(wx&&wx.indoor)return `<div class="wxsec"><span class="wx-l">PROJECTED WEATHER</span><span class="wx-indoor">Indoor — ${wx.roof}. Weather isn't a factor.</span></div>`;
  if(wx){const impact=(wx.wind>=15||wx.precip>=50);
    return `<div class="wxsec"><span class="wx-l">PROJECTED WEATHER</span><span class="wx-main">${wx.temp}°F · ${wxText(wx.code)}</span><span class="wx-sub">Wind ${wx.wind} mph · ${wx.precip}% precip</span>${impact?`<span class="wx-flag">wind/precip may suppress the total</span>`:''}</div>`;}
  if(g)return `<div class="wxsec"><span class="wx-l">PROJECTED WEATHER</span><span class="wx-sub">Forecast posts closer to kickoff.</span></div>`;
  return '';
}

function render(away,home,mktSpread,mktTotal){
  const h=T[home],a=T[away];
  const gobj=DATA.games.find(x=>x.away===away&&x.home===home);
  const qa=(gobj&&gobj.qbadj)||{};
  const p=project(away,home,qa.home||0,qa.away||0);
  const dkV=(gobj?gobj.dk:null), fdV=(gobj?gobj.fd:null);
  const bookBox=(label,v)=>v
    ? `<div class="lineval" style="font-size:24px">${lineStr(v.s,home,away)}</div><div class="linetotal">Total ${v.t.toFixed(1)}</div>`
    : `<div class="lineval" style="color:var(--muted);font-size:16px">—</div><div class="linetotal">not posted yet</div>`;
  document.getElementById('detail').innerHTML=`
    <div class="d-head"><div class="d-title"><span class="lnk" onclick="goTeam('${away}')">${a.city} ${a.name}</span> <span style="color:var(--muted);font-weight:600">at</span> <span class="lnk" onclick="goTeam('${home}')">${h.city} ${h.name}</span></div><div class="d-sub">${DATA.as_of}</div></div>
    <div class="lines">
      <div class="linebox"><div class="linelabel">MODEL</div><div class="lineval model">${lineStr(p.margin,home,away)}</div><div class="linetotal">Total ~ ${p.total.toFixed(1)}</div></div>
      <div class="linebox"><div class="linelabel">VEGAS</div>
        ${mktSpread!=null?`<div class="lineval" style="font-size:24px">${lineStr(mktSpread,home,away)}</div><div class="linetotal">Total ${mktTotal.toFixed(1)}</div>`:`<div class="lineval" style="color:var(--muted);font-size:16px">—</div><div class="linetotal">not on this week's slate</div>`}
      </div>
      <div class="linebox"><div class="linelabel">DRAFTKINGS</div>${bookBox('DK',dkV)}</div>
      <div class="linebox"><div class="linelabel">FANDUEL</div>${bookBox('FD',fdV)}</div>
    </div>
    <div id="leanzone"></div>
    ${qbNote(gobj)}
    ${wxHTML(gobj)}
    <div class="teams2">${teamCard(away,'AWAY')}${teamCard(home,'HOME')}</div>
    <div class="inj2"><div class="col"><h3 style="font-size:12px;font-weight:800;color:var(--muted);margin-bottom:10px">${away} injuries</h3>${injuryHTML(away,6)}</div><div class="col"><h3 style="font-size:12px;font-weight:800;color:var(--muted);margin-bottom:10px">${home} injuries</h3>${injuryHTML(home,6)}</div></div>
    <div class="why"><h3>Why — say this to a client</h3><p id="whytext"></p></div>`;
  // lean vs the best available book (DraftKings first), else Vegas
  if(dkV) fillLean(away,home,p,dkV.s,dkV.t,'DraftKings');
  else if(fdV) fillLean(away,home,p,fdV.s,fdV.t,'FanDuel');
  else if(mktSpread!=null) fillLean(away,home,p,mktSpread,mktTotal,'Vegas');
  else fillLean(away,home,p,null,null,'');
}

function americanFromProb(pr){
  if(pr<=0.02)return '+2500'; if(pr>=0.98)return '-5000';
  let ml=pr>=0.5?-100*pr/(1-pr):100*(1-pr)/pr; ml=Math.round(ml/5)*5;
  return (ml>0?'+':'')+ml;
}
function gameLinesCard(abbr){
  const t=T[abbr],ng=t.next;
  if(!ng)return '';
  const home=ng.home?abbr:ng.opp, away=ng.home?ng.opp:abbr;
  const saved=getBk('dk',away,home)||getBk('fd',away,home);
  const s=saved?saved.s:(ng.spread!=null?ng.spread:null);
  const tot=saved?saved.t:(ng.total!=null?ng.total:null);
  const src=saved?'your entered line':(ng.spread!=null?'consensus line':null);
  const p=project(away,home);
  const pHome=1-normCdf(0,p.margin,13.2),pAway=1-pHome;
  const dstr=new Date(ng.date+'T12:00:00').toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});
  const spCell=(side)=>s==null?`<div class="glcell"><div class="glnum">—</div></div>`:
    (()=>{const v=side==='home'?-s:s;return `<div class="glcell"><div class="glnum">${v>0?'+':''}${v.toFixed(1)}</div><div class="glprice">−110</div></div>`;})();
  const toCell=(ou)=>tot==null?`<div class="glcell"><div class="glnum">—</div></div>`:
    `<div class="glcell"><div class="glnum">${ou} ${tot.toFixed(1)}</div><div class="glprice">−110</div></div>`;
  const mlCell=(v)=>`<div class="glcell"><div class="glnum" style="color:var(--up)">${v}</div></div>`;
  return `<div class="gl">
    <div class="gl-date">Week ${ng.week} · ${dstr}${saved?' · DK entered':''}</div>
    <div class="gl-grid">
      <div></div><div class="gl-h">Spread</div><div class="gl-h">Total</div><div class="gl-h">Moneyline</div>
      <div class="gl-team"><span class="ab">${away}</span>${T[away].name}</div>${spCell('away')}${toCell('O')}${mlCell(americanFromProb(pAway))}
      <div class="gl-team"><span class="ab">${home}</span>${T[home].name}</div>${spCell('home')}${toCell('U')}${mlCell(americanFromProb(pHome))}
    </div>
    <div class="gl-note">Spread &amp; total: ${src||'not posted by books yet'}${src?' — edit it on the Matchups tab':''}. Moneyline is <b>model-implied</b> (a fair price to compare against DraftKings' actual number, not DK's line).</div>
  </div>`;
}

function fmtKick(dateStr,timeStr){
  const d=new Date(dateStr+'T12:00:00');
  let ds=d.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});
  if(!timeStr)return ds;
  let [h,m]=timeStr.split(':').map(Number);const ap=h>=12?'PM':'AM';h=h%12;if(h===0)h=12;
  return `${ds} · ${h}:${String(m).padStart(2,'0')} ${ap} ET`;
}
function injBadge(inj){
  if(!inj)return `<span class="pstatus active">Active — no injury reported</span>`;
  const cls={'Out':'out','Doubtful':'dbt','Questionable':'qst'}[inj.status]||'qst';
  const lbl={'Out':'OUT','Doubtful':'DOUBTFUL','Questionable':'QUESTIONABLE'}[inj.status]||inj.status.toUpperCase();
  return `<span class="pstatus ${cls}">${lbl}${inj.note?' — '+inj.note:''}</span>`;
}

function injuryHTML(abbr,max){
  const inj=(T[abbr].inj)||[];
  if(!inj.length)return `<div class="inj-none">No injuries on this week's report.</div>`;
  const cls={'Out':'out','Doubtful':'dbt','Questionable':'qst'};
  const shrt={'Out':'OUT','Doubtful':'DBT','Questionable':'Q'};
  return inj.slice(0,max||10).map(x=>{
    const key=playerKeyByNameTeam[x.name.toLowerCase()+'|'+abbr];
    const nm=key?`<span class="injname lnk" onclick="goPlayer('${key.replace(/'/g,"\\'")}')">${x.name}</span>`:`<span class="injname">${x.name}</span>`;
    return `<div class="injrow"><span class="injstat ${cls[x.status]||''}">${shrt[x.status]||x.status}</span><span class="injpos">${x.pos}</span>${nm}${x.note?`<span class="injnote">${x.note}</span>`:''}</div>`;
  }).join('');
}

function renderTeam(abbr){
  const t=T[abbr];
  const rows=(t.log||[]).slice().reverse().map(g=>{
    const oe=g.off>=0?'pos':'neg';
    return `<tr><td>Wk ${g.week}</td><td>vs ${g.opp}</td><td class="wl ${g.res}">${g.res}</td>
      <td>${g.pf}-${g.pa}</td><td class="oe ${oe}">${g.off>=0?'+':''}${g.off.toFixed(3)}</td></tr>`;}).join('');
  document.getElementById('teamdetail').innerHTML=`
    <div class="d-head"><div class="d-title">${t.city} ${t.name}</div>
      <div class="d-sub">Power rank #${t.ovr_rank} of 32 &nbsp;·&nbsp; ${DATA.as_of}</div></div>
    ${gameLinesCard(abbr)}
    <div class="teams2" style="grid-template-columns:1fr">
      <div class="tcard" style="border-right:none">
        <div class="stat"><div class="top"><span class="lab">Offense <span class="tier">#${t.off_rank} ${tier(t.off_rank)}</span></span><span class="num">${t.off>=0?'+':''}${t.off.toFixed(3)} EPA/play</span></div><div class="bar"><div class="mid"></div>${barFill(t.off,0.15)}</div></div>
        <div class="stat"><div class="top"><span class="lab">Defense <span class="tier">#${t.def_rank} ${tier(t.def_rank)}</span></span><span class="num">${t.def>=0?'+':''}${t.def.toFixed(3)} EPA saved</span></div><div class="bar"><div class="mid"></div>${barFill(t.def,0.15)}</div></div>
        <div class="stat"><div class="top"><span class="lab">Last 4 — offense</span><span class="num">${t.form_off>=0?'+':''}${t.form_off.toFixed(3)}</span></div><div class="bar"><div class="mid"></div>${barFill(t.form_off,0.2)}</div></div>
      </div></div>
    <div class="injsec"><h3>Injury report${DATA.inj_week?' — Week '+DATA.inj_week:''}</h3>${injuryHTML(abbr,12)}
      <div class="inj-note">Official report (Out / Doubtful / Questionable). Shown as context — the model does not auto-adjust its rating for injuries.</div></div>
    <div class="log"><h3>Season schedule${DATA.as_of?'':''}</h3>
      <table class="logtbl"><thead><tr><th>Wk</th><th>Matchup</th><th>Result / Kickoff</th></tr></thead>
      <tbody>${(t.sched||[]).map(g=>{
        const isNext=(!g.played)&&(t.next&&t.next.week===g.week);
        const right=g.played
          ? `<span class="wl ${g.res}">${g.res}</span> ${g.pf}-${g.pa}`
          : `<span class="kick">${fmtKick(g.date,g.time)}</span>`;
        return `<tr class="schrow ${isNext?'next':''}"><td>${g.week}</td><td>${g.home?'vs':'@'} ${g.opp}</td><td>${right}</td></tr>`;
      }).join('')||'<tr><td colspan=3>Schedule not available</td></tr>'}</tbody></table></div>
    <div class="log"><h3>Recent games (offensive EPA/play per game)</h3>
      <table class="logtbl"><thead><tr><th>Week</th><th>Opp</th><th>Res</th><th>Score</th><th>Off EPA</th></tr></thead>
      <tbody>${rows||'<tr><td colspan=5>No games yet</td></tr>'}</tbody></table></div>`;
}

// build slate
const board=document.getElementById('board');
document.getElementById('gcount').textContent=DATA.games.length+' games';
function buildBoard(){
  board.innerHTML='';
  const fmtDT=(dateStr,timeStr)=>{
    const d=new Date(dateStr+'T12:00:00');
    let ds=d.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});
    if(!timeStr)return ds;
    let [h,m]=timeStr.split(':').map(Number);const ap=h>=12?'PM':'AM';h=h%12;if(h===0)h=12;
    return `${ds} · ${h}:${String(m).padStart(2,'0')} ${ap} ET`;
  };
  DATA.games.forEach(g=>{
    const qa=g.qbadj||{};
    const p=project(g.away,g.home,qa.home||0,qa.away||0);
    const vFav=g.spread>0?g.home:g.away;
    const vsA=((p.margin>0)===(g.spread>0))&&Math.abs(p.margin-g.spread)<2;
    const vtA=Math.abs(p.total-g.total)<2;
    let lines=`<div class="mktline"><span class="mlbl">VEGAS</span><span class="${vsA?'num-agree':'num-disagree'}">${T[vFav].abbr} -${Math.abs(g.spread).toFixed(1)}</span><span class="mdot">·</span><span class="${vtA?'num-agree':'num-disagree'}">o/u ${g.total.toFixed(1)}</span></div>`;
    const savedDK=g.dk;
    if(savedDK){
      const dFav=savedDK.s>0?g.home:g.away;
      const dsA=((p.margin>0)===(savedDK.s>0))&&Math.abs(p.margin-savedDK.s)<2;
      const dtA=Math.abs(p.total-savedDK.t)<2;
      lines+=`<div class="mktline"><span class="mlbl" style="color:var(--amber)">DK</span><span class="${dsA?'num-agree':'num-disagree'}">${T[dFav].abbr} -${Math.abs(savedDK.s).toFixed(1)}</span><span class="mdot">·</span><span class="${dtA?'num-agree':'num-disagree'}">o/u ${savedDK.t.toFixed(1)}</span></div>`;
    }
    const savedFD=g.fd;
    if(savedFD){
      const fFav=savedFD.s>0?g.home:g.away;
      const fsA=((p.margin>0)===(savedFD.s>0))&&Math.abs(p.margin-savedFD.s)<2;
      const ftA=Math.abs(p.total-savedFD.t)<2;
      lines+=`<div class="mktline"><span class="mlbl" style="color:#6aa0e0">FD</span><span class="${fsA?'num-agree':'num-disagree'}">${T[fFav].abbr} -${Math.abs(savedFD.s).toFixed(1)}</span><span class="mdot">·</span><span class="${ftA?'num-agree':'num-disagree'}">o/u ${savedFD.t.toFixed(1)}</span></div>`;
    }
    const row=document.createElement('div');row.className='game';
    row.innerHTML=`<div><div class="matchup">${g.away}<span class="at">@</span>${g.home}</div><div class="gtime">${fmtDT(g.date,g.time)}</div></div><div class="mkt">${lines}</div>`;
    row.onclick=()=>{document.querySelectorAll('#board .game').forEach(x=>x.classList.remove('active'));
      row.classList.add('active');render(g.away,g.home,g.spread,g.total);
      if(innerWidth<=820)document.getElementById('detail').scrollIntoView({behavior:'smooth'});};
    board.appendChild(row);
  });
}
buildBoard();

// build team list (by power rank)
const tl=document.getElementById('teamlist');
abbrs.slice().sort((x,y)=>T[x].ovr_rank-T[y].ovr_rank).forEach(ab=>{
  const t=T[ab];const w=(t.log||[]).filter(g=>g.res==='W').length,l=(t.log||[]).filter(g=>g.res==='L').length;
  const row=document.createElement('div');row.className='trow';
  row.dataset.name=(t.city+' '+t.name).toLowerCase();
  row.innerHTML=`<div class="trk">${t.ovr_rank}</div><div class="tnm">${t.city} ${t.name}</div><div class="trec">${w}-${l}</div>`;
  row.onclick=()=>{document.querySelectorAll('#teamlist .trow').forEach(x=>x.classList.remove('active'));
    row.classList.add('active');renderTeam(ab);
    if(innerWidth<=820)document.getElementById('teamdetail').scrollIntoView({behavior:'smooth'});};
  tl.appendChild(row);
});

// dropdowns
const aw=document.getElementById('away'),hm=document.getElementById('home');
abbrs.forEach(ab=>{const lbl=T[ab].city+' '+T[ab].name;
  aw.insertAdjacentHTML('beforeend',`<option value="${ab}">${lbl}</option>`);
  hm.insertAdjacentHTML('beforeend',`<option value="${ab}">${lbl}</option>`);});
aw.value='DEN';hm.value='KC';
document.getElementById('go').onclick=()=>{if(aw.value===hm.value){alert('Pick two different teams.');return;}
  document.querySelectorAll('#board .game').forEach(x=>x.classList.remove('active'));
  const g=DATA.games.find(x=>x.away===aw.value&&x.home===hm.value);
  if(g)render(g.away,g.home,g.spread,g.total);else render(aw.value,hm.value,null,null);
  if(innerWidth<=820)document.getElementById('detail').scrollIntoView({behavior:'smooth'});};

// team search filter
document.getElementById('team-search').addEventListener('input',e=>{
  const q=e.target.value.toLowerCase();
  document.querySelectorAll('#teamlist .trow').forEach(r=>{
    r.style.display=r.dataset.name.includes(q)?'':'none';});});

// ---- player props ----
const P=DATA.players||{};
const playerKeyByNameTeam={};
Object.keys(P).forEach(k=>{const pl=P[k];playerKeyByNameTeam[pl.name.toLowerCase()+'|'+pl.team]=k;});
function goTeam(abbr){
  document.getElementById('tab-teams').click();
  const ts=document.getElementById('team-search'); if(ts){ts.value='';document.querySelectorAll('#teamlist .trow').forEach(r=>r.style.display='');}
  renderTeam(abbr);
  const nm=(T[abbr].city+' '+T[abbr].name).toLowerCase();
  document.querySelectorAll('#teamlist .trow').forEach(r=>r.classList.toggle('active',r.dataset.name===nm));
  window.scrollTo({top:0,behavior:'smooth'});
}
function goPlayer(key){
  if(!P[key])return;
  document.getElementById('tab-players').click();
  const ps=document.getElementById('player-search'); if(ps){ps.value='';document.querySelectorAll('#playerlist .prow').forEach(r=>r.style.display='');}
  renderPlayer(key);
  document.querySelectorAll('#playerlist .prow').forEach(r=>r.classList.toggle('active',r.dataset.pkey===key));
  window.scrollTo({top:0,behavior:'smooth'});
}
const STATLABEL={pass_yds:'Passing yards',rush_yds:'Rushing yards',rec_yds:'Receiving yards',receptions:'Receptions'};
function erf(x){const t=1/(1+0.3275911*Math.abs(x));
  const y=1-(((((1.061405429*t-1.453152027)*t+1.421413741)*t-0.284496736)*t+0.254829592)*t)*Math.exp(-x*x);
  return x>=0?y:-y;}
function normCdf(x,mu,sd){return sd<=0?(x>=mu?1:0):0.5*(1+erf((x-mu)/(sd*Math.SQRT2)));}
function projStat(vals){const n=vals.length;let sw=0,m=0;
  for(let i=0;i<n;i++){const w=0.5+0.5*(n>1?i/(n-1):1);sw+=w;m+=vals[i]*w;}m/=sw;
  const mean=vals.reduce((a,b)=>a+b,0)/n;
  const sd=Math.sqrt(vals.reduce((a,b)=>a+(b-mean)*(b-mean),0)/(n>1?n-1:1));
  return {proj:m,sd};}

function renderPlayer(key){
  const pl=P[key];let blocks='';
  for(const s in pl.stats){
    const vals=pl.stats[s],{proj,sd}=projStat(vals);
    const games=vals.map(v=>Math.round(v)).join(', ');
    blocks+=`<div class="propstat" data-stat="${s}" data-proj="${proj}" data-sd="${sd}">
      <div class="ps-head"><span class="ps-name">${STATLABEL[s]}</span>
        <span class="ps-proj">proj ${proj.toFixed(1)} &nbsp;·&nbsp; swing ±${sd.toFixed(0)}</span></div>
      <div class="ps-games">Last ${vals.length}: ${games}</div>
      <div class="ps-calc">
        <label>Book's line</label>
        <input class="lineinput" type="number" step="0.5" placeholder="${proj.toFixed(1)}" data-for="${s}">
        <span class="ps-out" id="out-${s}">enter a line →</span>
        <span class="ps-lean" id="lean-${s}" style="display:none"></span>
      </div></div>`;
  }
  document.getElementById('playerdetail').innerHTML=`
    <div class="d-head"><div class="d-title">${pl.name}</div>
      <div class="d-sub">${pl.pos} · ${pl.team} &nbsp;·&nbsp; ${DATA.as_of}</div>
      <div>${injBadge(pl.inj)}</div></div>
    ${blocks}
    <div class="ps-note">Projection is recency-weighted from recent games; "swing" is the game-to-game
      standard deviation. Type the number your book is posting to get the over/under probability and lean.
      <b>Props are high-variance</b> — treat any lean as one small bet in a large volume, never a lock.
      The model can't yet see this week's injuries, snap counts, or role changes.</div>`;
  document.querySelectorAll('#playerdetail .lineinput').forEach(inp=>{
    inp.addEventListener('input',()=>{
      const box=inp.closest('.propstat'),proj=+box.dataset.proj,sd=+box.dataset.sd,s=box.dataset.stat;
      const out=document.getElementById('out-'+s),lean=document.getElementById('lean-'+s);
      const L=parseFloat(inp.value);
      if(isNaN(L)){out.textContent='enter a line →';lean.style.display='none';return;}
      const pOver=1-normCdf(L,proj,sd),pUnder=1-pOver;
      out.innerHTML=`<span class="ov">Over ${(pOver*100).toFixed(0)}%</span> · <span class="un">Under ${(pUnder*100).toFixed(0)}%</span>`;
      const side=pOver>0.524?'OVER':pUnder>0.524?'UNDER':'no edge';
      lean.style.display='';lean.textContent=side==='no edge'?'≈ coin flip':'Lean '+side;
    });
  });
}

// build player list (sorted by name)
const plist=document.getElementById('playerlist');
const pkeys=Object.keys(P).sort((a,b)=>P[a].name.localeCompare(P[b].name));
document.getElementById('pcount').textContent=pkeys.length+' players';
pkeys.forEach(k=>{const pl=P[k];const row=document.createElement('div');row.className='prow';
  row.dataset.name=pl.name.toLowerCase();row.dataset.pkey=k;
  row.innerHTML=`<div class="pnm">${pl.name}</div><div class="ppos">${pl.pos} · ${pl.team}</div>`;
  row.onclick=()=>{document.querySelectorAll('#playerlist .prow').forEach(x=>x.classList.remove('active'));
    row.classList.add('active');renderPlayer(k);
    if(innerWidth<=820)document.getElementById('playerdetail').scrollIntoView({behavior:'smooth'});};
  plist.appendChild(row);});
document.getElementById('player-search').addEventListener('input',e=>{
  const q=e.target.value.toLowerCase();
  document.querySelectorAll('#playerlist .prow').forEach(r=>{
    r.style.display=r.dataset.name.includes(q)?'':'none';});});

// results / track record
(function renderResults(){
  const R=DATA.results||[], rec=DATA.record||{ats:{},ou:{},games:0};
  document.getElementById('rec-count').textContent=(rec.games||0)+' games graded';
  const wl=o=>`${(o&&o.w)||0}-${(o&&o.l)||0}${(o&&o.p)?('-'+o.p):''}`;
  const wp=o=>`${(o&&o.wr!=null)?o.wr:0}%`;
  const rcCard=(lbl,cls,sp,tt,building)=>`<div class="rccard"><div class="rclbl ${cls}">${lbl}</div>`+
    (building?`<div class="rcbuild">building — fills in going forward</div>`:
     `<div class="rcline"><span>Spread</span><b>${wl(sp)}</b> <span class="rcp">${wp(sp)}</span></div>
      <div class="rcline"><span>Total</span><b>${wl(tt)}</b> <span class="rcp">${wp(tt)}</span></div>`)+`</div>`;
  const cards=`<div class="rccards">
    ${rcCard('OUR MODEL','model',rec.ats,rec.ou,false)}
    ${rcCard('VEGAS','',rec.vats,rec.vou,false)}
    ${rcCard('DRAFTKINGS','',null,null,true)}
    ${rcCard('FANDUEL','fdl',null,null,true)}
  </div>`;
  const note=`<div class="rec-note">Each prediction is graded <b>against our own number</b> (${rec.games||0} games): the spread hits if our pick covers the margin we projected, and the total hits if the game landed <b>under</b> our projected total. Vegas is graded the same way for a fair side-by-side. DraftKings and FanDuel start empty and build up as games finish going forward. This is a small early sample, so read it as a trend, not proof.</div>`;
  const clv=DATA.clv_summary||{n:0};
  const clvBlock=clv.n>0
    ? `<div class="rec-card" style="margin-bottom:14px"><h4>CLOSING LINE VALUE — did the model beat the closing number?</h4><div class="rec-big">${clv.beatpct}% <span style="font-size:14px;color:var(--muted)">(${clv.beat}/${clv.n})</span></div><div class="rec-sub">avg ${clv.avg>=0?'+':''}${clv.avg} pts vs close · this predicts long-run profit better than win rate</div></div>`
    : `<div class="rec-card" style="margin-bottom:14px"><h4>CLOSING LINE VALUE</h4><div class="rec-sub" style="margin-top:4px;line-height:1.55">Accrues going forward — logs the line when the model picks, then compares to the close. Fills in after your first hosted week.</div></div>`;
  const bcls=res=>res==='W'?'hit':res==='L'?'miss':'push';
  const bsym=res=>res==='W'?'✓':res==='L'?'✗':'P';
  let rows='';
  R.slice().sort((a,b)=>b.week-a.week||(a.away<b.away?-1:1)).forEach(r=>{
    const c4=(lbl,cls,s,t)=>`<div class="c4 ${cls}"><div class="l">${lbl}</div>`+(s==null?`<div class="sp" style="color:var(--muted);font-size:13px">—</div><div class="to">not logged</div>`:`<div class="sp">${lineStr(s,r.home,r.away)}</div><div class="to">o/u ${t.toFixed(1)}</div>`)+`</div>`;
    const box=(r.aq&&r.aq.length)?`<table class="boxt"><thead><tr><th>Team</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Final</th></tr></thead><tbody>
      <tr><td>${r.away}</td>${r.aq.map(x=>`<td>${x}</td>`).join('')}<td class="qtot">${r.ascore}</td></tr>
      <tr><td>${r.home}</td>${r.hq.map(x=>`<td>${x}</td>`).join('')}<td class="qtot">${r.hscore}</td></tr></tbody></table>`
      :`<div class="inj-none">Quarter breakdown not available for this game.</div>`;
    const spMargin=Math.abs(r.result);
    const won=r.result>0?r.home:(r.result<0?r.away:'tie'); const offS=Math.abs(r.pm-r.result).toFixed(1);
    const outc=r.result===0?'Game tied':`${won} won by ${spMargin}`;
    const spText=`We predicted <b>${lineStr(r.pm,r.home,r.away)}</b> — needed ${r.pick} to win by ${Math.abs(r.pm).toFixed(1)}+. ${outc}.`;
    const offT=Math.abs(r.ptot-r.tot).toFixed(1);
    const dir=r.tot<r.ptot?'under':(r.tot>r.ptot?'over':'right on');
    const ouText=`We projected <b>${r.ptot.toFixed(1)} total</b> (under = hit). Game landed on ${r.tot} — ${dir} our number.`;
    rows+=`<div class="grow">
      <div class="ghead">
        <div class="gmu"><span class="gwk">W${r.week}</span>${r.away} @ ${r.home}</div>
        <div class="gfin">${r.away} <span class="${r.ascore>r.hscore?'w':''}">${r.ascore}</span>–<span class="${r.hscore>r.ascore?'w':''}">${r.hscore}</span> ${r.home}</div>
        <div class="gbadge ${bcls(r.ats)}">SPREAD ${bsym(r.ats)}</div>
        <div class="gbadge ${bcls(r.ou)}">TOTAL ${bsym(r.ou)}<span class="gchev">▾</span></div>
      </div>
      <div class="gdetail">
        <div class="gdh">BOX SCORE</div>${box}
        <div class="gdh">THE LINE — us vs the books</div>
        <div class="cmp4">${c4('OUR MODEL','mdl',r.pm,r.ptot)}${c4('VEGAS','',r.cs,r.ct)}${c4('DRAFTKINGS','',null,null)}${c4('FANDUEL','fdl',null,null)}</div>
        <div class="gdh">DID WE HIT?</div>
        <div class="vd">
          <div class="vdr"><div class="vdk">SPREAD</div><div class="vdt">${spText}</div><div class="vdres ${bcls(r.ats)}">${r.ats==='W'?'✓ HIT':r.ats==='P'?'PUSH':'✗ MISS'}</div></div>
          <div class="vdr"><div class="vdk">TOTAL</div><div class="vdt">${ouText}</div><div class="vdres ${bcls(r.ou)}">${r.ou==='W'?'✓ HIT':r.ou==='P'?'PUSH':'✗ MISS'}</div></div>
        </div>
      </div></div>`;
  });
  document.getElementById('results-body').innerHTML=cards+clvBlock+note+
    (R.length?`<div class="board">${rows}</div>`:'<div class="inj-none">No completed games yet this season.</div>');
  document.querySelectorAll('#results-body .ghead').forEach(h=>h.onclick=()=>h.parentElement.classList.toggle('open'));
})();

// tabs (4-way)
const TABS=[['tab-games','view-games'],['tab-teams','view-teams'],['tab-players','view-players'],['tab-results','view-results']];
TABS.forEach(([tb,vw])=>{
  document.getElementById(tb).onclick=()=>{
    TABS.forEach(([t,v])=>{
      document.getElementById(t).classList.toggle('on',t===tb);
      document.getElementById(v).classList.toggle('hidden',v!==vw);});};
});
</script></body></html>'''

HTML = HTML.replace('__DATA__', DATA_JS).replace('__ASOF__', data['as_of'])
with open('./index.html','w') as f:
    f.write(HTML)
print('Built index.html —', len(HTML), 'bytes')
