// Cloudflare Worker entry — routes /api/claude to the Anthropic proxy,
// and delegates everything else to static assets in ./public.

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/claude') {
      if (request.method !== 'POST') {
        return jsonResponse({ error: 'Method Not Allowed' }, 405);
      }
      return handleClaude(request, env);
    }

    // Everything else: static files (index.html, css, images, etc.)
    return env.ASSETS.fetch(request);
  },
};

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
    headers: { 'Content-Type': 'application/json' },
  });
}
