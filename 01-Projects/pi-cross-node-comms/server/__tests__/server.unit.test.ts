import { describe, expect, test } from "bun:test";
import { ulid, nowIso, isLoopback, tokensEqual, json, sseFrame } from "../coms-net-server.ts";

describe("ulid", () => {
	test("returns a 26-character string", () => {
		const id = ulid();
		expect(id.length).toBe(26);
	});

	test("generates unique values", () => {
		const set = new Set(Array.from({ length: 1000 }, () => ulid()));
		expect(set.size).toBe(1000);
	});
});

describe("nowIso", () => {
	test("returns ISO 8601 string", () => {
		const ts = nowIso();
		expect(ts).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
	});
});

describe("isLoopback", () => {
	test("recognizes 127.0.0.1", () => {
		expect(isLoopback("127.0.0.1")).toBe(true);
	});

	test("recognizes localhost", () => {
		expect(isLoopback("localhost")).toBe(true);
	});

	test("recognizes ::1 (IPv6 loopback)", () => {
		expect(isLoopback("::1")).toBe(true);
	});

	test("rejects 0.0.0.0 (not in implementation)", () => {
		// Implementation only checks 127.0.0.1, ::1, localhost
		// 0.0.0.0 is not treated as loopback by the current implementation
		expect(isLoopback("0.0.0.0")).toBe(false);
	});

	test("rejects 127.x.x.x except 127.0.0.1", () => {
		// Implementation only checks exact match on 127.0.0.1
		expect(isLoopback("127.0.0.2")).toBe(false);
	});

	test("rejects public IPs", () => {
		expect(isLoopback("192.168.0.1")).toBe(false);
		expect(isLoopback("10.0.0.1")).toBe(false);
	});

	test("rejects empty string", () => {
		expect(isLoopback("")).toBe(false);
	});
});

describe("tokensEqual", () => {
	test("matching tokens return true", () => {
		expect(tokensEqual("abc123", "abc123")).toBe(true);
	});

	test("different tokens return false", () => {
		expect(tokensEqual("token-a", "token-b")).toBe(false);
	});

	test("different lengths return false safely", () => {
		expect(tokensEqual("short", "much-longer-token")).toBe(false);
	});

	test("empty tokens match", () => {
		expect(tokensEqual("", "")).toBe(true);
	});
});

describe("json", () => {
	test("returns Response with JSON content type", () => {
		const res = json({ ok: true });
		expect(res.headers.get("content-type")).toBe("application/json");
		expect(res.status).toBe(200);
	});

	test("accepts custom status code", () => {
		const res = json({ error: "not found" }, 404);
		expect(res.status).toBe(404);
	});

	test("serializes the body", async () => {
		const res = json({ msg_id: "abc123", status: "delivered" });
		const body = await res.json();
		expect(body).toEqual({ msg_id: "abc123", status: "delivered" });
	});
});

describe("sseFrame", () => {
	test("formats SSE event without id", () => {
		const frame = sseFrame("prompt", { hello: "world" });
		expect(frame).toContain("event: prompt\n");
		expect(frame).toContain("data: ");
		expect(frame).toMatch(/\n\n$/);
	});

	test("formats SSE event with id", () => {
		const frame = sseFrame("heartbeat", { ts: 123 }, 42);
		expect(frame).toContain("id: 42\n");
	});

	test("data is JSON-encoded", () => {
		const frame = sseFrame("message_status", { status: "delivered" });
		const dataLine = frame.split("\n").find((l) => l.startsWith("data: "));
		expect(dataLine).toBeDefined();
		const parsed = JSON.parse(dataLine!.slice(6));
		expect(parsed.status).toBe("delivered");
	});
});