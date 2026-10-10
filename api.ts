import type { ChatRequest, ChatResponse, LegalAnswer, SourceCitation } from "@/types";

/**
 * Base URL of the FastAPI backend. Falls back to localhost:8000 for local
 * dev if NEXT_PUBLIC_API_URL isn't set (see .env.local.example).
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://localhost:8000";

/** Thrown by apiFetch for both network failures and non-2xx responses. */
export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const DEFAULT_TIMEOUT_MS = 30_000;

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...init?.headers,
      },
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("انتهت مهلة الاتصال بالخادم. حاول مرة أخرى.");
    }
    // fetch() rejects with a TypeError for connection-refused / DNS / CORS
    // failures -- i.e. exactly the "backend isn't running" case.
    throw new ApiError(
      "تعذر الاتصال بالخادم. تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
    );
  } finally {
    clearTimeout(timeout);
  }

  if (!res.ok) {
    let message = `حدث خطأ في الخادم (رمز ${res.status}).`;
    try {
      const body = (await res.json()) as { message?: string; detail?: unknown };
      if (typeof body.message === "string") message = body.message;
      else if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = "تعذر معالجة الطلب. تأكد من صياغة السؤال ثم حاول مرة أخرى.";
    } catch {
      // response body wasn't JSON -- keep the generic message
    }
    throw new ApiError(message, res.status);
  }

  try {
    return (await res.json()) as T;
  } catch {
    throw new ApiError("استجابة غير صالحة من الخادم.");
  }
}

interface BackendChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string; // markdown with ### section headers
}

const SECTION_KEYS: [string, keyof LegalAnswer][] = [
  ["فهم سؤالك", "understandingOfQuestion"],
  ["المجال القانوني", "legalDomain"],
  ["النصوص القانونية", "relevantLegalTexts"],
  ["الشرح", "explanation"],
  ["تطبيق مبدئي", "preliminaryApplication"],
  ["معلومات ناقصة", "missingInformation"],
  ["الإجراءات المحتملة", "possibleProcedures"],
  ["مصادر الإجابة", "answerSources"],
  ["تنبيه", "disclaimer"],
];

function bullets(text: string): string[] {
  return text
    .split("\n")
    .map((l) => l.replace(/^\s*(?:[-*\u2022]|\d+[.)])\s*/, "").trim())
    .filter(Boolean);
}

function toCitations(text: string, prefix: string): SourceCitation[] {
  return bullets(text)
    .filter((l) => !l.includes("لا توجد مصادر"))
    .map((l, i) => ({ id: `${prefix}-${i}`, lawName: l, status: "current" as const }));
}

/** Normalise Arabic-Indic digits and strip markdown decoration from a line. */
function cleanHeaderLine(line: string): string {
  return line
    .replace(/[\u0660-\u0669]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/^[\s>#*_`\-]+/, "")
    .replace(/^\d+\s*[.)\-:]\s*/, "")
    .replace(/^[\s*_`]+/, "");
}

/** Turn the backend's markdown answer into the 8-section structure the UI renders. */
function parseAnswer(raw: string): LegalAnswer {
  let markdown = raw.trim();
  // Truncated/unparsed JSON wrapper from the model: {"answer_markdown": "...
  const wrapped = markdown.match(/^\{\s*"answer_markdown"\s*:\s*"/);
  if (wrapped) {
    markdown = markdown.slice(wrapped[0].length).replace(/"\s*\}?\s*$/, "");
  }
  // Escaped newlines left over from JSON.
  if (!markdown.includes("\n") && markdown.includes("\\n")) {
    markdown = markdown.replace(/\\n/g, "\n").replace(/\\"/g, '"');
  }

  const sections: Record<string, string> = {};
  let current: string | null = null;
  for (const line of markdown.split("\n")) {
    const cleaned = cleanHeaderLine(line);
    const hit = cleaned.length < 120 ? SECTION_KEYS.find(([ar]) => cleaned.startsWith(ar)) : undefined;
    if (hit) {
      current = hit[1];
      // Content on the same line as the heading ("فهم سؤالك: ...").
      const rest = cleaned
        .slice(cleaned.indexOf(hit[0]))
        .replace(/^[^\n:：\-–—]*[:：\-–—]\s*/, "");
      const sameLine = cleaned.includes(":") || cleaned.includes("：") ? rest.replace(/\*+$/, "").trim() : "";
      sections[current] = sameLine ? sameLine + "\n" : "";
      continue;
    }
    if (current) sections[current] += line + "\n";
  }
  const get = (k: string) => (sections[k] || "").replace(/\*\*/g, "").trim();
  const core = ["understandingOfQuestion", "legalDomain", "explanation", "preliminaryApplication"];
  const coreEmpty = core.every((k) => !get(k));
  return {
    understandingOfQuestion: get("understandingOfQuestion"),
    legalDomain: get("legalDomain"),
    relevantLegalTexts: toCitations(get("relevantLegalTexts"), "law"),
    // Safety net: if nothing could be sectioned, show the whole answer rather than blanks.
    explanation: coreEmpty ? markdown : get("explanation"),
    preliminaryApplication: get("preliminaryApplication"),
    missingInformation: bullets(get("missingInformation")),
    possibleProcedures: bullets(get("possibleProcedures")),
    answerSources: toCitations(get("answerSources"), "src"),
    disclaimer:
      get("disclaimer") ||
      "هذه الإجابة لأغراض تعليمية وإرشادية فقط ولا تُغني عن استشارة محامٍ مختص.",
  };
}

/** POST /chat -- ask a legal question, get back a structured 8-section answer. */
export async function postChat(request: ChatRequest): Promise<ChatResponse> {
  const data = await apiFetch<BackendChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({
      message: request.question,
      conversation_id: request.conversationId ?? null,
    }),
  });
  return { answer: parseAnswer(data.answer), conversationId: data.conversation_id };
}
