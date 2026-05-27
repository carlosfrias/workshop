/**
 * Heartbeat tick logic — extracted from index.ts for testability.
 *
 * Bug: heartbeatTimer (setInterval every 10s) captured currentCtx
 * (module-level var set in session_start). When session was replaced via
 * ctx.reload() / ctx.fork(), currentCtx went stale. The next heartbeat
 * tick called ctx.getContextUsage() which threw:
 *   "This extension ctx is stale after session replacement or reload"
 *
 * Fix: try/catch with ctxWasStale signal so caller can null out the reference.
 */

export interface HeartbeatTickInput {
	/** May be null — no session active yet */
	currentCtx: { getContextUsage(): { percent: number } | null } | null;
	/** May be null — extension not initialized */
	identity: { project: string; session_id: string; model: string } | null;
	/** Inbound message queue depth */
	queueDepth: number;
}

export interface HeartbeatTickOutput {
	/** Context usage percent, rounded to nearest integer; 0 if unavailable */
	pct: number;
	/** Pass-through from input — queue depth for heartbeat payload */
	queue_depth: number;
	/** True when getContextUsage() threw (stale ctx after session replacement) */
	ctxWasStale: boolean;
}

/**
 * Perform a single heartbeat tick. Safe to call even with null/absent inputs.
 *
 * When ctxWasStale is true, the caller SHOULD null out its ctx reference
 * to prevent repeated failed calls on the stale object. The next
 * session_start will provide a fresh ctx.
 */
export function performHeartbeatTick(
	currentCtx: HeartbeatTickInput["currentCtx"],
	identity: HeartbeatTickInput["identity"],
	queueDepth: number,
): HeartbeatTickOutput {
	if (!identity) return { pct: 0, queue_depth: queueDepth, ctxWasStale: false };

	let pct = 0;
	let ctxWasStale = false;
	try {
		pct = Math.round(currentCtx?.getContextUsage()?.percent ?? 0);
	} catch {
		ctxWasStale = true;
	}
	return { pct, queue_depth: queueDepth, ctxWasStale };
}
