import assert from "node:assert/strict";
import test from "node:test";
import { handleRequest } from "../src/index.js";

const HOME_HTML = "<!doctype html><title>ShortRef</title><h1>稳定引用服务</h1>";
const NOT_FOUND_HTML = "<!doctype html><title>404</title><h1>引用不存在或已停用</h1>";

function envWith(record, error = null, assetError = null) {
  return {
    SHORTREF_KV: {
      async get() {
        if (error) throw error;
        return record;
      },
    },
    ASSETS: {
      async fetch(input) {
        if (assetError) throw assetError;
        const pathname = new URL(input).pathname;
        const body = pathname === "/index.html" ? HOME_HTML : NOT_FOUND_HTML;
        return new Response(body, {
          headers: { "Content-Type": "text/html" },
        });
      },
    },
  };
}

test("returns the service page at the root", async () => {
  let queried = false;
  const env = envWith(null);
  env.SHORTREF_KV.get = async () => {
    queried = true;
    return null;
  };

  const response = await handleRequest(new Request("https://shortref.example/"), env);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /稳定引用服务/);
  assert.equal(response.headers.get("content-type"), "text/html; charset=utf-8");
  assert.equal(response.headers.get("cache-control"), "no-store, max-age=0");
  assert.equal(queried, false);
});

test("redirects an active record with 302", async () => {
  const response = await handleRequest(
    new Request("https://shortref.example/Ab12Cd34"),
    envWith({ version: 1, url: "https://example.com/docs?a=1", status: "active" }),
  );
  assert.equal(response.status, 302);
  assert.equal(response.headers.get("location"), "https://example.com/docs?a=1");
  assert.equal(response.headers.get("cache-control"), "no-store, max-age=0");
});

test("supports HEAD requests without a response body", async () => {
  for (const url of ["https://shortref.example/", "https://shortref.example/Ab12Cd34"]) {
    const response = await handleRequest(
      new Request(url, { method: "HEAD" }),
      envWith({ version: 1, url: "https://example.com/", status: "active" }),
    );
    assert.equal(await response.text(), "");
  }
});

test("returns the HTML 404 page for invalid ids without querying KV", async () => {
  let queried = false;
  const response = await handleRequest(
    new Request("https://shortref.example/not-short"),
    {
      ...envWith(null),
      SHORTREF_KV: {
        async get() {
          queried = true;
          return null;
        },
      },
    },
  );
  assert.equal(response.status, 404);
  assert.match(await response.text(), /引用不存在或已停用/);
  assert.equal(response.headers.get("content-type"), "text/html; charset=utf-8");
  assert.equal(queried, false);
});

test("returns the HTML 404 page for inactive or malformed records", async () => {
  for (const record of [
    null,
    { version: 1, url: "https://example.com", status: "inactive" },
    { version: 1, url: "javascript:alert(1)", status: "active" },
    { version: 2, url: "https://example.com", status: "active" },
  ]) {
    const response = await handleRequest(
      new Request("https://shortref.example/Ab12Cd34"),
      envWith(record),
    );
    assert.equal(response.status, 404);
    assert.match(await response.text(), /引用不存在或已停用/);
  }
});

test("rejects write methods", async () => {
  const response = await handleRequest(
    new Request("https://shortref.example/Ab12Cd34", { method: "POST" }),
    envWith(null),
  );
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET, HEAD");
});

test("returns 503 when KV is unavailable", async () => {
  const response = await handleRequest(
    new Request("https://shortref.example/Ab12Cd34"),
    envWith(null, new Error("KV unavailable")),
  );
  assert.equal(response.status, 503);
  assert.equal(response.headers.get("retry-after"), "30");
});

test("returns 503 when a page asset is unavailable", async () => {
  const response = await handleRequest(
    new Request("https://shortref.example/"),
    envWith(null, null, new Error("Assets unavailable")),
  );
  assert.equal(response.status, 503);
  assert.equal(response.headers.get("retry-after"), "30");
});
