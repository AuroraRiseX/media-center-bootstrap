#!/usr/bin/python3
"""Nuvio curated catalog adapter.

Serves the Stremio-compatible addon used by the Nuvio home layout (catalogs,
Chinese metadata, region artwork) plus the local collection artwork. It binds
the loopback interface and, when NUVIO_CATALOG_HOST is a LAN address, the same
port is reachable from other devices on the home network (Apple TV, Android TV).

Read-only: this service never scrapes or serves streams.
"""
import json, subprocess, hashlib, time, threading, re, concurrent.futures, os, ctypes, functools, socket, random, sys
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, parse_qs, urlparse

ROOT = Path(os.environ.get('NUVIO_CATALOG_ROOT') or Path(__file__).parent).resolve()
CONFIG = json.loads((ROOT / 'catalogs.json').read_text())
CATALOGS = {x['id']: x for x in CONFIG}
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)
KEY = (ROOT / 'tmdb-key').read_text().strip()
ADDON = 'local.nuvio.curated.zh'
HOST = os.environ.get('NUVIO_CATALOG_HOST', '127.0.0.1')
PORT = int(os.environ.get('NUVIO_CATALOG_PORT', '17863'))
ASSET_DIRS = [
    Path.home() / 'Library/Application Support/Nuvio/custom-home-zh',
    Path.home() / 'Library/Application Support/Nuvio/custom-home-video',
]
GENRES = {28: '动作', 12: '冒险', 16: '动画', 35: '喜剧', 80: '犯罪', 99: '纪录片', 18: '剧情', 10751: '家庭', 14: '奇幻', 36: '历史', 27: '恐怖', 10402: '音乐', 9648: '悬疑', 10749: '爱情', 878: '科幻', 10770: '电视电影', 53: '惊悚', 10752: '战争', 37: '西部'}
LOCKS = {}
LOCK = threading.Lock()
TMDB_LIMIT = threading.BoundedSemaphore(8)


