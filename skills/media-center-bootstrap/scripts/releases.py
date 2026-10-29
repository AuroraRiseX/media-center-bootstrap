#!/usr/bin/env python3
import json,sys,urllib.request
repo=sys.argv[1]
if repo not in ['Nemu-x/ClashFest','pengchujin/aerial-tv','NuvioMedia/NuvioDesktop','NuvioMedia/NuvioTV']:raise SystemExit('Unsupported upstream')
req=urllib.request.Request('https://api.github.com/repos/'+repo+'/releases/latest',headers={'User-Agent':'media-center-bootstrap'})
with urllib.request.urlopen(req,timeout=25) as r:j=json.load(r)
print(json.dumps({'release':j['tag_name'],'page':j['html_url'],'assets':[{'name':a['name'],'url':a['browser_download_url'],'digest':a.get('digest')} for a in j.get('assets',[])]},indent=2))
