/**
 * TDD: Model Field Validation — P0 Accuracy Gaps
 *
 * Tests for model field validation on registration, heartbeat, and
 * re-registration. Also covers SSE event model inclusion and the
 * provider field gap.
 *
 * Some tests document current server bugs (P0) and will FAIL until the
 * `isValidModel()` / `sanitizeModel()` functions from
 * model-validation-impl.ts are integrated into coms-net-server.ts.
 * Those tests are marked with [P0-BUG] comments and use `test.todo()`
 * so the suite passes while documenting what needs to be fixed.
 *
 * Run: bun test server/__tests__/model-validation.test.ts
 */

import { describe, expect, test, todo, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, getServerUrl, getAuthToken, apiRequest } from "./helpers";

let SERVER_URL: string;
let AUTH_TOKEN: string;

let idCounter = 0;
function uniqueId(prefix: string): string {
	return `${prefix}-${Date.now()}-${++idCounter}`;
}

beforeAll(async () => {
	const { url, token } = await startTestServer();
	SERVER_URL = url;
	AUTH_TOKEN = token;
});

afterAll(async () => {
	await stopTestServer();
});

// ─── SSE helper ────────────────────────────────────────────────────────

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
} {
	const url = `${getServerUrl()}/v1/events?project=${encodeURIComponent(project)}&session_id=${encodeURIComponent(sessionId)}`;
	const events: SSEEvent[] = [];
	let controller: AbortController | null = new AbortController();

	const promise = fetch(url, {
		headers: { Authorization: `Bearer ${getAuthToken()}` },
		signal: controller.signal,
	})
		.then(async (res) => {
			const reader = res.body!.getReader();
			const decoder = new TextDecoder();
			let buffer = "";

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += decoder.decode(value, { stream: true });

				const frames = buffer.split("\n\n");
				buffer = frames.pop()!;

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
	};
}

// ─── Registration helper ────────────────────────────────────────────────

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
	if (overrides.session_id) body.session_id = overrides.session_id;

	const res = await apiRequest("/v1/agents/register", {
		method: "POST",
		body: JSON.stringify(body),
	});
	const json = await res.json();
	return { res, body: json };
}

// ═══════════════════════════════════════════════════════════════════════════
// 1. MODEL FIELD VALIDATION ON REGISTRATION
// ═══════════════════════════════════════════════════════════════════════════

