"use client";

import { useEffect, useRef, useState } from "react";
import { useChat } from "@/hooks/useChat";
import ChatMessage from "@/components/ChatMessage";

const EXAMPLE_QUESTIONS = [
  "صاحب الشقة عايز يطردني قبل ما العقد يخلص",
  "الشركة فصلتني من غير إنذار ومش عايزة تديني مستحقاتي",
  "اشتريت منتج بايظ والمحل رافض يرجعه",
  "شيك بدون رصيد، أعمل إيه؟",
];

export default function AskPage() {
  const { turns, loading, ask } = useChat();
  const [question, setQuestion] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get("q");
    if (q) {
      setQuestion(q);
      inputRef.current?.focus();
    }
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    const q = question;
    setQuestion("");
    await ask(q);
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-12">
      <div className="border-b-[1.5px] border-ink pb-6">
        <h1 className="font-legal text-5xl font-bold leading-[1.25]">أنا أضع النص. غيري يضع الظنّ.</h1>
        <p className="mt-3 text-lg text-[#3A4450]">
          اكتب مشكلتك بلهجتك وبأكبر قدر من التفاصيل. كل ما تكتبه أدق، تكون الإجابة أدق.
        </p>
      </div>

      {turns.length === 0 ? (
        <div className="space-y-6">
          <p className="font-legal text-4xl font-bold leading-[1.4] text-seal">مش معنى إنك عملتها يبقى إنت مذنب.</p>
          <div>
            <p className="mb-2 text-[13px] font-semibold text-muted">أسئلة يسألها الناس</p>
            <div className="flex flex-wrap gap-2.5">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => {
                    setQuestion(q);
                    inputRef.current?.focus();
                  }}
                  className="border border-[#C9C1B2] px-4 py-2 text-[15px] hover:border-seal hover:text-seal"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-10">
          {turns.map((turn, i) => (
            <ChatMessage key={turn.id} turn={turn} pending={loading && i === turns.length - 1} />
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-[1.5px] border-ink bg-white">
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
          className="block w-full resize-none bg-transparent px-5 pb-3 pt-4 text-xl leading-[1.7] outline-none placeholder:text-[#8A929C] disabled:opacity-60"
        />
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-sand px-5 py-3">
          <span className="text-[13px] text-muted">Enter للإرسال · Shift+Enter لسطر جديد · لا تكتب بياناتك الشخصية</span>
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="min-h-12 bg-seal px-9 text-[17px] font-semibold text-white hover:bg-[#6F1C29] disabled:cursor-not-allowed disabled:bg-[#C9C1B2]"
          >
            {loading ? "جارٍ البحث..." : "احصل على الإجابة"}
          </button>
        </div>
      </form>
    </div>
  );
}