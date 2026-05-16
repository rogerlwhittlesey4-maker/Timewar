// Cloudflare Pages Function — handles POST /api/claude
// File path -> URL mapping is automatic in Cloudflare Pages.
// This file lives at functions/api/claude.js, so it answers /api/claude.

export async function onRequestPost(context) {
  const { request, env } = context;

  const ANTHROPIC_API_KEY = env.ANTHROPIC_API_KEY;
  if (!ANTHROPIC_API_KEY) {
    return json({ error: 'API key not configured in Cloudflare environment variables' }, 500);
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ error: 'Invalid JSON body' }, 400);
  }

  try {
    const upstream = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });

    const data = await upstream.json();
    return json(data, upstream.status);
  } catch (e) {
    return json({ error: e.message }, 500);
  }
}

// Reject any non-POST method explicitly so the user gets a clean 405
// rather than the function silently not running.
export async function onRequest(context) {
  return json({ error: 'Method Not Allowed' }, 405);
}

function json(payload, status) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
