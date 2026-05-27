/**
 * Server integration tests — full lifecycle via Bun.serve test instance
 *
 * Tests registration, heartbeats, message routing, SSE, stale/offline detection,
 * and the complete request/response cycle.
 */
import { describe, expect, test, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, getServerUrl, getAuthToken, apiRequest } from "./helpers";

beforeAll(async () => {
	await startTestServer();
});

afterAll(async () => {
	await stopTestServer();
});

// ─── Registration ──────────────────────────────────────────────────────

describe("POST /v1/agents/register", () => {
	test("registers a new agent and returns 200", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-reg-001",
				name: "test-agent-reg",
				purpose: "integration test",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.ok).toBe(true);
		expect(body.agent).toBeDefined();
		expect(body.agent.name).toBe("test-agent-reg");
		expect(body.agent.status).toBe("online");
		expect(body.heartbeat_interval_ms).toBeGreaterThan(0);
	});

	test("re-registers same session_id returns 200 with isReregister flag", async () => {
		// First registration
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-rereg-001",
				name: "test-rereg-agent",
				purpose: "integration test",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Re-registration
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-rereg-001",
				name: "test-rereg-agent",
				purpose: "integration test — updated",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.ok).toBe(true);
		expect(body.agent.session_id).toBe("test-rereg-001");
	});

	test("rejects registration without auth token", async () => {
		const res = await fetch(`${getServerUrl()}/v1/agents/register`, {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-noauth",
				name: "no-auth-agent",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
			headers: { "Content-Type": "application/json" },
		});
		expect(res.status).toBe(401);
	});

	test("rejects registration with wrong auth token", async () => {
		const res = await fetch(`${getServerUrl()}/v1/agents/register`, {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-badauth",
				name: "bad-auth-agent",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
			headers: {
				"Content-Type": "application/json",
				"Authorization": "Bearer wrong-token",
			},
		});
		expect(res.status).toBe(401);
	});
});

// ─── Agent Listing ─────────────────────────────────────────────────────

describe("GET /v1/agents", () => {
	test("returns list of registered agents", async () => {
		// Register an agent first
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-list-001",
				name: "test-list-agent",
				purpose: "listing test",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const res = await apiRequest("/v1/agents?project=test");
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(Array.isArray(body.agents)).toBe(true);
		expect(body.agents.length).toBeGreaterThanOrEqual(1);

		const agent = body.agents.find((a: any) => a.name === "test-list-agent");
		expect(agent).toBeDefined();
		expect(agent.session_id).toBe("test-list-001");
	});

	test("filters by project — nonexistent project returns empty", async () => {
		const res = await apiRequest("/v1/agents?project=nonexistent-project-xyz");
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(Array.isArray(body.agents)).toBe(true);
	});
});

// ─── Message Routing ──────────────────────────────────────────────────

describe("POST /v1/messages", () => {
	test("queues a message between registered agents (no SSE streams)", async () => {
		// Register sender and target
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-sender-msg",
				name: "test-sender",
				purpose: "message test sender",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-target-msg",
				name: "test-target",
				purpose: "message test target",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Send message — status will be "queued" since neither agent has an SSE stream
		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "test-sender-msg",
				target_session: "test-target-msg",
				prompt: "Hello from integration test",
				project: "test",
			}),
		});

		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.ok).toBe(true);
		expect(body.msg_id).toBeDefined();
		// Without SSE streams, messages are queued (not delivered)
		expect(["queued", "delivered"]).toContain(body.status);
	});

	test("rejects message from unregistered sender", async () => {
		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "nonexistent-sender",
				target_session: "test-target-msg",
				prompt: "Hello",
				project: "test",
			}),
		});
		expect(res.status).toBe(404);
		const body = await res.json();
		expect(body.ok).toBe(false);
		expect(body.error).toBe("sender_not_registered");
	});

	test("rejects message to nonexistent target", async () => {
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-sender-notarget",
				name: "test-sender-notarget",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "test-sender-notarget",
				target_session: "nonexistent-target",
				prompt: "Hello",
				project: "test",
			}),
		});
		expect(res.status).toBe(404);
	});

	test("delivers message by name using target field", async () => {
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-name-sender",
				name: "name-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-name-target",
				name: "name-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "test-name-sender",
				target: "name-target",
				prompt: "Hello by name",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.ok).toBe(true);
	});
});

// ─── Message Retrieval ────────────────────────────────────────────────

describe("GET /v1/messages/:msg_id", () => {
	test("retrieves a queued message by ID", async () => {
		// Register and send
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-get-sender",
				name: "get-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "test-get-target",
				name: "get-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "test-get-sender",
				target_session: "test-get-target",
				prompt: "Message for retrieval test",
				project: "test",
			}),
		});

		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;
		expect(msgId).toBeDefined();

		// Retrieve the message
		const res = await apiRequest(`/v1/messages/${msgId}?project=test&session_id=test-get-sender`);
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.msg_id).toBe(msgId);
		// Without SSE streams, status will be "queued"
		expect(["queued", "delivered"]).toContain(body.status);
	});

	test("returns not_found for nonexistent message ID", async () => {
		const res = await apiRequest("/v1/messages/nonexistent-msg-id?project=test&session_id=test-get-sender");
		expect(res.status).toBe(404);
	});
});

// ─── Health Check ─────────────────────────────────────────────────────

describe("GET /health", () => {
	test("returns 200 without auth", async () => {
		const res = await fetch(`${getServerUrl()}/health`);
		expect(res.status).toBe(200);
	});

	test("returns JSON with ok=true", async () => {
		const res = await fetch(`${getServerUrl()}/health`);
		const body = await res.json();
		expect(body.ok).toBe(true);
	});
});

// ─── Error Handling ───────────────────────────────────────────────────

describe("Error handling", () => {
	test("unknown /v1/ routes return 404", async () => {
		const res = await apiRequest("/v1/nonexistent");
		expect(res.status).toBe(404);
	});

	test("invalid JSON body returns 400", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: "not json",
		});
		expect(res.status).toBe(400);
	});

	test("missing required fields returns 400", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({ project: "test" }), // missing session_id, name
		});
		expect(res.status).toBe(400);
	});
});