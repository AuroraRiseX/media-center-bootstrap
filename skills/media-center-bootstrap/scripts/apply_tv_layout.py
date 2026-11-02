#!/usr/bin/env python3
"""Merge portable collections into a user's current Nuvio state; never copy accounts."""
import argparse,json,urllib.request,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--tv');p.add_argument('--state-file',type=Path);p.add_argument('--output',type=Path,default=Path('private/tv-merge.json'));p.add_argument('--apply',action='store_true');a=p.parse_args()
if a.apply and (not a.tv or a.state_file):p.error('--apply requires --tv and no --state-file')
if not a.tv and not a.state_file:p.error('specify --tv or --state-file')
base=f'http://{a.tv}:8080'
def request(path,payload=None):
 r=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=60) as f:return json.load(f)
state=json.loads(a.state_file.read_text()) if a.state_file else request('/api/state')
assets=Path(__file__).resolve().parents[1]/'assets/tv';cols=json.loads((assets/'collections-new.json').read_text());layout=json.loads((assets/'layout.json').read_text())
urls=[]
for addon in state['addons']:
 u=addon['url']
 if addon.get('id')=='local.nuvio.curated.zh' or ':17863' in u:u='http://127.0.0.1:17863'
 if u not in urls:urls.append(u)
if 'http://127.0.0.1:17863' not in urls:urls.append('http://127.0.0.1:17863')
# Preserve unrelated custom collections; replace only portable IDs.
ids={c['id'] for c in cols};cols += [c for c in state['collections'] if c['id'] not in ids]
known=[c['key'] for c in state['catalogs']];order=[k for k in layout['order'] if k in known];order += [k for k in known if k not in order]
enabled=set(layout['enabled']);managed={c['id'] for c in cols}
payload={'urls':urls,'collections':cols,'catalogOrderKeys':order,'disabledCatalogKeys':[c['disableKey'] for c in state['catalogs'] if c['key'] not in enabled and not (c['key'].startswith('collection_') and c['key'] not in layout['order'])],'disabledCollectionKeys':layout.get('disabledCollectionKeys',[]),'followAddonsOrder':layout.get('followAddonsOrder',False)}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2));a.output.chmod(0o600)
a.output.with_suffix('.before.json').write_text(json.dumps(state,ensure_ascii=False,indent=2));a.output.with_suffix('.before.json').chmod(0o600)
print('Saved local backup and preview:',a.output,'; collections:',len(cols),'; addons:',len(urls))
if a.apply:
 result=request('/api/addons',payload);print('Result:',result.get('status'))
 if result.get('status')=='pending_confirmation':
  print('Confirm on TV. After installation, run again to restore hidden rows (Nuvio enables newly installed catalogs).')
  for _ in range(40):
   status=request('/api/status/'+result['id']).get('status')
   if status in ['confirmed','rejected','not_found']:print(status);break
   time.sleep(1.5)
  else:raise SystemExit('Confirmation not completed; check TV before retrying.')
