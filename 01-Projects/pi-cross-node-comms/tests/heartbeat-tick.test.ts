/**
 * Tests for performHeartbeatTick — the extracted heartbeat tick logic
 * that protects against stale-ctx crashes after session replacement/reload.
 *
 * Bug: heartbeatTimer (setInterval every 10s) captured currentCtx
 * (module-level var set in session_start). When session was replaced via
 * ctx.reload() / ctx.fork(), currentCtx went stale. The next heartbeat
 * tick called ctx.getContextUsage() which threw:
 *   "This extension ctx is stale after session replacement or reload"
 *
 * Fix: Extracted performHeartbeatTick() with try/catch. On catch, it
 * returns pct=0 and signals ctxWasStale=true so the caller can null out
 * the reference.
 */

import { describe, it, expect } from "bun:test";
import { performHeartbeatTick } from "../src/heartbeat-tick.ts";

// ━━ Mock helpers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function validIdentity() {
	return { project: "test", session_id: "01KS_TEST_SID", model: "qwen3.5:4b" };
}

function mockCtx(pct: number | null | Error) {
	if (pct instanceof Error) {
		return { getContextUsage: () => { throw pct; } };
	}
	return {
		getContextUsage: () => (pct === null ? null : { percent: pct }),
	} as any;
}

// ━━ Tests ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("performHeartbeatTick — null/absent inputs", () => {
	it("returns pct=0, ctxWasStale=false when currentCtx is null", () => {
		const result = performHeartbeatTick(null, validIdentity(), 0);
		expect(result.pct).toBe(0);
		expect(result.queue_depth).toBe(0);
		expect(result.ctxWasStale).toBe(false);
	});

	it("returns safe defaults when identity is null", () => {
		const result = performHeartbeatTick(mockCtx(42), null, 3);
		expect(result.pct).toBe(0);
		expect(result.queue_depth).toBe(3);
		expect(result.ctxWasStale).toBe(false);
	});

	it("returns pct=0 when getContextUsage returns null", () => {
		const result = performHeartbeatTick(mockCtx(null), validIdentity(), 0);
		expect(result.pct).toBe(0);
		expect(result.ctxWasStale).toBe(false);
	});

	it("returns pct=0 when getContextUsage returns undefined percent", () => {
		const ctx = { getContextUsage: () => ({}) } as any;
		const result = performHeartbeatTick(ctx, validIdentity(), 0);
		expect(result.pct).toBe(0);
		expect(result.ctxWasStale).toBe(false);
	});
});

describe("performHeartbeatTick — normal operation", () => {
	it("returns correct rounded pct from valid context", () => {
		const result = performHeartbeatTick(mockCtx(42.7), validIdentity(), 5);
		expect(result.pct).toBe(43);
		expect(result.queue_depth).toBe(5);
		expect(result.ctxWasStale).toBe(false);
	});

	it("rounds 0.4 down to 0", () => {
		const result = performHeartbeatTick(mockCtx(0.4), validIdentity(), 0);
		expect(result.pct).toBe(0);
	});

	it("rounds 99.5 up to 100", () => {
		const result = performHeartbeatTick(mockCtx(99.5), validIdentity(), 0);
		expect(result.pct).toBe(100);
	});

	it("preserves queue_depth from caller", () => {
		const result = performHeartbeatTick(mockCtx(10), validIdentity(), 7);
		expect(result.queue_depth).toBe(7);
	});
});

describe("performHeartbeatTick — stale-ctx crash path", () => {
	const STALE_ERROR = new Error(
		"This extension ctx is stale after session replacement or reload",
	);

	it("catches stale-ctx error, returns pct=0 with ctxWasStale=true", () => {
		const result = performHeartbeatTick(mockCtx(STALE_ERROR), validIdentity(), 0);
		expect(result.pct).toBe(0);
		expect(result.ctxWasStale).toBe(true);
	});

	it("does NOT throw when getContextUsage throws", () => {
		const explode = () =>
			performHeartbeatTick(mockCtx(STALE_ERROR), validIdentity(), 0);
		expect(explode).not.toThrow();
	});

	it("catches any error type (not just stale-ctx)", () => {
		const ctx = { getContextUsage: () => { throw "string error"; } } as any;
		const result = performHeartbeatTick(ctx, validIdentity(), 0);
		expect(result.pct).toBe(0);
		expect(result.ctxWasStale).toBe(true);
	});

	it("catches TypeError from missing method", () => {
		const ctx = {} as any; // no getContextUsage at all
		// This would throw TypeError, but optional chaining prevents it.
		// Let's verify it doesn't crash.
		expect(() => performHeartbeatTick(ctx, validIdentity(), 0)).not.toThrow();
	});
});

describe("performHeartbeatTick — edge cases", () => {
	it("handles identity with empty project string", () => {
		const id = { project: "", session_id: "x", model: "" };
		const result = performHeartbeatTick(mockCtx(50), id, 0);
		expect(result.pct).toBe(50);
		expect(result.ctxWasStale).toBe(false);
	});

	it("handles large queue_depth", () => {
		const result = performHeartbeatTick(mockCtx(10), validIdentity(), 999);
		expect(result.queue_depth).toBe(999);
	});

	it("is referentially transparent — repeated calls consistent", () => {
		const result1 = performHeartbeatTick(mockCtx(33), validIdentity(), 1);
		const result2 = performHeartbeatTick(mockCtx(33), validIdentity(), 1);
		expect(result1).toEqual(result2);
	});
});
