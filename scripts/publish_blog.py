#!/usr/bin/env python3
"""Create or update a Jekyll blog page while preserving the public URL structure."""
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blogs"
SITEMAP = ROOT / "sitemap.xml"
CATEGORY_KEYS = {
    "Finance": "finance",
    "Technology & AI": "ai",
    "Automation": "automation",
    "Education": "education",
    "Business": "business",
    "Digital Workplace": "workplace",
    "Cloud": "cloud",
    "Product": "product",
    "Smart Home": "home",
}

def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing required input: {name}")
    return value

try:
    mode = required("BLOG_MODE")
    if mode not in {"publish", "update"}:
        raise ValueError("Choose Publish new article or Update existing article.")
    title = required("BLOG_TITLE")
    slug = required("BLOG_SLUG").lower()
    description = required("BLOG_DESCRIPTION")
    category = required("BLOG_CATEGORY")
    body = required("BLOG_BODY").strip()
    image = os.environ.get("BLOG_IMAGE", "").strip()
    raw_date = os.environ.get("BLOG_DATE", "").strip()

    if len(slug) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Slug must use lowercase letters, numbers and single hyphens only (maximum 80 characters).")
    if len(title) > 120:
        raise ValueError("Title must be 120 characters or fewer.")
    if not 40 <= len(description) <= 180:
        raise ValueError("Summary must be between 40 and 180 characters.")
    if len(body) < 100:
        raise ValueError("Article body must contain at least 100 characters.")
    if len(body) > 60000:
        raise ValueError("Article body must be under 60,000 characters.")
    if category not in CATEGORY_KEYS:
        raise ValueError("Choose a category from the publishing form.")
    publish_date = date.fromisoformat(raw_date) if raw_date else datetime.now(timezone.utc).date()
    if image:
        image_path = Path(image.lstrip("/"))
        image_file = (ROOT / image_path).resolve()
        image_root = (ROOT / "assets" / "img").resolve()
        if image_file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"} or image_root not in image_file.parents or not image_file.is_file():
            raise ValueError("Cover image must be an existing image file under /assets/img/.")
        image = "/" + image_path.as_posix()

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    post_file = BLOG_DIR / f"{slug}.md"
    legacy_html = BLOG_DIR / f"{slug}.html"
    if mode == "publish":
        if post_file.exists() or legacy_html.exists():
            raise ValueError("That slug already exists. Choose Update only for an article created by this publishing tool.")
    elif not post_file.is_file():
        raise ValueError("No managed Markdown article exists with that slug. Existing HTML article URLs are protected.")

    key = CATEGORY_KEYS[category]
    reading_minutes = max(1, (len(body.split()) + 199) // 200)
    canonical = f"https://lumenaautomation.co.in/blogs/{slug}.html"
    fields = [
        "layout: blog-post",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"description: {json.dumps(description, ensure_ascii=False)}",
        f"canonical_url: {json.dumps(canonical)}",
        'og_image: "https://lumenaautomation.co.in/assets/img/lumena-automation-og-1200x630.png"',
        f"date: {publish_date.isoformat()}",
        f"categories: [{json.dumps(category, ensure_ascii=False)}]",
        f"category_key: {json.dumps(key)}",
        "blog_published: true",
        f"reading_minutes: {reading_minutes}",
        f"permalink: {json.dumps(f'/blogs/{slug}.html')}",
        'styles:\n  - "/assets/css/pages/blog-post.html.css"',
    ]
    if image:
        fields.append(f"image: {json.dumps(image)}")
    markdown = "---\n" + "\n".join(fields) + "\n---\n\n" + body + "\n"
    post_file.write_text(markdown, encoding="utf-8")

    sitemap_text = SITEMAP.read_text(encoding="utf-8")
    location = f"<url><loc>{canonical}</loc></url>"
    if location not in sitemap_text:
        if canonical in sitemap_text:
            raise ValueError("The public URL already exists in sitemap.xml; refusing to create a duplicate.")
        if "</urlset>" not in sitemap_text:
            raise ValueError("sitemap.xml has no closing urlset element.")
        sitemap_text = sitemap_text.replace("</urlset>", f"  {location}\n</urlset>")
        SITEMAP.write_text(sitemap_text, encoding="utf-8")
    ET.parse(SITEMAP)
    print(f"{'Created' if mode == 'publish' else 'Updated'} {post_file.relative_to(ROOT)}")
    print(f"Public URL: {canonical}")
except (ValueError, OSError, ET.ParseError) as exc:
    print(f"Blog publishing failed: {exc}", file=sys.stderr)
    sys.exit(1)
