"use client";

import { useCallback, useRef, useState } from "react";
import { postChat, ApiError } from "@/lib/api";
import type { ChatTurn } from "@/types";

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

interface UseChatResult {
  turns: ChatTurn[];
  loading: boolean;
  ask: (question: string) => Promise<void>;
  reset: () => void;
}

/** Manages the question/answer history for the /ask page. */
export function useChat(): UseChatResult {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  // Keep conversationId in a ref so it persists across renders without
  // causing extra re-renders and is always up-to-date inside the closure.
  const conversationIdRef = useRef<string | undefined>(undefined);

  const ask = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const id = newId();
    const createdAt = new Date().toISOString();

    setTurns((prev) => [...prev, { id, question: trimmed, createdAt }]);
    setLoading(true);

    try {
      const response = await postChat({
        question: trimmed,
        conversationId: conversationIdRef.current,
      });

      // Save the conversation ID returned by the backend so follow-up
      // questions are added to the same conversation thread.
      conversationIdRef.current = response.conversationId;

      setTurns((prev) =>
        prev.map((t) => (t.id === id ? { ...t, answer: response.answer } : t))
      );
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "حدث خطأ غير متوقع. حاول مرة أخرى.";
      setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, error: message } : t)));
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const reset = useCallback(() => {
    setTurns([]);
    conversationIdRef.current = undefined;
  }, []);

  return { turns, loading, ask, reset };
}
