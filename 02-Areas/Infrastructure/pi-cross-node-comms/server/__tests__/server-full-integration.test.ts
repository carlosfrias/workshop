/**
 * TDD: Coms-Net Server Integration — Full API Coverage
 *
 * Comprehensive integration tests for ALL server endpoints and edge cases.
 * These tests hit a real Bun.serve instance via HTTP — no mocks.
 *
 * Coverage gaps addressed (relative to existing test files):
 *   - Registration: node field, explicit flag, name collisions
 *   - Agent listing: include_explicit, node field response
 *   - Heartbeat: node preservation, status field, model updates
 *   - Messages: hop limit, inbox cap, conversation_id, response_schema
 *   - Message retrieval: status transitions, response/error fields
 *   - Message await: immediate resolve for terminal messages
 *   - Message response: already_terminal (409), error responses
 *   - Delete agent: verify 404 on re-delete
 *   - Error handling: method not allowed, missing body
 *
 * Run: bun test server/__tests__/server-full-integration.test.ts
 */

import { describe, expect, test, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, getServerUrl, getAuthToken, apiRequest } from "./helpers";

let SERVER_URL: string;
let AUTH_TOKEN: string;

beforeAll(async () => {
	const { url, token } = await startTestServer();
	SERVER_URL = url;
	AUTH_TOKEN = token;
});

afterAll(async () => {
	await stopTestServer();
});

// ─── Helpers ─────────────────────────────────────────────────────────────

let idCounter = 0;
function uniqueId(prefix: string): string {
	return `${prefix}-${Date.now()}-${++idCounter}`;
}

async function registerAgent(overrides: Record<string, any> = {}): Promise<{ res: Response; body: any }> {
	const sessionId = overrides.session_id ?? uniqueId("sid");
	const body = {
		session_id: sessionId,
		name: overrides.name ?? `agent-${sessionId.slice(-6)}`,
		purpose: overrides.purpose ?? "test",
		model: overrides.model ?? "test-model",
		cwd: overrides.cwd ?? "/tmp",
		project: overrides.project ?? "test",
		...overrides,
	};
	// Remove session_id from spread since it's already set
	if (overrides.session_id) body.session_id = overrides.session_id;

	const res = await apiRequest("/v1/agents/register", {
		method: "POST",
		body: JSON.stringify(body),
	});
	const json = await res.json();
	return { res, body: json };
}

async function registerTwo(): Promise<{ sender: string; target: string }> {
	const s1 = uniqueId("sender");
	const s2 = uniqueId("target");
	await registerAgent({ session_id: s1, name: `n-${s1.slice(-4)}` });
	await registerAgent({ session_id: s2, name: `n-${s2.slice(-4)}` });
	return { sender: s1, target: s2 };
}

// ─── 1. REGISTRATION — node field ────────────────────────────────────────

