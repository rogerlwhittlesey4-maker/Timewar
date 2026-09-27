// Cloudflare Worker entry.
//   POST /api/claude  -> Anthropic proxy (key lives in ANTHROPIC_API_KEY secret)
//   GET  /api/save    -> this user's cloud save
//   PUT  /api/save    -> store this user's cloud save (keeps hourly backups)
//   GET  /api/save/backups        -> list this user's backups (newest first)
//   GET  /api/save/backup?ts=...  -> one backup, to recover lost data from
//   everything else   -> static assets in ./public

// Hosts that sit behind Cloudflare Access. Cloud saves are refused on any other
// host (e.g. the *.workers.dev URL), because only Access-protected hosts carry a
// trustworthy Cf-Access-Authenticated-User-Email header.
const DEFAULT_SAVE_HOSTS = ['timewarrlw.com', 'www.timewarrlw.com'];
const DEV_HOSTS = ['localhost', '127.0.0.1'];
const BACKUP_EVERY_MS = 60 * 60 * 1000;       // at most one backup per hour
const BACKUP_TTL_SECONDS = 60 * 24 * 60 * 60; // backups kept 60 days

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/claude') {
      if (request.method !== 'POST') {
        return jsonResponse({ error: 'Method Not Allowed' }, 405);
      }
      return handleClaude(request, env);
    }

    if (url.pathname === '/api/save') {
      return handleSave(request, env, url);
    }
    if (url.pathname === '/api/save/backups' || url.pathname === '/api/save/backup') {
      return handleBackups(request, env, url);
    }

    // Everything else: static files (index.html, css, images, etc.)
    return env.ASSETS.fetch(request);
  },
};

// ── Cloud save ─────────────────────────────────────────────────────────────
function saveUser(request, env, url) {
  const host = url.hostname.toLowerCase();
  if (DEV_HOSTS.includes(host)) return env.DEV_EMAIL || 'dev@localhost';
  const allowed = (env.SAVE_HOSTS ? String(env.SAVE_HOSTS).split(',') : DEFAULT_SAVE_HOSTS)
    .map(h => h.trim().toLowerCase()).filter(Boolean);
  if (!allowed.includes(host)) return null;
  const email = request.headers.get('Cf-Access-Authenticated-User-Email');
  return email ? email.trim().toLowerCase() : null;
}

async function handleSave(request, env, url) {
  if (!env.TW_SAVES) {
    return jsonResponse({ error: 'Cloud save storage (TW_SAVES) is not bound to this Worker' }, 503);
  }
  const user = saveUser(request, env, url);
  if (!user) return jsonResponse({ error: 'Not signed in through Cloudflare Access' }, 401);
  const key = 'save:' + user;

  if (request.method === 'GET') {
    const current = await env.TW_SAVES.get(key, 'json');
    if (!current) return jsonResponse({ empty: true }, 404);
    return jsonResponse(current, 200);
  }

  if (request.method === 'PUT') {
    let body;
    try { body = await request.json(); } catch (e) {
      return jsonResponse({ error: 'Invalid JSON body' }, 400);
    }
    const updatedAt = Number(body && body.updatedAt);
    if (!isFinite(updatedAt) || updatedAt <= 0 || !body.data || typeof body.data !== 'object') {
      return jsonResponse({ error: 'Body needs updatedAt and data' }, 400);
    }

    const current = await env.TW_SAVES.get(key, 'json');
    // Refuse to let an out-of-date device overwrite newer cloud data unless forced.
    if (current && Number(current.updatedAt) > updatedAt && !body.force) {
      return jsonResponse({ conflict: true, current }, 409);
    }

    const now = Date.now();
    const lastBackupAt = current ? Number(current.lastBackupAt || 0) : 0;
    let nextBackupAt = lastBackupAt;
    // Back up the copy being replaced: hourly, and always when a device forces an
    // overwrite of newer data (so the other device's work can be recovered).
    if (current && (body.force || now - lastBackupAt >= BACKUP_EVERY_MS)) {
      await env.TW_SAVES.put('backup:' + user + ':' + now, JSON.stringify(current), {
        expirationTtl: BACKUP_TTL_SECONDS,
      });
      nextBackupAt = now;
    }

    // A forced overwrite must still move the cloud version forward, so every other
    // device sees it as newer than what it holds.
    const storedAt = current ? Math.max(updatedAt, Number(current.updatedAt || 0) + 1) : updatedAt;
    const record = {
      updatedAt: storedAt,
      savedAt: now,
      device: String(body.device || '').slice(0, 120),
      lastBackupAt: nextBackupAt,
      data: body.data,
    };
    await env.TW_SAVES.put(key, JSON.stringify(record));
    return jsonResponse({ ok: true, updatedAt: storedAt, savedAt: now }, 200);
  }

  return jsonResponse({ error: 'Method Not Allowed' }, 405);
}

// Read-only access to the user's own backups. Nothing here changes the current save;
// the page merges back only what the user chooses to recover.
async function handleBackups(request, env, url) {
  if (!env.TW_SAVES) return jsonResponse({ error: 'Cloud save storage (TW_SAVES) is not bound to this Worker' }, 503);
  if (request.method !== 'GET') return jsonResponse({ error: 'Method Not Allowed' }, 405);
  const user = saveUser(request, env, url);
  if (!user) return jsonResponse({ error: 'Not signed in through Cloudflare Access' }, 401);
  const prefix = 'backup:' + user + ':';
  if (url.pathname === '/api/save/backups') {
    const keys = [];
    let cursor;
    do {
      const page = await env.TW_SAVES.list({ prefix, cursor });
      page.keys.forEach(k => keys.push(Number(k.name.slice(prefix.length))));
      cursor = page.list_complete ? null : page.cursor;
    } while (cursor);
    keys.sort((a, b) => b - a);
    return jsonResponse({ backups: keys.filter(n => isFinite(n)).slice(0, 200) }, 200);
  }
  const ts = String(url.searchParams.get('ts') || '').replace(/[^0-9]/g, '');
  if (!ts) return jsonResponse({ error: 'ts required' }, 400);
  const rec = await env.TW_SAVES.get(prefix + ts, 'json');
  if (!rec) return jsonResponse({ error: 'No such backup' }, 404);
  return jsonResponse(rec, 200);
}

// ── Anthropic proxy ────────────────────────────────────────────────────────
async function handleClaude(request, env) {
  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return jsonResponse(
      { error: 'API key not configured in Cloudflare environment variables' },
      500
    );
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return jsonResponse({ error: 'Invalid JSON body' }, 400);
  }

  try {
    const upstream = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    return jsonResponse(data, upstream.status);
  } catch (e) {
    return jsonResponse({ error: e.message }, 500);
  }
}

function jsonResponse(payload, status) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}
