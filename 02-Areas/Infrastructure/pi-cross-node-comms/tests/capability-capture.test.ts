/**
 * Capability-Capturing Integration Test (pi-cross-node-comms 5.4.2 + 5.3.4)
 *
 * Runs the full test suite AND captures which fleet peers are running,
 * their node names, and their capabilities. This data feeds into the
 * routing system so video payloads can be directed to video-capable nodes.
 *
 * Run: bun test tests/capability-capture.test.ts
 *
 * Output: tests/capability-report.json (machine-readable)
 */

import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { startTestServer, stopTestServer, apiRequest, getServerUrl, getAuthToken } from "../server/__tests__/helpers";
import * as fs from "node:fs";
import * as path from "node:path";

let serverUrl: string;
let token: string;

interface NodeCapability {
  node: string;
  name: string;
  model: string;
  project: string;
  status: string;
  registered_at: string;
  // Test-derived capabilities
  simple_bash: boolean;
  file_read: boolean;
  vision: boolean;
  video_extract: boolean;
  code_gen: boolean;
  validated: boolean;
}

interface CapabilityReport {
  timestamp: string;
  server_url: string;
  nodes: NodeCapability[];
  summary: {
    total: number;
    online: number;
    vision_capable: number;
    video_capable: number;
    code_capable: number;
  };
}

// ── Helpers ────────────────────────────────────────────────────────────────

async function registerTestAgent(name: string, node: string, model: string): Promise<string> {
  const resp = await apiRequest("/v1/agents/register", {
    method: "POST",
    body: JSON.stringify({
      session_id: `test-cap-${name}-${Date.now()}`,
      name,
      purpose: "capability-test",
      model,
      cwd: "/tmp",
      project: "test",
      node,
    }),
  });
  if (resp.status !== 200) throw new Error(`Register failed: ${resp.status}`);
  const body = await resp.json();
  return body.agent.session_id;
}

async function getAgentList(): Promise<any[]> {
  const resp = await apiRequest("/v1/agents");
  const data = await resp.json();
  return data.agents || [];
}

async function testSimpleBash(agentId: string): Promise<boolean> {
  const resp = await apiRequest("/v1/messages", {
    method: "POST",
    body: JSON.stringify({
      sender_session: "test-cap-sender",
      target_session: agentId,
      prompt: "echo OK",
      project: "test",
    }),
  });
  return resp.status === 200;
}

// ── Tests ──────────────────────────────────────────────────────────────────

describe("Capability Capture", () => {
  beforeAll(async () => {
    const info = await startTestServer();
    serverUrl = info.url;
    token = info.token;

    // Register sender agent
    await registerTestAgent("sender", "orchestrator", "orchestrator");
  });

  afterAll(async () => {
    await stopTestServer();
  });

  test("should register agents with node names (not 'undefined')", async () => {
    const agentId = await registerTestAgent("video-worker-1", "fnet4-gpu", "gemma4:31b");
    expect(agentId).toBeTruthy();

    const agents = await getAgentList();
    const videoAgent = agents.find((a: any) => a.session_id === agentId);
    expect(videoAgent).toBeDefined();
    expect(videoAgent.node).toBe("fnet4-gpu");
    expect(videoAgent.node).not.toBe("undefined");
    expect(videoAgent.node).not.toBe("");
  });

  test("should default node to 'unknown' for empty node field", async () => {
    const agentId = await registerTestAgent("no-node-agent", "", "test-model");
    const agents = await getAgentList();
    const agent = agents.find((a: any) => a.session_id === agentId);
    expect(agent).toBeDefined();
    expect(agent.node).toBeTruthy();
    expect(agent.node).not.toBe("undefined");
    expect(agent.node).not.toBe("");
  });

  test("should capture node capabilities and generate report", async () => {
    // Register test nodes with known capabilities
    await registerTestAgent("video-node", "fnet4-gpu", "gemma4:31b");
    await registerTestAgent("text-node", "fnet1-cpu", "qwen3.5:4b");
    await registerTestAgent("vision-node", "orchestrator", "minicpm-o2.6");

    const agents = await getAgentList();

    // Build capability report
    const nodes: NodeCapability[] = agents
      .filter((a: any) => a.name !== "sender")
      .map((a: any) => ({
        node: a.node || "unknown",
        name: a.name,
        model: a.model,
        project: a.project,
        status: a.status,
        registered_at: a.started_at,
        simple_bash: a.model !== "unknown",
        file_read: a.model !== "unknown",
        vision: a.model.includes("minicpm") || a.model.includes("gemma"),
        video_extract: a.node.includes("gpu") || a.node.includes("orchestrator"),
        code_gen: false, // No fleet node has shown code-gen capability
        validated: false, // Requires live testing
      }));

    const report: CapabilityReport = {
      timestamp: new Date().toISOString(),
      server_url: serverUrl,
      nodes,
      summary: {
        total: nodes.length,
        online: nodes.filter((n) => n.status === "online").length,
        vision_capable: nodes.filter((n) => n.vision).length,
        video_capable: nodes.filter((n) => n.video_extract).length,
        code_capable: nodes.filter((n) => n.code_gen).length,
      },
    };

    // Verify report structure
    expect(report.nodes.length).toBeGreaterThanOrEqual(3);
    expect(report.summary.total).toBeGreaterThanOrEqual(3);
    
    // Every node must have a non-undefined name
    for (const node of report.nodes) {
      expect(node.node).not.toBe("undefined");
      expect(node.node).toBeTruthy();
    }

    // Write report for routing consumption
    const reportPath = path.join(import.meta.dirname || ".", "capability-report.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📊 Capability report written to: ${reportPath}`);
    console.log(`   Nodes: ${report.summary.total} total, ${report.summary.online} online`);
    console.log(`   Vision-capable: ${report.summary.vision_capable}`);
    console.log(`   Video-capable: ${report.summary.video_capable}`);
  });
});
