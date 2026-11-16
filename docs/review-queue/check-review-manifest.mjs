#!/usr/bin/env node
// Read-only gate for the 2026-11-11 legal research queue.
// Run: node docs/review-queue/check-review-manifest.mjs
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const base = dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(readFileSync(join(base, "2026-11-11-review-manifest.json"), "utf8"));
assert.equal(data.schema_version, 1);
assert.equal(data.publication_enabled, false, "Publication must remain disabled");
assert.equal(data.importable, false, "Manifest must not be importable");
assert.equal(data.status, "research_only");
const ids = new Set(), origins = new Set(), totals = { appeal: 0, real_world: 0 };
for (const r of data.records) {
  assert.ok(["appeal", "real_world"].includes(r.category), "Unknown category");
  totals[r.category]++;
  assert.match(r.review_id, /^(appeal|story)-\d{2}$/, "Invalid review ID");
  assert.ok(!ids.has(r.review_id), "Duplicate review ID: " + r.review_id);
  ids.add(r.review_id);
  const origin = r.source_file + ":" + r.source_id;
  assert.ok(!origins.has(origin), "Duplicate source origin: " + origin);
  origins.add(origin);
  assert.ok(!r.source_file.includes("/") && r.source_file.endsWith(".md"), "Unsafe source file");
  assert.ok(existsSync(join(base, r.source_file)), "Missing source: " + r.source_file);
  assert.equal(r.status, "draft");
  assert.equal(r.verification_status, "needs_review");
  assert.equal(r.publishable, false);
  assert.equal(r.approved, false);
  assert.equal(r.primary_source_checked, false);
}
assert.deepEqual(totals, { appeal: 20, real_world: 20 });
console.log("PASS: 20 appeals + 20 narratives indexed, unique IDs and origins, all quarantined.");
console.log("NOT CHECKED: judgment authenticity, narrative completeness, live DB duplicates, import compatibility.");
