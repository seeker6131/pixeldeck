# Pixeldeck Battle — handoff for a new Claude session

Live build: **b191** (15 Oct 2026 22:25: the invite-for-diamonds menu / FOUNDER invite event is off — `REF_ON=false` hides the lobby invite button, the invite action and its guide line. The FOUNDER title itself must KEEP showing for holders (owner's rule) — `FD_SHOW=true`; b190 wrongly hid it for a few minutes). Previous: b189 (released 15 Oct 2026 21:40: tank SL amulets also work in the Tower and future world boss (`C3_ON` true for b.tw / b.wb, never PvP; startTower calls c3Amu); tower sim 10★ SL team 409 -> grove 419, gstar ~457; popup news189. b188 21:05: PC never forced to fullscreen — `isPC()` by user agent (touch laptops count), PC pref key pdb_fs_pc, no sideways rotation on PC; b187 20:40: no flicker when picking cards — `prepSoft()` updates the rail and pick marks in place; fire canvases painted only after fireStep and only when on screen; b186 20:35 new Chapter 3 cover cover-c3.webp on login + loading, shown from the top; b185 20:30, b184 20:17, b183 20:05). Talk to the owner (Toey) in Thai, never call them "ต้อย". The game name stays English; the in-game credit is "PixelDeckBattle".

## Where things are
- Game source (single file): `src/game.src.html`. Admin page source: `tools/admin.src.html`.
- Published sites: remote `origin` = seeker6131/pixeldeck, remote `pdb` = pixeldeckbattle/pixeldeckbattle.github.io (the real game URL).
- Firestore rules reference: `firestore.rules` (OWNER_EMAIL stays a placeholder — never commit the real address). The owner pastes rules into the Firebase console themselves.
- GDD: Claude Docs project `98dc7285-97f9-44f7-8e3c-0186f59dbe8f`, tab node `ac85a622-c911`; the build table header row is block `m4v3m846h9s.28807` (insert a 3-cell row after it: build · date · what changed) and the intro line holds "โค้ดบิลด์ bNNN".
- In-chat test copy: Artifact https://claude.ai/artifact/Enf7gNXFm7S4srkv2z8JPR (publish the built game file there).

## Release workflow
1. Work dir: copy `src/game.src.html` → `<work>/bit8-clash.html`, `tools/admin.src.html` → `<work>/admin.src.html`, `tools/FB_CFG.json` → `<work>/FB_CFG.json`.
2. Edit with small python patches (assert each anchor appears once). Bump `const BUILD='bNNN'`.
3. Syntax: extract the biggest `<script>` and `node --check` it.
4. Tests: `python3 tools/mkt_page.py` (run from work dir) writes `_t.html`; `node t121.js` must show 0 errors, `node t142.js` must print 13 `"inside":true`. Chromium at `/opt/pw-browsers/chromium`. Online tests: replace `const FB_CFG=null;` with `let FB_CFG={t:1};` in `_t.html` and route gstatic to `tools/fbmock.js`.
5. From the work dir: `python3 tools/deploy.py` (writes index.html, version.json, admin.html). Copy sources back to `src/` and `tools/`. Delete `_t.html`.
6. Commit (author Claude <noreply@anthropic.com>), `git push origin HEAD` and `git push pdb HEAD:refs/heads/main`. Never force-push.
7. Update the GDD and the in-game guide (`guide()` SEC tabs) for every change.

## Standing rules from the owner
- Every update also updates the GDD and the in-game "วิธีเล่น".
- Build only on an explicit order ("ทำเลย / ลุย / ปล่อย / แก้เลย"); advice questions get answers only.
- Weigh the developer's revenue side when advising.
- Text for them to copy/post: no tables (code blocks / bullets). GPT art prompts: one self-contained block per image.
- Limited cards must stay the strongest (at least ~3% over SuperLegend). Dev account must hold every new thing at max (`devGrant`).
- Prefer admin-side fixes over forcing players to reload.
- Never handle secrets (Thunder API key, service-account JSON, card numbers, 2FA codes).

## State of the game (b182)
- Stages 1–1100. Chapter 2 (501–1100): 6 realms `RLM`, monsters `x11..x65`, maps `bg/r11..r62`, realm rules, lords every 100, stage stars + star chests, realm crystals `S.rs` (💠 ผลึกอาณาจักร).
- Stars 6–10 for L/SL/LT (`STAR_C2`, badges `ui/st6..st10.webp`), skill 4 at 10 stars (`SK4`, `SK4E`, `cast4`, icons `ic/s4*.webp`), skill-4 Lv 2–3.
- Glacius Rex `h28` (Limited tank): only the first 3 players to clear stage 1100 (Firestore `firsts/s1100`), later ones get 💠10.
- VIP: every active VIP (gifted, arena, bought) gets Auto x3, 10 h offline farm with amulet/card/crystal drops, crystal x1.5, plus Exp/Gold x2.
- b185 (LIVE): owner's design: pressing เข้าสู้ opens a setup popup `teamPop()` (tabs per team card, `tpStats` stats, `tpSkills` skill icons + desc + cooldown, smart/custom auto per card with order/on-off), Start -> `tpCount` 3-2-1 -> `startBattle`. Tutorial (S.tut!=null) skips it; loops skip it. Prep-screen 🤖 buttons removed.
- b184 (LIVE): owner moved the auto-skill setup off the card view onto the team screen before a stage: `prep()` shows a 🤖 button per team card (`data-act=askopen`), `askOpen(id)` opens `askPanel` in `ov()`, `askDo` re-renders it, Done returns to `prep()`. Guide/news text updated; t182 tests it via askOpen.
- b183 Chapter 3 (LIVE): MAXST 1500. RLM[6..8] have s/e ranges (Himmaphan 1101-1250 rule sky, Demon City 1251-1400 burn, Great Ocean 1401-1500 tide); `realmOf`/`rS`/`rE`, lord = realm's last stage. Monsters x71/x74(sp x71)/x75, x81/x84/x85, x91 & x94 (sp x11 placeholder until c91 art)/x95; maps bg/r71 r72 r81 r82 r91(=r92 copy). Difficulty `CH3_K=.82,CH3_G=.0008` on top of the Ch2 curve (owner chose option A, 15 Oct 20:00: best geared teams can reach 1500; owner plans a stronger amulet or card later). `C3_HUNT`: with no taunt, enemies hit the lowest-HP ally. Sim tools/simc3.js (10★, kfang on DPS) at the chosen values: no tank ~1109, tank no amulet ~1440, tank+SL tank amulet 1499-1500, Glacius/Hydra+amulet 1500. Vanarin skill 3 changed to aoe 1.45, crit 35 (PvP ~37% vs Wukong, Hydra still wins 70%). Tank HP bar wider/thicker (`.fig.tk`). Guide section ch3, news popup n183. Tank amulet values unchanged (all three tie ~1400).
- b183 cards (LIVE): 4 Thai-literature cards in `C`/`SK`/`SK4`/`SK4E`: h29 Vanarin (SL atk, dive 2.3), h30 Tenface Asura (SL tank, reflect .55), h31 Indigo Dragonsteed (SL mage, chain .5), h34 Temple Yaksha (L tank, stand). They use 8-frame sheets (`f8:1` -> `.spr.f8` CSS, 8x4 cells of 252x204) cut by tools/cardsheet8.py from tools/cards_in3. They join the normal rank pools (packs, drops, fusion). Not done: news popup/guide/GDD lines for them, Chapter 3 (waiting for monster art).
- b182 effects (LIVE in b183): AAA skill effects wired: `FX8` table + `fx8(id,name,{flip,t})` draws 8-frame strips (fx/ult-<SK4E type>.webp, fx-crit, fx-ko; cut by tools/fxcut8.py from tools/fx8_in/) on an overlay `#fxl` in #stage that survives `draw()`; skill 4 plays its strip at impact (`strike`) or on the caster (`pose`), `ultCam()` zoom+flash after the skill-4 cut-in, crit and KO strips from `hurt()`, `ghost()` dash afterimages in `lunge()`. Run deploy.py only when the owner says ปล่อย.
- b182: tank HP grows `TANK_HG`=1.3x faster per level (`stat()`, `hpG()`; `TANK_AG` ATK factor kept 1) — real stats in every mode; sims: SL★5 tank team ~700→~790 in Chapter 2, lord 800 still a wall, PvP win rates unchanged. Arena storm `pvRound()` from round `PV_STORM`=8 (6%/round rising, through shields) because tank-vs-tank duels stalled to the cap. Custom auto skills per card `S.ask[id]={o,f}` (`askPick` first in `autoPick` for mine only; panel `askPanel` in `zoom`). VIP retry on defeat `S.lpr` (`lprOn`, `LP_RETRY`=5, `loopL`/`loopW`; next-stage mode falls back to replaying the last won stage). Card fusion ⚡ fuse all (`fuAllPlan`/`fuAllDo`, double-tap confirm; amulet side already had "add all spare"). PC (`isPC()`) starts windowed, Esc out of fullscreen turns the pref off. `toast()` helper. Popup `news182`. Test `tools/t182.js`.
- b181: a broken SL fusion now burns half that try's Gold (`AFU.L.brk=.5`; success still costs the full 30,000). Test `tools/t181.js`.
- b180: tank SL amulets `grove`/`lion`/`gstar` (fields th HP x, tdf DEF x, tsh shields x, tc taunt damage taken, ls last stand; flag c3). Released now as a Gold sink (fusion-only); effects apply ONLY to tank cards on stages 1101–2000 (`C3_ON`, `c3Am`, `c3Amu(bt)` at battle start, hooks in `hurt()`), never in PvP/Tower. Values are first guesses; retune when Chapter 3 exists. Popup `news180`. Test `tools/t180.js`.
- b179: on-screen number pad `kp(ctx)` / `kpKey()` replaces the ± buttons on the Gold→diamond exchange (`exRaw`, rounded down to lots of 10, capped by Gold) and the market sell price (`mkRaw`, 100–MK_MAX). Test `tools/t179.js`.
- b178: diamond ledger `S.ld` (same shape as the Gold ledger `S.lg`): `ld(key,±n)` at every diamond change, untagged changes booked as `unk` in `save()`; started by `ldInit(0)` when the lobby opens. Admin Finance tab shows the economy card (Gold + diamond sources/uses, in/out per day, status สมดุล/เริ่มเฟ้อ/เฟ้อ/ฝืด). New diamond sources or sinks must call `ld()` and get a label in admin `LDI`/`LDO`.
- b177: diamond market CLOSED by the owner (tab removed, popup off, VIP/guide lines removed). `dmRefundAll()` in the lobby cancels the player's own open `dmo` orders once and refunds them, and collects `dmpay`. The dm code and rules are kept so it can come back.
- (history) Diamond market (b176): Market → 💎 tab, `dmView()`. Firestore `dmo` orders, `dmpay` maker payouts (`{order}_{q left}`), `dmt` trades, `dmc/{yyyymmdd}` 15-min candles. Price 1,000–2,000 (shop ceiling), any diamond sellable, stage 30, 100/day each way (VIP 200), tax 5% (VIP 3%); `CFG.dm` overrides from admin Switches. Tests `tools/t176*.js`. Admin Players tab has an economy card.
- Market: Buy / Sell / History modes. History reads Firestore `trades/` (buyer writes it after a purchase, best-effort; rule block in `firestore.rules`). Test: `tools/t175.js`.
- Balance sim: `tools/simc2.js` (Chapter 2), `tools/simst.js` (stages 1–500).

## Open / noted for later
- NEXT (planned with the owner, 15 Oct): Chapter 3, stages 1101–2000. Tank SL amulets (already live since b180) work ONLY on stages 1101–2000: มรกตพฤกษา `grove`, หัวใจราชสีห์ `lion`, ดาราพิทักษ์ `gstar` (all SL, fusion-only; art already in `am/` and `tools/am_in/`). Owner's design: on a tank they are strong (thick HP, taunt cut / shield / one last stand per battle), on any other card almost nothing (~HP/DEF +3%). Concept: tanks have visibly thick HP and stand long enough to cast skill 4. Tune the numbers against the real Chapter 3 monsters with the sims (target: walls barely move, Glacius Rex stays strongest). Gold is "starting to inflate": owner also wants a Gold sink (proposal: amulet upgrade +1..+10).
- DONE b182: auto-retry on defeat while looping a stage — VIP only. Today a loss ends the loop (`loop` handler after battle: `nx=!won?0:...`). Proposed shape: a toggle on the loop screen; replay mode retries the same stage after the 3s countdown; next-stage mode falls back to looping the last won stage; stop after 5 losses in a row; farm summary counts wins/losses.
- DONE b182 (from player Xavier): custom auto-skill setup per card — mode "smart" (current `autoPick`, default) or "custom": player orders skills 1–4 and can switch skills off; auto takes the first ready skill in that order; always a reset-to-smart button. Client only.
- DONE b182 (via per-level HP growth): raise tank cards' own base HP so they visibly look like tanks (thicker HP bar) and die later than teammates. Careful: an earlier sim showed a pure big tank-HP buff too strong — tune it with the sims together with Chapter 3 and the tank SL amulets (walls barely move, Glacius Rex stays strongest).
- NOTED (owner, 15 Oct, not ordered yet): new cards — 3 Legend + 5 SuperLegend covering every role; Claude proposes the role split. Proposal given: L = tank, sup (healer), phys shooter (`st:'shoot'`); SL = tank, sup (shield/buff, unlike Seraphina's heal), phys shooter, mage, phys assassin (exec). After it: L 2 tank/2 sup/5 atk, SL 2 tank/2 sup/5 atk. New SL stats must stay ≥3% under the Limited cards (h18, h28) and get skill 4 for stars 6–10. Needs art from the owner first (card art + sprite sheet each); suggested source: Chapter 3 drops + fusion. Ids from h29.
- IN PROGRESS (owner, 15 Oct, from player Mol2ez): real skill animations — owner got 14 GPT prompts (8-frame 2x4 sheets on magenta #FF00FF): ult-zero, ult-blood, ult-dive, ult-scorch, ult-rebirth, ult-chain, ult-forms, ult-halo, ult-hydra, ult-reflect, ult-stand, ult-fort (one per skill-4 type in `SK4E`), fx-crit, fx-ko; code side (hit-stop, shake, dash afterimage, ult camera zoom) goes in with the art; fxcut.py needs a 2x4 grid mode. Original note: real skill animations — skills should not look like fighters just running into each other. Today there are 18 generic effects in `fx/` plus `cutin(a,k)`. Idea: per-skill-type effects (projectile flying across, AoE across the enemy row, a beam or pillar on the target, heal/shield aura on allies, screen shake/flash for skill 4), with a stronger cut-in for skill 4. Needs effect sprite sheets from the owner (GPT, one prompt per effect); best done together with the new L/SL cards.
- DONE b182 as card fuse-all (amulets already had add-all): "fusion all" button — farmers have too many amulets to pick one by one. Fusion already does several tries at once (`afTimes`), the pain is picking. Idea: a "select all spare" button on the amulet fusion screen (fills `afPick` with `spare()` of every amulet, never locked/equipped ones), then the normal fuse with a summary (tries, Gold, materials); SL fusion gets a second confirm because a break burns Gold. Maybe a rarity filter. Good Gold/amulet sink.
- DECIDED (owner, 15 Oct 17:31): Chapter 3 waits for its art, done together with the new cards and skill effects (amulet retune goes with it). Tank HP buff (revised 17:33): change the tank cards' REAL stats so the card shows it and every mode uses it, PvP included (keep it simple, one rule game-wide). "Rising" = tanks get a bigger HP growth per level (`stat()`: HP uses a higher per-level gain for role tank), so Lv1 is unchanged and the gap grows by the level players have around stages 500-2000; never too strong; check PvP too. Stage-2000 first-clear reward and amulet +1..+10 upgrade: owner will decide later.
- IDEA, direction not decided (15 Oct, player GrienZa): profile level (owner's name: เลเวลโปรไฟล์) giving +0.1% to all card stats per level. Advised a cap (~+5%), convenience rewards past it, VIP x2 profile Exp; owner will work out the direction later. Not for b182.
- ART REQUESTED (15 Oct, prompts sent to owner, not built): new cards h29-h36, Thai-literature theme, English names. SL: h29 Vanarin (assassin, white monkey + golden trident), h30 Tenface Asura (tank, 10-face crown demon king + club), h31 Indigo Dragonsteed (mage, dragon-horse), h32 Kinnaree Dancer (sup shield/buff), h33 Verdant Bow Prince (archer). L: h34 Temple Yaksha (tank), h35 Naga Oracle (healer), h36 Hawk Ranger (crossbow). Each: <id>-<name>-art.png (5:3) + -walk/-attack/-front.png = 8-frame 2x4 sheets on magenta, facing RIGHT (front = facing camera) -> needs a new 8-frame cutter and fr8 animation in the game (today 6x4). Chapter 3 maps: 6 realms x 150 stages, 2 maps each, 16:9: c3-himmaphan, c3-lanka, c3-ocean, c3-naga, c3-sumeru, c3-war (-1/-2). Chapter 3 monsters/bosses: prompts still to send.
- DECIDED (owner, 15 Oct 19:28): Chapter 3 stops at stage 1500 for now (MAXST 1500). Realms of 150 per the map prompts: Himmaphan 1101-1250, Lanka 1251-1400, Ocean 1401-1500. Art in hand: tools/cards_in3 (h29 Vanarin, h30 Tenface, h31 Dragonsteed, h34 Yaksha: art + walk/attack/front 8-frame 2x4 sheets facing RIGHT) and tools/c3_maps (himmaphan-1/2, lanka-1/2, ocean-2; ocean-1 missing). Monsters: owner wants real Thai-style monster art first (prompts sent: c71-c75 Himmaphan, c81-c85 Lanka, c91-c95 Ocean, 6 idle over 6 attack facing LEFT on magenta, for ch2mon.py-style cutting). Kinnaree, Bow Prince, Naga, Hawk art not made yet.
- PLANNED next patch (owner, 15 Oct 21:01): weekly WORLD BOSS, Halloween theme. Proposal sent (not ordered, not built): server-shared boss HP in Firestore (one increment per attempt), 3 tries/day (+1 VIP, extra tickets for diamonds capped 2/day), 10-round fights, damage leaderboard, server-wide milestone rewards at 75/50/25/0% via mailbox, candy 🍬 event currency + candy shop, top ranks get a Halloween Limited amulet/frame; phases change with server progress; tanks matter (boss curse hits lowest HP). Art prompts sent: boss sheet wb1, map wb-map, candy icon, Limited amulet, event banner.
- Team presets; relax room / card-flex; party boss; weekly world boss; market reference price.
- Clearer skill-4 wording in game ("ใช้ได้ตั้งแต่รอบ 3 · ใช้แล้วพัก 5 รอบ") — offered, not ordered.
- Slip top-up outside 17:00–00:00: offered either queueing slips or a big warning — not ordered.

## OBT plan: how new cards come out (owner: "รอ obt", 15 Oct 2026 — do NOT build before the OBT prep)
- Problem seen in CBT: new cards (h29/h30/h31 SL, h34 L) came out too easily. Main cause: `fuDo` uses `randNew` (cards you don't own first), so the first L→SL fusion after release gave a new card 100%, and fuse-all made it instant. `bcTake` and mail rewards also use `randNew`. Normal pools went SL 4→7, so ~43% of any SL roll is a new card.
- Agreed direction for OBT: fusion rolls evenly (no "new first" for new cards); a rate-up "new card banner" sold for diamonds with visible pity; new cards locked to that banner for the first weeks (not in fusion, stage drops or normal packs); a slow free path (Chapter 3 drops give card shards, N shards = 1 card); later the cards join the normal pool.
- Measure with the admin card-source logs: % of active players owning the new card after 7 days (SL target ~5–15%), which source it came from.

## b192 built, NOT released (15 Oct 23:45): Bag menu
- Lobby dock first button "กระเป๋าไอเท็ม" (UI.bag) replaces My Cards; coll() has category tabs Cards / Amulets / Items (collTab 'it' -> itemsView(), list from itList()).
- VIP card bought (diamond shop or arena shop) while VIP runs goes to S.vb (vbStore/vbHold); "ใช้" in Items calls vbUse -> vipAdd. Admin gift VIP still applies at once.
- Waiting for the owner's release word.

## Planned: profile level + profile picture frames (owner, 15 Oct 23:46–23:52; not built)
- Profile level Exp from every mode, daily cap 150 (first clears +10, daily quests +30, PvP win +8 / loss +3, tower +10 per 10 floors, world boss hit +5, login +5). Rewards: small Gold/diamonds per level, a new profile frame every 10 levels; optional +0.1%/level card stats (max +5%) OFF in PvP. Modes stay unlocked by stages only (recommended; owner had asked whether to overlap).
- Profile picture: upload from phone, resized to 128x128 and stored on the account; the photo is visible to the OWNER ONLY (owner's choice) — others keep seeing the card character.
- Frames are round avatar frames, 16-frame 4x4 sheets on magenta: pf-01, pf-10, pf-20, pf-30, pf-40, pf-50, pf-hallow (prompts sent). The pumpkin card frame (tools/wb_in/frame-pumpkin.png) can serve as a big showcase frame.

## UI reskin plan (owner, 16 Oct 00:18; not built)
- GPT UI kit kept in tools/ui_in (cut pieces in tools/ui_in/cut): panel, main/sub buttons, slot row, title ribbon, tabs on/off, currency pill, dock tile, progress bar (frame+fill), round buttons (close/back/gear). All 9-slice friendly.
- Background chosen: option A "royal night blue" — radial gradient #2b3a8c → #151c4a → #0a0d24, faint star dots (34px grid, ~10% white), soft gold glow at the top. Mode accents done in code: shop gold glow, PvP red edge, tower ice-blue edge, world boss purple/green.
- Icon sheets still to come from GPT (prompts sent): icons-menu (25), icons-battle (25), icons-inline (25: diamond, coin, crystal, star stone, class tags, lock, gift, trophy, mail, ticket, crown, megaphone, clover, warning, 6 realm-rule icons). Goal: replace emoji across the game.
- The 1-bit UI pack (Batuhan) was tried and rejected by the owner ("ไม่สวย").

## World boss = PARTY mode (owner, 16 Oct 06:41–06:47; not built)
- 2–4 players per room, each brings ONE card (their best). Host (crown) starts once 2+ are in. Room screen mock: scratchpad wb-party.png (4 standing slots, profile frame + name above, class plate + ready state, empty slot with invite / random search, own card row, short room chat).
- Invite: host taps invite -> the invited player gets a small popup sliding down from the top wherever they are: "<name> ชวนตีบอสกันมั้ย?" with buttons สนใจ / ไว้ทีหลัง; auto-hides after 10 s with a countdown strip; the host can send again.
- Room number: every room has a 4-digit number; "join by number" box; a copy button gives a ready-to-paste line for chat/Discord ("มาตีบอสฟักทองกัน! ห้อง #4821 ขาดอีก N คน"). First come first served, full at 4.
- Proposed (owner not yet answered): bots fill to 2 after 30 s with no joiners (bots get no rewards); party damage cuts the server-wide boss HP, ranking per player; each member spends 1 ticket; candy +10% per member. Needs realtime room sync like the trade room (+2–3 days work).

## BETA (owner-only) — b195 on beta.html, LIVE index stays b191 (16 Oct 2026)
- tools/deploy_beta.py writes beta.html only (Dev account only; others are sent to ./; no version.json polling). Release = run tools/deploy.py as usual when the owner says so; update the GDD then.
- b192 Bag (see above). b193 profile level: S.pl, plGain/plBuff/plAv/plBox, frames pf/*.webp (tools/pfcut.py, 16-frame strips), own photo S.pl.ph (owner-only view).
- b194 Halloween world boss: module tools/wb_mod.js is pasted into the game before /* mailbox */ (keep them in sync or edit the game copy). Event WB.from/to = 24 Oct 00:00 – 8 Nov 00:00 Bangkok; Dev sees it any time.
  Shared HP on Firestore wb/hw26.dmg (increment), ranking wbr/hw26/s/{uid}; NEW firestore rules in firestore.rules (owner must paste/publish). Without them the Dev account plays a local copy (badge "โหมดทดสอบ").
  Party rooms on RTDB under rooms/wb_<code>, open-room index rooms/wbidx, invites rooms/inv_<uid> (fits the existing rooms/$room/$uid rule). Boss sprite spr/wb1(r).webp 16x4 @16fps (tools/wbsheet.py), assets tools/wbassets.py -> wb/*. Balance: tools/simwb.js (WB_BOSS atk = ch3 lord x0.25: tank party survives 10 rounds, no-tank ~4-5). HP Lv1 6,000,000 (CFG.wbhp overrides), x1.5 per level, 5 levels.
  Owner defaults taken (not answered): bots fill after 30 s, extra tickets 30/60 💎, Limited amulet 'hallow' in candy shop 1,000 (x1) + top 10.
- b195 Royal Night skin (background A + GPT UI kit ui2/*, icons ui2/i-*), emoji in text auto-replaced by pixel icons (emoFix in view/ov).
- b196 (beta): owner disliked the Royal Night skin ("ทุเรศ มองยาก") -> reverted to the normal skin (only the bag icon kept). World boss screens rebuilt on the normal rail/main layout (wbHub, wbRoom, wbShop, wbRank, result as an overlay dialog); checked at phone size 932x430. Lobby: when the world boss is open its button replaces the progress panel so nothing overlaps.
- b197 (beta): world boss screens in the orange-gold Halloween kit (ui2 panel/buttons/title) over a blurred, darkened map; two-column hub, 4-seat room with a card strip, shop/rank with side column; tested at 932x430 and 1280x720.
- b198 (beta): GPT UI kit (orange/gold buttons, gold panels, tabs, dock tiles, new menu icons) applied game-wide on the NORMAL background (no night-blue, no emoji swap). World boss room fix: wbSync looked for .wbroom (gone in b197) so picks/ready from RTDB never re-rendered; wbWrite now updates locally first.
- b199 (beta): text centred in every frame: buttons/tabs as centred flex, dock tile drawn as a 9-slice (70 60 130) so the name plate keeps its height and the label sits inside it, PvP menu buttons left-aligned consistently.
- b200 (beta): lobby logo restyled (gold PixelDeck + ember BATTLE, card fan, ornaments; .logo2); lobby team sprites removed (the .squad only renders during the tutorial, which points at it).
- b201 (beta): lobby logo = GPT 16-frame sheet (tools/logocut.py -> ui2/logo16.webp) at 16 fps with a soft float (.logo3).

## b204 — beta tester
- `TESTH` holds hashed emails of beta testers (first: Toey's friend for boss tests). Testers pass `isDev()`: beta.html access, Dev VIP, free PvP/boss tickets, instant bots, tower/stage dev buttons.
- `isOwn()` is the owner only: DEV back-office menu, VIP gifts, ADMIN diamond grants. Firestore rules still decide server-side.
- To add a tester: hash the lowercase email with h32(e,2166136261)+h32(e,40389) and push it into `TESTH`.

## b205 — boss fight fixes
- Result dialog buttons (Back / Again) live in #ov, which never routed data-act → added an #ov listener that sends `wb*` acts to `wbClick`.
- `SPOTWB(n)`: boss-fight formation, a diagonal line stepping toward the boss (back-right small → front-left big) so no plate covers another fighter.
- Player names over each ally (`.pnm`, own name gold, bots "บอท 1..3").
- `wbBar()`: boss HP bar top-right — name, Lv x/5, form (ร่าง 1 / ร่าง 2·คลั่ง below 50%), HP numbers, marks at 75 / 50 (ร่าง 2) / 25.

## b206 — party speed lock
- A boss fight with 2+ real players runs at a fixed x2 (button shows "x2 🔒"); own speed (`wbSpd0`) comes back in wbFinish / wbHub / home. Solo or bots-only keeps x1/x2/x3.

## 16-frame remake (started 16 Oct 2026) — owner's standing plan
- Every character gets a NEW model (new design, SAME name), 16 frames. Claude writes GPT prompts; Toey generates daily until the GPT quota runs out and sends that day's images.
- Store everything in tools/r16_in/<id>/ and build it into the work copy, but DO NOT deploy (not even beta) until Toey gives the word. Continue daily until done.
- Per character (5 images): 1 idle, 2 walk, 3 attack, 4 front-facing idle (lobby/avatar), 5 painted card art (cards only; monsters skip 5).
  Sheets: 4x4 grid = 16 frames, flat magenta #FF00FF, side views facing RIGHT (game mirrors), 16-bit pixel art. Attack: 1-4 wind-up, 5-8 strike (frame 7 = impact), 9-16 recover.
- Order: SL/LT cards -> L -> rest of cards -> bosses -> monsters -> 32 effects (one-row 16-frame strips).
- Batch 1 prompts sent 16 Oct: Vanarin (h29), Tenface Asura (h30), Indigo Dragonsteed (h31), Aegis Valkyrie (h27).
- Already 16-frame, skip: wb1/wb1r/wb1d, fx wb-curse / wb-pumpkin, logo16, rank-1 shield, profile frames.

## b207 — release candidate
- Guide: world-boss fight line (names, boss HP bar forms, party speed x2).
- Branch `release` holds index.html / version.json / admin.html built from this source (deploy.py) — ready, NOT pushed to pdb. To release: `git push pdb release:main` (after merging main if newer), then update the GDD.
- 16 Oct progress (branch r16, NOT live): ALL 32 cards + bosses b01-b05 + tower bosses tb1-tb5 + x65 x75 x85 x95 x14 x24 + x15 x25 x35 x45 x55 = ALL 21 bosses remade (monsters: idle/walk/attack only, idle doubles as front) — h29 h30 h31 h27 h03 h22 h07 h18 h28 h15 h13 h14 h19 h04 h26 h34 h05 h09 h10 h08 h02 h21.
  Still to do (prompts already sent for Storm Shaman h24 + Ironbark Guardian h25): h24 h25, then h16 Elder Treant, C/ST cards (h23 h17 h12 h01 h06 h20 h11), then bosses, monsters, effects.
  Built with tools/r16sheet.py (per-sheet scale, frame alignment, tint fixes COOL/GREY). Wiring f16 into the game (C[id].f16) is not done yet — do it when merging.

## b208 (branch r16 → release candidate, NOT live, NOT beta) — 16-frame remake wired in
- 53 sheets marked f16:1 in C/MON (32 cards, 21 bosses); f8 removed from h29/h30/h31/h34. Card faces/art regenerated. Images get ?16 so caches refresh (sprUrl()).
- Shop chests ui/ch_*16.webp and FOUNDER ui/founder16.webp: 16-frame strips (1600%, steps(16)). Built by tools/ui16.py from tools/ui16_in.
- loading() now preloads only the player's own cards (+ next stage monsters) — the 16-frame sheets doubled spr/ to ~54 MB.
- Still 6-frame: 44 normal monsters, star badges st6-10, tower shield tw1, 9 animated amulets, 32 fx. Prompts sent; add as they arrive (r16sheet.py 'M' rank / ui16.py).
- Release = `git push pdb release:main` (release branch = r16 + index.html/version.json/admin.html built by deploy.py), then update GDD.

## b210 animation tempo
- One tempo for every loop: 8 fps (16f=2s, 8f=1s, 6f=.75s) for characters idle/front, logo, chests, badges, frames, amulets, stars, world-boss items. Walk 12 fps. One-shot VFX/projectiles unchanged.
- 16-frame attacks use @keyframes fr16a: frames 1-6 fast (40 ms), impact frame 7 held 120 ms (hit-stop), 8-16 recover; total .8s/speed, impact still at 0.24 s.
