"""Shared presentational helpers. Each project contains its own copy."""
def pic(key,alt,cls='',caption='',eager=False):
    return f'<figure class="photo {cls}"><img src="{{{{asset:{key}}}}}" alt="{alt}" loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'+ (f'<figcaption>{caption}</figcaption>' if caption else '')+'</figure>'

def page(id,path,title,description,body):
    return dict(id=id,path=path,title=title,description=description,body=body)

def contact(brand,subject):
    from urllib.parse import quote
    return '''<section class="contact-opening"><div><p class="kicker">'''+brand+''' / Contact</p><h1>A useful conversation<br><em>starts with your context.</em></h1><p class="intro">Tell me what you’re building, where the work is getting stuck, and what you want to change.</p></div><div class="contact-panel metal-surface"><h2>Let’s talk.</h2><p>Send Keir a note. We can start with the question and work out the right next step.</p><a class="button" href="mailto:keir@dillonagency.co?subject='''+quote(subject)+'''">Email Keir</a><p class="email-address" id="contact-email">keir@dillonagency.co</p><button class="secondary" type="button" data-copy="contact-email">Copy email address</button><p class="note spacer">Opens your email app. You can also copy the address into your usual email service.</p><a class="text-action" href="https://linkedin.com/in/keirdillon" target="_blank" rel="noopener">Connect on LinkedIn <span aria-hidden="true">↗</span></a></div></section><section class="advisor-bridge"><h2>A little context<br><em>goes a long way.</em></h2><div><p>Include your role and firm, the priority you’re working on, who is involved today, and any timing that matters. A short note is enough to begin.</p><p>For partnerships, speaking, or an advisor question, tell me what you have in mind.</p></div></section>'''
