# Source of the game

`game.src.html` is the file the game is built from. `index.html` at the repository root is GENERATED from it
(`tools/deploy.py` wraps it in the page head, injects the Firebase web config and writes `version.json` and `admin.html`).

Edit `game.src.html`, never `index.html`: a change made straight to `index.html` is overwritten by the next build.
Bump `const BUILD='bNN'` on every release; players with the game open are told to reload when `version.json` changes.
