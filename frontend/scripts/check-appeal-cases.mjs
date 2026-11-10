import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const records = JSON.parse(readFileSync(new URL("../data/appeal-cases.json", import.meta.url), "utf8"));
assert.ok(Array.isArray(records), "Appeal cases must be an array");
const ids = new Set();
const docketDates = new Set();
const isOfficialCourtSource = (value) => {
  if (typeof value !== "string") return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:" &&
      (url.hostname === "cc.gov.eg" || url.hostname.endsWith(".cc.gov.eg")) &&
      !url.username && !url.password;
  } catch {
    return false;
  }
};
for (const c of records) {
  assert.ok(typeof c.id === "string" && c.id, "Case id required");
  assert.ok(!ids.has(c.id), "Duplicate case id");
  ids.add(c.id);
  assert.match(c.appealDate, /^\d{4}-\d{2}-\d{2}$/, "Appeal date must be YYYY-MM-DD");
  assert.equal(new Date(c.appealDate).toISOString().slice(0, 10), c.appealDate, "Invalid appeal date");
  const docketDateKey = c.appealNumber.replace(/\s+/g, "").trim() + ":" + c.appealDate;
  assert.ok(!docketDates.has(docketDateKey), "Duplicate appeal docket and hearing date");
  docketDates.add(docketDateKey);
  assert.ok(["research_only", "verified"].includes(c.status), "Unknown verification status");
  assert.ok(c.appealNumber && c.appealDate, "Docket and appeal date required");
  assert.ok(c.firstJudgment && c.challengedJudgment && c.appealOutcome, "All three judgment stages required");
  assert.ok(c.secondarySources?.every(u => u.startsWith("https://")), "Invalid secondary source URL");
  if (c.status === "verified") {
    assert.ok(isOfficialCourtSource(c.officialJudgmentUrl), "Verified case needs official cc.gov.eg source URL");
    assert.ok(c.reviewedAt && c.reviewedBy, "Verified case needs reviewer and date");
    assert.ok(c.primarySourceChecked === true, "Verified case needs affirmative source check");
  } else {
    assert.equal(c.officialJudgmentUrl, null, "Research case must not claim official source");
  }
}
const publicCases = records.filter(c => c.status === "verified");
console.log(`Checked ${records.length} appeal cases; ${publicCases.length} verified for publication.`);
