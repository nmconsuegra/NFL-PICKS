"""
WEEKLY UPDATE  —  run this once a week (Tuesday is ideal, after data settles).
It pulls the latest games, rebuilds the ratings, and regenerates nfl_app.html.
One command:   python update.py
"""
import nflreadpy as nfl, pandas as pd, numpy as np, json, time

WINDOW = [2020,2021,2022,2023,2024,2025,2026]  # recent history is all that matters
print("Pulling latest data... (~20s)")
t0=time.time()

frames=[]
QSCORES={}
for s in WINDOW:
    pbp=nfl.load_pbp(seasons=[s]).to_pandas()
    pl=pbp[((pbp['pass']==1)|(pbp['rush']==1))].dropna(subset=['epa','posteam','defteam'])
    off=pl.groupby(['game_id','posteam']).agg(off_epa=('epa','mean')).reset_index().rename(columns={'posteam':'team'})
    frames.append(off)
    if s==max(WINDOW):
        for gid,gp in pbp.groupby('game_id'):
            gp=gp.dropna(subset=['qtr'])
            if gp.empty: continue
            ht=gp['home_team'].iloc[0]; at=gp['away_team'].iloc[0]; wk=int(gp['week'].iloc[0])
            hc=[]; ac=[]
            for q in (1,2,3,4):
                qq=gp[gp['qtr']==q]
                hc.append(float(qq['total_home_score'].iloc[-1]) if len(qq) else (hc[-1] if hc else 0.0))
                ac.append(float(qq['total_away_score'].iloc[-1]) if len(qq) else (ac[-1] if ac else 0.0))
            hq=[int(hc[0])]+[int(hc[i]-hc[i-1]) for i in range(1,4)]
            aq=[int(ac[0])]+[int(ac[i]-ac[i-1]) for i in range(1,4)]
            QSCORES[(wk,at,ht)]={'aq':aq,'hq':hq}
epa=pd.concat(frames,ignore_index=True)

sch=nfl.load_schedules(seasons=WINDOW).to_pandas()
sch=sch[sch['game_type']=='REG']
played=sch.dropna(subset=['result','home_score','away_score'])
def te(gid,t):
    r=epa[(epa['game_id']==gid)&(epa['team']==t)]
    return r['off_epa'].iloc[0] if len(r) else np.nan
rows=[]
for _,g in played.iterrows():
    ho,ao=te(g['game_id'],g['home_team']),te(g['game_id'],g['away_team'])
    if pd.isna(ho) or pd.isna(ao): continue
    rows.append({'season':g['season'],'week':g['week'],'gameday':g['gameday'],
        'home':g['home_team'],'away':g['away_team'],'hs':int(g['home_score']),'as_':int(g['away_score']),
        'home_off':ho,'away_off':ao,
        'cs':(None if pd.isna(g['spread_line']) else float(g['spread_line'])),
        'ct':(None if pd.isna(g['total_line']) else float(g['total_line']))})
games=pd.DataFrame(rows).sort_values(['season','week','gameday']).reset_index(drop=True)
print(f"  {len(games)} games through {int(games.season.max())} week {int(games[games.season==games.season.max()].week.max())}  ({time.time()-t0:.0f}s)")

# ---- ratings (walk-forward EWMA) ----
ALPHA,CARRY=0.08,0.55
off_rtg,def_rtg,recent,logs={},{},{},{}
go=lambda t:off_rtg.get(t,0.0); gd=lambda t:def_rtg.get(t,0.0)
RB0,RB1,RTB0,RTB1=1.6,51.0,45.5,27.0
CURSEASON=int(games['season'].max())
import json as _json
try: DKFD_HIST=_json.load(open('dkfd_history.json'))
except Exception: DKFD_HIST={}
def _bkgrade(res,tot_act,sp,tt):
    if sp is None or tt is None: return None,None
    a2='P' if res==sp else ('W' if ((res>sp) if sp>=0 else (res<sp)) else 'L')
    o2='P' if tot_act==tt else ('W' if tot_act<tt else 'L')
    return a2,o2
