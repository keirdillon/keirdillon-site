"""Independent static builder: review by default; --production HTTPS_ORIGIN for launch."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import argparse,base64,json,posixpath,re,shutil,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from pages import PAGES
SITE=json.loads((ROOT/'site.json').read_text())
parser=argparse.ArgumentParser()
parser.add_argument('--production',default='',help='Confirmed HTTPS origin; enables indexing and domain metadata.')
parser.add_argument('--peer-origin',default='',help='Override the other brand origin for a coordinated preview.')
parser.add_argument('--output',default='dist',choices=['dist','dist-production'])
args=parser.parse_args()
def origin(value):
    u=urlsplit(value)
    if u.scheme!='https' or not u.hostname or u.username or u.password or u.port or u.path or u.query or u.fragment:raise SystemExit('Use an HTTPS origin without a path or trailing slash: '+value)
    return value
PRODUCTION=bool(args.production)
OWN=origin(args.production) if PRODUCTION else SITE.get('review_origin','')
PEER=origin(args.peer_origin) if args.peer_origin else (SITE['peer_domain'] if PRODUCTION else SITE.get('peer_review_origin') or SITE['peer_domain'])
PEER=origin(PEER)
assets=json.loads((ROOT/'src/assets.json').read_text())
byid={p['id']:p for p in PAGES}
if len(byid)!=len(PAGES) or len({p['path'] for p in PAGES})!=len(PAGES):raise SystemExit('Duplicate page ID or path')
css='\n'.join((ROOT/'src'/n).read_text() for n in ['fonts.css','style.css','visual.css','brand.css'])
scripts=(['tools.js'] if SITE['kind']=='personal' else [])+['site.js']
js='\n'.join((ROOT/'src'/n).read_text() for n in scripts)
def file_path(p):return p['path'].strip('/')+'/index.html' if p['path']!='/' else 'index.html'
def href(id,current=None):return '#'+id if current is None else posixpath.relpath(file_path(byid[id]),posixpath.dirname(file_path(current)) or '.')
def peer_tokens(text):return re.sub(r'\{\{peer:(/[a-z0-9/_-]*)\}\}',lambda m:PEER+m.group(1),text)
def nav(current=None):
    links=''.join('<a data-nav="'+id+'" href="'+href(id,current)+'"'+(' aria-current="page"' if current and current['id']==id else '')+'>'+label+'</a>' for id,label in SITE['nav'])
    return '<a class="skip" href="#main">Skip to content</a><header class="wrap"><div class="top"><div class="brand-lockup"><a class="wordmark" href="'+href('home',current)+'">'+SITE['brand']+'</a><small>'+SITE['descriptor']+'</small></div><button class="secondary menu-toggle" data-toggle-menu aria-controls="menu" aria-expanded="false">Menu</button><nav class="nav" id="menu" aria-label="Main">'+links+'</nav></div></header>'
def footer(current=None):
    if SITE['kind']=='personal':
        text='Keir Dillon · Founder of Dillon Agency';desc='Fractional CMO leadership. Practical ideas and resources for advisors.';note='Tool inputs stay in this page and are not transmitted or retained. Apply your firm’s review process to client-facing marketing.';peerlabel='Work with Dillon Agency'
    else:
        text='Dillon Agency · Led by Keir Dillon';desc='Brand strategy and marketing leadership for wealth management firms.';note='Firm services and delivery at Dillon Agency. Keir’s writing and advisor resources on his personal site.';peerlabel='Keir Dillon / Story & resources'
    return '<footer class="wrap footer"><div><span>'+text+'</span><p>'+desc+'</p><p class="note">'+note+'</p></div><div><a href="'+href('contact',current)+'">Contact</a><a href="'+PEER+'/">'+peerlabel+'</a><a href="https://linkedin.com/in/keirdillon" target="_blank" rel="noopener">LinkedIn</a><small>© 2026 '+SITE['brand']+'</small></div></footer><div id="notice" role="status" aria-live="polite" hidden></div>'
def render_body(p,current=None):
    text=re.sub(r'\[\[([a-z]+)\]\]',lambda m:href(m.group(1),current),peer_tokens(p['body']))
    def img(m):
        a=assets[m.group(1)];f=ROOT/'src/assets'/a['file']
        src='data:'+a['mime']+';base64,'+base64.b64encode(f.read_bytes()).decode() if current is None else posixpath.relpath('assets/'+a['file'],posixpath.dirname(file_path(current)) or '.')
        return 'src="'+src+'" width="'+str(a['width'])+'" height="'+str(a['height'])+'"'
    return re.sub(r'src="\{\{asset:([a-z-]+)\}\}"',img,text)
def head(title,desc,extra='',inline_css=''):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><meta name="description" content="'+escape(desc,quote=True)+'">'+extra+('<style>'+inline_css+'</style>' if inline_css else '')+'</head>'
def schema(p):
    person_domain=OWN if SITE['kind']=='personal' else PEER;agency_domain=PEER if SITE['kind']=='personal' else OWN
    person={'@type':'Person','@id':person_domain+'/#keir-dillon','name':'Keir Dillon','url':person_domain+'/','jobTitle':'Fractional CMO','sameAs':['https://linkedin.com/in/keirdillon'],'worksFor':{'@id':agency_domain+'/#organization'}}
    agency={'@type':'Organization','@id':agency_domain+'/#organization','name':'Dillon Agency','url':agency_domain+'/','founder':{'@id':person_domain+'/#keir-dillon'}}
    site={'@type':'WebSite','@id':OWN+'/#website','url':OWN+'/','name':SITE['brand'],'publisher':{'@id':person_domain+'/#keir-dillon' if SITE['kind']=='personal' else agency_domain+'/#organization'}}
    entity={'@type':'Article' if p['id'] in ['ideal','referrals','marketing'] else 'WebPage','@id':OWN+p['path']+'#page','url':OWN+p['path'],'name':p['title'],'description':p['description'],'isPartOf':{'@id':OWN+'/#website'},'author':{'@id':person_domain+'/#keir-dillon'}}
    if entity['@type']=='Article':entity['headline']=p['title']
    return json.dumps({'@context':'https://schema.org','@graph':[person,agency,site,entity]},ensure_ascii=False).replace('</',r'<\/')

# Replace only generated output in this source package, never authored source.
dist=ROOT/args.output
if dist.exists():shutil.rmtree(dist)
(dist/'assets').mkdir(parents=True)
(dist/'assets/style.css').write_text(css);(dist/'assets/site.js').write_text(js)
used=set(re.findall(r'\{\{asset:([a-z-]+)\}\}',''.join(p['body'] for p in PAGES)))
for key in used:
    a=assets[key];shutil.copyfile(ROOT/'src/assets'/a['file'],dist/'assets'/a['file'])
for p in PAGES:
    out=dist/file_path(p);out.parent.mkdir(parents=True,exist_ok=True);prefix=posixpath.relpath('assets',posixpath.dirname(file_path(p)) or '.')
    extra='<link rel="stylesheet" href="'+prefix+'/style.css">'
    if PRODUCTION:
        url=OWN+p['path']
        extra+='<link rel="canonical" href="'+url+'"><meta property="og:type" content="'+('article' if p['id'] in ['ideal','referrals','marketing'] else 'website')+'"><meta property="og:site_name" content="'+escape(SITE['brand'],quote=True)+'"><meta property="og:title" content="'+escape(p['title'],quote=True)+'"><meta property="og:description" content="'+escape(p['description'],quote=True)+'"><meta property="og:url" content="'+url+'"><script type="application/ld+json">'+schema(p)+'</script>'
    else:extra+='<meta name="robots" content="noindex,nofollow">'
    doc=head(p['title'] if SITE['brand'] in p['title'] else p['title']+' | '+SITE['brand'],p['description'],extra)+'<body data-mode="multi" data-brand="'+SITE['brand']+'">'+('' if PRODUCTION else '<div class="review-band">'+SITE['brand']+' / Website review · September 2026</div>')+nav(p)+'<main class="wrap" id="main">'+render_body(p,p)+'</main>'+footer(p)+'<script src="'+prefix+'/site.js"></script></body></html>'
    out.write_text(doc)
if PRODUCTION:
    (dist/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+OWN+'/sitemap.xml\n')
    (dist/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+OWN+p['path']+'</loc></url>' for p in PAGES)+'</urlset>')
else:(dist/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
if not PRODUCTION:
    single=head(SITE['brand']+' — Website review',PAGES[0]['description'],'<meta name="robots" content="noindex,nofollow">',css)+'<body data-mode="single" data-brand="'+SITE['brand']+'"><div class="review-band">'+SITE['brand']+' / Complete website review · September 2026</div>'+nav()+'<main class="wrap" id="main">'
    for i,p in enumerate(PAGES):single+='<section class="page" id="'+p['id']+'" data-page="'+p['id']+'" data-title="'+escape(p['title'],quote=True)+'" tabindex="-1"'+(' hidden' if i else '')+'>'+render_body(p)+'</section>'
    single+='<noscript><style>.page[hidden]{display:block!important}</style><p>All pages are shown. Enable JavaScript for navigation and interactive tools.</p></noscript></main>'+footer()+'<script>'+js+'</script></body></html>'
    (ROOT/SITE['standalone']).write_text(single)
(ROOT/'page-inventory.json').write_text(json.dumps([{k:p[k] for k in ['id','path','title','description']} for p in PAGES],indent=2))
print(json.dumps({'brand':SITE['brand'],'pages':len(PAGES),'images_used':len(used),'production':PRODUCTION,'output':str(dist),'peer_origin':PEER}))
