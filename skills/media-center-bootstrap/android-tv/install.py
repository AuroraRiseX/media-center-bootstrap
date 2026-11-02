#!/usr/bin/env python3
"""Install local TV catalog without embedding user credentials in the APK."""
import argparse,subprocess,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--serial',required=True);p.add_argument('--catalogs',type=Path,required=True);p.add_argument('--key-file',type=Path,required=True);a=p.parse_args()
adb=['adb','-s',a.serial]
def run(*args,**kw):return subprocess.run(adb+list(args),check=True,**kw)
def output(*args):return subprocess.check_output(adb+list(args),text=True).strip()
config=json.loads(a.catalogs.read_text());assert isinstance(config,list) and config
assert a.key_file.is_file() and a.key_file.read_text().strip()
run('install','-r',str(Path(__file__).resolve().parents[3]/'dist/nuvio-tv-catalog.apk'))
run('shell','run-as','local.nuvio.catalog','mkdir','-p','files/cache')
for source,name in [(a.catalogs,'catalogs.json'),(a.key_file,'tmdb-key')]:
 with source.open('rb') as f:run('shell','run-as','local.nuvio.catalog','sh','-c',"'cat > files/"+name+"'",stdin=f)
run('shell','run-as','local.nuvio.catalog','chmod','600','files/tmdb-key')
for permission in ['android.permission.WRITE_SECURE_SETTINGS','android.permission.POST_NOTIFICATIONS']:run('shell','pm','grant','local.nuvio.catalog',permission)
run('shell','dumpsys','deviceidle','whitelist','+local.nuvio.catalog')
for op in ['RUN_IN_BACKGROUND','RUN_ANY_IN_BACKGROUND','ACCESS_RESTRICTED_SETTINGS']:run('shell','cmd','appops','set','local.nuvio.catalog',op,'allow')
run('shell','cmd','notification','allow_listener','local.nuvio.catalog/.CatalogRevival')
old=output('shell','settings','get','secure','enabled_accessibility_services')
new=':'.join(dict.fromkeys([s for s in old.split(':') if s and s!='null']+['local.nuvio.catalog/.CatalogGuard']))
run('shell','settings','put','secure','enabled_accessibility_services',new)
run('shell','settings','put','secure','accessibility_enabled','1')
run('shell','am','start','-n','local.nuvio.catalog/.MainActivity')
print('Installed. Update Nuvio through its own addon/collection interface, preserving current IDs and ordering. Validate after reboot and standby.')
