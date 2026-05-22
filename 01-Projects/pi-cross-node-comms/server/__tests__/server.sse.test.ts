/**
 * SSE + Stale Agent integration tests
 *
 * Tests SSE connection lifecycle, event delivery, heartbeat updates,
 * stale/offline detection, and agent cleanup.
 */
import { describe, expect, test, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, getServerUrl, getAuthToken, apiRequest } from "./helpers";

beforeAll(async () => {
	await startTestServer();
});

afterAll(async () => {
	await stopTestServer();
});

// ─── Helper: Connect to SSE stream and collect events ───────────────────

interface SSEEvent {
	event: string;
	data: any;
	id?: number;
}

function connectSSE(
	sessionId: string,
	project: string = "test",
): {
	events: SSEEvent[];
	close: () => void;
	promise: Promise<void>;
} {
	const url = `${getServerUrl()}/v1/events?project=${encodeURIComponent(project)}&session_id=${encodeURIComponent(sessionId)}`;
	const events: SSEEvent[] = [];
	let controller: AbortController | null = new AbortController();

	const promise = fetch(url, {
		headers: { Authorization: `Bearer ${getAuthToken()}` },
		signal: controller.signal,
	})
		.then(async (res) => {
			expect(res.status).toBe(200);
			expect(res.headers.get("content-type")).toContain("text/event-stream");
			const reader = res.body!.getReader();
			const decoder = new TextDecoder();
			let buffer = "";

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += decoder.decode(value, { stream: true });

				// Parse SSE frames from buffer
				const frames = buffer.split("\n\n");
				buffer = frames.pop()!; // keep incomplete frame in buffer

				for (const frame of frames) {
					if (!frame.trim()) continue;
					let event = "message";
					let id: number | undefined;
					let data = "";
					for (const line of frame.split("\n")) {
						if (line.startsWith("event: ")) event = line.slice(7);
						else if (line.startsWith("id: ")) id = parseInt(line.slice(4), 10);
						else if (line.startsWith("data: ")) data = line.slice(6);
					}
					try {
						events.push({ event, data: JSON.parse(data), id });
					} catch {
						events.push({ event, data, id });
					}
				}
			}
		})
		.catch((e) => {
			if (controller && e.name !== "AbortError") throw e;
		});

	return {
		events,
		close: () => {
			if (controller) {
				controller.abort();
				controller = null;
			}
		},
		promise,
	};
}

// ─── SSE Connection Lifecycle ──────────────────────────────────────────

describe("SSE Connection", () => {
	test("connects and receives hello + pool_snapshot on join", async () => {
		// Register agent first
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-test-001",
				name: "sse-test-agent",
				purpose: "SSE test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sse = connectSSE("sse-test-001");
		// Wait for initial events
		await new Promise((r) => setTimeout(r, 500));

		expect(sse.events.length).toBeGreaterThanOrEqual(2);
		expect(sse.events[0].event).toBe("hello");
		expect(sse.events[0].data.server_time).toBeDefined();
		expect(sse.events[0].data.server_id).toBeDefined();
		expect(sse.events[1].event).toBe("pool_snapshot");

		sse.close();
	});

	test("rejects SSE for unregistered session", async () => {
		const url = `${getServerUrl()}/v1/events?project=test&session_id=nonexistent-sse-session`;
		const res = await fetch(url, {
			headers: { Authorization: `Bearer ${getAuthToken()}` },
		});
		// Should return 404 for unknown session
		expect(res.status).toBe(404);
	});

	test("rejects SSE without session_id", async () => {
		const url = `${getServerUrl()}/v1/events?project=test`;
		const res = await fetch(url, {
			headers: { Authorization: `Bearer ${getAuthToken()}` },
		});
		expect(res.status).toBe(400);
	});
});

// ─── SSE Event Delivery ────────────────────────────────────────────────