results=[]
prev=None
for _,g in games.iterrows():
    if prev is not None and g['season']!=prev:
        for t in list(off_rtg):off_rtg[t]*=CARRY
        for t in list(def_rtg):def_rtg[t]*=CARRY
    prev=g['season']
    h,a,ho,ao=g['home'],g['away'],g['home_off'],g['away_off']
    if g['season']==CURSEASON and g['cs'] is not None and g['ct'] is not None:
        sd=(go(h)+gd(h))-(go(a)+gd(a)); comb=(go(h)-gd(a))+(go(a)-gd(h))
        pm=RB0+RB1*sd; ptot=RTB0+RTB1*comb
        cs=float(g['cs']); ct=float(g['ct']); res=float(g['hs']-g['as_']); tot_act=int(g['hs']+g['as_'])
        pick=h if pm>0 else a
        cover=(res>pm) if pm>=0 else (res<pm)                 # did our winner cover OUR number
        ats='P' if res==pm else ('W' if cover else 'L')
        ou='P' if tot_act==ptot else ('W' if tot_act<ptot else 'L')   # under our total = hit
        vcov=(res>cs) if cs>=0 else (res<cs)                  # grade Vegas the same standalone way
        vats='P' if res==cs else ('W' if vcov else 'L')
        vou='P' if tot_act==ct else ('W' if tot_act<ct else 'L')
        qs=QSCORES.get((int(g['week']),a,h))
        aq=qs['aq'][:] if qs else []; hq=qs['hq'][:] if qs else []
        if aq: aq[-1]+=int(g['as_'])-sum(aq)
        if hq: hq[-1]+=int(g['hs'])-sum(hq)
        _dkl=DKFD_HIST.get(f"{CURSEASON}-{int(g['week'])}-{a}-{h}",{})
        dk_ats,dk_ou=_bkgrade(res,tot_act,_dkl.get('dk_s'),_dkl.get('dk_t'))
        fd_ats,fd_ou=_bkgrade(res,tot_act,_dkl.get('fd_s'),_dkl.get('fd_t'))
        _re={'week':int(g['week']),'away':a,'home':h,'ascore':int(g['as_']),'hscore':int(g['hs']),
            'result':res,'cs':cs,'pm':round(pm,1),'ats':ats,'pick':pick,'aq':aq,'hq':hq,
            'ct':ct,'ptot':round(ptot,1),'tot':tot_act,'ou':ou,'vats':vats,'vou':vou}
        if dk_ats: _re['dk_ats']=dk_ats; _re['dk_ou']=dk_ou
        if fd_ats: _re['fd_ats']=fd_ats; _re['fd_ou']=fd_ou
        results.append(_re)
    off_rtg[h]=go(h)+ALPHA*((ho+gd(a))-go(h)); off_rtg[a]=go(a)+ALPHA*((ao+gd(h))-go(a))
    def_rtg[h]=gd(h)+ALPHA*((go(a)-ao)-gd(h));  def_rtg[a]=gd(a)+ALPHA*((go(h)-ho)-gd(a))
    for t,oe in [(h,ho),(a,ao)]: recent.setdefault(t,[]).append(oe)
    if g['season']>=games.season.max()-1:
        for team,opp,pf,pa,oe in [(h,a,g['hs'],g['as_'],ho),(a,h,g['as_'],g['hs'],ao)]:
            logs.setdefault(team,[]).append({'season':int(g['season']),'week':int(g['week']),'opp':opp,
                'pf':int(pf),'pa':int(pa),'res':'W' if pf>pa else 'L' if pf<pa else 'T','off':round(float(oe),3)})

teams=sorted(off_rtg); overall={t:go(t)+gd(t) for t in teams}
off_rank={t:r+1 for r,t in enumerate(sorted(teams,key=lambda x:-go(x)))}
def_rank={t:r+1 for r,t in enumerate(sorted(teams,key=lambda x:-gd(x)))}
ovr_rank={t:r+1 for r,t in enumerate(sorted(teams,key=lambda x:-overall[x]))}
NAMES={'ARI':'Cardinals','ATL':'Falcons','BAL':'Ravens','BUF':'Bills','CAR':'Panthers','CHI':'Bears','CIN':'Bengals','CLE':'Browns','DAL':'Cowboys','DEN':'Broncos','DET':'Lions','GB':'Packers','HOU':'Texans','IND':'Colts','JAX':'Jaguars','KC':'Chiefs','LV':'Raiders','LAC':'Chargers','LA':'Rams','LAR':'Rams','MIA':'Dolphins','MIN':'Vikings','NE':'Patriots','NO':'Saints','NYG':'Giants','NYJ':'Jets','PHI':'Eagles','PIT':'Steelers','SEA':'Seahawks','SF':'49ers','TB':'Buccaneers','TEN':'Titans','WAS':'Commanders'}
CITY={'ARI':'Arizona','ATL':'Atlanta','BAL':'Baltimore','BUF':'Buffalo','CAR':'Carolina','CHI':'Chicago','CIN':'Cincinnati','CLE':'Cleveland','DAL':'Dallas','DEN':'Denver','DET':'Detroit','GB':'Green Bay','HOU':'Houston','IND':'Indianapolis','JAX':'Jacksonville','KC':'Kansas City','LV':'Las Vegas','LAC':'Los Angeles','LA':'Los Angeles','LAR':'Los Angeles','MIA':'Miami','MIN':'Minnesota','NE':'New England','NO':'New Orleans','NYG':'New York','NYJ':'New York','PHI':'Philadelphia','PIT':'Pittsburgh','SEA':'Seattle','SF':'San Francisco','TB':'Tampa Bay','TEN':'Tennessee','WAS':'Washington'}
def form(t,n=4):
    g=recent.get(t,[])[-n:]; return round(float(np.mean(g)),3) if g else 0.0
