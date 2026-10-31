# Roundrobin v3.1 QA (Oct 31, 2026 ~22:40 SAST)

## Environment
Headless google-chrome (workspace), desktop 800px and mobile 390px widths, file:// origin.

## Automated functional tests (tests/generate-functional-test.py)
The harness builds a copy of index.html with an appended test script that drives the REAL UI
(form submits, button clicks, file-import via DataTransfer, blob capture on export), then dumps
results via headless chrome. All 22 checks PASS:

- T1 create letter -> letter view shown
- T2 entry appended and rendered
- T3 export produces blob; embedded data JSON round-trips (v3, turn advanced); script-close escaping verified
- T4 fresh-shell import of exported file opens the letter with entries intact
- T5 append on second "device" + re-export carries both entries (v5)
- T6 hand-crafted file with script-breakout inside JSON data: rejected/neutralized, no execution
- T7 HTML/JS injection in entry body, member name, photo URL: rendered as escaped text, javascript: photo dropped, nothing executed
- T8 malformed file (no data block): rejected with warning, current letter unchanged
- T9 older-version divergent copy refused, newer local kept, OLDER warning shown
- T10 photo attach: resized and embedded as data:image/jpeg, rendered as image
- T11 divergent branches (same identity, same version counter, different entries) flagged as CONFLICT, neither copy changed, explicit choices offered
- T12 replacement happens only after explicit "Import the file anyway"
- T13 same-title unrelated letter (different identity) not auto-imported
- T14 identical content with a newer counter adopted quietly, NOT labeled a conflict
- T15 newer counter + DIFFERENT content: NOT silently replaced, conflict choices shown, backup export verified to retain current unique entries, replacement only on explicit choice

Letter identity and conflict model (v3.1): each letter gets a random id at creation; a content
fingerprint (id + entries) is computed on import - a version counter is NOT ancestry proof and
never establishes that one copy contains the other's contributions; title alone is not identity.
Import rules: same identity+same content -> "nothing new" (adopts newer counter silently). ANY
differing content on the same letter - older, equal, or newer counter - -> CONFLICT warning with
explicit Keep current / Export current as backup file / Import the file anyway choices; nothing is
silently replaced or discarded. Different identity (including same title) -> different-letter
warning with the same choices. On explicit replace, the previous letter is additionally kept in a
browser localStorage backup slot - supplementary only, single slot, not a recovery guarantee.
There is no automatic merge of divergent copies - stated limitation; CRDT (e.g. Automerge) is the
known proper fix if the concept graduates.

Version counter: every content mutation (+1 per entry/seal; +1 per pass-on export) bumps a file-stored counter used only for older/newer comparison - never as proof of identical content.

## Visual checks
Screenshots (attached to handoff): home desktop 800px, home mobile 390px, sample-letter desktop
800px, sample-letter mobile 390px. Layout readable, no overflow, neutral fictional names only.

## Real-device limitations (not yet verified)
- Actual phone download + re-import UX (iOS Safari/Files flows for .html attachments are awkward;
  recommended flow is hosted shell + file import). Needs a real device pass after deploy.
- Photo path verified only in headless chrome.

## Package contents (source only, no personal content)
index.html, README.md, qa.md, robots.txt (staging default: Disallow all), set-domain.py,
tests/generate-functional-test.py. Conflict-prompt screenshot (rr-conflict.png) sent with handoff. No sitemap.xml ships: set-domain.py generates it together with
the canonical URL and index,follow robots at deploy time, so a staging deploy stays noindex.