def fetch(path, params=None, ttl=21600):
    params = dict(params or {})
    params.setdefault('language', 'zh-CN')
    cachekey = hashlib.sha256((path + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    cf = CACHE / (cachekey + '.json')
    if cf.exists() and time.time() - cf.stat().st_mtime < ttl:
        return json.loads(cf.read_text())
    with LOCK:
        lock = LOCKS.setdefault(cachekey, threading.Lock())
    with lock:
        if cf.exists() and time.time() - cf.stat().st_mtime < ttl:
            return json.loads(cf.read_text())
        opts = ['silent', 'show-error', 'get', 'max-time = 18', 'retry = 1', 'url = ' + json.dumps('https://api.tmdb.org/3/' + path), 'data-urlencode = ' + json.dumps('api_key=' + KEY)]
        opts += ['data-urlencode = ' + json.dumps(str(k) + '=' + str(v)) for k, v in params.items()]
        with TMDB_LIMIT:
            p = subprocess.run(['/usr/bin/curl', '--config', '-'], input='\n'.join(opts) + '\n', capture_output=True, text=True, timeout=42)
        if p.returncode:
            if cf.exists():
                return json.loads(cf.read_text())
            raise RuntimeError('TMDB connection failed')
        data = json.loads(p.stdout)
        if 'status_code' in data and not data.get('success', True):
            raise RuntimeError('TMDB request rejected')
        tmp = cf.with_name(cf.name + '.' + str(os.getpid()) + '.' + str(threading.get_ident()) + '.tmp')
        tmp.write_text(json.dumps(data, ensure_ascii=False))
        tmp.replace(cf)
        return data


CF = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
PTR = ctypes.c_void_p
LONG = ctypes.c_long
UTF8 = 0x08000100
CF.CFStringCreateWithCString.argtypes = [PTR, ctypes.c_char_p, ctypes.c_uint]
CF.CFStringCreateWithCString.restype = PTR
CF.CFStringCreateMutableCopy.argtypes = [PTR, LONG, PTR]
CF.CFStringCreateMutableCopy.restype = PTR
CF.CFStringTransform.argtypes = [PTR, PTR, PTR, ctypes.c_bool]
CF.CFStringTransform.restype = ctypes.c_bool
CF.CFStringGetCString.argtypes = [PTR, ctypes.c_char_p, LONG, ctypes.c_uint]
CF.CFStringGetCString.restype = ctypes.c_bool
CF.CFRelease.argtypes = [PTR]


@functools.lru_cache(maxsize=4096)
def simplified(text):
    if not text:
        return text
    source = CF.CFStringCreateWithCString(None, text.encode(), UTF8)
    mutable = CF.CFStringCreateMutableCopy(None, 0, source)
    transform = CF.CFStringCreateWithCString(None, b'Traditional-Simplified', UTF8)
    try:
        CF.CFStringTransform(mutable, None, transform, False)
        buffer = ctypes.create_string_buffer(len(text.encode()) * 4 + 256)
        return buffer.value.decode() if CF.CFStringGetCString(mutable, buffer, len(buffer), UTF8) else text
    finally:
        for ref in [source, mutable, transform]:
            CF.CFRelease(ref)


def cjk(text):
    return bool(re.search('[\u4e00-\u9fff]', text or ''))


def chinese_details(d, media):
    d = dict(d)
    titlekey = 'title' if media == 'movie' else 'name'
    if cjk(d.get(titlekey)) and cjk(d.get('overview')):
        return d
    base = media + '/' + str(d['id'])
    try:
        translations = fetch(base + '/translations').get('translations', [])
        translations = sorted([x for x in translations if x.get('iso_639_1') == 'zh'], key=lambda x: {'CN': 0, 'SG': 1, 'TW': 2, 'HK': 3}.get(x.get('iso_3166_1'), 9))
    except Exception:
        translations = []
    if not cjk(d.get(titlekey)):
        # Mainland alternative titles often exist even when the primary zh-CN title is blank.
        try:
            aliases = fetch(base + '/alternative_titles')
            aliases = aliases.get('titles', aliases.get('results', []))
            cn = next((x['title'] for x in aliases if x.get('iso_3166_1') == 'CN' and cjk(x.get('title'))), None)
        except Exception:
            cn = None
        title = cn or next((x['data'].get(titlekey) for x in translations if cjk(x.get('data', {}).get(titlekey))), None)
        if title:
            d[titlekey] = simplified(title)
    if not cjk(d.get('overview')):
        overview = next((x['data'].get('overview') for x in translations if cjk(x.get('data', {}).get('overview'))), None)
        if overview:
            d['overview'] = simplified(overview)
    return d


def preview(m, typ):
    movie = typ == 'movie'
    date = m.get('release_date' if movie else 'first_air_date', '')
    return {k: v for k, v in dict(
        id='tmdb:' + str(m['id']), type=typ,
        name=m.get('title' if movie else 'name') or m.get('original_title' if movie else 'original_name'),
        poster='https://images.tmdb.org/t/p/w500' + m['poster_path'] if m.get('poster_path') else None,
        background='https://images.tmdb.org/t/p/w1280' + m['backdrop_path'] if m.get('backdrop_path') else None,
        description=m.get('overview', ''), releaseInfo=date[:4],
        imdbRating=str(m.get('vote_average', 0)),
        genres=[GENRES.get(g, str(g)) for g in m.get('genre_ids', [])], posterShape='poster').items() if v is not None}


def catalog(cid, typ, skip=0):
    spec = CATALOGS[cid]
    if spec.get('adapter') == 'localized-platform':
        return localized_platform(spec, typ, skip)
    if spec['type'] != typ:
        raise ValueError('Wrong media type')
    params = dict(spec['query'])
    # 'page' lets a catalog start at page 2/3 so a folder can offer "more" rows.
    params.update(page=spec.get('page', 1) + skip // 20, include_adult='false')
    data = fetch('discover/' + ('movie' if typ == 'movie' else 'tv'), params)
    result = data.get('results', [])
    # A failed request never falls back to an unrelated popular list.
    if not isinstance(result, list):
        raise RuntimeError('Invalid catalog data')
    return {'metas': [preview(m, typ) for m in result]}


def meta(typ, mid):
    requested_id = mid
    if re.fullmatch(r'tt\d+', mid):
        result = fetch('find/' + mid, {'external_source': 'imdb_id'}).get('movie_results' if typ == 'movie' else 'tv_results', [])
        if not result:
            raise ValueError('Chinese metadata unavailable for this IMDb id')
        mid = 'tmdb:' + str(result[0]['id'])
    if not re.fullmatch(r'tmdb:\d+', mid):
        raise ValueError('Unsupported id')
    path = ('movie' if typ == 'movie' else 'tv') + '/' + mid.split(':')[1]
    d = chinese_details(fetch(path, {'append_to_response': 'external_ids,credits'}), 'movie' if typ == 'movie' else 'tv')
    m = preview(d, typ)
    m['id'] = requested_id
    imdb = d.get('imdb_id') or d.get('external_ids', {}).get('imdb_id')
    m.update(genres=[g['name'] for g in d.get('genres', [])], runtime=str(d.get('runtime') or '') + ' min', cast=[p['name'] for p in d.get('credits', {}).get('cast', [])[:12]], director=[p['name'] for p in d.get('credits', {}).get('crew', []) if p.get('job') == 'Director'])
    if imdb:
        m.update(imdb_id=imdb, imdbId=imdb, links=[{'name': 'IMDb', 'category': 'imdb', 'url': 'https://www.imdb.com/title/' + imdb}])
    if typ == 'series':
        episodes = []
        for season in d.get('seasons', []):
            if season['season_number'] <= 0:
                continue
            s = fetch(path + '/season/' + str(season['season_number']))
            for ep in s.get('episodes', []):
                episodes.append({'id': (imdb or mid) + ':' + str(ep['season_number']) + ':' + str(ep['episode_number']), 'title': ep['name'], 'season': ep['season_number'], 'episode': ep['episode_number'], 'released': ep.get('air_date', '') + 'T00:00:00.000Z'})
        m['videos'] = episodes
    return {'meta': m}


def upstream_catalog(spec):
    url = spec['upstream_url']
    cf = CACHE / ('upstream-' + hashlib.sha256(url.encode()).hexdigest() + '.json')
    if cf.exists() and time.time() - cf.stat().st_mtime < 21600:
        return json.loads(cf.read_text())
    p = subprocess.run(['/usr/bin/curl', '--fail', '-L', '-s', '--max-time', '20', url], capture_output=True, text=True, timeout=24)
    if p.returncode:
        if cf.exists():
            return json.loads(cf.read_text())
        raise RuntimeError('Platform catalog is temporarily unavailable')
    data = json.loads(p.stdout)
    if not isinstance(data.get('metas'), list):
        raise RuntimeError('Invalid platform catalog')
    cf.write_text(json.dumps(data, ensure_ascii=False))
    return data


def localized_platform(spec, typ, skip=0):
    if typ != spec['type']:
        raise ValueError('Wrong platform media type')
    offset = spec.get('skip_offset', 0) + skip
    items = upstream_catalog(spec)['metas'][offset:offset + 20]

    def translate(original):
        original = dict(original)
        mid = original.get('id') or original.get('imdb_id')
        media = 'movie' if typ == 'movie' else 'tv'
        try:
            tid = original.get('moviedb_id')
            d = None
            if tid:
                try:
                    d = fetch(media + '/' + str(tid), {'append_to_response': 'external_ids'})
                except Exception:
                    d = None
            actual = (d.get('imdb_id') or d.get('external_ids', {}).get('imdb_id')) if d else None
            if actual != mid:
                found = fetch('find/' + mid, {'external_source': 'imdb_id'}).get('movie_results' if typ == 'movie' else 'tv_results', [])
                if not found:
                    return original
                d = fetch(media + '/' + str(found[0]['id']), {'append_to_response': 'external_ids'})
                actual = d.get('imdb_id') or d.get('external_ids', {}).get('imdb_id')
                if actual and actual != mid:
                    return original
            d = chinese_details(d, media)
            translated = preview(d, typ)
            translated['id'] = mid
            translated['imdb_id'] = mid
            translated['imdbId'] = mid
            translated['tmdbId'] = d['id']
            translated['genres'] = [g['name'] for g in d.get('genres', [])]
            if not translated.get('description'):
                translated['description'] = original.get('description', '')
            # Remove the English clearlogo so it does not conceal the Chinese title.
            original.pop('logo', None)
            original.pop('slug', None)
            original.pop('links', None)
            original.update(translated)
            return original
        except Exception:
            return original

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return {'metas': list(pool.map(translate, items))}


ART_MEMO = {}


def region_art(cid):
    """A random movie's backdrop from that region, so the cover changes.

    The choice is held for a short window (8 s) so the folder cover and the hero
    backdrop of the same folder resolve to the same movie, while a later reload
    picks a different one.
    """
    if not cid.startswith('country-'):
        raise ValueError('Only region artwork is supported')
    items = [m for m in catalog(cid, 'movie')['metas'] if m.get('background') or m.get('poster')]
    if not items:
        raise ValueError('Region catalog has no artwork')
    bucket = int(time.time() // 8)
    cached = ART_MEMO.get(cid)
    if cached and cached[0] == bucket and cached[1].get('id') in {m.get('id') for m in items}:
        item = cached[1]
    else:
        item = random.choice(items)
        ART_MEMO[cid] = (bucket, item)
    url = item.get('background') or item.get('poster')
    if not url or not url.startswith('https://images.tmdb.org/t/p/'):
        raise ValueError('Invalid artwork source')
    cf = CACHE / ('art-' + hashlib.sha256(url.encode()).hexdigest() + '.jpg')
    if not cf.exists():
        p = subprocess.run(['/usr/bin/curl', '--fail', '-L', '-s', '--max-time', '20', url], capture_output=True, timeout=24)
        if p.returncode or not p.stdout:
            raise RuntimeError('Artwork unavailable')
        tmp = cf.with_name(cf.name + '.' + str(os.getpid()) + '.tmp')
        tmp.write_bytes(p.stdout)
        tmp.replace(cf)
    return cf.read_bytes(), item['id']


def asset(name):
    """Serve the local collection logos/covers so TVs can load them over HTTP."""
    if not re.fullmatch(r'[A-Za-z0-9._-]+\.(?:png|jpg|jpeg|webp)', name):
        raise FileNotFoundError(name)
    for directory in ASSET_DIRS:
        candidate = directory / name
        if candidate.is_file():
            return candidate.read_bytes(), candidate.suffix.lower()
    raise FileNotFoundError(name)


MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}


def lan_addresses():
    """Every usable IPv4 address of this Mac, loopback excluded.

    A Mac can be on Wi-Fi and Ethernet at once (here 192.168.3.115 and
    192.168.1.3), so report all of them instead of only the default route.
    """
    found = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith('127.') and ip not in found:
                found.append(ip)
    except Exception:
        pass
    return found


def manifest():
    return {
        'id': ADDON, 'version': '1.2.0', 'name': '中文精选目录（本机）',
        'description': '按真实出品国家、类型、制片公司和年份筛选；仅提供影视目录。',
        'resources': ['catalog', {'name': 'meta', 'types': ['movie', 'series'], 'idPrefixes': ['tmdb:', 'tt']}],
        'types': ['movie', 'series'],
        'catalogs': [{'id': x['id'], 'type': x['type'], 'name': x['title'], 'extra': [{'name': 'skip', 'isRequired': False}]} for x in CONFIG],
        'behaviorHints': {'configurable': False},
    }


class Handler(BaseHTTPRequestHandler):
    server_version = 'NuvioCuratedCatalog/1.2'
    protocol_version = 'HTTP/1.1'
    timeout = 120

    def log_message(self, *args):
        pass

    def reply(self, code, body, ctype='application/json; charset=utf-8', cache='no-cache', head=False, extra=None):
        # TVs cancel in-flight image/catalog requests while scrolling; that is
        # normal, so a closed socket is not reported as a service error.
        try:
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', cache)
            self.send_header('Content-Length', str(len(body)))
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if not head:
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        self.dispatch(False)

    def do_HEAD(self):
        self.dispatch(True)

    def dispatch(self, head):
        try:
            parsed = urlparse(self.path)
            path = unquote(parsed.path).strip('/')
            query = parse_qs(parsed.query)
            if path == 'manifest.json':
                self.reply(200, json.dumps(manifest(), ensure_ascii=False).encode(), head=head)
                return
            if path == 'health':
                data = {'status': 'ok', 'addon': ADDON, 'catalogs': len(CONFIG), 'listen': f'{HOST}:{PORT}', 'lan': [f'http://{ip}:{PORT}' for ip in lan_addresses()]}
                self.reply(200, json.dumps(data, ensure_ascii=False).encode(), head=head)
                return
            if path.startswith('art/'):
                blob, mid = region_art(path.split('/', 1)[1].removesuffix('.jpg'))
                self.reply(200, blob, 'image/jpeg', 'no-store, max-age=0', head=head, extra={'X-Source-Movie': mid})
                return
            if path.startswith('assets/'):
                blob, suffix = asset(path.split('/', 1)[1])
                self.reply(200, blob, MIME.get(suffix, 'application/octet-stream'), 'public, max-age=3600', head=head)
                return
            if path.startswith('catalog/'):
                segs = [s for s in path.removesuffix('.json').split('/') if s]
                if len(segs) < 3:
                    raise ValueError('Incomplete catalog path')
                extra = dict(query)
                if len(segs) > 3:
                    extra.update(parse_qs(segs[3]))
                data = catalog(segs[2], segs[1], int(extra.get('skip', ['0'])[0]))
                self.reply(200, json.dumps(data, ensure_ascii=False).encode(), cache='public, max-age=300', head=head)
                return
            if path.startswith('meta/'):
                _, typ, mid = path.removesuffix('.json').split('/', 2)
                data = meta(typ, mid)
                self.reply(200, json.dumps(data, ensure_ascii=False).encode(), cache='public, max-age=300', head=head)
                return
            if path in ('favicon.ico', 'robots.txt'):
                self.send_response(204)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            self.reply(404, json.dumps({'error': 'Not found'}, ensure_ascii=False).encode(), head=head)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        except FileNotFoundError:
            self.reply(404, json.dumps({'error': 'Asset not found'}, ensure_ascii=False).encode(), head=head)
        except Exception as e:
            self.reply(502, json.dumps({'error': str(e)}, ensure_ascii=False).encode(), head=head)


class Server(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        # Closing the TV app or scrolling away cancels requests; not an error.
        if isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


if __name__ == '__main__':
    Server((HOST, PORT), Handler).serve_forever()