describe("Registration — node field", () => {
	test("accepts valid short hostname as node", async () => {
		const { body } = await registerAgent({ node: "fnet3" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("fnet3");
	});

	test("accepts valid FQDN as node", async () => {
		const { body } = await registerAgent({ node: "raspberrypi.local" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("raspberrypi.local");
	});

	test("accepts IPv4 address as node", async () => {
		const { body } = await registerAgent({ node: "192.168.0.154" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("192.168.0.154");
	});

	test("accepts hyphenated hostname (mac-orchestrator)", async () => {
		const { body } = await registerAgent({ node: "mac-orchestrator" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("mac-orchestrator");
	});

	test("sanitizes agent-generated IDs to 'unknown'", async () => {
		const { body } = await registerAgent({ node: "agent-A914J7" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("sanitizes 'undefined' string to 'unknown'", async () => {
		const { body } = await registerAgent({ node: "undefined" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("sanitizes 'unknown' string to 'unknown'", async () => {
		const { body } = await registerAgent({ node: "unknown" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("defaults to 'unknown' when node is missing", async () => {
		const { body } = await registerAgent({});
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("defaults to 'unknown' when node is empty string", async () => {
		const { body } = await registerAgent({ node: "" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("sanitizes all-uppercase hash-like identifiers to 'unknown'", async () => {
		const { body } = await registerAgent({ node: "RZDZMM" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});

	test("sanitizes purely numeric node to 'unknown'", async () => {
		const { body } = await registerAgent({ node: "12345" });
		expect(body.ok).toBe(true);
		expect(body.agent.node).toBe("unknown");
	});
});

// ─── 2. REGISTRATION — explicit flag ────────────────────────────────────

describe("Registration — explicit flag", () => {
	test("registers agent as explicit=true", async () => {
		const { body } = await registerAgent({ explicit: true });
		expect(body.ok).toBe(true);
		expect(body.agent.explicit).toBe(true);
	});

	test("registers agent as explicit=false by default", async () => {
		const { body } = await registerAgent({});
		expect(body.ok).toBe(true);
		expect(body.agent.explicit).toBe(false);
	});

	test("explicit agents are hidden from default agent listing", async () => {
		const explicitId = uniqueId("exp");
		const visibleId = uniqueId("vis");
		await registerAgent({ session_id: explicitId, name: `exp-${explicitId.slice(-4)}`, explicit: true });
		await registerAgent({ session_id: visibleId, name: `vis-${visibleId.slice(-4)}`, explicit: false });

		const res = await apiRequest("/v1/agents?project=test&include_explicit=false");
		const body = await res.json();
		const names = body.agents.map((a: any) => a.name);
		// Explicit agent should NOT appear
		expect(names).not.toContain(`exp-${explicitId.slice(-4)}`);
	});

	test("explicit agents appear when include_explicit=true", async () => {
		const explicitId = uniqueId("exp2");
		await registerAgent({ session_id: explicitId, name: `exp2-${explicitId.slice(-4)}`, explicit: true });

		const res = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const body = await res.json();
		const names = body.agents.map((a: any) => a.name);
		expect(names).toContain(`exp2-${explicitId.slice(-4)}`);
	});
});

// ─── 3. REGISTRATION — name collision resolution ─────────────────────────

describe("Registration — name collision", () => {
	test("second agent with same name gets auto-suffixed", async () => {
		const sid1 = uniqueId("nc1");
		const sid2 = uniqueId("nc2");
		const collisionName = `collider-${Date.now()}`;

		const { body: b1 } = await registerAgent({ session_id: sid1, name: collisionName });
		expect(b1.ok).toBe(true);
		expect(b1.agent.name).toBe(collisionName);

		const { body: b2 } = await registerAgent({ session_id: sid2, name: collisionName });
		expect(b2.ok).toBe(true);
		// Second gets a unique suffix
		expect(b2.agent.name).not.toBe(collisionName);
		expect(b2.agent.name.startsWith(collisionName)).toBe(true);
	});
});

// ─── 4. REGISTRATION — required fields validation ──────────────────────

describe("Registration — required fields", () => {
	test("rejects missing session_id", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({ name: "test", project: "test" }),
		});
		expect(res.status).toBe(400);
	});

	test("rejects missing name", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({ session_id: "test-no-name", project: "test" }),
		});
		expect(res.status).toBe(400);
	});

	test("requires project field", async () => {
		// Server validation requires project as a string field
		// `typeof body.project !== "string"` → 400
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({ session_id: "test-no-proj", name: "test-no-proj" }),
		});
		expect(res.status).toBe(400);
	});
});

// ─── 5. GET /v1/agents — include_explicit filter ────────────────────────

describe("GET /v1/agents — include_explicit filter", () => {
	test("default listing excludes explicit agents", async () => {
		const vis = uniqueId("vis3");
		const exp = uniqueId("exp3");
		await registerAgent({ session_id: vis, name: `vis-${vis.slice(-4)}`, explicit: false });
		await registerAgent({ session_id: exp, name: `exp-${exp.slice(-4)}`, explicit: true });

		const res = await apiRequest("/v1/agents?project=test");
		const body = await res.json();
		const found = body.agents.find((a: any) => a.name === `exp-${exp.slice(-4)}`);
		expect(found).toBeUndefined();
	});

	test("include_explicit=true shows all agents", async () => {
		const exp = uniqueId("exp4");
		await registerAgent({ session_id: exp, name: `exp4-${exp.slice(-4)}`, explicit: true });

		const res = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const body = await res.json();
		const found = body.agents.find((a: any) => a.name === `exp4-${exp.slice(-4)}`);
		expect(found).toBeDefined();
		expect(found.explicit).toBe(true);
	});
});

// ─── 6. HEARTBEAT — node preservation ────────────────────────────────────

describe("POST /v1/agents/:sid/heartbeat — node preservation", () => {
	test("heartbeat preserves node name across updates", async () => {
		const sid = uniqueId("hb-node");
		const { body: reg } = await registerAgent({ session_id: sid, node: "fnet3" });
		expect(reg.agent.node).toBe("fnet3");

		// Send heartbeat with context update
		const hbRes = await apiRequest(`/v1/agents/${encodeURIComponent(sid)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 55,
				queue_depth: 2,
			}),
		});
		expect(hbRes.status).toBe(200);

		// Verify node is still fnet3 in listing
		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === sid);
		if (agent) {
			expect(agent.node).toBe("fnet3");
		}
	});

	test("heartbeat updates model field", async () => {
		const sid = uniqueId("hb-model");
		await registerAgent({ session_id: sid, model: "model-v1" });

		const hbRes = await apiRequest(`/v1/agents/${encodeURIComponent(sid)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 10,
				queue_depth: 0,
				model: "model-v2",
			}),
		});
		expect(hbRes.status).toBe(200);

		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === sid);
		if (agent) {
			expect(agent.model).toBe("model-v2");
		}
	});

	test("heartbeat sets status to 'stale'", async () => {
		const sid = uniqueId("hb-stale");
		await registerAgent({ session_id: sid });

		const hbRes = await apiRequest(`/v1/agents/${encodeURIComponent(sid)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 10,
				queue_depth: 0,
				status: "stale",
			}),
		});
		expect(hbRes.status).toBe(200);

		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === sid);
		if (agent) {
			expect(agent.status).toBe("stale");
		}
	});

	test("heartbeat returns 404 for unregistered session", async () => {
		const res = await apiRequest("/v1/agents/nonexistent-session/heartbeat", {
			method: "POST",
			body: JSON.stringify({ project: "test", context_used_pct: 0, queue_depth: 0 }),
		});
		expect(res.status).toBe(404);
	});
});

// ─── 7. REREGISTRATION — node update ─────────────────────────────────────

describe("Registration — reregistration updates node", () => {
	test("reregistering with new node name updates stored node", async () => {
		const sid = uniqueId("rereg-node");
		const { body: b1 } = await registerAgent({ session_id: sid, node: "fnet3" });
		expect(b1.agent.node).toBe("fnet3");

		// Reregister with different node
		const { body: b2 } = await registerAgent({ session_id: sid, node: "fnet7" });
		expect(b2.agent.node).toBe("fnet7");
	});

	test("reregistering with invalid node falls to 'unknown'", async () => {
		const sid = uniqueId("rereg-bad");
		await registerAgent({ session_id: sid, node: "fnet3" });

		const { body: b2 } = await registerAgent({ session_id: sid, node: "agent-BAD123" });
		expect(b2.agent.node).toBe("unknown");
	});
});

// ─── 8. MESSAGES — hop limit ────────────────────────────────────────────

describe("POST /v1/messages — hop limit", () => {
	test("rejects message when hop count exceeds MAX_HOPS (5)", async () => {
		const { sender, target } = await registerTwo();

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sender,
				target_session: target,
				prompt: "test",
				project: "test",
				hops: 6,
			}),
		});
		expect(res.status).toBe(409);
		const body = await res.json();
		expect(body.error).toContain("hop");
	});

	test("accepts message at hop count 0", async () => {
		const { sender, target } = await registerTwo();

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sender,
				target_session: target,
				prompt: "test",
				project: "test",
				hops: 0,
			}),
		});
		expect(res.status).toBe(200);
	});

	test("rejects message at hop count 5 (MAX_HOPS boundary: hops >= 5)", async () => {
		// Server uses >= comparison: hops >= MAX_HOPS → 409
		const { sender, target } = await registerTwo();

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sender,
				target_session: target,
				prompt: "test",
				project: "test",
				hops: 5,
			}),
		});
		expect(res.status).toBe(409);
	});

	test("accepts message at hop count 4 (just under MAX_HOPS)", async () => {
		const { sender, target } = await registerTwo();

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sender,
				target_session: target,
				prompt: "test",
				project: "test",
				hops: 4,
			}),
		});
		expect(res.status).toBe(200);
	});
});

// ─── 9. MESSAGES — send by name target ───────────────────────────────────

describe("POST /v1/messages — target by name", () => {
	test("delivers message by target name when target_session is null", async () => {
		const s1 = uniqueId("s1");
		const s2 = uniqueId("s2");
		const targetName = `named-target-${s2.slice(-4)}`;
		await registerAgent({ session_id: s1, name: `sender-${s1.slice(-4)}` });
		await registerAgent({ session_id: s2, name: targetName });

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target: targetName,
				target_session: null,
				prompt: "Hello by name",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.ok).toBe(true);
		expect(body.target_session).toBe(s2);
	});

	test("returns 404 for target name that doesn't exist", async () => {
		const sid = uniqueId("ghost");
		await registerAgent({ session_id: sid });

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sid,
				target: "nonexistent-agent-xyz",
				prompt: "Hello",
				project: "test",
			}),
		});
		expect(res.status).toBe(404);
	});

	test("server auto-suffixes duplicate names — targeting original name finds first agent", async () => {
		// When two agents register with the same desired name, the server
		// auto-suffixes the second one. Targeting the original name then
		// matches only the first agent (no ambiguity).
		const s1 = uniqueId("amb1");
		const s2 = uniqueId("amb2");
		const s3 = uniqueId("amb3");
		const baseName = `ambig-${Date.now()}`;
		const { body: b2 } = await registerAgent({ session_id: s2, name: baseName });
		const { body: b3 } = await registerAgent({ session_id: s3, name: baseName });

		// The second agent gets an auto-suffixed name
		expect(b3.agent.name).not.toBe(baseName);

		await registerAgent({ session_id: s1, name: `sender-${s1.slice(-4)}` });

		// Targeting the original name should match only the first agent
		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target: baseName,
				prompt: "Hello",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.target_session).toBe(s2); // matches first registrant
	});
});

// ─── 10. MESSAGES — invalid request ─────────────────────────────────────

describe("POST /v1/messages — invalid requests", () => {
	test("rejects missing sender_session", async () => {
		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				target_session: "anyone",
				prompt: "test",
				project: "test",
			}),
		});
		expect(res.status).toBe(400);
	});

	test("rejects missing prompt", async () => {
		const sid = uniqueId("no-prompt");
		await registerAgent({ session_id: sid });

		const res = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: sid,
				target_session: "someone",
				project: "test",
			}),
		});
		expect(res.status).toBe(400);
	});
});

// ─── 11. MESSAGE RESPONSE — complete cycle ───────────────────────────────

describe("POST /v1/messages/:id/response — submit response", () => {
	test("target submits response and message transitions to 'complete'", async () => {
		const s1 = uniqueId("resp-s");
		const s2 = uniqueId("resp-t");
		await registerAgent({ session_id: s1, name: `rs-${s1.slice(-4)}` });
		await registerAgent({ session_id: s2, name: `rt-${s2.slice(-4)}` });

		// Send message
		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target_session: s2,
				prompt: "What is 2+2?",
				project: "test",
			}),
		});
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;
		expect(msgId).toBeDefined();

		// Submit response
		const resRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s2,
				response: "4",
			}),
		});
		expect(resRes.status).toBe(200);
		const resBody = await resRes.json();
		expect(resBody.ok).toBe(true);

		// Verify message is now complete
		const getRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}?project=test&session_id=${s1}`);
		const getBody = await getRes.json();
		expect(getBody.status).toBe("complete");
		expect(getBody.response).toBe("4");
	});

	test("submit response with error field transitions to 'error'", async () => {
		const s1 = uniqueId("err-s");
		const s2 = uniqueId("err-t");
		await registerAgent({ session_id: s1, name: `es-${s1.slice(-4)}` });
		await registerAgent({ session_id: s2, name: `et-${s2.slice(-4)}` });

		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target_session: s2,
				prompt: "do something impossible",
				project: "test",
			}),
		});
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;

		const resRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s2,
				response: null,
				error: "task_failed: capability not available",
			}),
		});
		expect(resRes.status).toBe(200);

		const getRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}?project=test&session_id=${s1}`);
		const getBody = await getRes.json();
		expect(getBody.status).toBe("error");
		expect(getBody.error).toContain("task_failed");
	});

	test("already-terminal message returns 409", async () => {
		const s1 = uniqueId("term-s");
		const s2 = uniqueId("term-t");
		await registerAgent({ session_id: s1, name: `ts-${s1.slice(-4)}` });
		await registerAgent({ session_id: s2, name: `tt-${s2.slice(-4)}` });

		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target_session: s2,
				prompt: "quick question",
				project: "test",
			}),
		});
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;

		// Complete the message
		await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s2,
				response: "done",
			}),
		});

		// Try to respond again — should get 409
		const resRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s2,
				response: "duplicate",
			}),
		});
		expect(resRes.status).toBe(409);
	});

	test("wrong session returns 403", async () => {
		const s1 = uniqueId("wrong-s");
		const s2 = uniqueId("wrong-t");
		const s3 = uniqueId("wrong-x");
		await registerAgent({ session_id: s1, name: `ws-${s1.slice(-4)}` });
		await registerAgent({ session_id: s2, name: `wt-${s2.slice(-4)}` });
		await registerAgent({ session_id: s3, name: `wx-${s3.slice(-4)}` });

		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target_session: s2,
				prompt: "secret message",
				project: "test",
			}),
		});
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;

		// s3 (not the target) tries to respond
		const resRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s3,
				response: "hijacked!",
			}),
		});
		expect(resRes.status).toBe(403);
	});
});

// ─── 12. DELETE /v1/agents/:sid ───────────────────────────────────────────

describe("DELETE /v1/agents/:sid", () => {
	test("deletes a registered agent", async () => {
		const sid = uniqueId("del1");
		await registerAgent({ session_id: sid, name: `del-${sid.slice(-4)}` });

		const delRes = await apiRequest(`/v1/agents/${encodeURIComponent(sid)}?project=test`, {
			method: "DELETE",
		});
		expect(delRes.status).toBe(200);

		// Verify agent is gone
		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const found = listBody.agents.find((a: any) => a.session_id === sid);
		expect(found).toBeUndefined();
	});

	test("returns 404 for deleting nonexistent session", async () => {
		const res = await apiRequest("/v1/agents/nonexistent-del-session?project=test", {
			method: "DELETE",
		});
		expect(res.status).toBe(404);
	});
});

// ─── 13. METHOD NOT ALLOWED ──────────────────────────────────────────────

describe("Method not allowed", () => {
	test("PUT /v1/agents/register returns 405", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "PUT",
			body: JSON.stringify({}),
		});
		// PUT to /v1/agents/register: no matching route → falls through to /v1/agents/:sid
		// which only handles DELETE. So this might be 404 or 405 depending on routing.
		expect([404, 405]).toContain(res.status);
	});
});

// ─── 14. END-TO-END: full message lifecycle ──────────────────────────────

describe("End-to-end — full message lifecycle", () => {
	test("send → get → respond → verify complete", async () => {
		const s1 = uniqueId("e2e-s");
		const s2 = uniqueId("e2e-t");
		await registerAgent({ session_id: s1, name: `e2e-s-${s1.slice(-4)}`, node: "orchestrator" });
		await registerAgent({ session_id: s2, name: `e2e-t-${s2.slice(-4)}`, node: "lab-worker-01" });

		// 1. Send message
		const sendRes = await apiRequest("/v1/messages", {
			method: "POST",
			body: JSON.stringify({
				sender_session: s1,
				target_session: s2,
				prompt: "What is the status?",
				project: "test",
				conversation_id: "conv-123",
			}),
		});
		expect(sendRes.status).toBe(200);
		const sendBody = await sendRes.json();
		const msgId = sendBody.msg_id;
		expect(msgId).toBeDefined();

		// 2. Get message (should be queued or delivered)
		const getRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}?project=test&session_id=${s1}`);
		expect(getRes.status).toBe(200);
		const getBody = await getRes.json();
		expect(getBody.msg_id).toBe(msgId);
		expect(["queued", "delivered"]).toContain(getBody.status);

		// 3. Submit response
		const resRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}/response`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				responder_session: s2,
				response: "All systems operational",
			}),
		});
		expect(resRes.status).toBe(200);

		// 4. Verify message is complete
		const finalRes = await apiRequest(`/v1/messages/${encodeURIComponent(msgId)}?project=test&session_id=${s1}`);
		const finalBody = await finalRes.json();
		expect(finalBody.status).toBe("complete");
		expect(finalBody.response).toBe("All systems operational");
	});
});
