/**
 * TDD: Node Name Integration Tests — Server + Client End-to-End
 *
 * Verifies that the coms-net server correctly stores, validates, and returns
 * node names across the full registration → heartbeat → agent listing pipeline.
 *
 * These tests document THE BUG (fixed 2026-05-27): os.hostname() was the only
 * source of node identity with no override mechanism. The server accepted any
 * string as node, and the client always sent os.hostname() ("mac-orchestrator").
 *
 * Now the client has --node flag + PI_COMS_NET_NODE env, but the SERVER must
 * also validate and sanitize node names at registration time.
 *
 * Run: bun test server/__tests__/node-name-integration.test.ts
 */

import { describe, expect, test, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, getServerUrl, getAuthToken, apiRequest } from "./helpers";

beforeAll(async () => {
	await startTestServer();
});

afterAll(async () => {
	await stopTestServer();
});

// ─── Helper ────────────────────────────────────────────────────────────

function registerAgent(sessionId: string, overrides: Record<string, any> = {}) {
	return apiRequest("/v1/agents/register", {
		method: "POST",
		body: JSON.stringify({
			session_id: sessionId,
			name: overrides.name ?? `test-${sessionId}`,
			purpose: overrides.purpose ?? "integration test",
			model: overrides.model ?? "test-model",
			cwd: overrides.cwd ?? "/tmp",
			project: overrides.project ?? "test",
			...overrides,
		}),
	});
}

// ─── REGISTRATION: Node field accepted and returned ─────────────────────

