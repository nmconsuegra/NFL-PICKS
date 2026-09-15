"""
SharpAPI odds fetcher — DraftKings + FanDuel FULL-GAME spread & total (free tier).

The free feed returns 200 rows/page across many pages (DK listed before FD), so we
walk EVERY page via the response's next_cursor until has_more is false, filtering the
query to spread+total. Keeps only full-game main lines (segment = None); skips
half/quarter, team totals, alternates. Teams matched by abbreviation. A short pause
between pages respects the 12-requests/min free-tier limit.

Returns {(away, home): {'dk': {'s':spread,'t':total}, 'fd': {'s':spread,'t':total}}}
's' internal convention: POSITIVE = home favored.  Fail-safe: errors return what's collected.
"""
import os, json, time, urllib.request, urllib.parse

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

def fetch_odds(api_key):
    if not api_key: return {}
    base = ('https://api.sharpapi.io/api/v1/odds?league=nfl'
            '&sportsbook=draftkings,fanduel&market=spread,total&limit=200')
    games = {}; scanned = 0; url = base
    try:
        for page in range(20):                       # hard cap so it can't loop forever
            req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=25) as r:
                    payload = json.load(r)
            except Exception as e:
                print('SharpAPI page error (stopping, using what we have):', e); break
            rows = payload.get('data', payload if isinstance(payload, list) else [])
            scanned += len(rows)
            for row in rows:
                bk = {'draftkings': 'dk', 'fanduel': 'fd'}.get(str(row.get('sportsbook', '')).lower())
                if not bk: continue
                if row.get('is_alternate_line'): continue
                seg = str(row.get('market_segment') or '').lower()
                mt = str(row.get('market_type') or '').lower()
                if 'half' in seg or 'quarter' in seg or 'half' in mt or 'quarter' in mt: continue
                is_spread = 'spread' in mt
                is_total = ('total' in mt) and ('team' not in mt)
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
            pg = payload.get('pagination') or {}
            cur = pg.get('next_cursor')
            if pg.get('has_more') and cur:
                url = base + '&cursor=' + urllib.parse.quote(str(cur))
                time.sleep(5)                        # stay under 12 requests/min
            else:
                break
        clean = {}
        for k, books in games.items():
            bb = {b: v for b, v in books.items() if 's' in v and 't' in v}
            if bb: clean[k] = bb
        print(f'SharpAPI: scanned {scanned} rows, matched {len(clean)} games '
              f'(DK: {sum(1 for v in clean.values() if "dk" in v)}, FD: {sum(1 for v in clean.values() if "fd" in v)})')
        return clean
    except Exception as e:
        print('SharpAPI fetch skipped:', e)
        return {}

if __name__ == '__main__':
    for k, v in list(fetch_odds(os.environ.get('SHARPAPI_KEY')).items())[:8]:
        print(k, v)
