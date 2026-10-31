import ComingSoon from "@/components/ComingSoon";

// TODO(backend): the entire /admin area needs authentication AND
// role-based access control (an "admin" role check) before it can be
// built for real -- backend/app currently has no auth or roles at all.
// Do not build any admin UI logic until that exists server-side, since an
// admin panel with no real access control would be a security hole.
export default function AdminPage() {
  return (
    <ComingSoon
      title="لوحة الإدارة"
      note="تتطلب هذه المنطقة نظام تسجيل دخول وصلاحيات (أدوار المستخدمين) قبل إتاحتها."
    />
  );
}
