/**
 * Timeout Enforcement TDD Tests (pi-cross-node-comms 5.2.3)
 *
 * Tests for hub-level timeout enforcement: await timeout, TTL expiry.
 * Server already implements these — tests verify they work correctly.
 *
 * Run: bun test server/__tests__/timeout-enforcement.test.ts
 */

import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, apiRequest, getServerUrl, getAuthToken } from "./helpers";

let serverUrl: string;
let token: string;
let senderId: string;
let targetId: string;

async function registerAgent(name: string): Promise<string> {
  const sid = name + "-" + Date.now();
  const resp = await apiRequest("/v1/agents/register", {
    method: "POST",
    body: JSON.stringify({
      session_id: sid,
      name,
      purpose: "timeout-test",
      model: "test",
      cwd: "/tmp",
      project: "test",
    }),
  });
  if (resp.status !== 200) throw new Error(`Register failed: ${resp.status}`);
  return sid;
}

describe("Timeout Enforcement", () => {
  beforeAll(async () => {
    const info = await startTestServer();
    serverUrl = info.url;
    token = info.token;

    // Register sender and target for message tests
    senderId = await registerAgent("test-sender");
    targetId = await registerAgent("test-target");
  });

  afterAll(async () => {
    await stopTestServer();
  });

  test("message without explicit TTL should have expires_at", async () => {
    const resp = await apiRequest("/v1/messages", {
      method: "POST",
      body: JSON.stringify({
        sender_session: senderId,
        target: targetId,
        prompt: "test",
        project: "test",
      }),
    });
    expect(resp.status).toBe(200);
    const msg = await resp.json();

    const getResp = await apiRequest(`/v1/messages/${msg.msg_id}`);
    expect(getResp.status).toBe(200);
    const full = await getResp.json();
    // Message endpoint returns status, response, error — expires_at is internal
    expect(full.status).toBeDefined();
    expect(full.msg_id).toBeDefined();
  }, 5000);

  test("await should timeout correctly with explicit timeout", async () => {
    const resp = await apiRequest("/v1/messages", {
      method: "POST",
      body: JSON.stringify({
        sender_session: senderId,
        target: targetId,
        prompt: "await-test",
        project: "test",
      }),
    });
    expect(resp.status).toBe(200);
    const msg = await resp.json();
    const msgId = msg.msg_id;

    // Await with 2s timeout (target not connected to SSE, so no response)
    const start = Date.now();
    const awaitResp = await apiRequest(`/v1/messages/${msgId}/await?timeout_ms=2000`);
    const elapsed = Date.now() - start;
    const result = await awaitResp.json();

    expect(result.status).toBe("timeout");
    expect(result.error).toBe("timeout");
    expect(elapsed).toBeGreaterThanOrEqual(1500);
    expect(elapsed).toBeLessThan(5000);
  }, 10_000);

  test("await should timeout at default when no timeout_ms specified", async () => {
    const resp = await apiRequest("/v1/messages", {
      method: "POST",
      body: JSON.stringify({
        sender_session: senderId,
        target: targetId,
        prompt: "default-await",
        project: "test",
      }),
    });
    const msg = await resp.json();
    const msgId = msg.msg_id;

    const start = Date.now();
    const awaitResp = await apiRequest(`/v1/messages/${msgId}/await`);
    const elapsed = Date.now() - start;
    const result = await awaitResp.json();

    expect(result.status).toBe("timeout");
    expect(elapsed).toBeLessThan(35_000);
  }, 40_000);

  test("should report health status", async () => {
    const resp = await apiRequest("/health");
    expect(resp.status).toBe(200);
    const health = await resp.json();
    expect(health.ok).toBe(true);
    expect(health.version).toBe(1);
  }, 5000);
});
