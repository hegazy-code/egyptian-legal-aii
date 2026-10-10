import type { ChatRequest, ChatResponse } from "@/types";

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
      const body = (await res.json()) as { message?: string; detail?: string };
      message = body.message || body.detail || message;
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

/** POST /chat -- ask a legal question, get back a structured 8-section answer. */
export async function postChat(request: ChatRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
