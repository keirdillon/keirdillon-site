"""Static content, assets, navigation, SEO, and browser-tool logic checks.

Does not claim browser rendering, clipboard/mail-client operation, or live indexing.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import argparse,json,subprocess,tempfile,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'site.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--peer-project');args=parser.parse_args()
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.targets=[];self.assets=[];self.images=[];self.scripts=[];self.schemas=[];self.script=None;self.script_type=None;self.h1=0;self.canonical=[];self.robots=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag in ('a','link') and a.get('href'):self.links.append(a['href'])
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content',''))
  for k in ['data-copy','data-download','data-example','data-output','data-go','aria-controls','aria-labelledby','for']:
   if a.get(k):self.targets.extend(a[k].split())
  if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
  if tag=='img':self.images.append(a)
  if tag=='script' and not a.get('src'):self.script='';self.script_type=a.get('type','')
 def handle_data(self,data):
  if self.script is not None:self.script+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.script is not None:
   (self.schemas if self.script_type=='application/ld+json' else self.scripts).append(self.script);self.script=None

files=[ROOT/S['standalone']]+sorted((ROOT/'dist').rglob('*.html'))
if (ROOT/'dist-production').exists():files+=sorted((ROOT/'dist-production').rglob('*.html'))
for file in files:
 text=file.read_text();doc=Doc(text)
 assert not [x for x,n in Counter(doc.ids).items() if n>1],(file,'duplicate IDs')
 for target in doc.targets:assert target in doc.ids,(file,target,'missing control target')
 for marker in ['[[','{{']:assert marker not in text,(file,'unresolved marker',marker)
 for link in doc.links+doc.assets:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=file.parent/unquote(u.path) if u.path else file
  assert target.exists(),(file,link,'missing local file')
  if u.fragment and target.suffix=='.html':assert u.fragment in Doc(target.read_text()).ids,(file,link,'missing anchor')
 for a in doc.images:assert a.get('alt') and a.get('width') and a.get('height'),(file,'image lacks accessible description or dimensions')
 for code in doc.scripts:
  with tempfile.NamedTemporaryFile(suffix='.js',mode='w') as t:
   t.write(code);t.flush();subprocess.run(['node','--check',t.name],check=True,capture_output=True)
 if file.name==S['standalone']:
  assert not any(urlsplit(x).scheme in ('https','http') for x in doc.assets),'remote required asset'
  assert 'url(data:' in text or 'url("data:' in text or 'url(\'data:' in text,'embedded fonts missing'
  assert len(set(x['src'] for x in doc.images))==len(doc.images),'repeated image in review'
 else:assert doc.h1==1,(file,'expected one H1')
 if 'dist-production' in file.parts:
  assert not any('noindex' in x for x in doc.robots),(file,'production is noindex')
  relative=file.relative_to(ROOT/'dist-production').as_posix();route='/' if relative=='index.html' else '/'+relative.removesuffix('index.html')
  assert doc.canonical==[S['domain']+route],(file,'canonical mismatch',doc.canonical)
  assert 'chatgpt.site' not in text,(file,'review URL in production')
  assert len(doc.schemas)==1,(file,'missing structured data')
  graph=json.loads(doc.schemas[0])['@graph'];assert {g['@type'] for g in graph}>={'Person','Organization','WebSite'}
 else:assert 'noindex,nofollow' in doc.robots,(file,'review indexing')

for a in json.loads((ROOT/'src/assets.json').read_text()).values():
 f=ROOT/'src/assets'/a['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'],('source asset changed',f)
for name in ['site.js']+(['tools.js'] if S['kind']=='personal' else []):subprocess.run(['node','--check',str(ROOT/'src'/name)],check=True,capture_output=True)
if S['kind']=='personal':
 subprocess.run(['node','-e',r'''
 const assert=require('node:assert/strict'), t=require('./src/tools.js');
 assert.throws(()=>t.brief({}),/Complete every field/);
 const b={audience:'  business owners ',moment:'considering a sale',help:'organizing the questions',process:'mapping decisions',proof:'documented process',channel:'existing association'};
 const result=t.brief(b);assert(result.includes('I work with business owners. My focus is organizing the questions.'));assert(!result.includes('  business'));
 assert(t.brief({...b,audience:'<script>alert(1)</script>'}).includes('<script>alert(1)</script>'));
 assert(t.audit(Array(8).fill('yes')).includes('8 clear / 0 partial / 0 missing'));
 const mixed=t.audit(['partly','yes','yes','yes','no','no','yes','yes']);assert(mixed.includes('5 clear / 1 partial / 2 missing'));assert(mixed.indexOf('Replace an unsupported promise')<mixed.indexOf('Make the client situation specific'));
 assert.throws(()=>t.audit(['yes']),/all eight/);assert.throws(()=>t.audit(Array(8).fill('unknown')),/all eight/);assert.throws(()=>t.content({}),/Complete the audience/);
 const c=t.content({audience:'retirees',question:'What happens first?',answer:'We discuss your questions.',next:'Ask a question.'});assert(c.includes('WEEK 4 | Show the process'));assert(c.includes('Your factual starting answer: We discuss your questions.'));
 '''],cwd=ROOT,check=True,capture_output=True)
if (ROOT/'dist-production/sitemap.xml').exists():
 urls=[x.text for x in ET.parse(ROOT/'dist-production/sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
 assert len(urls)==len(list((ROOT/'dist-production').rglob('*.html')))
 assert all(u.startswith(S['domain']+'/') for u in urls)
 assert 'Disallow: /' not in (ROOT/'dist-production/robots.txt').read_text()
peer_count=0
if args.peer_project:
 peer=Path(args.peer_project);cfg=json.loads((peer/'site.json').read_text());routes={p['path'] for p in json.loads((peer/'page-inventory.json').read_text())}
 origins=[cfg['domain'],cfg['review_origin']]
 for file in files:
  for link in Doc(file.read_text()).links:
   u=urlsplit(link)
   if u.scheme+'://'+u.netloc in origins:
    assert u.path in routes,(file,link,'missing peer route');peer_count+=1
 for name in ['fonts.css','style.css','visual.css','brand.css']:
  assert (ROOT/'src'/name).read_bytes()==(peer/'src'/name).read_bytes(),('design file differs',name)
report={'status':'passed','brand':S['brand'],'pages':len(list((ROOT/'dist').rglob('*.html'))),'html_files_checked':len(files),'peer_links_checked':peer_count,'production_metadata_checked':(ROOT/'dist-production').exists(),'checks':['Page/control IDs','Local links and assets','Single-file offline embedding','One H1 per published page','Source photo hashes','JavaScript syntax','Review indexing','Production canonicals, sitemap and entity graph when built','Three advisor tool functions for personal site'],'not_tested':['Browser rendering','Mail client launch, clipboard and downloads in a browser','Live search indexing','Existing production-site integrations']}
(ROOT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
