// Pixeldeck Battle - automatic top-up server (Cloudflare Worker)
//
// A player pays by PromptPay, then uploads the slip from the game. This Worker
//   1. checks who is asking (Firebase ID token -> player uid),
//   2. sends the slip to Thunder Solution, which confirms with the bank that it is real,
//   3. requires: paid INTO the owner's registered account, amount = exactly one diamond pack, made in the last 24 hours,
//   4. records the slip's bank reference so the same slip can never be used twice,
//   5. writes grants/{ref} in Firestore; the player's game collects the diamonds from there.
//
// Secrets to set in Cloudflare (Settings > Variables and Secrets). Never put them in this file or in the game:
//   THUNDER_KEY   Thunder Solution API key
//   FB_PROJECT    Firebase project id, e.g. pixeldeck-battle-1a625
//   FB_SA_EMAIL   client_email from the Firebase service-account JSON
//   FB_SA_KEY     private_key from the same JSON (the whole -----BEGIN PRIVATE KEY----- ... block)
//                 Easier: paste the WHOLE JSON file into FB_SA_KEY and skip FB_SA_EMAIL.
// Optional plain variable:
//   ALLOW_ORIGIN  site allowed to call this Worker (default https://seeker6131.github.io)

// [diamonds, bonus, price THB] - must match DPACKS in the game
const PACKS = [[60,0,35],[120,10,69],[300,30,169],[900,100,499],[1500,300,799],[2500,700,1490]];
const MAX_AGE_H = 24;          // a slip older than this is refused
const THROTTLE_MS = 15000;     // one attempt per player per 15 s (each attempt uses Thunder quota)
const MAX_IMAGE = 4 * 1024 * 1024;

let jwkCache = null, jwkAt = 0, tokCache = null, tokExp = 0;
const lastTry = new Map();

const b64u = s => { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return Uint8Array.from(atob(s), c => c.charCodeAt(0)); };
const toB64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const enc = s => new TextEncoder().encode(s);

async function verifyIdToken(token, project) {
  const p = String(token || '').split('.'); if (p.length !== 3) throw new Error('bad token');
  const head = JSON.parse(new TextDecoder().decode(b64u(p[0]))), body = JSON.parse(new TextDecoder().decode(b64u(p[1])));
  if (head.alg !== 'RS256') throw new Error('bad alg');
  if (!jwkCache || Date.now() - jwkAt > 3600e3) {
    const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
    if (!r.ok) throw new Error('keys'); jwkCache = (await r.json()).keys; jwkAt = Date.now();
  }
  const jwk = jwkCache.find(k => k.kid === head.kid); if (!jwk) throw new Error('unknown key');
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64u(p[2]), enc(p[0] + '.' + p[1]));
  const now = Date.now() / 1000;
  if (!ok || body.aud !== project || body.iss !== 'https://securetoken.google.com/' + project || !(body.exp > now) || !body.sub) throw new Error('token rejected');
  return body.sub;
}

// the secret may be the bare private key, or the whole service-account JSON file
function svc(env) {
  const raw = String(env.FB_SA_KEY || '').trim();
  if (raw[0] === '{') { try { const j = JSON.parse(raw); return { email: j.client_email || '', key: j.private_key || '' }; } catch (e) { return { email: '', key: '' }; } }
  return { email: String(env.FB_SA_EMAIL || '').trim().replace(/^"|"$/g, ''), key: raw };
}

async function accessToken(env) {
  const sa = svc(env);
  if (tokCache && Date.now() < tokExp - 60000) return tokCache;
  const now = Math.floor(Date.now() / 1000);
  const claim = { iss: sa.email, scope: 'https://www.googleapis.com/auth/datastore', aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600 };
  const unsigned = toB64u(enc(JSON.stringify({ alg: 'RS256', typ: 'JWT' }))) + '.' + toB64u(enc(JSON.stringify(claim)));
  const pem = String(sa.key).replace(/\\n/g, '\n').replace(/"/g, '').replace(/-----[^-]+-----/g, '').replace(/\s+/g, '');
  const key = await crypto.subtle.importKey('pkcs8', Uint8Array.from(atob(pem), c => c.charCodeAt(0)), { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const jwt = unsigned + '.' + toB64u(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, enc(unsigned)));
  const r = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: 'grant_type=' + encodeURIComponent('urn:ietf:params:oauth:grant-type:jwt-bearer') + '&assertion=' + jwt });
  const j = await r.json(); if (!r.ok || !j.access_token) throw new Error('google auth');
  tokCache = j.access_token; tokExp = Date.now() + (j.expires_in || 3600) * 1000; return tokCache;
}