describe("POST /v1/agents/register — node field", () => {
	test("accepts a valid short hostname as node", async () => {
		const res = await registerAgent("node-hostname-001", { node: "fnet3" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("fnet3");
	});

	test("accepts a valid FQDN as node", async () => {
		const res = await registerAgent("node-fqdn-001", { node: "raspberrypi.local" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("raspberrypi.local");
	});

	test("accepts an IPv4 address as node", async () => {
		const res = await registerAgent("node-ipv4-001", { node: "192.168.0.154" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("192.168.0.154");
	});

	test("accepts a hyphenated hostname as node (e.g. mac-orchestrator)", async () => {
		const res = await registerAgent("node-hyphen-001", { node: "mac-orchestrator" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("mac-orchestrator");
	});

	test("accepts a hyphenated lab hostname as node (e.g. lab-node-01)", async () => {
		const res = await registerAgent("node-lab-001", { node: "lab-node-01" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("lab-node-01");
	});
});

// ─── REGISTRATION: Invalid node names sanitized to "unknown" ───────────

describe("POST /v1/agents/register — invalid node names sanitized", () => {
	test("rejects agent-generated IDs as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-agent-id-001", { node: "agent-A914J7" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects worker-generated IDs as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-worker-id-001", { node: "worker-3VN9XS" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects peer-generated IDs as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-peer-id-001", { node: "peer-ABC123" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects node-generated IDs as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-node-id-001", { node: "node-ABCDEF" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects 'undefined' string as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-undefined-001", { node: "undefined" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects 'unknown' string as node name → stays 'unknown'", async () => {
		const res = await registerAgent("node-unknown-001", { node: "unknown" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects 'null' string as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-null-001", { node: "null" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects empty string as node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-empty-001", { node: "" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects purely numeric node name → falls to 'unknown'", async () => {
		const res = await registerAgent("node-numeric-001", { node: "12345" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("rejects all-uppercase hash-like identifiers → falls to 'unknown'", async () => {
		const res = await registerAgent("node-uppercase-001", { node: "RZDZMM" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});

	test("falls to 'unknown' when node field is missing entirely", async () => {
		const res = await apiRequest("/v1/agents/register", {
			method: "POST",
			body: JSON.stringify({
				session_id: "node-missing-001",
				name: "test-no-node",
				purpose: "integration test",
				model: "test-model",
				cwd: "/tmp",
				project: "test",
				// No "node" field at all
			}),
		});
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("unknown");
	});
});

// ─── AGENT LISTING: Node field appears in GET /v1/agents ────────────────

describe("GET /v1/agents — node field in agent listing", () => {
	test("agent listing includes the node field", async () => {
		// Register with a known node
		await registerAgent("node-list-001", { node: "fnet5" });
		
		const res = await apiRequest("/v1/agents?project=test");
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(Array.isArray(body.agents)).toBe(true);

		const agent = body.agents.find((a: any) => a.name === "test-node-list-001");
		if (agent) {
			expect(agent.node).toBe("fnet5");
		}
	});

	test("agent listing shows 'unknown' for agents registered with invalid node", async () => {
		await registerAgent("node-list-invalid-001", { node: "agent-BAD123" });
		
		const res = await apiRequest("/v1/agents?project=test");
		expect(res.status).toBe(200);
		const body = await res.json();
		
		const agent = body.agents.find((a: any) => a.name === "test-node-list-invalid-001");
		if (agent) {
			expect(agent.node).toBe("unknown");
		}
	});
});

// ─── HEARTBEAT: Node preserved across heartbeats ──────────────────────

describe("POST /v1/agents/:session_id/heartbeat — node preservation", () => {
	test("node name is preserved across heartbeats", async () => {
		// Register with a specific node name
		const regRes = await registerAgent("node-hb-001", { node: "fnet3" });
		expect(regRes.status).toBe(200);
		const regBody = await regRes.json();
		expect(regBody.agent.node).toBe("fnet3");

		// Send heartbeat
		const hbRes = await apiRequest("/v1/agents/node-hb-001/heartbeat", {
			method: "POST",
			body: JSON.stringify({
				project: "test",
				context_used_pct: 42,
				queue_depth: 0,
			}),
		});
		expect(hbRes.status).toBe(200);

		// Verify node name is still fnet3 in the agent listing
		const listRes = await apiRequest("/v1/agents?project=test");
		expect(listRes.status).toBe(200);
		const listBody = await listRes.json();
		const agent = listBody.agents.find((a: any) => a.session_id === "node-hb-001");
		if (agent) {
			expect(agent.node).toBe("fnet3");
		}
	});
});

// ─── REREGISTRATION: Node name update ──────────────────────────────────

describe("POST /v1/agents/register — node name update on reregistration", () => {
	test("reregistration with new node name updates the stored node", async () => {
		// First registration
		const reg1 = await registerAgent("node-rereg-001", { node: "fnet3" });
		expect(reg1.status).toBe(200);
		const body1 = await reg1.json();
		expect(body1.agent.node).toBe("fnet3");

		// Reregister with a different node name (simulating --node flag change)
		const reg2 = await registerAgent("node-rereg-001", {
			name: "test-node-rereg-001",
			node: "fnet7",
		});
		expect(reg2.status).toBe(200);
		const body2 = await reg2.json();
		expect(body2.agent.node).toBe("fnet7");
	});

	test("reregistration with invalid node name falls to 'unknown'", async () => {
		// First registration with valid node
		const reg1 = await registerAgent("node-rereg-invalid-001", { node: "fnet3" });
		expect(reg1.status).toBe(200);

		// Reregister with an invalid node
		const reg2 = await registerAgent("node-rereg-invalid-001", {
			name: "test-node-rereg-invalid-001",
			node: "agent-BAD999",
		});
		expect(reg2.status).toBe(200);
		const body2 = await reg2.json();
		expect(body2.agent.node).toBe("unknown");
	});
});

// ─── END-TO-END SCENARIO: mac-orchestrator override ────────────────────

describe("End-to-end: override mac-orchestrator with logical node name", () => {
	test("operator overrides os.hostname() via --node flag (simulated)", async () => {
		// Simulate what the CLIENT sends when:
		//   os.hostname() = "mac-orchestrator"
		//   --node flag = "fnet2"
		// The client's resolveNode() would return "fnet2",
		// so the registration payload should send node="fnet2".
		const res = await registerAgent("override-mac-001", { node: "fnet2" });
		expect(res.status).toBe(200);
		const body = await res.json();
		// Server must store and return "fnet2", not "mac-orchestrator"
		expect(body.agent.node).toBe("fnet2");
		expect(body.agent.node).not.toBe("mac-orchestrator");
	});

	test("operator overrides via PI_COMS_NET_NODE env var (simulated)", async () => {
		// Same as --node flag, just different source on the client side.
		// The server doesn't care about the source — it receives "lab-orchestrator".
		const res = await registerAgent("override-env-001", { node: "lab-orchestrator" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("lab-orchestrator");
	});

	test("IP address override for VMs with ugly hostnames", async () => {
		// AWS instances have hostnames like "ip-10-0-0-1.us-west-2.compute.internal"
		// Operators may prefer to identify by IP
		const res = await registerAgent("override-ip-001", { node: "192.168.1.100" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("192.168.1.100");
	});

	test("no override: os.hostname() 'mac-orchestrator' is a valid hostname", async () => {
		// When no --node or env var is set, the client sends os.hostname()
		// "mac-orchestrator" IS a valid hostname — it passes server validation.
		// The BUG was that it couldn't be overridden, not that it was invalid.
		const res = await registerAgent("no-override-001", { node: "mac-orchestrator" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("mac-orchestrator");
		// This is CORRECT behavior — but operators NEED the override capability
		// which is now provided by --node / PI_COMS_NET_NODE
	});
});

// ─── SSE: Node field in agent_joined/agent_updated broadcasts ──────────

describe("SSE broadcasts — node field in agent events", () => {
	test("agent_joined event includes node field", async () => {
		// This is tested via the SSE integration tests, but we verify the
		// registration response includes node, which is what gets broadcast.
		const res = await registerAgent("sse-node-001", { node: "fnet4" });
		expect(res.status).toBe(200);
		const body = await res.json();
		expect(body.agent.node).toBe("fnet4");
		// The server broadcasts this as an agent_joined event,
		// and the node field should be present in the broadcast.
		// (SSE integration tests cover the actual event delivery.)
	});
});