team_data={}
for t in teams:
    team_data[t]={'abbr':t,'name':NAMES.get(t,t),'city':CITY.get(t,t),'off':round(go(t),3),'def':round(gd(t),3),
        'overall':round(overall[t],3),'off_rank':off_rank[t],'def_rank':def_rank[t],'ovr_rank':ovr_rank[t],
        'form_off':form(t),'form_def':0.0,'log':logs.get(t,[])[-8:]}

up=sch[sch['result'].isna()].dropna(subset=['spread_line','total_line'])
gl=[]
for _,g in up.sort_values(['gameday','gametime']).iterrows():
    if g['home_team'] in team_data and g['away_team'] in team_data:
        gl.append({'week':int(g['week']),'away':g['away_team'],'home':g['home_team'],
            'spread':float(g['spread_line']),'total':float(g['total_line']),
            'date':str(g['gameday']),'time':(None if pd.isna(g['gametime']) else str(g['gametime']))})
import urllib.request, json as _json
STAD={'ARI':(33.5277,-112.2626,'retract'),'ATL':(33.7554,-84.4008,'retract'),'BAL':(39.2780,-76.6227,'open'),'BUF':(42.7738,-78.7870,'open'),'CAR':(35.2258,-80.8528,'open'),'CHI':(41.8623,-87.6167,'open'),'CIN':(39.0954,-84.5160,'open'),'CLE':(41.5061,-81.6995,'open'),'DAL':(32.7473,-97.0945,'retract'),'DEN':(39.7439,-105.0201,'open'),'DET':(42.3400,-83.0456,'dome'),'GB':(44.5013,-88.0622,'open'),'HOU':(29.6847,-95.4107,'retract'),'IND':(39.7601,-86.1639,'retract'),'JAX':(30.3239,-81.6373,'open'),'KC':(39.0489,-94.4839,'open'),'LV':(36.0909,-115.1833,'dome'),'LAC':(33.9535,-118.3392,'dome'),'LA':(33.9535,-118.3392,'dome'),'LAR':(33.9535,-118.3392,'dome'),'MIA':(25.9580,-80.2389,'open'),'MIN':(44.9736,-93.2575,'dome'),'NE':(42.0909,-71.2643,'open'),'NO':(29.9511,-90.0812,'dome'),'NYG':(40.8135,-74.0745,'open'),'NYJ':(40.8135,-74.0745,'open'),'PHI':(39.9008,-75.1675,'open'),'PIT':(40.4468,-80.0158,'open'),'SEA':(47.5952,-122.3316,'open'),'SF':(37.4030,-121.9700,'open'),'TB':(27.9759,-82.5033,'open'),'TEN':(36.1665,-86.7713,'open'),'WAS':(38.9076,-76.8645,'open')}
_wxc={}
def fetch_wx(lat,lon,date,tm):
    if not tm: return None
    ck=(round(lat,2),round(lon,2),date)
    try:
        if ck not in _wxc:
            url=(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,wind_speed_10m,weather_code&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America%2FNew_York&forecast_days=16")
            with urllib.request.urlopen(url,timeout=15) as r: _wxc[ck]=_json.load(r)
        d=_wxc[ck];hrs=d['hourly']['time'];cand=[h for h in hrs if h.startswith(date)]
        if not cand: return None
        hr=int(tm[:2]);pick=min(cand,key=lambda h:abs(int(h[11:13])-hr));i=hrs.index(pick)
        return {'temp':round(d['hourly']['temperature_2m'][i]),'wind':round(d['hourly']['wind_speed_10m'][i]),'precip':d['hourly']['precipitation_probability'][i],'code':d['hourly']['weather_code'][i]}
    except Exception: return None
for g in gl:
    st=STAD.get(g['home'])
    if not st: g['wx']=None; continue
    lat,lon,roof=st
    if roof in ('dome','retract'): g['wx']={'indoor':True,'roof':('Dome' if roof=='dome' else 'Retractable roof')}
    else: g['wx']=fetch_wx(lat,lon,g['date'],g['time'])
# ---- optional: auto-fetch DraftKings & FanDuel odds via SharpAPI (needs SHARPAPI_KEY) ----
try:
    import os
    from sharpapi_odds import fetch_odds
    _odds=fetch_odds(os.environ.get('SHARPAPI_KEY'))
    for g in gl:
        bm=_odds.get((g['away'],g['home']))
        if bm:
            if 'dk' in bm: g['dk']=bm['dk']
            if 'fd' in bm: g['fd']=bm['fd']
    if _odds: print(f'SharpAPI: odds attached for {len(_odds)} games')
    # snapshot DK/FD lines so completed games can be graded going forward
    for g in gl:
        if not g.get('dk') and not g.get('fd'): continue
        k=f"{CURSEASON}-{g['week']}-{g['away']}-{g['home']}"
        rec=DKFD_HIST.get(k,{})
        if g.get('dk'): rec['dk_s']=g['dk']['s']; rec['dk_t']=g['dk']['t']
        if g.get('fd'): rec['fd_s']=g['fd']['s']; rec['fd_t']=g['fd']['t']
        DKFD_HIST[k]=rec
    _json.dump(DKFD_HIST,open('dkfd_history.json','w'))
except Exception as e:
    print('SharpAPI hook skipped (manual entry still works):', e)
unplayed=sch[(sch['game_type']=='REG')&(sch['result'].isna())].sort_values(['week','gameday'])
for t in team_data:
    tg=unplayed[(unplayed['home_team']==t)|(unplayed['away_team']==t)]
    if len(tg):
        g0=tg.iloc[0]; hm=(g0['home_team']==t)
        team_data[t]['next']={'opp':(g0['away_team'] if hm else g0['home_team']),'home':bool(hm),
            'week':int(g0['week']),'date':str(g0['gameday']),
            'spread':(None if pd.isna(g0['spread_line']) else float(g0['spread_line'])),
            'total':(None if pd.isna(g0['total_line']) else float(g0['total_line']))}
    else:
        team_data[t]['next']=None
maxwk=int(games[games.season==games.season.max()].week.max())
# ---- player props ----
pstats=nfl.load_player_stats(seasons=[games.season.max()-1,games.season.max()]).to_pandas()
pstats=pstats[pstats['position'].isin(['QB','RB','WR','TE'])].sort_values(['season','week'])
SBP={'QB':['passing_yards','rushing_yards'],'RB':['rushing_yards','receiving_yards','receptions'],
     'WR':['receiving_yards','receptions'],'TE':['receiving_yards','receptions']}
SH={'passing_yards':'pass_yds','rushing_yards':'rush_yds','receiving_yards':'rec_yds','receptions':'receptions'}
players={}
for (nm,pos),grp in pstats.groupby(['player_display_name','position']):
    if len(grp)<4: continue
    tm=grp['team'].iloc[-1]; key=nm if nm not in players else f"{nm} ({tm})"; st={}
    for col in SBP[pos]:
        v=grp[col].dropna().astype(float).tolist()[-8:]
        if v: st[SH[col]]=[round(x,1) for x in v]
    main=SH[SBP[pos][0]]
    if main in st and sum(st[main])/len(st[main])>=15:
        players[key]={'name':nm,'pos':pos,'team':tm,'stats':st}
# ---- player prop grading (walk-forward, graded vs our own projection) ----
notable=set(players[k]['name'] for k in players)
def _wproj(vals):
    v=vals[-8:]; n=len(v)
    if n<3: return None
    ws=[0.5+0.5*(i/(n-1) if n>1 else 1) for i in range(n)]
    return sum(v[i]*ws[i] for i in range(n))/sum(ws)
prop_results=[]; cur_s=int(games.season.max())
for (nm,pos),grp in pstats.groupby(['player_display_name','position']):
    if nm not in notable or pos not in SBP: continue
    grp=grp.sort_values(['season','week'])
    for _,row in grp[grp['season']==cur_s].iterrows():
        wk=int(row['week']); tm=row['team']; ent={}
        for col in SBP[pos]:
            prior=grp[(grp['season']<cur_s)|((grp['season']==cur_s)&(grp['week']<wk))][col].dropna().astype(float).tolist()
            proj=_wproj(prior)
            if proj is None or pd.isna(row[col]): continue
            actual=float(row[col]); res='W' if actual>proj else ('L' if actual<proj else 'P')
            ent[SH[col]]=[round(proj,1),round(actual),res]
        if ent: prop_results.append({'w':wk,'p':nm,'pos':pos,'tm':tm,'s':ent})
def _prec(k):
    w=l=p=0
    for e in prop_results:
        if k in e['s']:
            r=e['s'][k][2]
            if r=='W':w+=1
            elif r=='L':l+=1
            else:p+=1
    n=w+l; return {'w':w,'l':l,'p':p,'wr':round(w/n*100,1) if n else 0}
prop_record={'rec_yds':_prec('rec_yds'),'receptions':_prec('receptions'),'rush_yds':_prec('rush_yds'),'pass_yds':_prec('pass_yds')}
inj_week=None
try:
    ij=nfl.load_injuries(seasons=[int(games.season.max())]).to_pandas()
    ij=ij[ij['report_status'].isin(['Out','Doubtful','Questionable'])]
    for t in team_data: team_data[t]['inj']=[]
    if len(ij):
        inj_week=int(ij['week'].max()); ij=ij[ij['week']==inj_week]
        ordr={'Out':0,'Doubtful':1,'Questionable':2}
        for tm,grp in ij.groupby('team'):
            if tm not in team_data: continue
            lst=[{'name':str(r['full_name']),'pos':str(r['position']),'status':str(r['report_status']),
                  'note':('' if pd.isna(r['practice_primary_injury']) else str(r['practice_primary_injury']))} for _,r in grp.iterrows()]
            lst.sort(key=lambda x:ordr.get(x['status'],3)); team_data[tm]['inj']=lst[:10]
except Exception as e:
    print('injury pull failed:',e)
    for t in team_data: team_data[t]['inj']=[]
import re as _re
def nrm(s):
    s=str(s).lower().replace('.','').replace("'",'').replace('-',' ')
    s=_re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s)
    return ' '.join(s.split())
