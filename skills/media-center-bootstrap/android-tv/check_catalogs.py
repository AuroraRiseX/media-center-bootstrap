#!/usr/bin/env python3
import concurrent.futures,json,time,urllib.request
from pathlib import Path
base='http://127.0.0.1:17864/'
manifest=json.load(urllib.request.urlopen(base+'manifest.json'))
def check(s):
 start=time.time()
 try:
  with urllib.request.urlopen(base+'catalog/'+s['type']+'/'+s['id']+'.json',timeout=120) as r:
   data=json.load(r);items=data['metas']
  assert all(m.get('id') and m.get('type')==s['type'] for m in items)
  return dict(id=s['id'],count=len(items),seconds=round(time.time()-start,2))
 except Exception as e:return dict(id=s['id'],error=str(e))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(check,manifest['catalogs']):
  results.append(r)
  if len(results)%20==0 or 'error' in r: print('checked',len(results),'last',r,flush=True)
Path(__file__).with_name('private').mkdir(exist_ok=True)
Path(__file__).with_name('private').joinpath('catalog-check.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('TOTAL',len(results),'PASSED',sum('error' not in x for x in results),'EMPTY',[x['id'] for x in results if x.get('count')==0],flush=True)
