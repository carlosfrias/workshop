/**
 * TDD: Fleet-dispatcher agent definition validation.
 *
 * Guards against the root cause of the 2026-05-26 incident:
 * fleet-dispatcher agent ran 46+ minutes (78K tokens) with no output
 * because coms_net_await timed out at 30min default with no degradation.
 *
 * These tests FAIL if the agent definition lacks cost-control constraints.
 * They encode the fix so this failure mode cannot recur.
 */
import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Parse YAML-like frontmatter from a Markdown agent definition. */
function parseFrontmatter(content: string): Record<string, unknown> {
	const match = content.match(/^---\n([\s\S]*?)\n---/);
	if (!match) return {};
	const lines = match[1]!.split("\n");
	const result: Record<string, unknown> = {};
	for (const line of lines) {
		const colon = line.indexOf(":");
		if (colon < 0) continue;
		const key = line.slice(0, colon).trim();
		const value = line.slice(colon + 1).trim();
		if (value.match(/^\d+$/)) result[key] = parseInt(value, 10);
		else if (value === "true") result[key] = true;
		else if (value === "false") result[key] = false;
		else result[key] = value;
	}
	return result;
}

/** Read the fleet-dispatcher agent definition. */
function readAgentDef(): { path: string; content: string; frontmatter: Record<string, unknown> } {
	// Project-level definition overrides global — test the project one
	// Path: server/__tests__/ → workspace/.pi/agents/fleet-dispatcher.md
	const projectPath = resolve(import.meta.dirname ?? ".", "../../../../../.pi/agents/fleet-dispatcher.md");
	const content = readFileSync(projectPath, "utf8");
	return { path: projectPath, content, frontmatter: parseFrontmatter(content) };
}

// ── TDD: Cost-Control Constraints ───────────────────────────────────────────

describe("fleet-dispatcher agent definition", () => {
	const def = readAgentDef();

	describe("maxTurns constraint (RED → GREEN)", () => {
		test("must have maxTurns set to prevent runaway agent loops", () => {
			expect(def.frontmatter.maxTurns).toBeDefined();
			expect(def.frontmatter.maxTurns).toBeLessThanOrEqual(15);
		});
	});

	describe("HARD CONSTRAINTS section", () => {
		test("must exist to encode cost-control rules", () => {
			expect(def.content).toContain("HARD CONSTRAINTS");
		});

		test("must require coms_net_await timeout ≤ 120s", () => {
			expect(def.content).toMatch(/coms_net_await.*timeout.*120/);
			expect(def.content).not.toMatch(/30min/);
		});

		test("must require pre-flight coms_net_list before Tier 1 dispatch", () => {
			expect(def.content).toMatch(/coms_net_list.*before.*Tier 1/);
		});

		test("must require immediate degradation on fleet timeout", () => {
			expect(def.content).toMatch(/times out.*degrade immediately/);
		});

		test("must require immediate degradation on Tier 2 failure", () => {
			expect(def.content).toMatch(/Tier 2.*fail.*degrade immediately/);
		});

		test("must require DEGRADED status report for non-Tier-1 completion", () => {
			expect(def.content).toContain("DEGRADED");
		});
	});
});
