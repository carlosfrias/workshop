/**
 * Proposed implementation: isValidModel() and sanitizeModel()
 *
 * These functions mirror the `isValidNodeName()` pattern already in
 * coms-net-server.ts. They should be added to the server source and
 * called in:
 *
 *   1. handleRegister() — sanitize body.model before storing
 *   2. handleHeartbeat() — sanitize body.model before updating entry.model
 *
 * Integration points in coms-net-server.ts:
 *
 *   In handleRegister():
 *     BEFORE:  model: body.model ?? "unknown",
 *     AFTER:   model: sanitizeModel(body.model),
 *             // For re-registration, preserve existing when omitted:
 *             //   model: body.model !== undefined
 *             //     ? sanitizeModel(body.model)
 *             //     : (existing?.model ?? "unknown"),
 *
 *   In handleHeartbeat():
 *     BEFORE:  if (typeof body.model === "string") entry.model = body.model;
 *     AFTER:   if (typeof body.model === "string") {
 *                const sanitized = sanitizeModel(body.model);
 *                if (sanitized !== "unknown" || entry.model === "unknown") {
 *                  entry.model = sanitized;
 *                }
 *              }
 *              // Rationale: if heartbeat sends an invalid model like "",
 *              // "undefined", or "   ", sanitizeModel returns "unknown".
 *              // We should NOT overwrite a known-good model with "unknown"
 *              // from a bad heartbeat. Only allow "unknown" if the current
 *              // model is already "unknown" (nothing to preserve).
 */

// ─────────────────────────────────────────────────────────────────────────────
// Model validation constants
// ─────────────────────────────────────────────────────────────────────────────

/** Maximum allowed length for a model identifier string. */
const MAX_MODEL_LENGTH = 128;

/** Sentinel values that should never be stored as model names. */
const MODEL_SENTINELS = new Set(["undefined", "null", "unknown"]);

/**
 * Allowed character pattern for model identifiers.
 *
 * Real model names follow these patterns:
 *   qwen3.5:4b            → lowercase + digits + dots + colons
 *   claude-3.5-sonnet     → lowercase + digits + dots + hyphens
 *   gemini-2.5-flash       → lowercase + digits + dots + hyphens
 *   gpt-4o                 → lowercase + digits + hyphens
 *   ollama/qwen3.5:4b     → lowercase + digits + dots + colons + slashes
 *   code_llama_34b         → lowercase + digits + underscores
 *
 * We allow: letters (a-z, A-Z), digits, dots, colons, hyphens, underscores,
 * and forward slashes. The string must start and end with an alphanumeric.
 */
const MODEL_PATTERN = /^[a-zA-Z0-9](?:[a-zA-Z0-9.:\-_/]*[a-zA-Z0-9])?$/;

/**
 * Check whether a model string looks like a real model identifier.
 *
 * Mirrors the validation logic of isValidNodeName() but adapted for model
 * identifiers which have different character set requirements.
 *
 * Rules:
 *   1. Must be a non-empty string (after trimming).
 *   2. Must not be a known sentinel value ("undefined", "null", "unknown").
 *   3. Must not be whitespace-only.
 *  4. Must not be all-uppercase alphanumeric (hash-like: "ABCDEF", "A1B2C3").
 *   5. Must not be purely numeric ("12345").
 *   6. Must not exceed MAX_MODEL_LENGTH characters.
 *   7. Must contain at least one lowercase letter (real model names always do).
 *   8. Must match MODEL_PATTERN (allowed chars only).
 *
 * @param s - The model string to validate (may be undefined/null)
 * @returns true if the model string is valid, false otherwise
 */
export function isValidModel(s: string | undefined | null): boolean {
	// Rule 1: Must be a non-empty string
	if (typeof s !== "string") return false;
	if (s.length === 0) return false;

	const trimmed = s.trim();

	// Rule 3: Must not be whitespace-only
	if (trimmed.length === 0) return false;

	// Rule 2: Must not be a sentinel value
	if (MODEL_SENTINELS.has(trimmed)) return false;

	// Rule 4: Must not be all-uppercase alphanumeric hash-like identifiers
	// This catches "ABCDEF", "A1B2C3", etc.
	// Allow mixed case and purely lowercase — real model names have lowercase.
	if (/^[A-Z0-9]+$/.test(trimmed) && trimmed.length >= 3) return false;

	// Rule 5: Must not be purely numeric
	if (/^\d+$/.test(trimmed)) return false;

	// Rule 6: Must not exceed max length
	if (trimmed.length > MAX_MODEL_LENGTH) return false;

	// Rule 7: Must contain at least one lowercase letter
	// Real model names always have lowercase: "qwen", "claude", "gemini", "gpt"
	if (!/[a-z]/.test(trimmed)) return false;

	// Rule 8: Must match the allowed character pattern
	if (!MODEL_PATTERN.test(trimmed)) return false;

	return true;
}

/**
 * Sanitize a model string for safe storage.
 *
 * Returns the trimmed model string if valid, or "unknown" if invalid.
 * This function should be used wherever a model string enters the system
 * (registration, heartbeat, re-registration).
 *
 * @param s - The model string to sanitize (may be undefined/null)
 * @returns The validated+trimmed model string, or "unknown" if invalid
 */
export function sanitizeModel(s: string | undefined | null): string {
	if (isValidModel(s)) {
		return s!.trim();
	}
	return "unknown";
}

// ─────────────────────────────────────────────────────────────────────────────
// Proposed changes to coms-net-server.ts
// ─────────────────────────────────────────────────────────────────────────────

/**
 * PATCH 1: handleRegister() — model field
 *
 * Current code (line ~619):
 *   model: body.model ?? "unknown",
 *
 * Proposed:
 *   model: body.model !== undefined
 *     ? sanitizeModel(body.model)
 *     : (existing?.model ?? "unknown"),
 *
 * Explanation:
 *   - If model is provided, sanitize it (empty string, "undefined", etc → "unknown")
 *   - If model is omitted on re-registration, preserve the existing model
 *   - If model is omitted on first registration, default to "unknown"
 */

/**
 * PATCH 2: handleHeartbeat() — model field
 *
 * Current code (line ~841):
 *   if (typeof body.model === "string") entry.model = body.model;
 *
 * Proposed:
 *   if (typeof body.model === "string") {
 *     const sanitized = sanitizeModel(body.model);
 *     // Only update if sanitized is a real model, OR if we have nothing to preserve
 *     if (sanitized !== "unknown" || entry.model === "unknown") {
 *       entry.model = sanitized;
 *     }
 *   }
 *
 * Explanation:
 *   - Sanitize the incoming model string first
 *   - If sanitization yields "unknown" (bad input), don't overwrite a known-good model
 *   - If the current model is already "unknown", allow the overwrite (nothing to lose)
 *   - Valid model strings always overwrite (normal update behavior)
 */