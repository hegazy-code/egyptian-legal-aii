interface DisclaimerProps {
  /** Override the default text (e.g. to show the backend's own tanbih text). */
  text?: string;
  className?: string;
}

const DEFAULT_TEXT =
  "هذه معلومات قانونية عامة وليست استشارة قانونية رسمية، ولا تُغني عن استشارة محامٍ مرخّص. قد تحتوي الإجابة على أخطاء أو تكون غير مكتملة، ولا يجوز الاعتماد عليها بمفردها في اتخاذ قرارات قانونية.";

/** Reusable "not a substitute for a licensed lawyer" banner (spec §22, §52). */
export default function Disclaimer({ text, className = "" }: DisclaimerProps) {
  return (
    <div
      role="note"
      className={`flex gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm leading-relaxed text-amber-900 dark:border-amber-700/60 dark:bg-amber-950/40 dark:text-amber-200 ${className}`}
    >
      <span aria-hidden className="shrink-0 text-lg leading-none">⚠️</span>
      <p className="font-medium">{text ?? DEFAULT_TEXT}</p>
    </div>
  );
}
