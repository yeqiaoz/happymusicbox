# Happy Music Box: Site Plan
*Oct 3, 2026 · One-page static site for Shuai's product, built the same way as uracquet-v2 (build.py → site/, copy deck in content/).*

## 1. Goal
One fast page that explains the product and sends people to the Amazon listing. Design follows Shuai's mockup, `432.jpg`.

## 2. Sources (facts only from these)
- Amazon listing, Pink: https://www.amazon.com/dp/B0HC9TPS27 · Blue: https://www.amazon.com/dp/B0HC9XZ8BC (brand Happy Music Box, seller Cloud & Tree Store, first available July 31, 2026)
- Shuai's mockup `432.jpg` (layout, palette, hero/feature/footer copy, support@happymusicbox.com)
- Listing photos, 8 JPGs saved to `assets/source/amz_*.jpg` (gitignored); Yeqiao approved the download Oct 3, 2026

## 3. Build
- `python3 build.py`. Needs Pillow. Wipes and rebuilds `site/`. Copy lives in `build.py`, mirrored in `content/home.md`.
- Preview: `.claude/launch.json` → `happymusicbox` on port 8766.
- `BASE_URL` env var: unset = no canonical, og:url, sitemap or robots. Set it once the domain is known.
- Images: product shots are padded to a square and their white edges fade into the page (CSS mask), because a hard cut-out left a halo. Lifestyle tiles are crops of the listing collage (500 px source, so they stay small).

## 4. Deliberate departures from the mockup
- **Hero photo:** the mockup's cube is a render that doesn't match the real product. The site uses the real listing photo.
- **Testimonials:** "Sarah J. / Mike L. / Chloe K." aren't real reviews, so they're not used (FTC rules on fake reviews). The page shows the one real Amazon review plus a "Read reviews on Amazon" card. Add more only once they're real.
- **GIF panel:** no clip exists yet. It's an animated color panel labelled "7 LED light modes", with no fake play button.
- **Blog:** dropped from the nav and footer, because there's no blog.
- **Price:** not shown. Amazon's price changes, and the buttons go straight to it.

## 5. Open questions [ASK]
1. **Domain and email:** happymusicbox.com doesn't resolve (checked Oct 3). Does Shuai own it? Is support@ live?
2. **Hosting:** a GitHub Pages repo, as with uracquet?
3. **Claims:** "Therapy" (headline), "promote deep sleep" (features) and "Healing" (528 Hz label) are Shuai's own words, used as written. Should she soften them for a wellness product? The Amazon text says relaxation and meditation.
4. **Review:** OK to quote the Y.Z. review? Leave it off if the reviewer is a friend or family member.
5. **Media:** higher-resolution photos, a lifestyle hero shot, or a real clip of the light modes would all help. Listing images max out at 500 to 993 px.

## 6. GitHub Pages: Oct 3, 2026
- Repo `github.com/yeqiaoz/happymusicbox` (public). A push to `main` deploys `site/` via `.github/workflows/pages.yml` (copied from uracquet). `site/` is committed; Actions doesn't build.
- Pushes use the repo-local deploy key `~/.ssh/github_happymusicbox` (`core.sshCommand`). Never read or copy the key.
- `432.jpg` (the mockup) is gitignored, as are the source photos.
- `DRAFT = True` in build.py adds `noindex` while Shuai reviews it. At launch, set it to False and set BASE_URL.
