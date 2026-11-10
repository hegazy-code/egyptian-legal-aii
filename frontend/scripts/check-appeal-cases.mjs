import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const records = JSON.parse(readFileSync(new URL("../data/appeal-cases.json", import.meta.url), "utf8"));
assert.ok(Array.isArray(records), "Appeal cases must be an array");
const ids = new Set();
for (const c of records) {
  assert.ok(typeof c.id === "string" && c.id, "Case id required");
  assert.ok(!ids.has(c.id), "Duplicate case id");
  ids.add(c.id);
  assert.ok(["research_only", "verified"].includes(c.status), "Unknown verification status");
  assert.ok(c.appealNumber && c.appealDate, "Docket and appeal date required");
  assert.ok(c.firstJudgment && c.challengedJudgment && c.appealOutcome, "All three judgment stages required");
  assert.ok(c.secondarySources?.every(u => u.startsWith("https://")), "Invalid secondary source URL");
  if (c.status === "verified") {
    assert.ok(c.officialJudgmentUrl?.startsWith("https://"), "Verified case needs primary judgment URL");
    assert.ok(c.reviewedAt && c.reviewedBy, "Verified case needs reviewer and date");
    assert.ok(c.primarySourceChecked === true, "Verified case needs affirmative source check");
  } else {
    assert.equal(c.officialJudgmentUrl, null, "Research case must not claim official source");
  }
}
const publicCases = records.filter(c => c.status === "verified");
console.log(`Checked ${records.length} appeal cases; ${publicCases.length} verified for publication.`);