inj_lookup={}
for t in team_data:
    for x in team_data[t].get('inj',[]): inj_lookup[(nrm(x['name']),t)]={'status':x['status'],'note':x['note']}
for pl in players.values(): pl['inj']=inj_lookup.get((nrm(pl['name']),pl['team']))
# ---- QB adjustment: downgrade a team's projection when its starter is OUT ----
try:
    _qb=pstats[(pstats['position']=='QB')].dropna(subset=['attempts']); _qb=_qb[_qb['attempts']>0]
    _agg=_qb.groupby(['player_display_name','team']).agg(epa=('passing_epa','sum'),att=('attempts','sum')).reset_index()
    LEAGUE_QB=_qb['passing_epa'].sum()/_qb['attempts'].sum(); _agg['ea']=_agg['epa']/_agg['att']
    starters,backups,qbval={},{},{}
    for tm,grp in _agg.sort_values('att',ascending=False).groupby('team'):
        rws=grp.to_dict('records'); starters[tm]=rws[0]['player_display_name']
        if len(rws)>1: backups[tm]=rws[1]['player_display_name']
        for r in rws: qbval[(r['player_display_name'],tm)]=r['ea'] if r['att']>=30 else None
    qb_out=set()
    if inj_week:
        for _,r in ij[ij['position']=='QB'].iterrows():
            if str(r['report_status']) in ('Out','Doubtful'): qb_out.add((nrm(str(r['full_name'])),r['team']))
    def _qb_delta(team):
        st=starters.get(team)
        if not st or (nrm(st),team) not in qb_out: return 0.0,None
        sv=qbval.get((st,team)); sv=sv if sv is not None else LEAGUE_QB
        bk=backups.get(team); bv=qbval.get((bk,team)) if bk else None
        bv=bv if bv is not None else (LEAGUE_QB-0.10)
        d=max(-0.15,min(0.05,(bv-sv)*0.58))
        return round(d,3),(f"{st} OUT"+(f" \u2192 {bk}" if bk else ""))
    for g in gl:
        dh,nh=_qb_delta(g['home']); da,na=_qb_delta(g['away'])
        if dh or da: g['qbadj']={'home':dh,'away':da,'hnote':nh,'anote':na}
