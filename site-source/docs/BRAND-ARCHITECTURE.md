# Keir Dillon + Dillon Agency: approved brand architecture

Keir Dillon is the founder and fractional CMO. Dillon Agency is the business through which he leads and delivers firm engagements.

## Two websites, distinct jobs

| Decision | KeirDillon.com | DillonAgency.co |
|---|---|---|
| Primary job | Build trust in Keir’s judgment | Help a firm evaluate a commercial engagement |
| Main voice | First person, personal perspective | Company voice, visibly led by Keir |
| Content home | Full biography, archive, writing, Google Yourself, advisor tools, The Operator’s Room | Firm services, CMO role, delivery, scope of work, engagement details |
| Evidence | Keir’s contribution and lessons; concise work summaries | Responsibilities, permitted artifacts, defined outcomes when available |
| Next step | Contact Keir; explore firm work through Dillon Agency | Discuss the firm’s needs with Keir |
| Contact | keir@dillonagency.co | keir@dillonagency.co |

The personal site keeps fractional CMO positioning prominent. It does not become only an advisor education site. The agency’s detailed service pages are the primary commercial home. Each substantial article or case study has one primary home; the other site summarizes and links.

## Commercial and audience rules

The core paid work is fractional CMO leadership and agreed firm projects. Current advisor tools are available at no cost and without registration. A future workshop or program would have a separately stated scope and terms. No membership platform, newsletter backend, payment system, AI API, or promised client-acquisition result has been created.

Advisors are a valued audience and possible advocates. Their use of a tool is not consent for sales or recruiting outreach. Firm buyers still need direct conversations and evidence of the leadership role.

## Design ownership

Both projects carry identical copies of fonts.css, style.css, visual.css, and brand.css. Palette: warm paper #FAF8F4, cream #F5F0E8, charcoal #1E1D1A, orange #D4663A, walnut #A07850. Typography: DM Sans and Instrument Serif. Paper texture, brushed-metal gradients, walnut details, editorial imagery, and responsive behavior follow the approved design.

The projects have no shared runtime, parent-folder import, symlink, remote stylesheet, or required image CDN. When changing design tokens later, make the same intentional change in both repositories and compare those four files. Their content and site configuration remain independent.

## Evidence boundaries

The Coastal Wealth page describes Keir’s reported current scope: brand strategy, team leadership, recruiting strategy and implementation, and advisor support. It does not claim measured recruiting or revenue results. AI pages describe a proposed approach and capability, not an installed client system. FRENDS and OPEN are Keir’s founder history, not agency client engagements. Generated advisor scenes are fictional illustrations, not testimonials or actual client photography.

## Review links and production links

Review builds use each project’s peer_review_origin to link between the two new review sites. Production builds use peer_domain to link between https://keirdillon.com and https://dillonagency.co. To test the eventual two Vercel previews together, override --peer-origin or set PEER_PREVIEW_ORIGIN when using build_vercel.py. Coordinate both launches so deep links do not arrive at pages that are still absent from the other production site.

## Contact and measurement

Both contact pages use the email address published on the existing sites and offer email, copy-address, and LinkedIn actions. No message is submitted by the website itself. Preserve a working existing form and its provider during integration if that is the intended production experience; update public privacy/cookie disclosures to match any retained or added data collection. Keep existing analytics and verification where appropriate. Do not claim they were configured or tested here.

## References checked

- Existing personal site: https://keirdillon.com/
- Existing agency site: https://dillonagency.co/
- Both public contact pages publish keir@dillonagency.co: https://keirdillon.com/contact and https://dillonagency.co/contact
- Google canonical guidance: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Vercel output-directory/build configuration: https://vercel.com/docs/builds/configure-a-build
- Vercel build image and available runtimes: https://vercel.com/docs/builds/build-image

Public source review: September 7, 2026. The architecture is a recommendation approved by Keir, not a claim that two sites automatically improve search rankings or company value.
