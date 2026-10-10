import ComingSoon from "@/components/ComingSoon";

// TODO(backend): this page needs real user authentication (login/session)
// before it can show anything -- there is no user account system yet
// (backend/app has no auth routes/models implemented). Wire this up once
// POST /auth/login + a session/JWT mechanism exist.
export default function DashboardPage() {
  return <ComingSoon title="لوحة التحكم" note="تحتاج هذه الصفحة إلى نظام تسجيل دخول فعّال أولاً." />;
}