except Exception as e:
    print('QB adjustment skipped:',e)
cur=sch[(sch['season']==games.season.max())&(sch['game_type']=='REG')]
for t in team_data: team_data[t]['sched']=[]
for _,g in cur.sort_values(['week']).iterrows():
    pl_=not pd.isna(g['result'])
    for team,opp,hm,pf,pa in [(g['home_team'],g['away_team'],True,g['home_score'],g['away_score']),
                              (g['away_team'],g['home_team'],False,g['away_score'],g['home_score'])]:
        if team not in team_data: continue
        e={'week':int(g['week']),'opp':opp,'home':bool(hm),'played':bool(pl_),
           'date':str(g['gameday']),'time':(None if pd.isna(g['gametime']) else str(g['gametime']))}
        if pl_: e['pf']=int(pf); e['pa']=int(pa); e['res']='W' if pf>pa else 'L' if pf<pa else 'T'
        team_data[team]['sched'].append(e)
def _rec(key):
    w=sum(1 for r in results if r[key]=='W'); l=sum(1 for r in results if r[key]=='L')
    pu=sum(1 for r in results if r[key]=='P'); n=w+l
    return {'w':w,'l':l,'p':pu,'wr':round(w/n*100,1) if n else 0,'roi':round((w*0.909-l)/n*100,1) if n else 0}