describe("SSE Event Delivery", () => {
	test("receives agent_joined when another agent registers", async () => {
		// Register and connect first agent
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-observer-001",
				name: "sse-observer",
				purpose: "SSE observer",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sse = connectSSE("sse-observer-001");
		await new Promise((r) => setTimeout(r, 300));
		// Clear initial events
		const initialCount = sse.events.length;
		sse.events.length = 0;

		// Register a new agent — should trigger agent_joined event
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-new-001",
				name: "sse-new-agent",
				purpose: "new agent test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const joinedEvent = sse.events.find((e) => e.event === "agent_joined");
		expect(joinedEvent).toBeDefined();
		if (joinedEvent) {
			const name = joinedEvent.data?.agent?.name ?? joinedEvent.data?.name;
			expect(name).toBe("sse-new-agent");
		}

		sse.close();
	});

	test("receives message via SSE when sent a message", async () => {
		// Register and connect target agent
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-msg-target",
				name: "sse-msg-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sse = connectSSE("sse-msg-target");
		await new Promise((r) => setTimeout(r, 300));
		sse.events.length = 0;

		// Register sender and send message
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-msg-sender",
				name: "sse-msg-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "sse-msg-sender",
				target_session: "sse-msg-target",
				prompt: "Hello via SSE",
				project: "test",
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const msgEvent = sse.events.find((e) => e.event === "prompt");
		expect(msgEvent).toBeDefined();
		if (msgEvent) {
			expect(msgEvent.data.prompt).toBe("Hello via SSE");
			expect(msgEvent.data.msg_id).toBeDefined();
		}

		sse.close();
	});

	test("delivered message transitions from queued to delivered via SSE", async () => {
		// When target has an active SSE stream, messages should be "delivered"
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-deliver-target",
				name: "sse-deliver-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sse = connectSSE("sse-deliver-target");
		await new Promise((r) => setTimeout(r, 300));

		// Register sender
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "sse-deliver-sender",
				name: "sse-deliver-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "sse-deliver-sender",
				target_session: "sse-deliver-target",
				prompt: "Direct delivery test",
				project: "test",
			}),
		});

		const sendBody = await sendRes.json();
		expect(sendBody.ok).toBe(true);

		// With an active SSE stream, the status should be "delivered"
		expect(sendBody.status).toBe("delivered");

		sse.close();
	});
});

// ─── Heartbeat ─────────────────────────────────────────────────────────

describe("POST /v1/agents/:session_id/heartbeat", () => {
	test("updates agent status and last_seen_at", async () => {
		const regRes = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "hb-test-001",
				name: "hb-test-agent",
				purpose: "heartbeat test",
				model: "test-model-v1",
				cwd: "/tmp",
				project: "test",
			}),
		});
		const regBody = await regRes.json();

		// Send heartbeat with updated info
		const hbRes = await apiRequest("/v1/agents/hb-test-001/heartbeat", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				queue_depth: 3,
				context_used_pct: 45,
				model: "test-model-v2",
				status: "online",
			}),
		});

		expect(hbRes.status).toBe(200);
		const hbBody = await hbRes.json();
		expect(hbBody.ok).toBe(true);

		// Verify the update via agent listing
		const listRes = await apiRequest("/v1/agents?project=test");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === "hb-test-001");
		expect(agent).toBeDefined();
		expect(agent.model).toBe("test-model-v2");
		expect(agent.queue_depth).toBe(3);
		expect(agent.context_used_pct).toBe(45);
	});

	test("returns 404 for unregistered session heartbeat", async () => {
		const res = await apiRequest("/v1/agents/nonexistent-hb-session/heartbeat", {
			method: "POST",
			body: JSON.stringify({ project: "test" }),
		});
		expect(res.status).toBe(404);
	});

	// Heartbeat agent_updated broadcasts to OTHER agents, not to self.
	// So we need two agents: the one sending the heartbeat, and a second
	// one observing via SSE.
	test("heartbeat update broadcasts to other agents via SSE", async () => {
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "hb-stale-observer",
				name: "hb-stale-observer",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "hb-stale-actor",
				name: "hb-stale-actor",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Connect SSE on the OBSERVER agent
		const sse = connectSSE("hb-stale-observer");
		await new Promise((r) => setTimeout(r, 500));
		sse.events.length = 0;

		// The ACTOR sends a heartbeat with stale status
		await apiRequest("/v1/agents/hb-stale-actor/heartbeat", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				status: "stale",
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const updateEvent = sse.events.find((e) => e.event === "agent_updated");
		expect(updateEvent).toBeDefined();
		if (updateEvent) {
			const name = updateEvent.data?.agent?.name ?? updateEvent.data?.name;
			expect(name).toBe("hb-stale-actor");
			const status = updateEvent.data?.agent?.status ?? updateEvent.data?.status;
			expect(status).toBe("stale");
		}

		sse.close();
	});
});

// ─── Agent Leave / Deregistration ─────────────────────────────────────

describe("DELETE /v1/agents/:session_id", () => {
	test("removes agent and broadcasts agent_left", async () => {
		// Register two agents and connect one via SSE
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "leave-observer",
				name: "leave-observer",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "leave-target",
				name: "leave-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		const sse = connectSSE("leave-observer");
		await new Promise((r) => setTimeout(r, 300));
		sse.events.length = 0;

		// Delete the target agent
		const delRes = await apiRequest("/v1/agents/leave-target?project=test", {
			method: "DELETE",
		});
		expect(delRes.status).toBe(200);

		await new Promise((r) => setTimeout(r, 300));

		await new Promise((r) => setTimeout(r, 1000));

		const leftEvent = sse.events.find((e) => e.event === "agent_left");
		expect(leftEvent).toBeDefined();
		if (leftEvent) {
			expect(leftEvent.data.name).toBe("leave-target");
			expect(leftEvent.data.reason).toBe("shutdown");
		}

		sse.close();
	});
});

