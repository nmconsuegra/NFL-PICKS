"""
SharpAPI odds fetcher — DraftKings + FanDuel full-game spread & total (free tier).

Each sportsbook is walked in its OWN paced pass (draftkings, then fanduel), so FanDuel
gets a complete cursor walk instead of being the leftovers after DraftKings exhausts the
rate budget. ~5s between pages stays under the 12-requests/min free-tier limit; on HTTP 429
we back off (20/40/60s) and retry the page. Keeps only full-game main lines; skips
half/quarter, team totals, alternates. Partial lines (spread OR total) are kept, not dropped.

Returns {(away, home): {'dk': {'s':spread,'t':total}, 'fd': {'s':spread,'t':total}}}
's' internal convention: POSITIVE = home favored.  Fail-safe: errors return what's collected.
"""
import os, json, time, urllib.request, urllib.parse, urllib.error

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

def _parse_rows(rows, games):
    """Parse a page of rows into the shared games dict. Returns count added."""
    for row in rows:
        bk = {'draftkings': 'dk', 'fanduel': 'fd'}.get(str(row.get('sportsbook', '')).lower())
        if not bk: continue
        if row.get('is_alternate_line') is True: continue
        if row.get('is_main_line') is False: continue
        seg = str(row.get('market_segment') or '').lower()
        mt = str(row.get('market_type') or '').lower()
        if 'half' in seg or 'quarter' in seg or 'half' in mt or 'quarter' in mt: continue
        is_spread = 'point_spread' in mt
        is_total = 'total_points' in mt
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

def _walk_book(api_key, book, games):
    """Walk every page for ONE sportsbook, into `games`. Backs off on HTTP 429.
    Returns rows scanned for this book."""
    base = ('https://api.sharpapi.io/api/v1/odds?league=nfl'
            f'&sportsbook={book}&market=spread,total&limit=200')
    url = base; scanned = 0
    for page in range(80):                           # generous per-book cap
        req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
        payload = None
        for attempt in range(3):                     # retry this page on 429 / transient error
            try:
                with urllib.request.urlopen(req, timeout=25) as r:
                    payload = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 20 * (attempt + 1)         # back off: 20s, 40s, 60s
                    print(f'  {book}: rate-limited (429), backing off {wait}s and retrying...')
                    time.sleep(wait); continue
                print(f'  {book}: HTTP {e.code} (stopping this book):', e); return scanned
            except Exception as e:
                print(f'  {book}: page error (stopping this book):', e); return scanned
        if payload is None:                          # all retries exhausted
            print(f'  {book}: gave up after repeated 429s (using what we have)'); return scanned
        rows = payload.get('data', payload if isinstance(payload, list) else [])
        scanned += len(rows)
        _parse_rows(rows, games)
        pg = payload.get('pagination') or {}
        cur = pg.get('next_cursor')
        if pg.get('has_more') and cur:
            url = base + '&cursor=' + urllib.parse.quote(str(cur))
            time.sleep(5)                            # ~12 requests/min: the free-tier ceiling
        else:
            break
    return scanned

def fetch_odds(api_key):
    if not api_key: return {}
    games = {}; scanned = 0
    try:
        # Fetch each book in its OWN paced pass, so FanDuel gets a complete walk of its
        # own instead of being the leftovers after DraftKings exhausts the rate budget.
        for book in ('draftkings', 'fanduel'):
            scanned += _walk_book(api_key, book, games)
        # keep any book that returned a spread OR a total (don't discard a half-loaded line)
        clean = {}
        for k, books in games.items():
            bb = {b: v for b, v in books.items() if ('s' in v or 't' in v)}
            if bb: clean[k] = bb
        _full = lambda v: 's' in v and 't' in v
        print(f'SharpAPI: scanned {scanned} rows, matched {len(clean)} games '
              f'(DK: {sum(1 for v in clean.values() if "dk" in v)}, FD: {sum(1 for v in clean.values() if "fd" in v)}; '
              f'full lines — DK: {sum(1 for v in clean.values() if "dk" in v and _full(v["dk"]))}, '
              f'FD: {sum(1 for v in clean.values() if "fd" in v and _full(v["fd"]))})')
        return clean
    except Exception as e:
        print('SharpAPI fetch skipped:', e)
        return {}

if __name__ == '__main__':
    for k, v in list(fetch_odds(os.environ.get('SHARPAPI_KEY')).items())[:8]:
        print(k, v)