// create a document only if it does not exist yet; returns 'ok' | 'exists' | 'error'
async function createDoc(env, coll, id, fields) {
  const url = `https://firestore.googleapis.com/v1/projects/${env.FB_PROJECT}/databases/(default)/documents/${coll}?documentId=${encodeURIComponent(id)}`;
  const r = await fetch(url, { method: 'POST', headers: { authorization: 'Bearer ' + await accessToken(env), 'content-type': 'application/json' }, body: JSON.stringify({ fields }) });
  return r.ok ? 'ok' : r.status === 409 ? 'exists' : 'error';
}
const sv = v => ({ stringValue: String(v) }), iv = v => ({ integerValue: String(v) });

export default {
  async fetch(req, env) {
    const origin = env.ALLOW_ORIGIN || 'https://seeker6131.github.io';
    const cors = { 'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type', 'vary': 'origin' };
    const out = (status, o) => new Response(JSON.stringify(o), { status, headers: { ...cors, 'content-type': 'application/json' } });
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (req.method !== 'POST') return out(405, { ok: false, code: 'method' });
    if (!env.THUNDER_KEY || !env.FB_PROJECT || !svc(env).email || !svc(env).key) return out(500, { ok: false, code: 'not_configured' });
    try {
      const form = await req.formData(), img = form.get('image'), pi = Number(form.get('pack'));
      const pack = Number.isInteger(pi) ? PACKS[pi] : null;
      if (!pack) return out(400, { ok: false, code: 'bad_pack' });
      if (!img || typeof img === 'string' || !img.size) return out(400, { ok: false, code: 'no_image' });
      if (img.size > MAX_IMAGE) return out(400, { ok: false, code: 'image_too_large' });
      let uid; try { uid = await verifyIdToken(form.get('token'), env.FB_PROJECT); } catch (e) { return out(401, { ok: false, code: 'login' }); }
      const t = Date.now(); if (t - (lastTry.get(uid) || 0) < THROTTLE_MS) return out(429, { ok: false, code: 'slow_down' });
      lastTry.set(uid, t); if (lastTry.size > 5000) lastTry.clear();

      const price = pack[2], dia = pack[0] + pack[1];
      const tf = new FormData(); tf.append('image', img, img.name || 'slip.jpg'); tf.append('matchAccount', 'true'); tf.append('matchAmount', String(price)); tf.append('remark', uid.slice(0, 60));
      const tr = await fetch('https://api.thunder.in.th/v2/verify/bank', { method: 'POST', headers: { authorization: 'Bearer ' + env.THUNDER_KEY }, body: tf });
      let tj = null; try { tj = await tr.json(); } catch (e) {}
      if (!tr.ok || !tj || !tj.success || !tj.data) {
        const c = tj && (tj.code || (tj.error && tj.error.code)) || '';
        return out(400, { ok: false, code: c === 'SLIP_PENDING' ? 'pending' : c === 'SLIP_NOT_FOUND' ? 'no_qr' : tr.status === 401 || tr.status === 403 ? 'checker_auth' : tr.status === 402 || tr.status === 429 ? 'checker_quota' : 'not_verified', detail: String(c).slice(0, 40) });
      }
      const d = tj.data, raw = d.rawSlip || {}, ref = String(raw.transRef || '');
      const amt = Number(d.amountInSlip != null ? d.amountInSlip : raw.amount && raw.amount.amount);
      if (!/^[A-Za-z0-9]{8,64}$/.test(ref)) return out(400, { ok: false, code: 'not_verified' });
      if (!d.matchedAccount) return out(400, { ok: false, code: 'wrong_account' });
      if (!(Math.abs(amt - price) < 0.005)) return out(400, { ok: false, code: 'wrong_amount', paid: amt, need: price });
      const when = Date.parse(raw.date || ''); if (!(when > 0) || t - when > MAX_AGE_H * 3600e3 || when - t > 600e3) return out(400, { ok: false, code: 'too_old' });

      const iso = new Date(t).toISOString();
      const led = await createDoc(env, 'slips', ref, { to: sv(uid), dia: iv(dia), thb: iv(price), at: { timestampValue: iso }, paid: { timestampValue: new Date(when).toISOString() } });
      if (led === 'exists') return out(409, { ok: false, code: 'used' });
      if (led !== 'ok') return out(502, { ok: false, code: 'store' });
      const g = await createDoc(env, 'grants', ref, { to: sv(uid), dia: iv(dia), by: sv('auto'), ref: sv(ref), at: { timestampValue: iso } });
      if (g !== 'ok' && g !== 'exists') return out(502, { ok: false, code: 'grant_failed', ref });
      return out(200, { ok: true, dia, ref });
    } catch (e) { return out(500, { ok: false, code: 'server' }); }
  }
};
