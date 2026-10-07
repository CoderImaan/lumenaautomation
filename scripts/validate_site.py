#!/usr/bin/env python3
"""Validate generated pages, local links/assets, metadata, and GitHub Pages files."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re, sys, xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
domain = "https://lumenaautomation.co.in"

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.canonicals=[]; self.title_count=0; self.ids=set(); self.metas=set(); self.primary_navs=0; self.footers=0; self.images_without_alt=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        if tag=="meta":
            if a.get("name"): self.metas.add(("name",a["name"].lower()))
            if a.get("property"): self.metas.add(("property",a["property"].lower()))
        if tag in ("a","link","script","img","source","iframe"):
            for key in ("href","src","srcset"):
                if a.get(key):
                    vals=a[key].split(",") if key=="srcset" else [a[key]]
                    self.refs.extend(v.strip().split()[0] for v in vals)
        if tag=="link" and "canonical" in a.get("rel","").lower().split(): self.canonicals.append(a.get("href",""))
        if tag=="title": self.title_count+=1
        if tag=="nav" and a.get("aria-label")=="Primary navigation": self.primary_navs+=1
        if tag=="footer": self.footers+=1
        if tag=="img" and "alt" not in a: self.images_without_alt+=1
    def handle_endtag(self, tag): pass

errors=[]; pages=sorted(root.rglob("*.html")); parsed={}
for file in pages:
    parser=PageParser()
    try: parser.feed(file.read_text(encoding="utf-8",errors="replace"))
    except Exception as exc: errors.append(f"{file.relative_to(root)}: HTML parse error: {exc}"); continue
    rel=file.relative_to(root)
    if parser.title_count!=1: errors.append(f"{rel}: expected one title; found {parser.title_count}")
    required_meta={("name","description"),("name","robots"),("name","twitter:card"),("name","twitter:title"),("name","twitter:description"),("name","twitter:image"),("property","og:title"),("property","og:description"),("property","og:url"),("property","og:image")}
    for key in sorted(required_meta-parser.metas): errors.append(f"{rel}: missing {key[0]} metadata {key[1]}")
    if len(parser.canonicals)!=1: errors.append(f"{rel}: expected one canonical; found {len(parser.canonicals)}")
    if parser.primary_navs!=1: errors.append(f"{rel}: expected one shared primary navigation; found {parser.primary_navs}")
    if parser.footers!=1: errors.append(f"{rel}: expected one shared footer; found {parser.footers}")
    if parser.images_without_alt: errors.append(f"{rel}: {parser.images_without_alt} image(s) missing alt attributes")
    for canonical in parser.canonicals:
        if not canonical.startswith(domain+"/"): errors.append(f"{rel}: invalid canonical {canonical}")
    for ref in parser.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc or not u.path: continue
        target=unquote(u.path)
        dest=(root/target.lstrip("/")) if target.startswith("/") else file.parent/target
        if dest.is_dir(): dest=dest/"index.html"
        if not dest.exists(): errors.append(f"{rel}: missing local target {ref}")
    parsed[file]=parser

for file,parser in parsed.items():
    for ref in parser.refs:
        u=urlsplit(ref); fragment=unquote(u.fragment)
        if not fragment or u.scheme or u.netloc: continue
        dest=(root/unquote(u.path).lstrip("/")) if u.path.startswith("/") else file.parent/unquote(u.path)
        if not u.path: dest=file
        if dest.is_dir(): dest=dest/"index.html"
        if dest in parsed and fragment not in parsed[dest].ids: errors.append(f"{file.relative_to(root)}: missing fragment target {ref}")

for css in root.rglob("*.css"):
    source=css.read_text(encoding="utf-8",errors="replace")
    for value in re.findall(r"url\(\s*[\"']?([^\"')]+)",source,re.I):
        value=value.strip()
        if value.startswith(("data:","http:","https:","//","#")): continue
        target=(root/value.lstrip("/")) if value.startswith("/") else css.parent/value
        if not target.exists(): errors.append(f"{css.relative_to(root)}: missing CSS asset {value}")

for required in ("admin/index.html","about.html","services.html","endpoint-management.html","ai-automation.html","saas-engineering.html","products.html","budgetmanager.html","farmserve.html","kids-fun-test.html","blogs.html","contact.html","careers.html","privacy.html","terms.html","refund.html","cookies.html","404.html","robots.txt","sitemap.xml","CNAME"):
    if not (root/required).exists(): errors.append(f"missing generated {required}")
if (root/"admin/index.html").exists() and 'content="noindex, nofollow"' not in (root/"admin/index.html").read_text(encoding="utf-8"): errors.append("admin publishing page must remain noindex, nofollow")
if (root/"CNAME").exists() and (root/"CNAME").read_text(encoding="utf-8").strip()!="lumenaautomation.co.in": errors.append("CNAME does not match production domain")
if (root/"robots.txt").exists() and domain+"/sitemap.xml" not in (root/"robots.txt").read_text(encoding="utf-8"): errors.append("robots.txt sitemap URL does not match canonical domain")
try:
    tree=ET.parse(root/"sitemap.xml"); locations=[n.text or "" for n in tree.findall(".//{*}loc")]
    if not locations: errors.append("sitemap.xml has no URLs")
    for location in locations:
        if not location.startswith(domain+"/"): errors.append(f"sitemap URL uses noncanonical host: {location}")
        path=urlsplit(location).path
        destination=root/(path.lstrip("/") or "index.html")
        if destination.is_dir(): destination=destination/"index.html"
        if not destination.exists(): errors.append(f"sitemap URL has no generated page: {location}")
except Exception as exc: errors.append(f"sitemap.xml is invalid: {exc}")

if errors:
    print("\n".join(errors)); print(f"FAIL: {len(errors)} issue(s) in {len(pages)} pages"); sys.exit(1)
print(f"PASS: {len(pages)} generated HTML pages; internal references, CSS assets, canonicals, CNAME, robots.txt, and sitemap validated.")
