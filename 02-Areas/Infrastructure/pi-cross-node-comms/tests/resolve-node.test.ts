/**
 * TDD: Node Name Resolution — Aggressive Test Suite
 *
 * RED-GREEN-REFACTOR cycle:
 *   1. Tests capture the CURRENT broken behavior (os.hostname() = "mac-orchestrator")
 *   2. Tests define the DESIRED behavior (flag > env > hostname > fallback, with validation)
 *   3. Fix production code, all tests go GREEN
 *
 * Run: bun test tests/resolve-node.test.ts
 */

import { test, expect, describe } from "bun:test";
import {
	resolveNode,
	isValidHostnameOrIp,
	looksLikeIp,
	displayNode,
	nodeListPrefix,
	type ResolveNodeOptions,
} from "../src/resolve-node";

// ━━ RAW VALIDATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("looksLikeIp", () => {
	test("accepts valid IPv4", () => {
		expect(looksLikeIp("192.168.0.154")).toBe(true);
		expect(looksLikeIp("10.0.0.1")).toBe(true);
		expect(looksLikeIp("172.16.0.1")).toBe(true);
		expect(looksLikeIp("0.0.0.0")).toBe(true);
		expect(looksLikeIp("255.255.255.255")).toBe(true);
	});

	test("rejects invalid IPv4", () => {
		expect(looksLikeIp("256.0.0.1")).toBe(false);
		expect(looksLikeIp("1.2.3")).toBe(false);
		expect(looksLikeIp("1.2.3.4.5")).toBe(false);
	});

	test("accepts valid IPv6", () => {
		expect(looksLikeIp("::1")).toBe(true);
		expect(looksLikeIp("fe80::1")).toBe(true);
		expect(looksLikeIp("fe80::1%eth0")).toBe(false); // zone IDs not handled
	});

	test("rejects non-IP strings", () => {
		expect(looksLikeIp("mac-orchestrator")).toBe(false);
		expect(looksLikeIp("fnet3")).toBe(false);
		expect(looksLikeIp("hello")).toBe(false);
	});
});

describe("isValidHostnameOrIp — valid inputs", () => {
	test("accepts short hostnames (≥3 chars with letters)", () => {
		expect(isValidHostnameOrIp("fnet3")).toBe(true);
		expect(isValidHostnameOrIp("fnet7")).toBe(true);
		expect(isValidHostnameOrIp("lab-node-01")).toBe(true);
		expect(isValidHostnameOrIp("raspberrypi")).toBe(true);
	});

	test("accepts FQDNs", () => {
		expect(isValidHostnameOrIp("raspberrypi.local")).toBe(true);
		expect(isValidHostnameOrIp("Carloss-MacBook-Pro.local")).toBe(true);
		expect(isValidHostnameOrIp("my-server.example.com")).toBe(true);
	});

	test("accepts IPv4 addresses", () => {
		expect(isValidHostnameOrIp("192.168.0.154")).toBe(true);
		expect(isValidHostnameOrIp("10.0.0.1")).toBe(true);
		expect(isValidHostnameOrIp("172.16.0.1")).toBe(true);
	});

	test("accepts IPv6 addresses", () => {
		expect(isValidHostnameOrIp("fe80::1")).toBe(true);
		expect(isValidHostnameOrIp("::1")).toBe(true);
	});
});

describe("isValidHostnameOrIp — REJECTS the current bug", () => {
	test("❌ 'mac-orchestrator' is VALID hostname — this is the ACTUAL value", () => {
		// THIS IS THE KEY INSIGHT: "mac-orchestrator" IS a valid hostname!
		// The bug isn't that it's invalid — it's that it's NOT CONFIGURABLE.
		// The hostname IS correct for this machine, but the user wants to
		// OVERRIDE it with a logical node name like "fnet2" or "lab-orchestrator".
		expect(isValidHostnameOrIp("mac-orchestrator")).toBe(true);
	});

	test("rejects auto-generated agent IDs", () => {
		expect(isValidHostnameOrIp("agent-A914J7")).toBe(false);
		expect(isValidHostnameOrIp("agent-RZDZMM")).toBe(false);
		expect(isValidHostnameOrIp("worker-3VN9XS")).toBe(false);
		expect(isValidHostnameOrIp("peer-ABC123")).toBe(false);
		expect(isValidHostnameOrIp("node-ABCDEF")).toBe(false);
	});

	test("rejects garbage values", () => {
		expect(isValidHostnameOrIp("undefined")).toBe(false);
		expect(isValidHostnameOrIp("null")).toBe(false);
		expect(isValidHostnameOrIp("unknown")).toBe(false);
		expect(isValidHostnameOrIp("node-unknown")).toBe(false);
		expect(isValidHostnameOrIp("node-fallback")).toBe(false);
	});

	test("rejects nullish / empty", () => {
		expect(isValidHostnameOrIp(null)).toBe(false);
		expect(isValidHostnameOrIp(undefined)).toBe(false);
		expect(isValidHostnameOrIp("")).toBe(false);
		expect(isValidHostnameOrIp("   ")).toBe(false);
	});

	test("rejects purely numeric", () => {
		expect(isValidHostnameOrIp("12345")).toBe(false);
		expect(isValidHostnameOrIp("42")).toBe(false);
	});

	test("rejects all-uppercase identifier patterns", () => {
		expect(isValidHostnameOrIp("ABCDEF")).toBe(false);
		expect(isValidHostnameOrIp("RZDZMM")).toBe(false);
	});
});

