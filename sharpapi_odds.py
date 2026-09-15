"""
SharpAPI odds fetcher — DraftKings + FanDuel FULL-GAME spread & total (free tier).

Walks ALL pages of the odds feed (default page size is only 50 rows, which covers
~1 game), filters to DraftKings/FanDuel full-game main lines, and matches teams by
their abbreviation. Skips 1st-half / 1st-quarter / alternate markets.

Returns: {(away_abbr, home_abbr): {'dk': {'s':spread,'t':total},
                                   'fd': {'s':spread,'t':total}}}
's' is internal convention: POSITIVE = home team favored.
Fail-safe: any error returns {} and the site shows "not posted yet".
"""
import os, json, urllib.request, urllib.parse

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
    node = row.get(side)
    if isinstance(node, dict) and node.get('abbreviation'):
        x = str(node['abbreviation']).upper(); x = ALIAS.get(x, x)
        if x in OURTEAMS: return x
    name = str(row.get(side + '_team', '')).lower()
    for nick, ab in NICK2ABBR.items():
        if nick in name: return ab
    return None

def _next_url(payload, base):
    links = payload.get('links') or {}
    if isinstance(links, dict) and links.get('next'):
        return links['next']
    meta = payload.get('meta') or {}
    cur = meta.get('next_cursor') or payload.get('next_cursor')
    if cur:
        return base + '&cursor=' + urllib.parse.quote(str(cur))
    return None

def fetch_odds(api_key):
    if not api_key: return {}
    base = 'https://api.sharpapi.io/api/v1/odds?league=nfl&sportsbook=draftkings,fanduel&limit=500'
    games = {}; url = base; pages = 0; scanned = 0
    try:
        while url and pages < 15:
            req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=25) as r:
                payload = json.load(r)
            rows = payload.get('data', payload if isinstance(payload, list) else [])
            scanned += len(rows)
            for row in rows:
                bk = {'draftkings': 'dk', 'fanduel': 'fd'}.get(str(row.get('sportsbook', '')).lower())
                if not bk: continue
                if row.get('is_alternate_line'): continue
                seg = str(row.get('market_segment') or '').lower()
                mt = str(row.get('market_type') or '').lower()
                if 'half' in seg or 'quarter' in seg or 'half' in mt or 'quarter' in mt: continue
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
            nxt = _next_url(payload, base)
            if not nxt or nxt == url: break
            url = nxt; pages += 1
        clean = {}
        for k, books in games.items():
            bb = {b: v for b, v in books.items() if 's' in v and 't' in v}
            if bb: clean[k] = bb
        print(f'SharpAPI: scanned {scanned} rows over {pages+1} page(s), matched {len(clean)} games '
              f'(DK: {sum(1 for v in clean.values() if "dk" in v)}, FD: {sum(1 for v in clean.values() if "fd" in v)})')
        return clean
    except Exception as e:
        print('SharpAPI fetch skipped:', e)
        return {}

if __name__ == '__main__':
    res = fetch_odds(os.environ.get('SHARPAPI_KEY'))
    for k, v in list(res.items())[:8]:
        print(k, v)
