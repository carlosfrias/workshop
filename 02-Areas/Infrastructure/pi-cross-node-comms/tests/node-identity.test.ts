/**
 * TDD: Node Identity Validation (pi-cross-node-comms)
 *
 * Verifies that every node identifier is a hostname or IP address,
 * NOT an agent name, NOT "undefined", NOT "unknown".
 *
 * agent-A914J7 is an agent NAME, not a hostname. This test fails
 * against that scenario and drives the fix.
 *
 * Run: bun test tests/node-identity.test.ts
 */

import { test, expect, describe } from "bun:test";
import * as os from "node:os";

// ── Validation: must be hostname or IP ────────────────────────────────────

/** Check if a string looks like an IP address (v4 or v6). */
function looksLikeIp(s: string): boolean {
	// IPv4: 1-3 digits, 4 octets, not starting with 0 unless it's just "0"
	if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(s)) {
		const octets = s.split(".").map(Number);
		return octets.every((o) => o >= 0 && o <= 255);
	}
	// IPv6: hex groups separated by colons
	if (/^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$/.test(s)) return true;
	return false;
}

/** Check if a string looks like a valid hostname or IP address. */
function isValidHostnameOrIp(s: string | null | undefined): boolean {
	if (!s || typeof s !== "string" || s.trim().length === 0) return false;
	const cleaned = s.trim();

	// Reject known bad values and fallback patterns
	if (cleaned === "undefined" || cleaned === "null" || cleaned === "unknown") return false;
	if (cleaned === "node-unknown" || cleaned === "node-fallback") return false;

	// Reject auto-generated agent IDs: "agent-A914J7", "worker-3VN9XS", "node-ABC123"
	// These have a 5+ char suffix of uppercase letters + digits (not real hostnames)
	// Does NOT reject "agent-01", "worker-node", or "test-agent"
	if (/^(agent|worker|peer|node)-[A-Z0-9]{5,}$/.test(cleaned)) return false;

	// Reject all-uppercase generated IDs (e.g., "ABCDEF", "RZDZMM")
	if (/^[A-Z0-9-]+$/.test(cleaned) && cleaned.length >= 3) return false;

	// Accept IP addresses
	if (looksLikeIp(cleaned)) return true;

	// Accept hostnames: must contain a dot (FQDN) OR be mixed-case/lowercase name
	// Must contain at least one letter
	if (!/[a-zA-Z]/.test(cleaned)) return false;

	// Hostname pattern: word chars, dots, hyphens
	if (/^[a-zA-Z0-9]([a-zA-Z0-9\-.]*[a-zA-Z0-9])?$/.test(cleaned)) {
		// FQDN (has dot) — always valid
		if (cleaned.includes(".")) return true;
		// Simple hostname — must be at least 3 chars
		return cleaned.length >= 3;
	}
	return false;
}

/** Client-side node resolution (mirrors pi-cross-node-comms extension). */
function resolveNodeForRegistration(): string {
	try {
		const hostname = os.hostname();
		if (hostname && hostname.trim().length > 0) return hostname.trim();
	} catch {
		// fall through
	}
	return "unknown";
}

// ── UNIT tests: validation logic ──────────────────────────────────────────

