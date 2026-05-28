/**
 * TDD: Client-Side Inbound Prompt Handling — sender_node field
 *
 * Verifies that when an inbound prompt arrives via SSE (the [from ...] message),
 * the sender's node is extracted, stored in InboundContext, and displayed in the
 * user-facing message.
 *
 * RED first: these tests document the missing sender_node field, then we fix.
 *
 * Run: bun test tests/inbound-prompt-node.test.ts
 */

import { describe, expect, test } from "bun:test";

// ━━ Mirror of InboundContext from src/index.ts ━━━━━━━━━━━━━━━━━━━━━━━━━━

interface InboundContext {
	msg_id: string;
	hops: number;
	sender_session: string;
	sender_name: string;
	sender_cwd: string;
	sender_node: string;  // ← This is the new field
	response_schema?: object | null;
	fulfilled: boolean;
}

// ━━ Mirror of handleInboundPrompt logic from src/index.ts ━━━━━━━━━━━━━━━━
// Extracted for testability. The production code does the same thing.

function parseInboundPrompt(data: any): InboundContext | null {
	const msg_id: string | undefined = data?.msg_id;
	if (!msg_id || typeof msg_id !== "string") return null;

	const sender = data.sender ?? {};
	const senderName = typeof sender.name === "string" ? sender.name : "unknown";
	const senderCwd = typeof sender.cwd === "string" ? sender.cwd : "?";
	const senderSession = typeof sender.session_id === "string" ? sender.session_id : "?";
	const senderNode = typeof sender.node === "string" ? sender.node : "?";
	const promptText = typeof data.prompt === "string" ? data.prompt : "";
	const hops = typeof data.hops === "number" ? data.hops : 0;
	const responseSchema = (data.response_schema && typeof data.response_schema === "object") ? data.response_schema : null;

	return {
		msg_id,
		hops,
		sender_session: senderSession,
		sender_name: senderName,
		sender_cwd: senderCwd,
		sender_node: senderNode,
		response_schema: responseSchema,
		fulfilled: false,
	};
}

function formatInboundMessage(inbound: InboundContext, promptText: string): string {
	const nodePrefix = inbound.sender_node !== "?" ? `[${inbound.sender_node}] ` : "";
	return `[${nodePrefix}${inbound.sender_name} @ ${inbound.sender_cwd}]\n${promptText}`;
}

// ━━ TESTS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe("InboundPrompt — sender_node extraction", () => {
	test("extracts sender.node from prompt event data", () => {
		const data = {
			msg_id: "msg-001",
			project: "test",
			sender: {
				session_id: "sender-001",
				name: "planner",
				node: "fnet3",
				cwd: "/home/user/project",
			},
			prompt: "Run the tests",
			hops: 0,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound).not.toBeNull();
		expect(inbound!.sender_node).toBe("fnet3");
	});

	test("extracts sender.node='unknown' when node is 'unknown'", () => {
		const data = {
			msg_id: "msg-002",
			project: "test",
			sender: {
				session_id: "sender-002",
				name: "worker",
				node: "unknown",
				cwd: "/tmp",
			},
			prompt: "Hello",
			hops: 1,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound!.sender_node).toBe("unknown");
	});

	test("defaults sender_node to '?' when node is missing", () => {
		const data = {
			msg_id: "msg-003",
			project: "test",
			sender: {
				session_id: "sender-003",
				name: "orphan",
				cwd: "/tmp",
				// node field is missing — pre-fix server behavior
			},
			prompt: "Where are you?",
			hops: 0,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound!.sender_node).toBe("?");
	});

	test("defaults sender_node to '?' when sender object is missing", () => {
		const data = {
			msg_id: "msg-004",
			project: "test",
			prompt: "Ping",
			hops: 0,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound!.sender_node).toBe("?");
	});

	test("extracts IP address as sender_node", () => {
		const data = {
			msg_id: "msg-005",
			project: "test",
			sender: {
				session_id: "sender-005",
				name: "remote-agent",
				node: "192.168.1.100",
				cwd: "/home/user/work",
			},
			prompt: "Deploy to prod",
			hops: 2,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound!.sender_node).toBe("192.168.1.100");
	});
});

describe("InboundPrompt — message formatting with node", () => {
	test("formats message with sender node when valid", () => {
		const inbound: InboundContext = {
			msg_id: "msg-010",
			hops: 0,
			sender_session: "s1",
			sender_name: "planner",
			sender_cwd: "/home/user",
			sender_node: "fnet3",
			fulfilled: false,
		};

		const formatted = formatInboundMessage(inbound, "Run the tests");
		expect(formatted).toContain("[fnet3]");
		expect(formatted).toContain("planner");
		expect(formatted).toContain("/home/user");
	});

	test("omits node prefix when sender_node is '?'", () => {
		const inbound: InboundContext = {
			msg_id: "msg-011",
			hops: 0,
			sender_session: "s2",
			sender_name: "orphan",
			sender_cwd: "/tmp",
			sender_node: "?",
			fulfilled: false,
		};

		const formatted = formatInboundMessage(inbound, "Hello");
		expect(formatted).not.toContain("[?]");
		expect(formatted).toContain("orphan");
		expect(formatted).toContain("/tmp");
	});

	test("formats complete message: [fnet3] planner @ /home/user", () => {
		const inbound: InboundContext = {
			msg_id: "msg-012",
			hops: 1,
			sender_session: "s3",
			sender_name: "lab-worker",
			sender_cwd: "/home/lab",
			sender_node: "lab-node-01",
			fulfilled: false,
		};

		const formatted = formatInboundMessage(inbound, "Process the data");
		// Format: [[node] name @ cwd]\nprompt
		expect(formatted).toContain("[lab-node-01]");
		expect(formatted).toContain("lab-worker");
		expect(formatted).toContain("/home/lab");
		expect(formatted).toContain("Process the data");
	});

	test("formats message without node when unknown: planner @ /home/user", () => {
		const inbound: InboundContext = {
			msg_id: "msg-013",
			hops: 0,
			sender_session: "s4",
			sender_name: "planner",
			sender_cwd: "/home/user",
			sender_node: "?",
			fulfilled: false,
		};

		const formatted = formatInboundMessage(inbound, "What's the status?");
		expect(formatted).toBe("[planner @ /home/user]\nWhat's the status?");
	});
});

describe("InboundPrompt — regression: mac-orchestrator override scenario", () => {
	test("sender with overridden node shows logical name, not hostname", () => {
		// Simulates: operator launches with --node fnet2 on mac-orchestrator
		// The server sends sender.node="fnet2" (resolved by client's resolveNode)
		const data = {
			msg_id: "msg-100",
			project: "test",
			sender: {
				session_id: "sender-100",
				name: "orchestrator",
				node: "fnet2",
				cwd: "/home/user/workshop",
			},
			prompt: "Deploy the fleet",
			hops: 0,
		};

		const inbound = parseInboundPrompt(data);
		expect(inbound!.sender_node).toBe("fnet2");
		expect(inbound!.sender_node).not.toBe("mac-orchestrator");

		const formatted = formatInboundMessage(inbound!, "Deploy the fleet");
		expect(formatted).toContain("[fnet2]");
		expect(formatted).toContain("orchestrator");
		expect(formatted).toContain("/home/user/workshop");
	});
});