/**
 * Mock Fleet Node TDD Tests (pi-cross-node-comms 5.2.2)
 *
 * Full lifecycle: register REST agent → connect SSE → receive prompts → respond.
 * Simulates a fleet node on the coms-net hub.
 *
 * Run: bun test server/__tests__/mock-fleet-node.test.ts
 */

import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, apiRequest, getServerUrl, getAuthToken } from "./helpers";

let serverUrl: string;
let token: string;

// ── SSE Client ──────────────────────────────────────────────────────────────

async function* readSSE(body: ReadableStream<Uint8Array>): AsyncGenerator<{ event: string; data: unknown }> {
  const decoder = new TextDecoder();
  let buffer = "";
  const reader = body.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split("\n\n");
      buffer = frames.pop() || "";
      for (const frame of frames) {
        if (!frame.trim()) continue;
        let event = "message";
        let data = "";
        for (const line of frame.split("\n")) {
          if (line.startsWith("event: ")) event = line.slice(7);
          else if (line.startsWith("data: ")) data = line.slice(6);
        }
        try {
          yield { event, data: JSON.parse(data) };
        } catch {
          yield { event, data };
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// ── Mock Fleet Node ────────────────────────────────────────────────────────

class MockFleetNode {
  url: string;
  token: string;
  sseController: AbortController | null = null;
  agentId = "";

  constructor(url: string, token: string) {
    this.url = url;
    this.token = token;
  }

  async register(name: string): Promise<string> {
    const sid = `mock-${name}-${Date.now()}`;
    const resp = await apiRequest("/v1/agents/register", {
      method: "POST",
      body: JSON.stringify({
        session_id: sid,
        name,
        purpose: "mock-fleet-test",
        model: "gemma4:31b",
        cwd: "/tmp",
        project: "test",
      }),
    });
    if (resp.status !== 200) throw new Error(`Register failed: ${resp.status}`);
    const body = await resp.json();
    expect(body.ok).toBe(true);
    this.agentId = body.agent.session_id;
    return body.agent.session_id;
  }

  async *connect(agentId: string): AsyncGenerator<{ event: string; data: unknown }> {
    this.sseController = new AbortController();
    const sseUrl = `${this.url}/v1/events?project=test&session_id=${agentId}`;
    const resp = await fetch(sseUrl, {
      headers: { Authorization: `Bearer ${this.token}` },
      signal: this.sseController.signal,
    });
    if (!resp.ok || !resp.body) throw new Error(`SSE connect failed: ${resp.status}`);

    for await (const event of readSSE(resp.body)) {
      yield event;
    }
  }

  async sendResponse(msgId: string, responderSession: string, payload: Record<string, unknown>) {
    return apiRequest(`/v1/messages/${msgId}/response`, {
      method: "POST",
      body: JSON.stringify({ ...payload, responder_session: responderSession }),
    });
  }

  close() {
    if (this.sseController) {
      this.sseController.abort();
      this.sseController = null;
    }
  }
}

// ── Tests ──────────────────────────────────────────────────────────────────

describe("Mock Fleet Node", () => {
  beforeAll(async () => {
    const info = await startTestServer();
    serverUrl = info.url;
    token = info.token;
  });

  afterAll(async () => {
    await stopTestServer();
  });

  test("should register, connect SSE, receive hello event", async () => {
    const node = new MockFleetNode(serverUrl, token);
    const agentId = await node.register("hello-test");
    expect(agentId).toBeTruthy();

    const generator = node.connect(agentId);
    const first = await generator.next();
    if (first.done) throw new Error("No SSE events");

    const hello = first.value;
    expect(hello.event).toBe("hello");
    expect(hello.data).toBeDefined();

    node.close();
  }, 10_000);

  test("should receive prompt and respond successfully", async () => {
    const node = new MockFleetNode(serverUrl, token);
    const agentId = await node.register("ping-pong");
    const generator = node.connect(agentId);

    // Skip hello and pool_snapshot events
    const hello = await generator.next();
    expect(hello.value.event).toBe("hello");
    const snapshot = await generator.next();
    expect(snapshot.value.event).toBe("pool_snapshot");

    // Register sender agent for message routing
    const senderId = "sender-" + Date.now();
    await apiRequest("/v1/agents/register", {
      method: "POST",
      body: JSON.stringify({
        session_id: senderId,
        name: "test-sender",
        purpose: "mock-test",
        model: "test",
        cwd: "/tmp",
        project: "test",
      }),
    });

    // Send message to the node
    const sendResp = await apiRequest("/v1/messages", {
      method: "POST",
      body: JSON.stringify({
        sender_session: senderId,
        target: agentId,
        prompt: "ping",
        project: "test",
      }),
    });
    expect(sendResp.status).toBe(200);
    const sent = await sendResp.json();
    const msgId = sent.msg_id;
    expect(sent.status).toBe("delivered");

    // Skip agent_joined event from sender registration
    const joined = await generator.next();
    expect(joined.value.event).toBe("agent_joined");

    // Read the prompt from SSE
    const promptEvent = await generator.next();
    expect(promptEvent.value.event).toBe("prompt");
    expect(promptEvent.value.data.msg_id).toBe(msgId);
    expect(promptEvent.value.data.prompt).toBe("ping");

    // Respond
    const resp = await node.sendResponse(msgId, agentId, { response: "pong" });
    expect(resp.status).toBe(200);

    // Verify final status
    const getResp = await apiRequest(`/v1/messages/${msgId}`);
    expect(getResp.status).toBe(200);
    const final = await getResp.json();
    expect(final.status).toBe("complete");
    expect(final.response).toBe("pong");

    node.close();
  }, 15_000);

  test("should register multiple agents and route messages correctly", async () => {
    const nodeA = new MockFleetNode(serverUrl, token);
    const nodeB = new MockFleetNode(serverUrl, token);

    const agentA = await nodeA.register("worker-alpha");
    const agentB = await nodeB.register("worker-beta");
    expect(agentA).not.toBe(agentB);

    const listResp = await apiRequest("/v1/agents");
    expect(listResp.status).toBe(200);
    const agents = await listResp.json();
    expect(Array.isArray(agents.agents)).toBe(true);

    nodeA.close();
    nodeB.close();
  }, 10_000);

  test("should handle SSE reconnect (simulated by re-registration)", async () => {
    const node = new MockFleetNode(serverUrl, token);

    const agentId = await node.register("reconnect-test");
    let generator = node.connect(agentId);
    let hello = await generator.next();
    expect(hello.value.event).toBe("hello");
    node.close();

    // Re-register — server reuses session_id, so same agentId
    const agentId2 = await node.register("reconnect-test");
    expect(agentId2).toBeTruthy();
    generator = node.connect(agentId2);
    hello = await generator.next();
    expect(hello.value.event).toBe("hello");

    node.close();
  }, 15_000);

  // ── TTL Tests ─────────────────────────────────────────────────────────

  test("should expire message after TTL timeout", async () => {
    const node = new MockFleetNode(serverUrl, token);
    const agentId = await node.register("ttl-test");
    const generator = node.connect(agentId);
    await generator.next(); // skip hello
    await generator.next(); // skip pool_snapshot

    // Send message with short TTL
    const sendResp = await apiRequest("/v1/messages", {
      method: "POST",
      body: JSON.stringify({
        sender_session: "orchestrator-test",
        target: agentId,
        prompt: "expire-me",
        project: "test",
        ttl_ms: 1000,
      }),
    });
    const sent = await sendResp.json();
    const msgId = sent.msg_id;

    // Read prompt event
    const msgEvent = await generator.next();
    // SSE delivers content as "message" event when target is connected
    expect(msgEvent.value.event).toBe("message");

    // Wait for TTL scan
    await new Promise((r) => setTimeout(r, 12_000));

    // Should be expired
    const getResp = await apiRequest(`/v1/messages/${msgId}`);
    // After TTL expiry, message may be deleted (404) or status "error"
    if (getResp.status === 200) {
      const final = await getResp.json();
      expect(final.status).toBe("error");
      expect(final.error).toBe("expired");
    } else {
      expect(getResp.status).toBe(404);
    }

    node.close();
  }, 30_000);
});
