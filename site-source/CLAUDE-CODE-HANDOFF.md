# Claude Code handoff: Keir Dillon

This source package is for **https://keirdillon.com**. Work in `/Users/keirdillon/Projects/keirdillon-site`. Confirm the existing Git remote, Vercel project, and domain before implementation. This is one of two separate projects; do not combine the repositories or copy one brand’s configuration into the other.

## First inspect

Read the existing repository instructions and README, check Git status, and identify pages, assets, forms, providers, analytics, Google verification, robots.txt, sitemap.xml, redirects, legal/privacy pages, and Vercel build settings. Preserve uncommitted work.

Extract the incoming ZIP into a fresh subfolder, not over the existing site. Read this README, site.json, docs/BRAND-ARCHITECTURE.md, and docs/ROUTE-MAP.csv. Review the standalone HTML and the generated pages. Use src/pages.py as the current editable copy authority. This edition replaces the earlier advisor-first and single-site CMO handoffs.

Report a concrete route-by-route merge plan, the current deployment setup, missing integrations, and any actual unresolved choices. Then implement the approved direction on a separate branch and prepare a Vercel preview before the production merge.

## The approved job of this site

Keir Dillon owns personal reputation, story, writing, advisor resources, and a concise Work with me page. The commercial position is fractional CMO and marketing leadership for wealth management firms. Keir Dillon is the founder and senior lead; Dillon Agency is the business through which firm engagements are delivered. The near-term business goal is one or two additional well-matched firm relationships.

Current public tools are available at no cost. The agency’s firm engagements are commercial now. Do not launch a paid advisor offer, invent a live community, or make a forever-free promise. Do not imply a fixed in-house team, client results, endorsements, or AI implementations that have not been substantiated.

## Preserve the design and behavior

Keep the exact Rams palette, fonts, background layers, metal/walnut treatments, photography, framing, readable typography, responsive layouts, and all working features. Both projects contain identical CSS/font files and independent assets. Preserve the other project’s content boundaries; do not duplicate full guides or cases onto both domains.

Use the existing architecture where practical. The provided static build has no runtime dependency on the other project. Full source and local assets are included; a framework rewrite is unnecessary unless the existing application requires it.

## Merge and publish correctly

Preserve useful existing URLs and deep resources. Follow the route map as a recommendation, confirm it against the actual repository, and redirect only deliberately retired pages to a relevant destination. Preserve working contact providers, analytics, verification, and policy pages. The supplied contact page uses the verified email address directly; do not replace a working form with a nonfunctional mockup.

Inspect vercel.example.json and build_vercel.py before adopting them. Keep previews noindex. Rebuild production with the confirmed domain, use the peer production domain for cross-links, merge sitemap entries, and check canonicals, robots, metadata, and Person/Organization relationships. Do not promote a noindex preview artifact without a production-mode rebuild.

Serve only the final intended public output. Never expose the ZIP, internal docs, source configuration, or handoff files as public downloads. The builder clears its generated output directory, so preserved old routes must be integrated into the final build pipeline.

Test desktop/mobile framing, navigation, internal and cross-site links, contact actions, all three advisor tools and copy/download behavior, and existing integrations in the actual preview. Report checks honestly. Coordinate launch with the companion site so cross-domain deep links resolve. Show the final preview and change summary before merging to the existing production branch or changing domain settings.

Use the same contact destination on both sites. Keep the user’s GitHub repositories as the long-term source of truth; the ChatGPT review sites do not automatically sync to them.
