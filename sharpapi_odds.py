"""SharpAPI fetcher — DIAGNOSTIC BUILD. Prints what the feed actually contains so we
can see how full-game markets are named / paginated. Still returns {} safely so the
site falls back to 'not posted yet'."""
import os, json, urllib.request
from collections import Counter

def fetch_odds(api_key):
    if not api_key:
        return {}
    try:
        url = 'https://api.sharpapi.io/api/v1/odds?league=nfl&sportsbook=draftkings,fanduel&limit=500'
        req = urllib.request.Request(url, headers={'X-API-Key': api_key, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=25) as r:
            payload = json.load(r)
        rows = payload.get('data', payload if isinstance(payload, list) else [])
        print('DIAG payload keys:', list(payload.keys()) if isinstance(payload, dict) else 'LIST')
        print('DIAG links:', payload.get('links') if isinstance(payload, dict) else None)
        print('DIAG meta:', payload.get('meta') if isinstance(payload, dict) else None)
        print('DIAG total rows:', len(rows))
        print('DIAG by sportsbook:', dict(Counter(str(r.get('sportsbook')) for r in rows)))
        print('DIAG market_types:', sorted(set(str(r.get('market_type')) for r in rows)))
        print('DIAG market_segments:', sorted(set(str(r.get('market_segment')) for r in rows)))
        # first row that mentions spread, however named
        for r in rows:
            if 'spread' in str(r.get('market_type','')).lower():
                print('DIAG sample spread row:', {k: r.get(k) for k in
                      ('sportsbook','market_type','market_segment','selection','selection_type',
                       'team_side','line','is_alternate_line','is_main_line')})
                break
    except Exception as e:
        print('SharpAPI DIAG error:', e)
    return {}
