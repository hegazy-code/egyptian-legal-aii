"use client";

import { useRef, useState } from "react";
import { useChat } from "@/hooks/useChat";
import ChatMessage from "@/components/ChatMessage";
import Disclaimer from "@/components/Disclaimer";

const EXAMPLE_QUESTIONS = [
  "ما هي إجراءات فسخ عقد الإيجار قبل انتهاء مدته؟",
  "ما هي حقوق العامل عند الفصل التعسفي؟",
  "كيف أرفع دعوى مطالبة بدين تجاري؟",
];

export default function AskPage() {
  const { turns, loading, ask } = useChat();
  const [question, setQuestion] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    const q = question;
    setQuestion("");
    await ask(q);
  }

  function fillExampleQuestion(q: string) {
    setQuestion(q);
    inputRef.current?.focus();
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">اسأل سؤالك القانوني</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          اكتب سؤالك بوضوح وبأكبر قدر من التفاصيل للحصول على إجابة أدق.
        </p>
      </div>

      {turns.length === 0 ? (
        <div className="space-y-4">
          <Disclaimer />
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => fillExampleQuestion(q)}
                className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-teal-600 hover:text-teal-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:text-teal-400"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-8">
          {turns.map((turn, i) => (
            <ChatMessage key={turn.id} turn={turn} pending={loading && i === turns.length - 1} />
          ))}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="sticky bottom-4 flex flex-col gap-2 rounded-xl border border-slate-300 bg-white p-3 shadow-md dark:border-slate-700 dark:bg-slate-900"
      >
        <textarea
          ref={inputRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          rows={3}
          placeholder="اكتب سؤالك القانوني هنا..."
          disabled={loading}
          className="w-full resize-none rounded-lg border-0 bg-transparent p-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:opacity-60 dark:text-slate-100"
        />
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs text-slate-400">اضغط Enter للإرسال، Shift+Enter لسطر جديد</span>
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-lg bg-teal-700 px-5 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500 dark:disabled:bg-slate-700 dark:disabled:text-slate-400"
          >
            {loading ? "جارٍ الإرسال..." : "إرسال"}
          </button>
        </div>
      </form>
    </div>
  );
}
