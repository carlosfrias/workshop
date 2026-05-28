/**
 * resolve-node.ts — Node name resolution for coms-net identity
 *
 * Extracted from index.ts for testability.
 *
 * Resolution chain (highest priority wins):
 *   1. CLI flag: --node <name>
 *   2. Env var:  PI_COMS_NET_NODE
 *   3. OS hostname: os.hostname()
 *   4. Fallback: "unknown"
 *
 * After resolution, the node name is validated:
 *   - Must look like a hostname or IP (not an agent auto-generated ID)
 *   - Invalid values fall back to "unknown" with an audit warning
 */

import * as os from "node:os";

// ━━ Validation ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/** Check if a string looks like an IP address (v4 or v6). */
export function looksLikeIp(s: string): boolean {
	// IPv4
	if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(s)) {
		const octets = s.split(".").map(Number);
		return octets.every((o) => o >= 0 && o <= 255);
	}
	// IPv6
	if (/^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$/.test(s)) return true;
	return false;
}

/**
 * Validate that a string is a real hostname or IP address.
 *
 * Rejects:
 *   - "undefined", "null", "unknown", "node-unknown", "node-fallback"
 *   - Auto-generated agent IDs like "agent-A914J7", "worker-3VN9XS"
 *   - Purely numeric strings
 *   - All-uppercase identifiers (looks like ULID/hash fragments)
 *   - Strings with no letters (can't be a hostname)
 *
 * Accepts:
 *   - IPv4 / IPv6 addresses
 *   - FQDNs (contain dots)
 *   - Short hostnames ≥3 chars with at least one letter
 */
export function isValidHostnameOrIp(s: string | null | undefined): boolean {
	if (!s || typeof s !== "string" || s.trim().length === 0) return false;
	const cleaned = s.trim();

	// Reject known bad values and fallback patterns
	if (cleaned === "undefined" || cleaned === "null" || cleaned === "unknown") return false;
	if (cleaned === "node-unknown" || cleaned === "node-fallback") return false;

	// Reject auto-generated agent IDs: "agent-A914J7", "worker-3VN9XS", "node-ABC123"
	if (/^(agent|worker|peer|node)-[A-Z0-9]{5,}$/.test(cleaned)) return false;

	// Reject all-uppercase generated IDs (e.g., "ABCDEF", "RZDZMM")
	if (/^[A-Z0-9-]+$/.test(cleaned) && cleaned.length >= 3) return false;

	// Accept IP addresses
	if (looksLikeIp(cleaned)) return true;

	// Must contain at least one letter (not pure numeric)
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

// ━━ Node resolution ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export interface ResolveNodeOptions {
	/** CLI --node flag value (highest priority) */
	cliFlag?: string;
	/** PI_COMS_NET_NODE environment variable */
	envVar?: string;
	/** Override os.hostname() for testing */
	hostname?: string;
}

/**
 * Resolve the node name for coms-net registration.
 *
 * Priority: --node flag > PI_COMS_NET_NODE env > os.hostname() > "unknown"
 *
 * After resolution, validates the result. Invalid names (agent IDs, garbage)
 * fall back to "unknown" so the TUI never displays garbage.
 */
export function resolveNode(options: ResolveNodeOptions = {}): { node: string; source: string; valid: boolean } {
	const cliFlag = options.cliFlag;
	const envVar = options.envVar;
	const hostname = options.hostname ?? os.hostname();

	// 1. CLI flag (highest priority)
	if (cliFlag && cliFlag.trim().length > 0) {
		const trimmed = cliFlag.trim();
		if (isValidHostnameOrIp(trimmed)) {
			return { node: trimmed, source: "flag", valid: true };
		}
		// CLI flag was explicitly set but invalid — fall through with warning
	}

	// 2. Env var
	if (envVar && envVar.trim().length > 0) {
		const trimmed = envVar.trim();
		if (isValidHostnameOrIp(trimmed)) {
			return { node: trimmed, source: "env", valid: true };
		}
		// Env var was set but invalid — fall through
	}

	// 3. OS hostname
	if (hostname && hostname.trim().length > 0) {
		const trimmed = hostname.trim();
		if (isValidHostnameOrIp(trimmed)) {
			return { node: trimmed, source: "hostname", valid: true };
		}
	}

	// 4. Fallback — nothing valid
	return { node: "unknown", source: "fallback", valid: false };
}

/**
 * Sanitize a node name for display in the TUI.
 * Returns the node if valid, "?" if invalid/unknown.
 */
export function displayNode(node: string | null | undefined): string {
	if (isValidHostnameOrIp(node)) return node!.trim();
	return "?";
}

/**
 * Format a node name for coms_net_list tool output.
 * Returns "@hostname" if valid, or empty string if not.
 */
export function nodeListPrefix(node: string | null | undefined): string {
	const display = displayNode(node);
	return display !== "?" ? `@${display} ` : "";
}