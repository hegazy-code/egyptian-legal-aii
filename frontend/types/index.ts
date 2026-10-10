/**
 * Types mirroring the backend's answer shape.
 *
 * The backend (see /home/claude/egyptian-legal-ai/backend) does not yet expose
 * a `/chat` endpoint -- these types are written against the product spec
 * (8-section Arabic answer format + citation/no-hallucination policy) and are
 * the contract the frontend expects. When the real backend lands, adjust the
 * field names here to match its actual JSON -- lib/api.ts is the only place
 * that needs to change shape-mapping logic.
 */

/** Whether a legal text is currently in force or has been repealed/amended. */
export type SourceStatus = "current" | "historical";

/**
 * Whether a piece of the answer is a direct quote/citation of a legal text,
 * or an AI-generated inference/summary built on top of one.
 * (spec section 52: no-hallucination policy -- the UI should visually
 * distinguish these when the backend provides the distinction.)
 */
export type AnswerBasis = "from_law" | "ai_inference";

export type SourceKind = "law" | "judgment" | "procedure" | "other";

/** A single citation: a law article, a court judgment, or another source. */
export interface SourceCitation {
  id: string;
  /** e.g. "القانون المدني المصري" */
  lawName: string;
  /** e.g. "المادة 163" */
  articleNumber?: string;
  kind?: SourceKind;
  status: SourceStatus;
  /** Short quoted/summarized excerpt of the text, if available. */
  excerpt?: string;
  /** Link to the source document, if available. */
  sourceUrl?: string;
  basis?: AnswerBasis;
}

/**
 * The 8-section Arabic answer format:
 * 1. فهم سؤالك              -> understandingOfQuestion
 * 2. المجال القانوني         -> legalDomain
 * 3. النصوص القانونية ذات الصلة -> relevantLegalTexts
 * 4. الشرح                  -> explanation
 * 5. تطبيق مبدئي على الوقائع  -> preliminaryApplication
 * 6. معلومات ناقصة           -> missingInformation
 * 7. الإجراءات المحتملة       -> possibleProcedures
 * 8. مصادر الإجابة           -> answerSources
 * + تنبيه (disclaimer, always present, spec section 22)
 */
export interface LegalAnswer {
  understandingOfQuestion: string;
  legalDomain: string;
  relevantLegalTexts: SourceCitation[];
  explanation: string;
  preliminaryApplication: string;
  missingInformation: string[];
  possibleProcedures: string[];
  answerSources: SourceCitation[];
  disclaimer: string;
}

/** One exchange in the /ask conversation. */
export interface ChatTurn {
  id: string;
  question: string;
  answer?: LegalAnswer;
  /** Set when the request failed (network error, backend error, etc). */
  error?: string;
  createdAt: string;
}

export interface ChatRequest {
  question: string;
  conversationId?: string;
}

export interface ChatResponse {
  answer: LegalAnswer;
  conversationId?: string;
}