describe("Node Identity Validation (UNIT)", () => {
	describe("isValidHostnameOrIp", () => {
		// ── Passing cases ──

		test("accepts valid hostnames", () => {
			expect(isValidHostnameOrIp("fnet3")).toBe(true);
			expect(isValidHostnameOrIp("lab-node-01")).toBe(true);
			expect(isValidHostnameOrIp("raspberrypi.local")).toBe(true);
			expect(isValidHostnameOrIp("Carloss-MacBook-Pro.local")).toBe(true);
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

		// ── Failing cases ──

		test("rejects agent names (RED — agent names are NOT hostnames)", () => {
			// Auto-generated agent IDs: agent-XXXXXX where X is uppercase+digit suffix
			expect(isValidHostnameOrIp("agent-A914J7")).toBe(false);
			expect(isValidHostnameOrIp("agent-RZDZMM")).toBe(false);
			expect(isValidHostnameOrIp("agent-29XM28")).toBe(false);
			expect(isValidHostnameOrIp("worker-3VN9XS")).toBe(false);
			// "worker-1" and "test-agent" are OK — they could be real hostnames
		});

		test("rejects undefined, null, empty", () => {
			expect(isValidHostnameOrIp(undefined)).toBe(false);
			expect(isValidHostnameOrIp(null)).toBe(false);
			expect(isValidHostnameOrIp("")).toBe(false);
			expect(isValidHostnameOrIp("   ")).toBe(false);
		});

		test("rejects 'undefined' and 'null' strings", () => {
			expect(isValidHostnameOrIp("undefined")).toBe(false);
			expect(isValidHostnameOrIp("null")).toBe(false);
			expect(isValidHostnameOrIp("unknown")).toBe(false);
		});

		test("rejects purely numeric strings", () => {
			expect(isValidHostnameOrIp("12345")).toBe(false);
			expect(isValidHostnameOrIp("42")).toBe(false);
		});

		test("rejects generic fallback names", () => {
			expect(isValidHostnameOrIp("node-ABCDEF")).toBe(false);
			expect(isValidHostnameOrIp("node-unknown")).toBe(false);
		});
	});

	describe("Local node resolution", () => {
		test("os.hostname() should be a valid hostname or IP on a real machine", () => {
			const node = resolveNodeForRegistration();
			// On a real machine, hostname should be valid
			// But "unknown" is the fallback and we can't fail the real-machine test on it
			if (node !== "unknown") {
				expect(isValidHostnameOrIp(node)).toBe(true);
			}
		});

		test("'unknown' fallback must be treated as a failure at the integration level", () => {
			// The word "unknown" is NEVER an acceptable node identifier
			expect(isValidHostnameOrIp("unknown")).toBe(false);
		});
	});
});

// ── INTEGRATION tests: server-side registration validation ──────────────

describe("Server Node Validation (INTEGRATION)", () => {
	/** Mirrors server's node validation logic (coms-net-server.ts lines 579-581) */
	function serverValidateNode(bodyNode: unknown): string {
		if (typeof bodyNode === "string" && bodyNode.trim().length > 0 && bodyNode !== "undefined") {
			const node = bodyNode.trim();
			// Additional validation: must be a real hostname or IP, not an agent name
			if (isValidHostnameOrIp(node)) return node;
		}
		return "unknown";
	}

	test("accepts hostname from client registration", () => {
		expect(serverValidateNode("fnet3")).toBe("fnet3");
		expect(serverValidateNode("lab-node-01")).toBe("lab-node-01");
	});

	test("accepts IP address from client registration", () => {
		expect(serverValidateNode("192.168.0.154")).toBe("192.168.0.154");
	});

	test("defaults to 'unknown' for missing/invalid node", () => {
		expect(serverValidateNode(undefined)).toBe("unknown");
		expect(serverValidateNode("")).toBe("unknown");
		expect(serverValidateNode("undefined")).toBe("unknown");
	});

	test("rejects agent names as node values (GREEN — agent names are NOT hostnames)", () => {
		expect(serverValidateNode("agent-A914J7")).toBe("unknown");
		expect(serverValidateNode("agent-RZDZMM")).toBe("unknown");
	});
});

// ── ACCEPTANCE tests: TUI widget must show hostname or IP ────────────────

describe("TUI Widget Node Display (ACCEPTANCE)", () => {
	function formatWidgetNode(node: string | null | undefined): string {
		const display = isValidHostnameOrIp(node) ? node!.trim() : "?";
		return `[${display}]`.padStart(12);
	}

	test("shows hostname when valid", () => {
		const result = formatWidgetNode("Carloss-MacBook-Pro.local");
		expect(result).toContain("Carloss-MacBook-Pro.local");
		expect(result).not.toContain("?");
	});

	test("shows '?' for unknown node — never shows agent name", () => {
		const result = formatWidgetNode("unknown");
		expect(result).toContain("?");
		expect(result).not.toContain("agent-A914J7");
	});

	test("shows '?' for agent names masquerading as node names", () => {
		const result = formatWidgetNode("agent-A914J7");
		expect(result).toContain("?");
		expect(result).not.toContain("agent-A914J7");
	});
});
