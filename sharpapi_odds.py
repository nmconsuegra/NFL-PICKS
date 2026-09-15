"""
SharpAPI odds fetcher — DraftKings + FanDuel NFL spreads & totals (free tier).

Matches SharpAPI's documented v1 schema:
  GET https://api.sharpapi.io/api/v1/odds?league=NFL&market=spread,total
  Header: X-API-Key: <your key, starts with sk_live_>
  Response: { "data": [ {row}, ... ], "meta": {...} }
  Each row flat: sportsbook, market_type, home_team, away_team, selection, line

Returns: {(away_abbr, home_abbr): {'dk': {'s':spread,'t':total},
                                   'fd': {'s':spread,'t':total}}}
where 's' is internal convention: POSITIVE = home team favored.
Fail-safe: any error returns {} and the site falls back to manual entry.
"""
import os, json, urllib.request

NICK2ABBR = {
 'cardinals':'ARI','falcons':'ATL','ravens':'BAL','bills':'BUF','panthers':'CAR',
 'bears':'CHI','bengals':'CIN','browns':'CLE','cowboys':'DAL','broncos':'DEN',
 'lions':'DET','packers':'GB','texans':'HOU','colts':'IND','jaguars':'JAX',
 'chiefs':'KC','raiders':'LV','chargers':'LAC','rams':'LA','dolphins':'MIA',
 'vikings':'MIN','patriots':'NE','saints':'NO','giants':'NYG','jets':'NYJ',
 'eagles':'PHI','steelers':'PIT','seahawks':'SEA','49ers':'SF','buccaneers':'TB',
 'titans':'TEN','commanders':'WAS'}

def _abbr(name):
    if not name: return None
    n = str(name).lower()
    for nick, ab in NICK2ABBR.items():
        if nick in n: return ab
    return None

def fetch_odds(api_key):
    if not api_key: return {}
    try:
        url = 'https://api.sharpapi.io/api/v1/odds?league=NFL&market=spread,total'
        req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=25) as r:
            payload = json.load(r)
        rows = payload.get('data', payload if isinstance(payload, list) else [])
      (keep it lined up under 'rows'): print('SHARP RAW:', [r for r in rows if 'bills' in str(r.get('away_team','')).lower() or 'bills' in str(r.get('home_team','')).lower()][:6])
        BOOK = {'draftkings': 'dk', 'fanduel': 'fd'}
        games = {}
        for row in rows:
            bk = BOOK.get(str(row.get('sportsbook', '')).lower())
            if not bk: continue
            home = _abbr(row.get('home_team')); away = _abbr(row.get('away_team'))
            if not home or not away: continue
            line = row.get('line')
            if line is None: continue
            line = float(line)
            mkt = str(row.get('market_type', '')).lower()
            slot = games.setdefault((away, home), {}).setdefault(bk, {})
            if 'spread' in mkt:
                sel = _abbr(row.get('selection'))
                if sel == home: slot['s'] = -line
                elif sel == away: slot['s'] = line
            elif 'total' in mkt:
                slot['t'] = line
        clean = {}
        for k, books in games.items():
            bb = {b: v for b, v in books.items() if 's' in v and 't' in v}
            if bb: clean[k] = bb
        return clean
    except Exception as e:
        print('SharpAPI fetch skipped:', e)
        return {}

if __name__ == '__main__':
    res = fetch_odds(os.environ.get('SHARPAPI_KEY'))
    print(f'Got odds for {len(res)} games')
    for k, v in list(res.items())[:6]:
        print(k, v)