record={'ats':_rec('ats'),'ou':_rec('ou'),'vats':_rec('vats'),'vou':_rec('vou'),'games':len(results),'season':CURSEASON}
# ---- CLV tracking: records the line when the model picks, compares to close (accrues over daily runs) ----
try:
    import os as _os, json as _js
    LH='line_history.json'; hist={}
    if _os.path.exists(LH):
        try: hist=_js.load(open(LH))
        except Exception: hist={}
    def _gk(aw,hm,wk): return f"{wk}:{aw}@{hm}"
    nowts=str(pd.Timestamp.utcnow())[:16]
    for g in gl:
        k=_gk(g['away'],g['home'],g['week']); hh=team_data[g['home']]; aa=team_data[g['away']]
        qa=g.get('qbadj') or {}
        pm=RB0+RB1*((hh['off']+hh['def'])-(aa['off']+aa['def'])+qa.get('home',0)-qa.get('away',0))
        rec=hist.get(k,{})
        if 'open_spread' not in rec:
            rec.update({'away':g['away'],'home':g['home'],'week':g['week'],'open_spread':g['spread'],
                'open_total':g['total'],'pick_home':bool(pm>g['spread']),'opened':nowts})
        rec['cur_spread']=g['spread']; rec['cur_total']=g['total']; rec['updated']=nowts; hist[k]=rec
    clv=[]
    for r in results:
        rec=hist.get(_gk(r['away'],r['home'],r['week']))
        if rec and 'open_spread' in rec:
            osp=rec['open_spread']; pts=(osp-r['cs']) if rec['pick_home'] else (r['cs']-osp)
            clv.append({'week':r['week'],'away':r['away'],'home':r['home'],'open':osp,'close':r['cs'],'pts':round(pts,1),'beat':pts>0})
    _js.dump(hist, open(LH,'w'))
    n=len(clv); beat=sum(1 for c in clv if c['beat'])
    clv_summary={'n':n,'beat':beat,'beatpct':round(beat/n*100,1) if n else 0,'avg':round(sum(c['pts'] for c in clv)/n,2) if n else 0}
except Exception as e:
    print('CLV tracking skipped:',e); clv=[]; clv_summary={'n':0,'beat':0,'beatpct':0,'avg':0}
out={'teams':team_data,'games':gl,'players':players,'inj_week':inj_week,'results':results,'record':record,'prop_results':prop_results,'prop_record':prop_record,'clv':clv,'clv_summary':clv_summary,'cal':{'B0':1.6,'B1':51.0,'TB0':45.5,'TB1':27.0},
     'as_of':f'Through {int(games.season.max())} Week {maxwk}'}
json.dump(out,open('./nfl_data.json','w'))
print(f"  Ratings rebuilt. Upcoming games with lines: {len(gl)}")

import subprocess
subprocess.run(['python3','./build_site.py'])
print("DONE — nfl_app.html regenerated with the latest games.")
