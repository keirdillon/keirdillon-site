# keirdillon.com

Personal brand and authority site for Keir Dillon.

## Files

```
index.html       Home — pattern, career arc, what I do now, thinking preview
story.html       Story — six chapters (Foundations, Athlete, Broadcaster, FRENDS, OPEN, Agency)
thinking.html    Thinking — content hub for POVs on brand, AI, positioning
contact.html     Contact — form + Calendly + social links
style.css        Shared styles (AdvisorOS / Dieter Rams design system)
main.js          Scroll animations + mobile nav
vercel.json      Clean URLs, security headers, caching
```

## Deploy to Vercel

1. Create a new GitHub repo: `keirdillon-site`
2. Push all files to `main`
3. Go to vercel.com > Add New Project > Import repo
4. Framework Preset: "Other"
5. Deploy
6. Add custom domain: keirdillon.com
7. Update DNS to Vercel

## Terminal commands

```bash
cd ~/Projects/keirdillon-site
git init
git add .
git commit -m "initial commit - keirdillon.com"
gh repo create keirdillon-site --public --source=. --push
npx vercel --prod
npx vercel domains add keirdillon.com
```

## Cross-linking

- Home links to dillonagency.co ("See Dillon Agency")
- Story page links to dillonagency.co at the end
- dillonagency.co/background links back here for the full personal story
- Both sites share the same contact pipeline

## To-do before launch

- [ ] Add headshot / portrait photo
- [ ] Add favicon
- [ ] Add OG image
- [ ] Connect contact form backend (Formspree)
- [ ] Add Calendly URL
- [ ] Connect analytics
- [ ] Submit sitemap to Search Console
- [ ] Write first Thinking article
