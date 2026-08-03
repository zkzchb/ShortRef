const ID_PATTERN = /^[0-9A-Za-z]{8,12}$/;

const SECURITY_HEADERS = Object.freeze({
  "Cache-Control": "no-store, max-age=0",
  "Content-Security-Policy": [
    "default-src 'none'",
    "style-src 'unsafe-inline'",
    "frame-ancestors 'none'",
    "base-uri 'none'",
    "form-action 'none'",
  ].join("; "),
  "Referrer-Policy": "no-referrer",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
});

function textResponse(body, status, extraHeaders = {}) {
  return new Response(body, {
    status,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      ...SECURITY_HEADERS,
      ...extraHeaders,
    },
  });
}

async function pageResponse(request, env, assetPath, status) {
  try {
    const assetUrl = new URL(assetPath, request.url);
    const asset = await env.ASSETS.fetch(assetUrl);

    if (!asset.ok) {
      throw new Error(`Page asset returned ${asset.status}`);
    }

    const headers = new Headers(asset.headers);
    headers.set("Content-Type", "text/html; charset=utf-8");
    for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
      headers.set(name, value);
    }

    return new Response(request.method === "HEAD" ? null : asset.body, {
      status,
      headers,
    });
  } catch {
    return textResponse("Service Unavailable", 503, {
      "Retry-After": "30",
    });
  }
}

function parseTarget(record) {
  if (
    !record ||
    typeof record !== "object" ||
    record.version !== 1 ||
    record.status !== "active" ||
    typeof record.url !== "string"
  ) {
    return null;
  }

  try {
    const target = new URL(record.url);
    if (target.protocol !== "http:" && target.protocol !== "https:") {
      return null;
    }
    return target.href;
  } catch {
    return null;
  }
}

export async function handleRequest(request, env) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return textResponse("Method Not Allowed", 405, { Allow: "GET, HEAD" });
  }

  const requestUrl = new URL(request.url);

  if (requestUrl.pathname === "/") {
    return pageResponse(request, env, "/index.html", 200);
  }

  const id = requestUrl.pathname.slice(1);

  if (!ID_PATTERN.test(id)) {
    return pageResponse(request, env, "/404.html", 404);
  }

  try {
    const record = await env.SHORTREF_KV.get(id, {
      type: "json",
      cacheTtl: 60,
    });
    const target = parseTarget(record);

    if (!target) {
      return pageResponse(request, env, "/404.html", 404);
    }

    return new Response(null, {
      status: 302,
      headers: {
        Location: target,
        ...SECURITY_HEADERS,
      },
    });
  } catch {
    return textResponse("Service Unavailable", 503, {
      "Retry-After": "30",
    });
  }
}

export default {
  fetch(request, env) {
    return handleRequest(request, env);
  },
};
