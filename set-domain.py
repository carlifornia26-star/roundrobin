#!/usr/bin/env python3
"""Deployment substitution for Roundrobin prototype.
Usage: python3 set-domain.py https://your.domain/path/
Run BEFORE publishing. It:
  - replaces the canonical placeholder in index.html with the real URL
  - flips the robots meta from noindex to index
  - generates robots.txt (allow + sitemap reference) and sitemap.xml
Until this runs, the page ships noindex and robots.txt disallows everything:
a staging deploy cannot be indexed by mistake.
"""
import sys, re, datetime
if len(sys.argv) != 2 or not sys.argv[1].startswith('https://'):
    sys.exit('Usage: python3 set-domain.py https://your.domain/path/')
base = sys.argv[1].rstrip('/') + '/'
src = open('index.html').read()
if '<meta name="robots" content="index,follow">' in src:
    sys.exit('index.html already configured for a domain; refusing to run twice.')
assert '<meta name="robots" content="noindex,nofollow">' in src, 'robots meta not found; aborting'
src = src.replace('<meta name="robots" content="noindex,nofollow">',
                  '<meta name="robots" content="index,follow">\n<link rel="canonical" href="%s">' % base)
open('index.html','w').write(src)
open('robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % base)
today = datetime.date.today().isoformat()
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n'
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
  '  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n</urlset>\n' % (base, today))
print('Configured for', base)
