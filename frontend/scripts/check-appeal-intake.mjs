import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const candidates = JSON.parse(readFileSync(new URL("../data/appeal-case-intake-candidates.json", import.meta.url), "utf8"));
const published = JSON.parse(readFileSync(new URL("../data/appeal-cases.json", import.meta.url), "utf8"));
assert(Array.isArray(candidates), "Candidate intake must be an array");
const ids = new Set(published.map(c => c.id));
const docketDates = new Set(published.map(c => c.appealNumber.replace(/\s+/g, "") + ":" + c.appealDate));
for (const c of candidates) {
  assert(c.id && !ids.has(c.id), "Duplicate or missing candidate id: " + c.id);
  ids.add(c.id);
  assert(c.docket && /^\d{4}-\d{2}-\d{2}$/.test(c.hearingDate), "Docket and ISO date required");
  assert.equal(new Date(c.hearingDate).toISOString().slice(0,10), c.hearingDate, "Invalid hearing date");
  const key = c.docket.replace(/\s+/g, "") + ":" + c.hearingDate;
  assert(!docketDates.has(key), "Duplicate docket/date: " + key);
  docketDates.add(key);
  const url = new URL(c.sourceUrl);
  assert(url.protocol === "https:" && !url.username && !url.password, "HTTPS source required");
  assert(c.sourceType && c.reportedOutcome, "Source type and attributed outcome required");
  assert(c.publishable === false, "Intake candidates must not be auto-published");
  assert(c.status === "candidate_needs_first_judgment", "Unexpected candidate status");
  assert(c.missing?.includes("الحكم السابق ومنطوقه"), "Missing previous judgment must be disclosed");
}
console.log("PASS: " + candidates.length + " attributed leads checked for format and duplicates; none approved for publication. URL reachability and claims NOT verified.");
