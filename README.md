# Roundrobin - the slow group letter (experimental prototype v3.1)

Working name, provisional internal label only (final public naming needs clearance; "round robin"
is generic scheduling vocabulary and a physical travelling-letter tradition exists, e.g. Swap-bot).

## Concept
Human friction: group chats die under notification overload and reply pressure; context collapse
stops people posting; timezones desync close friends.
Paradigm shift: the group conversation is a recurring compiled artifact (a "letter issue"), not a
stream. Members write when free; everyone reads a sealed issue; nothing notifies anyone.
Platform shape: NO new network, server or accounts. The letter is a single self-contained HTML file
passed through the group chat people already have.

## Prototype truthfulness
- Local-only. No account, no server upload by this page.
- Multi-person use = members deliberately export the file and pass it on in their own chat.
  There is no automatic delivery, no notification system, no simulated/fake activity.
- Sealing an issue is a reading convention, not immutability.
- Letters carry a random identity and content fingerprint. Imports never silently discard:
  identical content = "nothing new"; older version = refused; newer version = imported with the
  previous local copy auto-backed-up in the browser; divergent branches or a different letter =
  explicit Keep / Export-backup / Import-anyway choice. There is NO automatic merge of divergent
  copies (documented limitation).
- The "sample letter" button loads clearly labeled placeholder demo data.
- Minimal truthful JSON-LD (WebApplication, isAccessibleForFree); no ratings/claims.

## Deploy (Tony's builder)
1. python3 set-domain.py https://your.domain/path/  -> sets canonical, flips robots to index,
   generates robots.txt + sitemap.xml. The shipped page is noindex + Disallow until this runs.
2. Serve the directory statically. No build step, no backend.
3. Search Console submission/indexing stays with the deploying side's own authority.

## Tests
python3 tests/generate-functional-test.py  (from the package root) writes /tmp/rr-test.html;
run it in headless chrome and read the embedded results block. 22/22 PASS - see qa.md.

## QA status
See qa.md.
