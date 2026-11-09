/* Content-integrity checks for the public real-world stories.
   Run: node scripts/check-real-world-stories.mjs */
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const source = readFileSync(new URL("../app/real-world/stories.ts", import.meta.url), "utf8");
const prefix = "export const realWorldStories = ";
assert(source.startsWith(prefix), "Expected JSON-compatible stories export");
const stories = JSON.parse(source.slice(prefix.length).trim().replace(/;$/, ""));
assert.equal(stories.length, 10, "Expected ten stories");
const ids = new Set();
let sourceCount = 0;
for (const story of stories) {
  assert(Number.isInteger(story.id) && story.id > 0, "Invalid story id");
  assert(!ids.has(story.id), "Duplicate story id " + story.id);
  ids.add(story.id);
  assert(story.title?.trim() && story.subtitle?.trim() && story.era?.trim(), "Missing story heading");
  assert.equal(story.chapters?.length, 5, "Expected five chapters in " + story.title);
  for (const chapter of story.chapters) {
    assert(chapter.heading?.trim() && chapter.body?.trim(), "Empty chapter in " + story.title);
  }
  assert(story.sources?.length >= 2, "Missing independent source leads in " + story.title);
  for (const link of story.sources) {
    const url = new URL(link);
    assert.equal(url.protocol, "https:", "Non-HTTPS source in " + story.title);
    assert(url.hostname && !url.hostname.includes("example."), "Placeholder source");
    sourceCount++;
  }
  assert(story.verification && typeof story.verification.primaryJudgmentAvailable === "boolean", "Missing verification status");
  assert(/^\\d{4}-\\d{2}-\\d{2}$/.test(story.verification.reviewedAt), "Invalid review date");
  assert(story.verification.editorialNote?.trim(), "Missing editorial note");
  if (story.verification.primaryJudgmentAvailable) {
    assert(story.verification.primaryJudgmentUrl?.startsWith("https://"), "Official judgment link required before primary verification");
  }
}
const page = readFileSync(new URL("../app/real-world/page.tsx", import.meta.url), "utf8");
for (const id of ids) assert(new RegExp("^" + id + ":\\[", "m").test(page), "Missing timeline for " + id);
assert(page.includes("لم تُطابق نسخة رسمية كاملة"), "Verification warning must remain visible");
assert(page.includes("target=\"_blank\"") && page.includes("noopener noreferrer"), "Source links must be safe");
console.log("PASS: " + stories.length + " stories, " + sourceCount + " source leads, timelines, and verification notices. Link reachability and legal accuracy NOT tested.");