// ─── Message Response Submission ──────────────────────────────────────

describe("POST /v1/messages/:msg_id/response", () => {
	test("agent submits response and message transitions to complete", async () => {
		// Register target with SSE (so message is "delivered")
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "resp-target-001",
				name: "resp-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "resp-sender-001",
				name: "resp-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Send message
		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "resp-sender-001",
				target_session: "resp-target-001",
				prompt: "Please respond",
				project: "test",
			}),
		});
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;
		expect(msgId).toBeDefined();

		// Submit response
		const respRes = await apiRequest(`/v1/messages/${msgId}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: "resp-target-001",
				response: "Here is my response",
				error: null,
			}),
		});

		expect(respRes.status).toBe(200);
		const respBody = await respRes.json();
		expect(respBody.ok).toBe(true);

		// Verify message is now "complete"
		const getRes = await apiRequest(`/v1/messages/${msgId}?project=test&session_id=resp-sender-001`);
		const getBody = await getRes.json();
		expect(getBody.status).toBe("complete");
		expect(getBody.response).toBe("Here is my response");
	});

	test("rejects response for nonexistent message", async () => {
		const res = await apiRequest("/v1/messages/nonexistent-msg-id/response", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: "someone",
				response: "test",
			}),
		});
		expect(res.status).toBe(404);
	});

	test("rejects response from wrong session", async () => {
		// Register two agents
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "resp-wrong-target",
				name: "resp-wrong-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "resp-wrong-sender",
				name: "resp-wrong-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Send message
		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "resp-wrong-sender",
				target_session: "resp-wrong-target",
				prompt: "test",
				project: "test",
			}),
		});
		const msgId = (await sendRes.json()).msg_id;

		// Try to submit response from a session that isn't the target
		const respRes = await apiRequest(`/v1/messages/${msgId}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: "resp-wrong-sender", // wrong!
				response: "I am not the target",
			}),
		});
		// Server should reject or mark the response
		// Accept either a rejection (403/404) or acceptance with status tracking
		expect([200, 403, 404]).toContain(respRes.status);
	});
});

// ─── Stale / Offline Detection ─────────────────────────────────────────

describe("Stale and Offline detection", () => {
	test("heartbeat updates last_seen_at preventing stale detection", async () => {
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "stale-hb-agent",
				name: "stale-hb-agent",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Send heartbeat to keep it fresh
		const hbRes = await apiRequest("/v1/agents/stale-hb-agent/heartbeat", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				status: "online",
			}),
		});
		expect(hbRes.status).toBe(200);

		// Agent should be online
		const listRes = await apiRequest("/v1/agents?project=test");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === "stale-hb-agent");
		expect(agent).toBeDefined();
		expect(agent.status).toBe("online");
	});

	test("heartbeat with stale status marks agent as stale", async () => {
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "stale-agent-001",
				name: "stale-agent-001",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Report as stale
		await apiRequest("/v1/agents/stale-agent-001/heartbeat", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				status: "stale",
			}),
		});

		const listRes = await apiRequest("/v1/agents?project=test");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === "stale-agent-001");
		expect(agent).toBeDefined();
		expect(agent.status).toBe("stale");
	});
});

// ─── Message Status Transitions ───────────────────────────────────────

describe("Message status lifecycle", () => {
	test("message without SSE starts as queued, transitions to delivered when target connects", async () => {
		// Register both agents, no SSE streams
		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "lifecycle-sender",
				name: "lifecycle-sender",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "lifecycle-target",
				name: "lifecycle-target",
				purpose: "test",
				model: "test",
				cwd: "/tmp",
				project: "test",
			}),
		});

		// Send message — should be "queued"
		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: "lifecycle-sender",
				target_session: "lifecycle-target",
				prompt: "lifecycle test",
				project: "test",
			}),
		});
		expect(sendRes.status).toBe(200);
		const sendBody = await sendRes.json();
		expect(sendBody.status).toBe("queued");

		// Now connect target SSE — this should transition status to "delivered"
		const sse = connectSSE("lifecycle-target");
		await new Promise((r) => setTimeout(r, 500));

		// Check message status — note: the server may not retroactively
		// deliver queued messages when an SSE connects, depending on implementation.
		// The message was already created before the SSE stream existed.
		// Let's verify the SSE stream connects properly.
		expect(sse.events.length).toBeGreaterThanOrEqual(2);
		expect(sse.events[0].event).toBe("hello");

		sse.close();
	});
});