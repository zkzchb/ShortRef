import assert from "node:assert/strict";
import test from "node:test";
import { handleRequest } from "../src/index.js";

function envWith(record, error = null) {
  return {
    SHORTREF_KV: {
      async get() {
        if (error) throw error;
        return record;
      },
    },
  };
}

test("redirects an active record with 302", async () => {
  const response = await handleRequest(
    new Request("https://reference.gany.app/Ab12Cd34"),
    envWith({ version: 1, url: "https://example.com/docs?a=1", status: "active" }),
  );
  assert.equal(response.status, 302);
  assert.equal(response.headers.get("location"), "https://example.com/docs?a=1");
  assert.equal(response.headers.get("cache-control"), "no-store, max-age=0");
});

test("supports HEAD requests", async () => {
  const response = await handleRequest(
    new Request("https://reference.gany.app/Ab12Cd34", { method: "HEAD" }),
    envWith({ version: 1, url: "https://example.com/", status: "active" }),
  );
  assert.equal(response.status, 302);
  assert.equal(await response.text(), "");
});

test("returns 404 for invalid ids without querying KV", async () => {
  let queried = false;
  const response = await handleRequest(
    new Request("https://reference.gany.app/not-short"),
    { SHORTREF_KV: { async get() { queried = true; return null; } } },
  );
  assert.equal(response.status, 404);
  assert.equal(queried, false);
});

test("returns 404 for inactive or malformed records", async () => {
  for (const record of [
    null,
    { version: 1, url: "https://example.com", status: "inactive" },
    { version: 1, url: "javascript:alert(1)", status: "active" },
    { version: 2, url: "https://example.com", status: "active" },
  ]) {
    const response = await handleRequest(
      new Request("https://reference.gany.app/Ab12Cd34"), envWith(record),
    );
    assert.equal(response.status, 404);
  }
});

test("rejects write methods", async () => {
  const response = await handleRequest(
    new Request("https://reference.gany.app/Ab12Cd34", { method: "POST" }), envWith(null),
  );
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET, HEAD");
});

test("returns 503 when KV is unavailable", async () => {
  const response = await handleRequest(
    new Request("https://reference.gany.app/Ab12Cd34"),
    envWith(null, new Error("KV unavailable")),
  );
  assert.equal(response.status, 503);
  assert.equal(response.headers.get("retry-after"), "30");
});
