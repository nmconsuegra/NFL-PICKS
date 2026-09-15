"""
SharpAPI odds fetcher — DraftKings + FanDuel FULL-GAME spread & total (free tier).

GET https://api.sharpapi.io/api/v1/odds?league=NFL&market=spread,total
Header: X-API-Key: <your key, starts with sk_live_>
Response: { "data": [ {row}, ... ] } — one flat row per book/market/selection.

Only FULL-GAME main lines are used (1st-half / 1st-quarter / alternate lines are
skipped). Teams are matched by the row's reliable abbreviation field.

Returns: {(away_abbr, home_abbr): {'dk': {'s':spread,'t':total},
                                   'fd': {'s':spread,'t':total}}}
where 's' is internal convention: POSITIVE = home team favored.
Fail-safe: any error returns {} and the site shows "not posted yet".
"""
import os, json, urllib.request

OURTEAMS = {'ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB','HOU',
 'IND','JAX','KC','LV','LAC','LA','MIA','MIN','NE','NO','NYG','NYJ','PHI','PIT','SEA','SF',
 'TB','TEN','WAS'}
ALIAS = {'LAR':'LA','STL':'LA','WSH':'WAS','JAC':'JAX','LVR':'LV','OAK':'LV','SD':'LAC'}
NICK2ABBR = {'cardinals':'ARI','falcons':'ATL','ravens':'BAL','bills':'BUF','panthers':'CAR',
 'bears':'CHI','bengals':'CIN','browns':'CLE','cowboys':'DAL','broncos':'DEN','lions':'DET',
 'packers':'GB','texans':'HOU','colts':'IND','jaguars':'JAX','chiefs':'KC','raiders':'LV',
 'chargers':'LAC','rams':'LA','dolphins':'MIA','vikings':'MIN','patriots':'NE','saints':'NO',
 'giants':'NYG','jets':'NYJ','eagles':'PHI','steelers':'PIT','seahawks':'SEA','49ers':'SF',
 'buccaneers':'TB','titans':'TEN','commanders':'WAS'}

def _ab(row, side):
    # prefer the reliable nested abbreviation, fall back to nickname on the name
    node = row.get(side)
    if isinstance(node, dict) and node.get('abbreviation'):
        x = str(node['abbreviation']).upper(); x = ALIAS.get(x, x)
        if x in OURTEAMS: return x
    name = str(row.get(side + '_team', '')).lower()
    for nick, ab in NICK2ABBR.items():
        if nick in name: return ab
    return None

def fetch_odds(api_key):
    if not api_key: return {}
    try:
        url = 'https://api.sharpapi.io/api/v1/odds?league=NFL&market=spread,total'
        req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=25) as r:
            payload = json.load(r)
        rows = payload.get('data', payload if isinstance(payload, list) else [])
        BOOK = {'draftkings': 'dk', 'fanduel': 'fd'}
        games = {}
        for row in rows:
            bk = BOOK.get(str(row.get('sportsbook', '')).lower())
            if not bk: continue
            if row.get('is_alternate_line'): continue                      # skip alternate lines
            seg = str(row.get('market_segment') or '').lower()
            mt = str(row.get('market_type') or '').lower()
            if 'half' in seg or 'quarter' in seg or 'half' in mt or 'quarter' in mt:
                continue                                                    # skip partial-game markets
            is_spread = 'point_spread' in mt or mt == 'spread'
            is_total = 'total_points' in mt or mt == 'total'
            if not (is_spread or is_total): continue
            line = row.get('line')
            if line is None: continue
            line = float(line)
            home = _ab(row, 'home'); away = _ab(row, 'away')
            if not home or not away: continue
            slot = games.setdefault((away, home), {}).setdefault(bk, {})
            if is_spread:
                side = str(row.get('team_side') or row.get('selection_type') or '').lower()
                if side == 'home': slot['s'] = -line
                elif side == 'away': slot['s'] = line
            elif is_total:
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
    print(f'Got FULL-GAME odds for {len(res)} games')
    for k, v in list(res.items())[:6]:
        print(k, v)
