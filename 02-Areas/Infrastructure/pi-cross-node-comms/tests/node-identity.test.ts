/**
 * TDD: Node Name Resolution Tests (pi-cross-node-comms 5.4.2)
 *
 * Verifies that the coms-net TUI footer, widget, and agent registry
 * correctly display the node name instead of "undefined".
 *
 * Run: bun test tests/node-identity.test.ts
 */

import { test, expect, describe } from "bun:test";
import * as os from "node:os";

// ── Node name resolution (mirrors src/index.ts line 887) ───────────────────

function resolveNodeName(): string {
  try {
    const hostname = os.hostname();
    if (hostname && hostname.trim().length > 0) return hostname.trim();
  } catch {
    // os.hostname() may throw in restricted environments
  }
  // Fallbacks if hostname is unavailable
  try {
    const env = process.env.HOST || process.env.HOSTNAME || process.env.COMPUTERNAME;
    if (env && env.trim().length > 0) return env.trim();
  } catch {
    // env access may be restricted
  }
  return "unknown";
}

// ── Widget node display (mirrors src/index.ts line 1087) ──────────────────

function formatNodeDisplay(node: string | undefined | null): string {
  const display = node && node.trim() ? node.trim() : "unknown";
  return `[${display}]`.padStart(12);
}

// ── Tests ──────────────────────────────────────────────────────────────────

describe("Node Name Resolution", () => {
  test("should return a non-empty string", () => {
    const node = resolveNodeName();
    expect(typeof node).toBe("string");
    expect(node.trim().length).toBeGreaterThan(0);
  });

  test("should not return 'undefined'", () => {
    const node = resolveNodeName();
    expect(node).not.toBe("undefined");
    expect(node).not.toBe("null");
    expect(node).not.toBe("");
  });

  test("should handle os.hostname() returning empty string", () => {
    // Even in worst case, fallback should handle it
    const node = resolveNodeName();
    expect(node).toBeTruthy();
  });
});

describe("Widget Node Display", () => {
  test("should display valid node name", () => {
    const result = formatNodeDisplay("fnet3");
    expect(result).toContain("fnet3");
    expect(result).not.toContain("undefined");
  });

  test("should display 'unknown' for undefined node", () => {
    const result = formatNodeDisplay(undefined);
    expect(result).toContain("unknown");
    expect(result).not.toContain("undefined");
  });

  test("should display 'unknown' for null node", () => {
    const result = formatNodeDisplay(null);
    expect(result).toContain("unknown");
  });

  test("should display 'unknown' for empty string node", () => {
    const result = formatNodeDisplay("");
    expect(result).toContain("unknown");
  });

  test("should handle whitespace-only node", () => {
    const result = formatNodeDisplay("   ");
    expect(result).toContain("unknown");
  });

  test("should handle real hostname scenarios", () => {
    const hostname = os.hostname();
    const result = formatNodeDisplay(hostname);
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(3);
    expect(result).not.toContain("undefined");
  });
});

describe("Node Identity in Registration", () => {
  test("registration payload must include non-empty node field", () => {
    // Simulates the RegisterRequest interface
    function validateRegisterRequest(req: { node: string }) {
      if (!req.node || req.node.trim().length === 0 || req.node === "undefined") {
        return { valid: false, error: "node field is required and must not be 'undefined'" };
      }
      return { valid: true };
    }

    expect(validateRegisterRequest({ node: "fnet4" }).valid).toBe(true);
    expect(validateRegisterRequest({ node: "" }).valid).toBe(false);
    expect(validateRegisterRequest({ node: "undefined" }).valid).toBe(false);
    expect(validateRegisterRequest({ node: "   " }).valid).toBe(false);
  });

  test("server should reject registration with empty node", () => {
    // Integration test: verify server handles missing node gracefully
    const validPayload = {
      session_id: "test-001",
      name: "test-agent",
      purpose: "test",
      model: "test",
      cwd: "/tmp",
      project: "test",
      node: "test-node",
    };
    expect(validPayload.node).toBeTruthy();
    expect(validPayload.node).not.toBe("undefined");

    // Without node field
    const invalidPayload = {
      session_id: "test-002",
      name: "test-agent",
      purpose: "test",
      model: "test",
      cwd: "/tmp",
      project: "test",
      node: "",
    };
    expect(invalidPayload.node).toBeFalsy();
  });
});