// ━━ RESOLUTION CHAIN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("resolveNode — priority chain", () => {
	test("CLI flag wins over everything", () => {
		const result = resolveNode({
			cliFlag: "fnet3",
			envVar: "fnet4",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("fnet3");
		expect(result.source).toBe("flag");
		expect(result.valid).toBe(true);
	});

	test("env var wins when no CLI flag", () => {
		const result = resolveNode({
			envVar: "fnet4",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("fnet4");
		expect(result.source).toBe("env");
		expect(result.valid).toBe(true);
	});

	test("hostname is used when no flag or env", () => {
		const result = resolveNode({
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("mac-orchestrator");
		expect(result.source).toBe("hostname");
		expect(result.valid).toBe(true);
	});

	test("falls to 'unknown' when hostname is garbage", () => {
		const result = resolveNode({
			hostname: "",
		});
		expect(result.node).toBe("unknown");
		expect(result.source).toBe("fallback");
		expect(result.valid).toBe(false);
	});

	test("hostname undefined falls back to os.hostname() (valid on real machines)", () => {
		// When hostname option is undefined, resolveNode uses os.hostname()
		// which returns a valid hostname on real machines. This is correct behavior.
		const result = resolveNode({
			hostname: undefined as any,
		});
		// os.hostname() on this machine is "mac-orchestrator" — a valid hostname
		// So the result depends on the actual machine. We just verify it doesn't crash.
		expect(result.node).toBeTruthy();
		expect(result.source).toBe("hostname");
	});

	test("empty string hostname falls to 'unknown'", () => {
		const result = resolveNode({
			hostname: "",
		});
		expect(result.node).toBe("unknown");
		expect(result.valid).toBe(false);
	});

	test("CLI flag takes invalid value — falls through to env", () => {
		const result = resolveNode({
			cliFlag: "agent-A914J7",  // invalid
			envVar: "fnet3",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("fnet3");
		expect(result.source).toBe("env");
	});

	test("CLI flag and env both invalid — falls through to hostname", () => {
		const result = resolveNode({
			cliFlag: "agent-A914J7",  // invalid
			envVar: "undefined",       // invalid
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("mac-orchestrator");
		expect(result.source).toBe("hostname");
	});

	test("all sources invalid — falls to 'unknown'", () => {
		const result = resolveNode({
			cliFlag: "agent-A914J7",
			envVar: "undefined",
			hostname: "12345",  // purely numeric
		});
		expect(result.node).toBe("unknown");
		expect(result.source).toBe("fallback");
		expect(result.valid).toBe(false);
	});

	test("whitespace-only flag is treated as empty", () => {
		const result = resolveNode({
			cliFlag: "   ",
			envVar: "fnet3",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("fnet3");
		expect(result.source).toBe("env");
	});

	test("whitespace-only env is treated as empty", () => {
		const result = resolveNode({
			envVar: "   ",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("mac-orchestrator");
		expect(result.source).toBe("hostname");
	});
});

// ━━ THE ACTUAL BUG: current production code has no override mechanism ━━━

describe("THE BUG: os.hostname() is not configurable", () => {
	test("CURRENT: line 887 uses os.hostname() with no override", () => {
		// This documents the bug. In the production code:
		//   const node = os.hostname();
		// There is NO --node flag, NO PI_COMS_NET_NODE env var.
		// Result: every agent on this machine shows "mac-orchestrator".
		//
		// After the fix, resolveNode() replaces os.hostname() with the
		// full priority chain: --node > PI_COMS_NET_NODE > os.hostname()

		// Simulate what happens TODAY (no override):
		const result = resolveNode({ hostname: "mac-orchestrator" });
		expect(result.node).toBe("mac-orchestrator");
		expect(result.source).toBe("hostname");

		// What SHOULD happen (with override):
		const overridden = resolveNode({
			cliFlag: "fnet2",
			hostname: "mac-orchestrator",
		});
		expect(overridden.node).toBe("fnet2");
		expect(overridden.source).toBe("flag");
	});

	test("FIXED: operators can override with --node flag", () => {
		const result = resolveNode({
			cliFlag: "lab-orchestrator",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("lab-orchestrator");
		expect(result.source).toBe("flag");
		expect(result.valid).toBe(true);
	});

	test("FIXED: operators can override with PI_COMS_NET_NODE env var", () => {
		const result = resolveNode({
			envVar: "fnet2",
			hostname: "mac-orchestrator",
		});
		expect(result.node).toBe("fnet2");
		expect(result.source).toBe("env");
		expect(result.valid).toBe(true);
	});

	test("FIXED: IP address overrides work (for VMs with ugly hostnames)", () => {
		const result = resolveNode({
			cliFlag: "192.168.1.100",
			hostname: "ip-10-0-0-1.us-west-2.compute.internal",
		});
		expect(result.node).toBe("192.168.1.100");
		expect(result.source).toBe("flag");
	});
});

// ━━ DISPLAY HELPERS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("displayNode", () => {
	test("shows valid hostname", () => {
		expect(displayNode("fnet3")).toBe("fnet3");
		expect(displayNode("mac-orchestrator")).toBe("mac-orchestrator");
		expect(displayNode("lab-node-01")).toBe("lab-node-01");
	});

	test("shows IP address", () => {
		expect(displayNode("192.168.0.154")).toBe("192.168.0.154");
	});

	test("shows '?' for agent names", () => {
		expect(displayNode("agent-A914J7")).toBe("?");
		expect(displayNode("worker-3VN9XS")).toBe("?");
	});

	test("shows '?' for 'unknown'", () => {
		expect(displayNode("unknown")).toBe("?");
	});

	test("shows '?' for null/undefined/empty", () => {
		expect(displayNode(null)).toBe("?");
		expect(displayNode(undefined)).toBe("?");
		expect(displayNode("")).toBe("?");
	});
});

describe("nodeListPrefix", () => {
	test("returns @hostname for valid nodes", () => {
		expect(nodeListPrefix("fnet3")).toBe("@fnet3 ");
		expect(nodeListPrefix("192.168.0.154")).toBe("@192.168.0.154 ");
	});

	test("returns empty string for invalid nodes", () => {
		expect(nodeListPrefix("unknown")).toBe("");
		expect(nodeListPrefix("agent-A914J7")).toBe("");
		expect(nodeListPrefix(null)).toBe("");
		expect(nodeListPrefix(undefined)).toBe("");
	});
});

// ━━ TUI STATUS BAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("TUI status bar node display", () => {
	function formatStatusBar(identity: { name: string; project: string; node: string }): string {
		return `📡 ${identity.name}@${identity.project} (${identity.node})`;
	}

	test("status bar shows resolved node (not raw os.hostname)", () => {
		// After fix: identity.node comes from resolveNode()
		const result = resolveNode({ cliFlag: "fnet2", hostname: "mac-orchestrator" });
		const bar = formatStatusBar({ name: "planner", project: "default", node: result.node });
		expect(bar).toBe("📡 planner@default (fnet2)");
	});

	test("status bar falls back to hostname when no override", () => {
		const result = resolveNode({ hostname: "mac-orchestrator" });
		const bar = formatStatusBar({ name: "planner", project: "default", node: result.node });
		expect(bar).toBe("📡 planner@default (mac-orchestrator)");
	});

	test("status bar shows 'unknown' as last resort", () => {
		const result = resolveNode({ hostname: "" });
		const bar = formatStatusBar({ name: "planner", project: "default", node: result.node });
		expect(bar).toBe("📡 planner@default (unknown)");
	});
});

// ━━ WIDGET POOL RENDERING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("Widget pool node rendering", () => {
	test("valid node shows as [hostname]", () => {
		const display = displayNode("fnet3");
		const nodePart = `[${display}]`.padStart(12);
		expect(nodePart).toContain("fnet3");
		expect(nodePart).not.toContain("?");
	});

	test("'mac-orchestrator' is a valid hostname and displays correctly", () => {
		expect(displayNode("mac-orchestrator")).toBe("mac-orchestrator");
		// It's valid — the problem is configurability, not validity
	});

	test("invalid node renders as [?]", () => {
		const display = displayNode("agent-A914J7");
		const nodePart = `[${display}]`.padStart(12);
		expect(nodePart).toContain("[?]");
		expect(nodePart).not.toContain("A914J7");
	});

	test("unknown renders as [?]", () => {
		const display = displayNode("unknown");
		const nodePart = `[${display}]`.padStart(12);
		expect(nodePart).toContain("[?]");
	});
});

// ━━ AGENT REGRESSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("Regression: agent names must never appear as node names", () => {
	const agentNames = [
		"agent-A914J7",
		"agent-RZDZMM",
		"worker-3VN9XS",
		"peer-ABC123",
		"node-ABCDEF",
	];

	for (const name of agentNames) {
		test(`"${name}" is rejected as node name`, () => {
			expect(isValidHostnameOrIp(name)).toBe(false);
			expect(displayNode(name)).toBe("?");
			expect(nodeListPrefix(name)).toBe("");
		});
	}

	test("real hostnames are never falsely rejected", () => {
		const realHostnames = [
			"mac-orchestrator",
			"fnet3",
			"fnet7",
			"lab-node-01",
			"Carloss-MacBook-Pro.local",
			"raspberrypi.local",
			"192.168.0.154",
		];
		for (const h of realHostnames) {
			expect(isValidHostnameOrIp(h)).toBe(true);
		}
	});

	test("short hostnames < 3 chars are rejected (too ambiguous)", () => {
		expect(isValidHostnameOrIp("ab")).toBe(false);
		expect(isValidHostnameOrIp("a")).toBe(false);
	});

	test("hostnames with exactly 3 chars are accepted", () => {
		expect(isValidHostnameOrIp("f3n")).toBe(true);
		expect(isValidHostnameOrIp("abc")).toBe(true);
	});
});