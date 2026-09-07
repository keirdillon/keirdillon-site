"""Optional Vercel adapter. Merge the example config into the existing project.

Production builds use the confirmed domain in site.json. Other builds remain
noindex. PEER_PREVIEW_ORIGIN may point to the other project's review deployment.
This script does not deploy, change DNS, or preserve an old site's routes for you.
"""
from pathlib import Path
import json,os,subprocess,sys
root=Path(__file__).resolve().parent
site=json.loads((root/'site.json').read_text())
cmd=[sys.executable,str(root/'build.py')]
if os.environ.get('VERCEL_ENV')=='production':
    cmd+=['--production',site['domain']]
elif os.environ.get('PEER_PREVIEW_ORIGIN'):
    cmd+=['--peer-origin',os.environ['PEER_PREVIEW_ORIGIN']]
subprocess.run(cmd,cwd=root,check=True)