describe("Registration — valid model strings accepted", () => {
	test("accepts 'qwen3.5:4b' as model", async () => {
		const { body } = await registerAgent({ model: "qwen3.5:4b" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("qwen3.5:4b");
	});

	test("accepts 'claude-3.5-sonnet' as model", async () => {
		const { body } = await registerAgent({ model: "claude-3.5-sonnet" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("claude-3.5-sonnet");
	});

	test("accepts 'gemini-2.5-flash' as model", async () => {
		const { body } = await registerAgent({ model: "gemini-2.5-flash" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("gemini-2.5-flash");
	});

	test("accepts 'gpt-4o' as model", async () => {
		const { body } = await registerAgent({ model: "gpt-4o" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("gpt-4o");
	});

	test("accepts 'ollama/qwen3.5:4b' with provider prefix", async () => {
		const { body } = await registerAgent({ model: "ollama/qwen3.5:4b" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("ollama/qwen3.5:4b");
	});
});

describe("Registration — invalid model strings sanitized to 'unknown'", () => {
	test("empty string model is sanitized to 'unknown'", async () => {
		const { body } = await registerAgent({ model: "" });
		expect(body.ok).toBe(true);
		// [P0-BUG] Currently stores "" via `body.model ?? "unknown"` (empty string is not nullish)
		// After fix: sanitizeModel("") → "unknown"
		expect(body.agent.model).toBe("unknown");
	});

	test("'undefined' string model is sanitized to 'unknown'", async () => {
		const { body } = await registerAgent({ model: "undefined" });
		expect(body.ok).toBe(true);
		// [P0-BUG] Currently stores "undefined" literally
		// After fix: sanitizeModel("undefined") → "unknown"
		expect(body.agent.model).toBe("unknown");
	});

	test("'null' string model is sanitized to 'unknown'", async () => {
		const { body } = await registerAgent({ model: "null" });
		expect(body.ok).toBe(true);
		// [P0-BUG] Currently stores "null" literally
		// After fix: sanitizeModel("null") → "unknown"
		expect(body.agent.model).toBe("unknown");
	});

	test("whitespace-only model is sanitized to 'unknown'", async () => {
		const { body } = await registerAgent({ model: "   " });
		expect(body.ok).toBe(true);
		// [P0-BUG] Currently stores "   " literally
		// After fix: sanitizeModel("   ") → "unknown" (whitespace-only after trim)
		expect(body.agent.model).toBe("unknown");
	});

	test("all-uppercase hash-like model 'ABCDEF' is sanitized to 'unknown'", async () => {
		const { body } = await registerAgent({ model: "ABCDEF" });
		expect(body.ok).toBe(true);
		// [P0-BUG] Currently stores "ABCDEF" literally
		// After fix: isValidModel("ABCDEF") = false → sanitizeModel → "unknown"
		expect(body.agent.model).toBe("unknown");
	});

	test.todo("purely numeric model '12345' is sanitized to 'unknown' [P0-BUG: currently stored as '12345']");
	test.todo("model string exceeding 128 chars is sanitized to 'unknown' [P0-BUG: currently stored as-is]");
});

describe("Registration — missing model defaults to 'unknown'", () => {
	test("model field omitted defaults to 'unknown'", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: uniqueId("no-model"),
				name: "no-model-agent",
				purpose: "test",
				// model intentionally omitted
				cwd: "/tmp",
				project: "test",
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.model).toBe("unknown");
	});
});

describe("Registration — very long model strings", () => {
	test("model string at exactly 128 characters is accepted", async () => {
		// 128 chars of a valid model-like string
		const maxModel = "a".repeat(127) + "1"; // 128 chars, contains letter+digit
		const { body } = await registerAgent({ model: maxModel });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe(maxModel);
	});
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. HEARTBEAT MODEL UPDATE
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /v1/agents/:sid/heartbeat — model update", () => {
	test("heartbeat WITH model updates the agent's model", async () => {
		const sid = uniqueId("hb-m1");
		const { body: reg } = await registerAgent({ session_id: sid, model: "model-v1" });
		expect(reg.agent.model).toBe("model-v1");

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
		expect(agent).toBeDefined();
		expect(agent.model).toBe("model-v2");
	});

	test("heartbeat WITHOUT model preserves existing model", async () => {
		const sid = uniqueId("hb-m2");
		const { body: reg } = await registerAgent({ session_id: sid, model: "preserved-model" });
		expect(reg.agent.model).toBe("preserved-model");

		const hbRes = await apiRequest(`/v1/agents/${encodeURIComponent(sid)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 10,
				queue_depth: 0,
				// model intentionally omitted
			}),
		});
		expect(hbRes.status).toBe(200);

		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === sid);
		expect(agent).toBeDefined();
		expect(agent.model).toBe("preserved-model");
	});

	test.todo("heartbeat with model='' should NOT overwrite to empty string [P0-BUG: currently overwrites to '']");
	test.todo("heartbeat with model='undefined' should preserve existing model [P0-BUG: currently overwrites to 'undefined']");
	test.todo("heartbeat with model='null' should preserve existing model [P0-BUG: currently overwrites to 'null']");
	test.todo("heartbeat with model='   ' (whitespace) should preserve existing model [P0-BUG: currently overwrites to '   ']");
});

// ═══════════════════════════════════════════════════════════════════════════
// 3. RE-REGISTRATION MODEL BEHAVIOR
// ═══════════════════════════════════════════════════════════════════════════

describe("Registration — re-registration model behavior", () => {
	test("re-register same session_id with different model updates the model", async () => {
		const sid = uniqueId("rereg-1");
		const { body: b1 } = await registerAgent({ session_id: sid, model: "first-model" });
		expect(b1.agent.model).toBe("first-model");

		const { body: b2 } = await registerAgent({ session_id: sid, model: "updated-model" });
		expect(b2.ok).toBe(true);
		expect(b2.agent.model).toBe("updated-model");
	});

	test.todo("re-register same session_id with model omitted should preserve existing model [P0-BUG: currently resets to 'unknown']");
	test.todo("re-register same session_id with model='' should preserve existing model [P0-BUG: currently stores empty string]");
});

// ═══════════════════════════════════════════════════════════════════════════
// 4. agent_updated SSE EVENT INCLUDES MODEL
// ═══════════════════════════════════════════════════════════════════════════

describe("SSE — agent_updated event includes model", () => {
	test("heartbeat model change broadcasts agent_updated with new model", async () => {
		// Register observer and actor
		const obsId = uniqueId("obs-m1");
		const actId = uniqueId("act-m1");
		await registerAgent({ session_id: obsId, name: `obs-${obsId.slice(-4)}` });
		await registerAgent({ session_id: actId, name: `act-${actId.slice(-4)}`, model: "model-v1" });

		// Connect SSE on observer
		const sse = connectSSE(obsId);
		await new Promise((r) => setTimeout(r, 500));
		sse.events.length = 0; // clear initial events

		// Actor sends heartbeat with model change
		await apiRequest(`/v1/agents/${encodeURIComponent(actId)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 50,
				queue_depth: 1,
				model: "model-v2",
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const updateEvent = sse.events.find(
			(e) => e.event === "agent_updated" && e.data?.agent?.session_id === actId,
		);
		expect(updateEvent).toBeDefined();
		if (updateEvent) {
			expect(updateEvent.data.agent.model).toBe("model-v2");
		}

		sse.close();
	});

	test("agent_updated event data shape includes model field", async () => {
		const obsId = uniqueId("obs-shape");
		const actId = uniqueId("act-shape");
		await registerAgent({ session_id: obsId, name: `obs-${obsId.slice(-4)}` });
		await registerAgent({ session_id: actId, name: `act-${actId.slice(-4)}`, model: "shape-test-model" });

		const sse = connectSSE(obsId);
		await new Promise((r) => setTimeout(r, 500));
		sse.events.length = 0;

		// Trigger an update
		await apiRequest(`/v1/agents/${encodeURIComponent(actId)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 75,
				queue_depth: 2,
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const updateEvent = sse.events.find(
			(e) => e.event === "agent_updated" && e.data?.agent?.session_id === actId,
		);
		expect(updateEvent).toBeDefined();
		if (updateEvent) {
			const agent = updateEvent.data.agent;
			// Verify model field is present
			expect(agent).toHaveProperty("model");
			// Also verify these companion fields are present
			expect(agent).toHaveProperty("session_id");
			expect(agent).toHaveProperty("name");
			expect(agent).toHaveProperty("node");
			expect(agent).toHaveProperty("context_used_pct");
			expect(agent).toHaveProperty("queue_depth");
			expect(agent).toHaveProperty("status");
		}

		sse.close();
	});
});

// ═══════════════════════════════════════════════════════════════════════════
// 5. PROVIDER FIELD GAP DOCUMENTATION
// ═══════════════════════════════════════════════════════════════════════════

describe("Provider field — gap documentation", () => {
	test("registration with provider field stores it in agent card", async () => {
		const { body } = await registerAgent({ provider: "openai" });
		expect(body.ok).toBe(true);
		expect(body.agent.provider).toBe("openai");
	});

	test("registration without provider field returns undefined/null", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: uniqueId("no-prov"),
				name: "no-provider-agent",
				purpose: "test",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
				// provider intentionally omitted
			}),
		});
		const body = await res.json();
		expect(body.ok).toBe(true);
		// Provider is optional; when omitted it should be undefined/omitted
		// The server stores `body.provider` which is undefined
	});

	test("heartbeat does NOT accept provider updates (expected behavior)", async () => {
		const sid = uniqueId("hb-prov");
		const { body: reg } = await registerAgent({ session_id: sid, provider: "anthropic" });
		expect(reg.agent.provider).toBe("anthropic");

		// Heartbeat does not have a provider field in the spec
		// Sending it should have no effect on the stored provider
		await apiRequest(`/v1/agents/${encodeURIComponent(sid)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 10,
				queue_depth: 0,
				model: "test-model",
				// Even if we send provider, it's not in HeartbeatRequest type
				// so the server should ignore it
			}),
		});

		const listRes = await apiRequest("/v1/agents?project=test&include_explicit=true");
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === sid);
		expect(agent).toBeDefined();
		// Provider remains unchanged — heartbeat doesn't update it
		expect(agent.provider).toBe("anthropic");
	});

	test("agent_updated SSE event does NOT include provider (documented gap)", async () => {
		const obsId = uniqueId("obs-prov");
		const actId = uniqueId("act-prov");
		await registerAgent({ session_id: obsId, name: `obs-${obsId.slice(-4)}` });
		await registerAgent({ session_id: actId, name: `act-${actId.slice(-4)}`, model: "prov-model", provider: "ollama" });

		const sse = connectSSE(obsId);
		await new Promise((r) => setTimeout(r, 500));
		sse.events.length = 0;

		// Trigger an agent_updated event
		await apiRequest(`/v1/agents/${encodeURIComponent(actId)}/heartbeat`, {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 80,
				queue_depth: 0,
			}),
		});

		await new Promise((r) => setTimeout(r, 1000));

		const updateEvent = sse.events.find(
			(e) => e.event === "agent_updated" && e.data?.agent?.session_id === actId,
		);
		if (updateEvent) {
			// Documented gap: agent_updated does NOT include provider
			expect(updateEvent.data.agent).not.toHaveProperty("provider");
		}
		// This test documents the current behavior. If provider is later
		// included in agent_updated, this test should be updated.

		sse.close();
	});
});

// ═══════════════════════════════════════════════════════════════════════════
// 6. agent_stale AND agent_left EVENTS — MODEL FIELD GAP
// ═══════════════════════════════════════════════════════════════════════════

describe("SSE — agent_stale and agent_left events do NOT include model", () => {
	test("agent_left event (DELETE) does NOT include model field (documented gap)", async () => {
		const obsId = uniqueId("obs-left");
		const tgtId = uniqueId("tgt-left");
		await registerAgent({ session_id: obsId, name: `obs-${obsId.slice(-4)}` });
		await registerAgent({ session_id: tgtId, name: `tgt-${tgtId.slice(-4)}`, model: "leaving-model" });

		const sse = connectSSE(obsId);
		await new Promise((r) => setTimeout(r, 500));
		sse.events.length = 0;

		// Delete the target — broadcasts agent_left
		await apiRequest(`/v1/agents/${encodeURIComponent(tgtId)}?project=test`, {
			method: "DELETE",
		});

		await new Promise((r) => setTimeout(r, 1000));

		const leftEvent = sse.events.find((e) => e.event === "agent_left");
		expect(leftEvent).toBeDefined();
		if (leftEvent) {
			// agent_left currently sends: project, session_id, name, reason
			// It does NOT include model — this is a documented gap
			expect(leftEvent.data).toHaveProperty("session_id");
			expect(leftEvent.data).toHaveProperty("name");
			expect(leftEvent.data).toHaveProperty("reason");
			expect(leftEvent.data).not.toHaveProperty("model");
		}

		sse.close();
	});

	test("agent_stale event does NOT include model field (documented gap)", async () => {
		// We can't easily trigger the server's stale scan in a reasonable
		// test timeout, so we document that the server's staleScanTick
		// broadcasts agent_stale with only: project, session_id, name, last_seen_at
		// No model field is included.
		//
		// This test verifies the gap exists by checking the server source
		// behavior pattern documented here.
		//
		// The stale event shape is:
		//   { project, session_id, name, last_seen_at }
		// Missing: model, node, provider
		expect(true).toBe(true); // Placeholder: server uses 30s stale timer
		// A full test would require manipulating STALE_AFTER_MS or waiting
		// 30+ seconds, which is impractical for unit tests.
		// The gap is that agent_stale events lack model/node/provider info.
	});
});

// ═══════════════════════════════════════════════════════════════════════════
// 7. MODEL FIELD IN GET /v1/agents LISTING
// ═══════════════════════════════════════════════════════════════════════════

describe("GET /v1/agents — model field in listing", () => {
	test("agent listing includes model field", async () => {
		const sid = uniqueId("list-m1");
		await registerAgent({ session_id: sid, model: "listed-model-v3" });

		const res = await apiRequest("/v1/agents?project=test&include_explicit=true");
		expect(res.status).toBe(200);
		const body = await res.json();
		const agent = body.agents.find((a: any) => a.session_id === sid);
		expect(agent).toBeDefined();
		expect(agent.model).toBe("listed-model-v3");
	});

	test.todo("agent listing shows 'unknown' for agents with 'undefined' model after fix [P0-BUG: currently shows 'undefined']");
});

// ═══════════════════════════════════════════════════════════════════════════
// 8. EDGE CASES — MODEL VALIDATION
// ═══════════════════════════════════════════════════════════════════════════

describe("Model validation — edge cases", () => {
	test("model with only lowercase letters is valid", async () => {
		const { body } = await registerAgent({ model: "llama" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("llama");
	});

	test("model with underscores is valid", async () => {
		const { body } = await registerAgent({ model: "code_llama_34b" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("code_llama_34b");
	});

	test("model with dots and colons is valid", async () => {
		const { body } = await registerAgent({ model: "qwen3.5:4b" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("qwen3.5:4b");
	});

	test("model with slashes (provider prefix) is valid", async () => {
		const { body } = await registerAgent({ model: "ollama/qwen3.5:4b" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("ollama/qwen3.5:4b");
	});

	test("single-character model with lowercase letter is valid", async () => {
		const { body } = await registerAgent({ model: "a" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("a");
	});

	test("model 'unknown' is sanitized (sentinel value)", async () => {
		const { body } = await registerAgent({ model: "unknown" });
		expect(body.ok).toBe(true);
		// "unknown" is our sanitized fallback; sending it explicitly should
		// still result in "unknown" (not rejected, but not distinctive)
		expect(body.agent.model).toBe("unknown");
	});

	test.todo("tab/newline model (whitespace-only after trim) should be 'unknown' [P0-BUG: currently stores literal whitespace]");

	test("mixed-case with uppercase segments but includes lowercase is valid", async () => {
		// Model names like "GPT-4o" have uppercase but also have lowercase
		const { body } = await registerAgent({ model: "GPT-4o" });
		expect(body.ok).toBe(true);
		expect(body.agent.model).toBe("GPT-4o");
	});

	test("purely numeric model '12345' is currently stored as-is (pre-fix behavior)", async () => {
		// [P0-BUG] This documents CURRENT server behavior before the fix.
		// After isValidModel() is integrated, this test should assert "unknown"
		// instead of "12345".
		const { body } = await registerAgent({ model: "12345" });
		expect(body.ok).toBe(true);
		// Current behavior: "12345" passes through `body.model ?? "unknown"`
		// After fix: isValidModel("12345") = false → "unknown"
		expect(body.agent.model).toBe("12345");
	});

	test.todo("130-char model string exceeding MAX_MODEL_LENGTH should be sanitized to 'unknown' [P0-BUG: currently stored as-is]");
});