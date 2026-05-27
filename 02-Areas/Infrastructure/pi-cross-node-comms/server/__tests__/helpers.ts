/**
 * Test helpers for spinning up a coms-net server instance
 * for integration tests. Creates a temporary server on a random port,
 * provides a authenticated client, and tears it down after each test suite.
 */
import { expect, test, describe, beforeAll, afterAll } from "bun:test";

// ─────────────────────────────────────────────────────────────────────────────
// Server harness
// ─────────────────────────────────────────────────────────────────────────────

let serverBaseUrl: string;
let authToken: string;
let serverProcess: ReturnType<typeof Bun.spawn> | null = null;
let tmpDir: string;

export function getServerUrl(): string {
	return serverBaseUrl;
}

export function getAuthToken(): string {
	return authToken;
}

/**
 * Start a coms-net server on a random port for integration testing.
 * Sets PI_COMS_NET_AUTH_TOKEN and PI_COMS_NET_PORT=0 (random).
 */
export async function startTestServer(): Promise<{ url: string; token: string }> {
	const { mkdirSync, mkdtempSync, rmSync } = await import("node:fs");
	const { join } = await import("node:path");
	const { tmpdir } = await import("node:os");

	authToken = crypto.randomUUID().replace(/-/g, "");
	tmpDir = mkdtempSync(join(tmpdir(), "coms-net-test-"));

	const env: Record<string, string> = {
		...process.env,
		PI_COMS_NET_AUTH_TOKEN: authToken,
		PI_COMS_NET_PORT: "0", // random port
		PI_COMS_NET_HOST: "127.0.0.1",
		PI_COMS_NET_LOG_QUIET: "1",
		PI_COMS_NET_PROJECT: "test",
		// Point the server's state dir to our temp dir
		HOME: tmpDir,
	};

	serverProcess = Bun.spawn({
		cmd: ["bun", "run", import.meta.dir + "/../coms-net-server.ts"],
		env,
		stdout: "pipe",
		stderr: "pipe",
		cwd: import.meta.dir + "/..",
	});

	// Wait for the server to write server.json (indicates it's ready)
	const serverJsonPath = join(tmpDir, ".pi", "coms-net", "projects", "test", "server.json");
	let attempts = 0;
	while (attempts < 50) {
		try {
			const content = Bun.file(serverJsonPath);
			if (await content.exists()) {
				const json = await content.json();
				serverBaseUrl = json.local_url;
				return { url: serverBaseUrl, token: authToken };
			}
		} catch {
			// File not ready yet
		}
		await new Promise((r) => setTimeout(r, 100));
		attempts++;
	}

	throw new Error("Server did not start within 5 seconds");
}

/**
 * Stop the test server and clean up temp files.
 */
export async function stopTestServer(): Promise<void> {
	if (serverProcess) {
		serverProcess.kill("SIGTERM");
		await serverProcess.exited;
		serverProcess = null;
	}
	if (tmpDir) {
		const { rmSync } = await import("node:fs");
		try {
			rmSync(tmpDir, { recursive: true, force: true });
		} catch {
			// best effort
		}
	}
}

/**
 * Make an authenticated request to the test server.
 */
export async function apiRequest(
	path: string,
	options: RequestInit = {},
): Promise<Response> {
	const url = `${serverBaseUrl}${path}`;
	const headers = new Headers(options.headers || {});
	if (!headers.has("Authorization")) {
		headers.set("Authorization", `Bearer ${authToken}`);
	}
	if (!headers.has("Content-Type") && options.method !== "GET") {
		headers.set("Content-Type", "application/json");
	}
	return fetch(url, { ...options, headers });
}