# LumenaAutomation website

Production website for [lumenaautomation.co.in](https://lumenaautomation.co.in/), built with Jekyll and deployed to GitHub Pages.

## Build and validation

The repository uses the GitHub Pages-compatible Jekyll configuration in `_config.yml`. After building to `_site`, run `python scripts/validate_site.py _site` to check generated page metadata, local links and assets, the custom domain, `robots.txt`, and `sitemap.xml`.

## Deployment

Pushes to `master` are built and deployed by `.github/workflows/deploy-pages.yml`. Pull requests and modernization branches run `.github/workflows/validate.yml`.
