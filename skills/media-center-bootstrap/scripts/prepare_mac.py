#!/usr/bin/env python3
import argparse,json,os,re,shutil,datetime,plistlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',type=int,required=True);p.add_argument('--base',default='http://127.0.0.1:17863');p.add_argument('--listen',default='127.0.0.1');p.add_argument('--apply',action='store_true');p.add_argument('--tmdb-key-file',type=Path);a=p.parse_args()
if a.profile<1:p.error('profile must be >= 1')
assets=Path(__file__).resolve().parents[1]/'assets';root=Path.home()/'Library/Application Support/Nuvio';stage=a.output.resolve();stage.mkdir(parents=True,exist_ok=True)
def replace(v):
 if isinstance(v,dict):return {k:replace(x) for k,x in v.items()}
 if isinstance(v,list):return [replace(x) for x in v]
 if isinstance(v,str):return v.replace('${CATALOG_BASE}',a.base.rstrip('/')).replace('${ASSET_ROOT_URI}',root.as_uri()).replace('${ASSET_ROOT}',str(root))
 return v
snap=replace(json.loads((assets/'mac-profile.json').read_text()));missing=[]
def esc(s):
 result=''
 for c in s:
  if c in '\\=:#!':result+='\\'+c
  elif c=='\n':result+='\\n'
  elif c=='\r':result+='\\r'
  elif c=='\t':result+='\\t'
  elif ord(c)>126:result+=''.join('\\u%04x'%int.from_bytes(c.encode('utf-16-be',errors='surrogatepass')[i:i+2],'big') for i in range(0,len(c.encode('utf-16-be',errors='surrogatepass')),2))
  else:result+=c
 return result
for name,values in snap.items():
 lines=['# Portable Nuvio preferences']
 for key,obj in values.items():
  key=re.sub('_1$',f'_{a.profile}',key);value=json.dumps(obj['json'],ensure_ascii=True,separators=(',',':')) if 'json' in obj else obj['text']
  missing+=re.findall(r'\$\{(?:PRIVATE_SOURCE_\d+|SECRET_REQUIRED)\}',value);lines.append(esc(key)+'='+esc(value))
 (stage/name).write_text('\n'.join(lines)+'\n')
for n in ['collections-new.json','layout.json','platform-order.json']:
 f=assets/'tv'/n
 if f.exists():(stage/('tv-'+n)).write_text(json.dumps(replace(json.loads(f.read_text())),ensure_ascii=True,indent=2))
print('Staged configuration:',stage);print('Missing placeholders:',sorted(set(missing)))
if a.apply:
 if missing:p.error('Resolve private-source placeholders before applying; edit a private copy of the template.')
 if not a.tmdb_key_file or not a.tmdb_key_file.is_file():p.error('--tmdb-key-file required')
 running=subprocess.run(['pgrep','-f','^/Applications/Nuvio.app/Contents/MacOS/Nuvio$'],capture_output=True)
 if running.returncode==0:p.error('Quit Nuvio before applying')
 backup=root/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True)
 for f in stage.glob('*.properties'):
  dest=root/f.name
  if dest.exists():shutil.copy2(dest,backup/dest.name)
  shutil.copy2(f,dest)
 for n in ['custom-home-zh','custom-home-video']:
  if (assets/n).exists():shutil.copytree(assets/n,root/n,dirs_exist_ok=True)
 if (assets/'tv/artwork').exists():shutil.copytree(assets/'tv/artwork',root/'custom-home-video',dirs_exist_ok=True)
 service=root/'custom-catalog-service';shutil.copytree(assets/'catalog-service',service,dirs_exist_ok=True)
 shutil.copy2(a.tmdb_key_file,service/'tmdb-key');os.chmod(service/'tmdb-key',0o600)
 agent=Path.home()/'Library/LaunchAgents/local.nuvio.curated-catalog.plist';agent.parent.mkdir(exist_ok=True)
 agent.write_bytes(plistlib.dumps(dict(Label='local.nuvio.curated-catalog',ProgramArguments=[shutil.which('python3'),str(service/'server.py')],EnvironmentVariables={'NUVIO_CATALOG_HOST':a.listen},RunAtLoad=True,KeepAlive=True,StandardOutPath=str(service/'service.log'),StandardErrorPath=str(service/'service-error.log'))))
 print('Installed files; backup:',backup);print('Activate with: launchctl bootstrap gui/$(id -u)',agent);print('Then import/save within the target Nuvio account and validate after restart.')
